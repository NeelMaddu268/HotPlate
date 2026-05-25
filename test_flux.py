import os
import requests
from dotenv import load_dotenv

load_dotenv(".env")
FLUX_API_KEY = os.getenv("FLUX_API_KEY")

try:
    response = requests.post(
        "https://api.bfl.ml/v1/flux-pro-1.1",
        headers={"x-key": FLUX_API_KEY, "Content-Type": "application/json"},
        json={"prompt": "burger"},
        timeout=5
    )
    print(response.status_code, response.text)
except Exception as e:
    print(e)
