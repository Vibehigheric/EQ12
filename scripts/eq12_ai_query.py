"""
EQ12 AI Query Helper - Multi-Provider AI with Auto-Fallback
Supports: OpenAI → Groq → OpenRouter → Claude
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_env_keys():
    """Load API keys from .env"""
    env_path = Path(__file__).parent.parent / ".env"
    keys = {}
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    keys[key.strip()] = value.strip().strip('"')
    
    return keys

def query_groq(prompt, model="llama-3.1-70b-versatile"):
    """Fallback to Groq (FREE, fast)"""
    try:
        import requests
        keys = load_env_keys()
        api_key = keys.get("GROQ_API_KEY")
        
        if not api_key:
            return None
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
        
    except Exception:
        return None

def query_openrouter(prompt, model="meta-llama/llama-3.1-70b-instruct"):
    """Fallback to OpenRouter (many models)"""
    try:
        import requests
        keys = load_env_keys()
        api_key = keys.get("OPENROUTER_API_KEY")
        
        if not api_key:
            return None
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://eq12.com",
                "X-Title": "EQ12 AI System"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return None
        
    except Exception:
        return None

def query_claude(prompt):
    """Fallback to Claude (Anthropic)"""
    try:
        import requests
        keys = load_env_keys()
        api_key = keys.get("claud ai key")  # Your key name format
        
        if not api_key:
            return None
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-sonnet-20240229",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        return None
        
    except Exception:
        return None

def query_with_fallback(prompt, model="gpt-4o"):
    """Try OpenAI first, then fallback to alternatives"""
    
    # Try OpenAI first
    try:
        from eq12_openai_client import query_openai
        result = query_openai(prompt, model=model)
        
        # Check if it's an error message
        if not result.startswith("❌"):
            return f"[OpenAI] {result}"
    except Exception:
        pass
    
    # Fallback 1: Groq (FREE and FAST)
    result = query_groq(prompt)
    if result:
        return f"[Groq/Llama-3.1-70B] {result}"
    
    # Fallback 2: OpenRouter
    result = query_openrouter(prompt)
    if result:
        return f"[OpenRouter/Llama-3.1-70B] {result}"
    
    # Fallback 3: Claude
    result = query_claude(prompt)
    if result:
        return f"[Claude-3-Sonnet] {result}"
    
    # All providers failed
    return "❌ All AI providers failed. Check API keys in .env:\n- OPENAI_API_KEY (quota issue)\n- GROQ_API_KEY (free alternative)\n- OPENROUTER_API_KEY\n- claud ai key"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python eq12_ai_query.py <question> [model]")
        sys.exit(1)
    
    question = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gpt-4o"
    
    result = query_with_fallback(question, model=model)
    print(result)
