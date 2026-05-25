import os
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def main():
    client = genai.Client(api_key=GEMINI_API_KEY)
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt='A delicious spicy tuna crispy rice roll',
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        for generated_image in result.generated_images:
            image_bytes = generated_image.image.image_bytes
            print(f"Success! Generated image of size {len(image_bytes)} bytes")
    except Exception as e:
        print(f"Failed: {e}")

asyncio.run(main())
