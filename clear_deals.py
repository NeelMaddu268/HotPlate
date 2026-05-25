import asyncio
from sqlmodel import delete
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal

async def main():
    async with AsyncSession(engine) as session:
        await session.execute(delete(Deal))
        await session.commit()
        print("Successfully wiped all deals from the database.")
        
asyncio.run(main())
