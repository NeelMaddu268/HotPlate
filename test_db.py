import asyncio
import asyncpg

async def main():
    try:
        conn = await asyncpg.connect("postgresql://postgres.knxzhvjrvdpyphmrkgmw:BigPotato12!%40@aws-1-us-east-1.pooler.supabase.com:5432/postgres")
        # Check if restaurant exists first to avoid duplicate constraint errors
        val = await conn.fetchval("SELECT id FROM restaurants WHERE phone_number = '+14708075701'")
        if not val:
            await conn.execute("INSERT INTO restaurants (name, phone_number, zip_code) VALUES ('Neel Restaurant', '+14708075701', '30040')")
            print("Inserted restaurant!")
        else:
            print("Restaurant already exists!")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
