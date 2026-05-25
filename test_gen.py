import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv("backend/.env")

from backend.app.services.processing import generate_food_image
import uuid

async def main():
    deal_id = str(uuid.uuid4())
    url = await generate_food_image("Spicy Tuna Crispy Rice", deal_id)
    print("FINAL URL:", url)

asyncio.run(main())
