import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def cleanup_expired_deals():
    db_url = os.getenv("SUPABASE_DB_URL", "")
    if not db_url:
        print("Error: SUPABASE_DB_URL is not set.")
        return

    # Strip asyncpg dialect for native asyncpg connection
    clean_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    print("Connecting to database for cleanup...")
    try:
        conn = await asyncpg.connect(clean_url)
        
        # Delete deals where the expiration timestamp is strictly less than the current UTC time
        query = "DELETE FROM deals WHERE expires_at < timezone('utc'::text, now())"
        
        print("Executing cleanup query...")
        status = await conn.execute(query)
        
        # asyncpg execute returns a string like "DELETE 0"
        print(f"Cleanup completed successfully. Result: {status}")
        
        await conn.close()
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_expired_deals())
