import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# We strip the +asyncpg so asyncpg can parse the standard postgresql url
url = os.getenv("SUPABASE_DB_URL", "").replace("postgresql+asyncpg://", "postgresql://")

async def apply_schema():
    print("Connecting to Supabase...")
    try:
        conn = await asyncpg.connect(url)
        with open("../supabase_schema.sql", "r") as f:
            sql = f.read()
            
        print("Applying SQL schema...")
        await conn.execute(sql)
        print("Schema applied successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error applying schema: {e}")

if __name__ == "__main__":
    asyncio.run(apply_schema())
