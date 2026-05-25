import asyncio
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

from backend.app.services.processing import parse_sms_with_gemini, generate_food_image, generate_embedding

async def main():
    print("Testing parse_sms_with_gemini...")
    try:
        deal = await parse_sms_with_gemini("Donut")
        print("Success:", deal)
    except Exception as e:
        print("Error parsing:", e)
        return

    print("Testing generate_food_image...")
    try:
        img = await generate_food_image("Donut")
        print("Success img:", img)
    except Exception as e:
        print("Error img:", e)

    print("Testing generate_embedding...")
    try:
        emb = await generate_embedding("Donut")
        print("Success emb len:", len(emb))
    except Exception as e:
        print("Error emb:", e)

asyncio.run(main())
