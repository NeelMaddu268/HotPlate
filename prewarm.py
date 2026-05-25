import asyncio
import httpx
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Deal))
        deals = result.scalars().all()
        
    async with httpx.AsyncClient() as client:
        for d in deals:
            print(f"Warming cache for {d.item_name}...")
            try:
                await client.get(d.image_url, timeout=30.0)
                print("  Success")
            except Exception as e:
                print(f"  Error: {e}")

asyncio.run(main())
