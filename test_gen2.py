import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv(".env")

from backend.app.services.processing import generate_food_image
import uuid
import sys

async def main():
    deal_id = str(uuid.uuid4())
    import urllib.parse
    prompt = "Delicious professional food photography of burger, studio lighting, appetizing"
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=800&nologo=true&model=flux&seed={deal_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=30.0)
            resp.raise_for_status()
            image_bytes = resp.content
            
            filename = f"{deal_id}.jpg"
            
            from supabase import create_client
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
            
            def upload_to_supabase():
                res = supabase.storage.from_("deals").upload(
                    path=filename, 
                    file=image_bytes, 
                    file_options={"content-type": "image/jpeg", "upsert": "true"}
                )
                return supabase.storage.from_("deals").get_public_url(filename)
                
            public_url = await asyncio.to_thread(upload_to_supabase)
            print("FINAL URL:", public_url)
    except Exception as e:
        print(f"FAILED WITH EXCEPTION: {repr(e)}")

asyncio.run(main())
