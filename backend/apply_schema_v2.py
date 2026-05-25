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
        with open("schema_v2.sql", "r") as f:
            sql = f.read()
            
        print("Applying SQL schema v2...")
        await conn.execute(sql)
        print("Schema v2 applied successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error applying schema v2: {e}")

if __name__ == "__main__":
    asyncio.run(apply_schema())
