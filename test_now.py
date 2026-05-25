import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine

async def main():
    async with AsyncSession(engine) as session:
        query = text("""
            SELECT d.item_name, d.expires_at, d.expires_at > NOW() as is_valid
            FROM deals d
        """)
        result = await session.execute(query)
        for row in result.fetchall():
            print(row)
        
asyncio.run(main())
