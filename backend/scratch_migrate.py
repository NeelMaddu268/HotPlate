import asyncio
import os
import httpx
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
from app.core.db import engine
from app.models import Deal

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Deal))
        deals = result.scalars().all()
        
    async with httpx.AsyncClient() as client:
        for deal in deals:
            # Only migrate if not already a supabase URL
            if "supabase.co/storage" in deal.image_url:
                continue
                
            print(f"Migrating {deal.item_name}...")
            try:
                # 1. Download image
                resp = await client.get(deal.image_url, timeout=30.0)
                resp.raise_for_status()
                image_bytes = resp.content
                
                # 2. Upload to Supabase Storage
                filename = f"{deal.id}.jpg"
                res = supabase.storage.from_("deals").upload(
                    path=filename, 
                    file=image_bytes, 
                    file_options={"content-type": "image/jpeg", "upsert": "true"}
                )
                
                # 3. Get public URL
                public_url = supabase.storage.from_("deals").get_public_url(filename)
                
                # 4. Update Database
                async with AsyncSession(engine) as session:
                    await session.execute(update(Deal).where(Deal.id == deal.id).values(image_url=public_url))
                    await session.commit()
                
                print(f"  Success: {public_url}")
            except Exception as e:
                print(f"  Failed: {e}")

asyncio.run(main())
