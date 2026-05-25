import asyncio
from datetime import datetime, timedelta
from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine
from backend.app.models import Deal

async def main():
    async with AsyncSession(engine) as session:
        new_expires = datetime.utcnow() + timedelta(hours=24)
        stmt = update(Deal).where(Deal.item_name == 'Donut').values(expires_at=new_expires)
        await session.execute(stmt)
        await session.commit()
        print("Updated Donut deal expiration to 24 hours from now!")

asyncio.run(main())
