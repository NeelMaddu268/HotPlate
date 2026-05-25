import asyncio
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Deal).where(Deal.item_name.contains('Cookie')))
        for d in result.scalars().all():
            print(f"Deal: {d.item_name}")
            print(f"Image: {d.image_url}")
        
asyncio.run(main())
