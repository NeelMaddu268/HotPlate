import asyncio
from backend.app.services.processing import generate_embedding
from dotenv import load_dotenv

load_dotenv("backend/.env")

async def main():
    embed = await generate_embedding("burger")
    print(len(embed))

asyncio.run(main())
