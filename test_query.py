import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("backend/.env")
from backend.app.core.db import engine

async def main():
    async with AsyncSession(engine) as session:
        now = datetime.utcnow()
        print("Now:", now)
        query = text("""
            SELECT d.item_name, d.expires_at, d.expires_at > :now as is_valid
            FROM deals d
        """)
        result = await session.execute(query, {"now": now})
        for row in result.fetchall():
            print(row)
        
asyncio.run(main())
