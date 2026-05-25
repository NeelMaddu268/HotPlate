import asyncio
import urllib.parse
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
            prompt = f"Delicious professional food photography of {deal.item_name}, studio lighting, appetizing"
            encoded_prompt = urllib.parse.quote(prompt)
            new_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=800&nologo=true"
            stmt = update(Deal).where(Deal.id == deal.id).values(image_url=new_url)
            await session.execute(stmt)
        await session.commit()
        print("Updated all existing images!")

asyncio.run(main())
