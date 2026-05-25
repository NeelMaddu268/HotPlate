import asyncio
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

from backend.app.services.processing import parse_sms_with_gemini

async def main():
    print("Testing parse_sms_with_gemini...")
    try:
        deal = await asyncio.wait_for(parse_sms_with_gemini("Donut"), timeout=15.0)
        print("Success:", deal)
    except Exception as e:
        print("Error parsing:", type(e), e)

asyncio.run(main())
