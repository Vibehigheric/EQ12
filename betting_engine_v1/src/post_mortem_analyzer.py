import os
import json
import argparse
import requests
from datetime import datetime

# Configuration
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))
PICKS_FILE = os.path.join(LOGS_DIR, "gpt_picks.json")
PROMPT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/prompts/betting_system_prompt.md"))
EVOLUTION_LOG = os.path.join(LOGS_DIR, "prompt_evolution_log.md")

# HARDCODED KEY (Same as gpt_analyzer.py)
OPENAI_API_KEY = "OPENROUTER_API_KEY_PLACEHOLDER"

def load_picks():
    """Loads the last set of picks made by the AI."""
    if not os.path.exists(PICKS_FILE):
        print(f"Error: No picks file found at {PICKS_FILE}")
        return None
    try:
        with open(PICKS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading picks file: {e}")
        return None

def load_current_prompt():
    """Loads the current system prompt."""
    if not os.path.exists(PROMPT_FILE):
        print(f"Error: No prompt file found at {PROMPT_FILE}")
        return None
    with open(PROMPT_FILE, 'r') as f:
        return f.read()

def get_reflection_from_gpt(current_prompt, picks, actual_results, analysis):
    """Asks GPT-4o to improve the system prompt based on the loss."""
    
    meta_prompt = f"""
    You are the "AI Supervisor" for a sports betting bot.
    The bot recently made some bad picks. Your job is to REWRITE the bot's System Prompt to fix its logic.

    ---
    CURRENT SYSTEM PROMPT:
    {current_prompt}
    ---

    THE BOT'S PICKS:
    {json.dumps(picks, indent=2)}

    ACTUAL RESULTS:
    {json.dumps(actual_results, indent=2)}

    ANALYSIS OF FAILURE:
    {analysis}

    ---
    INSTRUCTIONS:
    1. Analyze why the bot failed based on the results.
    2. Rewrite the System Prompt to include specific rules or "mental models" to prevent this mistake again.
    3. Keep the JSON output format EXACTLY the same as the original prompt.
    4. Output ONLY the new System Prompt text. Do not add markdown code blocks or explanations.
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://eq12.local", 
        "X-Title": "EQ12 Post-Mortem"
    }

    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": "You are an expert AI prompt engineer."},
            {"role": "user", "content": meta_prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling OpenRouter: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="EQ12 Post-Mortem Analyzer (Self-Learning Engine)")
    parser.add_argument("--result", type=str, help="JSON string of actual results (e.g., '{\"winner\": \"Ravens\"}')", required=True)
    parser.add_argument("--analysis", type=str, help="Your human analysis of why it lost (e.g., 'Ravens QB was injured')", default="General underperformance.")
    
    args = parser.parse_args()

    print("🧠 EQ12 Post-Mortem Engine Starting...")
    
    # 1. Load Data
    picks = load_picks()
    if not picks:
        return

    current_prompt = load_current_prompt()
    if not current_prompt:
        return

    # 2. Parse Results
    try:
        actual_results = json.loads(args.result)
    except json.JSONDecodeError:
        print("Error: --result must be valid JSON string.")
        return

    print(f"📉 Analyzing failure for picks: {json.dumps(picks, indent=2)}")
    print(f"🔍 Human Insight: {args.analysis}")

    # 3. Call the Reflector AI
    print("🤔 Consulting the Supervisor AI (OpenRouter)...")
    new_prompt = get_reflection_from_gpt(current_prompt, picks, actual_results, args.analysis)

    if new_prompt:
        # 4. Save the New Prompt
        print("💡 Supervisor has generated a new System Prompt!")
        
        # Backup old prompt
        backup_path = PROMPT_FILE + ".bak"
        with open(backup_path, 'w') as f:
            f.write(current_prompt)
        print(f"Start backup saved to {backup_path}")

        # Write new prompt
        with open(PROMPT_FILE, 'w') as f:
            f.write(new_prompt)
        
        # Log the evolution
        log_entry = f"""
## Evolution Event: {datetime.now().isoformat()}
**Reason**: {args.analysis}
**Changes**: Updated system prompt to address recent losses.
---
"""
        with open(EVOLUTION_LOG, 'a') as f:
            f.write(log_entry)
            
        print(f"✅ SUCCESS: System Prompt updated. The bot is now smarter.")
        print(f"📂 New Prompt saved to: {PROMPT_FILE}")
    else:
        print("❌ Failed to generate new prompt.")

if __name__ == "__main__":
    main()
