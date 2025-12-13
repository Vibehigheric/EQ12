import json
import argparse
import os
import random

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), '../config/prompts/system_prompts_100.json')

def load_prompts():
    if not os.path.exists(PROMPTS_FILE):
        print(f"Error: Prompts file not found at {PROMPTS_FILE}")
        return None
    with open(PROMPTS_FILE, 'r') as f:
        return json.load(f)

def list_categories(prompts):
    print("Available Categories:")
    for category in prompts.keys():
        print(f" - {category}")

def get_prompt(prompts, category=None, index=None, random_mode=False):
    if random_mode:
        cat = random.choice(list(prompts.keys()))
        prompt = random.choice(prompts[cat])
        return f"[{cat}] {prompt}"
    
    if category:
        if category not in prompts:
            print(f"Error: Category '{category}' not found.")
            return None
        
        if index is not None:
            if 0 <= index < len(prompts[category]):
                return prompts[category][index]
            else:
                print(f"Error: Index {index} out of range for category '{category}'.")
                return None
        else:
            # Return all in category
            return "\n".join([f"{i}. {p}" for i, p in enumerate(prompts[category])])
    
    return None

def main():
    parser = argparse.ArgumentParser(description="EQ12 System Prompt Runner")
    parser.add_argument('--list', action='store_true', help="List all categories")
    parser.add_argument('--category', type=str, help="Select a category")
    parser.add_argument('--index', type=int, help="Select a specific prompt index within a category")
    parser.add_argument('--random', action='store_true', help="Get a random powerful prompt")
    parser.add_argument('--dump', action='store_true', help="Dump all prompts")

    args = parser.parse_args()
    prompts = load_prompts()

    if not prompts:
        return

    if args.list:
        list_categories(prompts)
    elif args.random:
        print(get_prompt(prompts, random_mode=True))
    elif args.category:
        result = get_prompt(prompts, category=args.category, index=args.index)
        if result:
            print(result)
    elif args.dump:
        print(json.dumps(prompts, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
