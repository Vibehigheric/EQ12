import os
import google.generativeai as genai
from dotenv import load_dotenv
import requests

load_dotenv()

def check_google():
    print("\n--- Checking Google AI ---")
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    if not api_key:
        print("❌ GOOGLE_AI_API_KEY not found in env")
        return

    print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")
    genai.configure(api_key=api_key)
    try:
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

def check_github():
    print("\n--- Checking GitHub Models ---")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not found in env")
        return
    
    print(f"Token found: {token[:5]}...{token[-5:]}")
    
    url = "https://models.inference.ai.azure.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # Minimal payload for a check
    payload = {
        "messages": [{"role": "user", "content": "Hi"}],
        "model": "gpt-4o",
        "max_tokens": 5
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ GitHub Models API is working!")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting: {e}")

if __name__ == "__main__":
    check_google()
    check_github()
