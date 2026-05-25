import asyncio
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Deal).where(Deal.item_name.contains('Cookie')))
        deal = result.scalars().first()
        if deal:
            new_url = deal.image_url + "&v=2"
            await session.execute(update(Deal).where(Deal.id == deal.id).values(image_url=new_url))
            await session.commit()
            print("Cache busted!")
        
asyncio.run(main())
