import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
if not token:
    # Fallback to the one found in .env
    token = os.getenv("GITHUB_TOKEN_2")

url = "https://models.inference.ai.azure.com/models"
headers = {"Authorization": f"Bearer {token}"}

print(f"Listing GitHub models with token: {token[:4]}...")
try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json()
        for m in models:
            print(f"- {m.get('name')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Exception: {e}")
