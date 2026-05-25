import os
import asyncio
import httpx
from datetime import datetime, timedelta
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional
import uuid
from supabase import create_client, Client

from app.models import Restaurant, Deal
from app.core.db import engine

# Initialize Gemini Client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FLUX_API_KEY = os.getenv("FLUX_API_KEY")

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class DealSchema(BaseModel):
    item_name: str
    price: float
    expires_in_hours: int

async def verify_restaurant(phone_number: str) -> Optional[Restaurant]:
    """Verify if the incoming phone number belongs to a registered restaurant."""
    # Normalize phone number (e.g., ensure it starts with +, no spaces)
    normalized = phone_number.replace(" ", "").replace("-", "")
    if not normalized.startswith("+"):
        normalized = "+" + normalized

    async with AsyncSession(engine) as session:
        statement = select(Restaurant).where(Restaurant.phone_number == normalized)
        result = await session.execute(statement)
        return result.scalars().first()

async def parse_sms_with_gemini(text: str) -> DealSchema:
    """Parse the SMS text using Gemini 1.5 Flash to extract deal info."""
    # We must run synchronous google-genai client in a thread pool for true async, 
    # but google.genai supports async natively in newer versions.
    # Assuming google-genai provides async client:
    
    # Due to google-genai 2.x API:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Create an async wrapper for the synchronous call if needed, 
    # but typically it's fine to use asyncio.to_thread for network calls.
    def call_gemini():
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Extract the deal from this SMS: '{text}'",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DealSchema,
                ),
            )
        except Exception as e:
            print(f"gemini-2.5-flash failed ({e}), falling back to gemini-2.5-flash-lite...")
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=f"Extract the deal from this SMS: '{text}'",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DealSchema,
                ),
            )
        return response.text
        
    response_text = await asyncio.to_thread(call_gemini)
    return DealSchema.model_validate_json(response_text)

async def generate_food_image(item_name: str, deal_id: str) -> str:
    """Generate an 8k food photo using Pollinations AI (Flux model), download it, and upload to Supabase Storage."""
    import urllib.parse
    prompt = f"Delicious professional food photography of {item_name}, studio lighting, appetizing"
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Using model=flux bypasses the default model's strict rate limit
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=800&nologo=true&model=flux&seed={deal_id}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=120.0)
                resp.raise_for_status()
                image_bytes = resp.content
                
                filename = f"{deal_id}.jpg"
                def upload_to_supabase():
                    supabase.storage.from_("deals").upload(
                        path=filename, 
                        file=image_bytes, 
                        file_options={"content-type": "image/jpeg", "upsert": "true"}
                    )
                    return supabase.storage.from_("deals").get_public_url(filename)
                    
                return await asyncio.to_thread(upload_to_supabase)
        except Exception as e:
            print(f"Warning: Image generation failed on attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt) # Exponential backoff
            
    # If all retries fail, return a gradient placeholder instead of a completely unrelated stock photo
    return f"https://placehold.co/800x800/f43f5e/ffffff.png?text={urllib.parse.quote(item_name)}"

async def generate_embedding(item_name: str) -> list[float]:
    """Generate 768-d vector using text-embedding-004."""
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your"):
        print(f"[DEBUG] Mocking embedding for {item_name}")
        return [0.0] * 768

    client = genai.Client(api_key=GEMINI_API_KEY)
    def call_embedding():
        result = client.models.embed_content(
            model='gemini-embedding-001',
            contents=item_name
        )
        # The model returns a 3072-dimensional vector, but our database is setup for 768.
        # We truncate the list to exactly 768 dimensions.
        return result.embeddings[0].values[:768]

    return await asyncio.to_thread(call_embedding)

# Feature flag to toggle between instant publishing and wait-for-assets
INSTANT_PUBLISH = True

async def generate_assets_background(deal_id: uuid.UUID, item_name: str):
    """Background task to generate assets and update the DB."""
    try:
        image_url, embedding = await asyncio.gather(
            generate_food_image(item_name, str(deal_id)),
            generate_embedding(item_name)
        )
    except Exception as e:
        print(f"Failed to generate assets: {e}")
        return

    # Update database
    from sqlmodel import update
    async with AsyncSession(engine) as session:
        statement = update(Deal).where(Deal.id == deal_id).values(
            image_url=image_url,
            embedding=embedding
        )
        await session.execute(statement)
        await session.commit()
    print(f"Assets updated in background for deal {deal_id}")

async def process_sms_workflow(phone_number: str, sms_body: str):
    """The main async workflow that orchestrates the sub-tasks."""
    print(f"Starting async workflow for {phone_number}: {sms_body}")
    
    # 1. Verify Restaurant
    restaurant = await verify_restaurant(phone_number)
    if not restaurant:
        print(f"Unauthorized phone number: {phone_number}")
        return

    # 2. Parse SMS
    try:
        deal_info = await parse_sms_with_gemini(sms_body)
    except Exception as e:
        print(f"Failed to parse SMS: {e}")
        return

    # Generate Deal ID upfront to use for image filename
    deal_id = uuid.uuid4()
    hours = deal_info.expires_in_hours if deal_info.expires_in_hours > 0 else 24
    expires_at = datetime.utcnow() + timedelta(hours=hours)

    if INSTANT_PUBLISH:
        import urllib.parse
        # Insert immediately with placeholders
        loading_url = "https://placehold.co/800x800/f43f5e/ffffff.png?text=Generating+Image..."
        new_deal = Deal(
            id=deal_id,
            restaurant_id=restaurant.id,
            item_name=deal_info.item_name,
            price=deal_info.price,
            image_url=loading_url,
            # Use a near-zero vector to avoid divide-by-zero errors in cosine similarity
            embedding=[0.0001] * 768, 
            expires_at=expires_at
        )
        async with AsyncSession(engine) as session:
            session.add(new_deal)
            await session.commit()
        
        # Run asset generation in background
        asyncio.create_task(generate_assets_background(deal_id, deal_info.item_name))
        print(f"Instantly published deal: {deal_info.item_name} (generating assets in background)")
    else:
        # Old behavior: wait for assets, then insert
        try:
            image_url, embedding = await asyncio.gather(
                generate_food_image(deal_info.item_name, str(deal_id)),
                generate_embedding(deal_info.item_name)
            )
        except Exception as e:
            print(f"Failed to generate assets: {e}")
            return
            
        new_deal = Deal(
            id=deal_id,
            restaurant_id=restaurant.id,
            item_name=deal_info.item_name,
            price=deal_info.price,
            image_url=image_url,
            embedding=embedding,
            expires_at=expires_at
        )
        async with AsyncSession(engine) as session:
            session.add(new_deal)
            await session.commit()
            
        print(f"Successfully processed deal: {deal_info.item_name}")
