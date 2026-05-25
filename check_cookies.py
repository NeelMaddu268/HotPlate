import asyncio
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal
from datetime import datetime

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Deal))
        for d in result.scalars().all():
            print(f"Deal: {d.item_name}")
            print(f"  Expires: {d.expires_at} (Now: {datetime.utcnow()})")
            print(f"  Similarity to 'cookie': (skipping full math)")
        
asyncio.run(main())
