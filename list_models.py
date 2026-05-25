import os
from google import genai
from dotenv import load_dotenv

load_dotenv(".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
for m in client.models.list():
    if "imagen" in m.name or "image" in m.name:
        print(m.name)
