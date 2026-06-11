import os
import json
import argparse
import requests

# Configuration
OPENAI_API_KEY = "OPENROUTER_API_KEY_PLACEHOLDER" # Hardcoded for demo, move to env in prod
API_URL = "https://openrouter.ai/api/v1/chat/completions"

META_PROMPT_SYSTEM = """
You are the "Meta-Prompter", an expert AI Prompt Engineer.
Your goal is to take a vague user request and transform it into a PERFECT, HIGH-PERFORMANCE SYSTEM PROMPT for an LLM.

Follow this Chain of Thought:
1. **Analyze the Goal**: What is the user actually trying to achieve? What are the hidden requirements?
2. **Define the Persona**: Who should the AI be? (e.g., "Senior Python Architect", "Marketing Genius").
3. **Set Constraints**: What should the AI *not* do? (e.g., "No markdown", "JSON only").
4. **Define Output Format**: How exactly should the response look?
5. **Draft the Prompt**: Write the actual system prompt.

Output ONLY the final System Prompt in a code block. Do not output the reasoning.
"""

def generate_perfect_prompt(user_goal):
    """Generates a high-quality system prompt from a vague goal."""
    print(f"🧠 Meta-Prompter is thinking about: '{user_goal}'...")
    
    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": META_PROMPT_SYSTEM},
            {"role": "user", "content": f"Generate a system prompt for this goal: {user_goal}"}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://eq12.cluster", 
        "X-Title": "EQ12 Meta-Prompter"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        
        # Extract content from code blocks if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("markdown") or content.startswith("text"):
                content = content.split("\n", 1)[1]
        
        return content.strip()
        
    except Exception as e:
        print(f"Error generating prompt: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EQ12 Meta-Prompter")
    parser.add_argument("goal", help="The vague goal you want to turn into a perfect prompt")
    parser.add_argument("--save", help="Path to save the generated prompt", default=None)
    
    args = parser.parse_args()
    
    perfect_prompt = generate_perfect_prompt(args.goal)
    
    if perfect_prompt:
        print("\n=== ✨ GENERATED PERFECT PROMPT ✨ ===\n")
        print(perfect_prompt)
        print("\n======================================\n")
        
        if args.save:
            with open(args.save, "w") as f:
                f.write(perfect_prompt)
            print(f"Saved to {args.save}")
