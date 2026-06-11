import google.generativeai as genai
import os

# Hardcoded key from the client file
api_key = "GOOGLE_API_KEY_PLACEHOLDER"
genai.configure(api_key=api_key)

print("Listing available Google AI models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
