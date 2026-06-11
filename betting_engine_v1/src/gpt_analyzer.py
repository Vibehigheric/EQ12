import os
import json
import glob
import requests
from datetime import datetime

import argparse

# Configuration
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
OUTPUT_FILE = os.path.join(LOGS_DIR, "gpt_picks.json")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def load_latest_odds(specific_file=None):
    """Finds the most recent odds JSON file in the logs directory, or uses a specific file."""
    if specific_file:
        if os.path.exists(specific_file):
            try:
                with open(specific_file, 'r') as f:
                    data = json.load(f)
                    return data, specific_file
            except Exception as e:
                print(f"Error reading {specific_file}: {e}")
                return None, None
        else:
            print(f"File not found: {specific_file}")
            return None, None

    pattern = os.path.join(LOGS_DIR, 'odds_*.json')
    list_of_files = glob.glob(pattern)
    
    if not list_of_files:
        print(f"No odds files found in {LOGS_DIR}")
        return None, None
        
    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
            return data, latest_file
    except Exception as e:
        print(f"Error reading {latest_file}: {e}")
        return None, None

def analyze_with_gpt(odds_data, source_file):
    """Sends odds data to GPT for analysis."""
    # HARDCODED KEY FOR TESTING
    api_key = "OPENROUTER_API_KEY_PLACEHOLDER"

    if not api_key:
        print("Error: API Key not set.")
        return None

    # Prepare a simplified summary for the prompt to save tokens
    games_summary = []
    for game in odds_data[:5]: # Analyze top 5 games to save tokens
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        bookmakers = game.get('bookmakers', [])
        
        if not bookmakers:
            continue
            
        # Get first bookmaker's odds (usually the best available in this dataset)
        markets = bookmakers[0].get('markets', [])
        if not markets:
            continue
            
        outcomes = markets[0].get('outcomes', [])
        odds_str = ", ".join([f"{o['name']}: {o['price']}" for o in outcomes])
        
        games_summary.append(f"{home_team} vs {away_team} | Odds: {odds_str}")

    prompt_content = "\n".join(games_summary)
    
    # Load system prompt from external file to allow for self-learning updates
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/prompts/betting_system_prompt.md"))
    try:
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(f"Warning: Prompt file not found at {prompt_path}. Using default.")
        system_prompt = """
        You are an expert sports betting analyst. 
        Your goal is to identify the best value bets and the safest locks from the provided list of games.
        
        Output strictly valid JSON with this structure:
        {
            "analysis_date": "YYYY-MM-DD",
            "smart_money": {
                "matchup": "Team A vs Team B",
                "pick": "Team Name",
                "odds": 0.0,
                "reasoning": "Short explanation of why this is good value."
            },
            "safe_money": {
                "matchup": "Team A vs Team B",
                "pick": "Team Name",
                "odds": 0.0,
                "reasoning": "Short explanation of why this is a safe bet."
            }
        }
        """

    # Load memory (Self-Learning Injection)
    memory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/learning_memory.md"))
    if os.path.exists(memory_path):
        try:
            with open(memory_path, "r") as f:
                memory_content = f.read()
            if memory_content:
                system_prompt += f"\n\n### LEARNING MEMORY (CRITICAL: DO NOT REPEAT THESE MISTAKES)\n{memory_content}"
                print(" [MEMORY] Injected past lessons into System Prompt.")
        except Exception as e:
            print(f"Warning: Could not load memory: {e}")

    user_prompt = f"Analyze these games from {os.path.basename(source_file)}:\n\n{prompt_content}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/EQ12", # Optional, for including your app on openrouter.ai rankings.
        "X-Title": "EQ12 Betting Engine" # Optional. Shows in rankings on openrouter.ai.
    }

    payload = {
        "model": "openai/gpt-4o", # OpenRouter model format
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": { "type": "json_object" },
        "temperature": 0.7
    }

    print("Sending request to OpenRouter...")
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        if response:
            print(response.text)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze odds with GPT")
    parser.add_argument("--file", help="Specific JSON odds file to analyze")
    args = parser.parse_args()

    print("Starting GPT Analysis...")
    data, filename = load_latest_odds(args.file)
    
    if data:
        print(f"Loaded data from {filename}")
        picks = analyze_with_gpt(data, filename)
        
        if picks:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(picks, f, indent=2)
            print(f"✅ Analysis complete. Picks saved to {OUTPUT_FILE}")
        else:
            print("❌ Analysis failed.")
    else:
        print("❌ No data to analyze.")
