import asyncio
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal

async def main():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Deal))
        deals = result.scalars().all()
        for deal in deals:
            # Avoid appending multiple seeds if already present
            if "&seed=" not in deal.image_url:
                new_url = deal.image_url + "&seed=42"
                await session.execute(update(Deal).where(Deal.id == deal.id).values(image_url=new_url))
        await session.commit()
        print("Updated all images to use deterministic seeds!")
        
asyncio.run(main())
