import json
import os
import copy

# Configuration
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../n8n/generated"))
BASE_WORKFLOW_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../n8n/workflow.json"))

# Matrix of Products
SPORTS = [
    {"key": "americanfootball_nfl", "name": "NFL", "emoji": "🏈"},
    {"key": "basketball_nba", "name": "NBA", "emoji": "🏀"},
    {"key": "icehockey_nhl", "name": "NHL", "emoji": "🏒"},
    {"key": "mma_mixed_martial_arts", "name": "UFC", "emoji": "🥊"},
    {"key": "soccer_epl", "name": "EPL", "emoji": "⚽"},
    {"key": "baseball_mlb", "name": "MLB", "emoji": "⚾"},
    {"key": "cricket_ipl", "name": "IPL", "emoji": "🏏"},
    {"key": "tennis_atp", "name": "ATP Tennis", "emoji": "🎾"}
]

STRATEGIES = [
    {"key": "safe_lock", "name": "Safe Lock", "risk_level": "Low", "prompt_modifier": "Focus ONLY on heavy favorites with >70% win probability."},
    {"key": "value_underdog", "name": "Value Underdog", "risk_level": "High", "prompt_modifier": "Focus ONLY on underdogs with positive expected value (EV+)."},
    {"key": "arbitrage_hunter", "name": "Arb Hunter", "risk_level": "Zero", "prompt_modifier": "Identify discrepancies between bookmakers where a guaranteed profit exists."},
    {"key": "parlay_builder", "name": "Parlay Builder", "risk_level": "Medium", "prompt_modifier": "Construct a 3-leg parlay with correlated outcomes."}
]

def load_base_workflow():
    if not os.path.exists(BASE_WORKFLOW_PATH):
        print(f"Error: Base workflow not found at {BASE_WORKFLOW_PATH}")
        return None
    with open(BASE_WORKFLOW_PATH, 'r') as f:
        return json.load(f)

def generate_workflows():
    base_workflow = load_base_workflow()
    if not base_workflow:
        return

    count = 0
    print(f"🏭 Starting Workflow Factory...")
    print(f"📍 Output Directory: {OUTPUT_DIR}")

    for sport in SPORTS:
        for strategy in STRATEGIES:
            # Create a deep copy of the base workflow
            new_workflow = copy.deepcopy(base_workflow)
            
            # Customize Metadata
            product_name = f"EQ12 {sport['name']} {strategy['name']} Engine"
            new_workflow['name'] = product_name
            
            # Customize Nodes (Mocking the customization logic)
            # In a real scenario, we would inject specific Python arguments or SQL queries here
            for node in new_workflow['nodes']:
                if node['name'] == "Telegram Alert":
                    # Customize the alert message
                    current_text = node['parameters']['text']
                    custom_header = f"{sport['emoji']} **{product_name}** {sport['emoji']}\nRisk: {strategy['risk_level']}\n\n"
                    node['parameters']['text'] = custom_header + current_text
                
                if node['name'] == "Analyze with GPT":
                    # Inject the strategy into the command arguments (conceptually)
                    # We would update the python script to accept --sport and --strategy args
                    cmd = node['parameters']['command']
                    node['parameters']['command'] = f"{cmd} --sport {sport['key']} --strategy {strategy['key']}"

            # Save the new workflow file
            filename = f"workflow_{sport['key']}_{strategy['key']}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w') as f:
                json.dump(new_workflow, f, indent=2)
            
            count += 1
            # print(f"  -> Generated: {filename}")

    print(f"✅ Factory Run Complete.")
    print(f"🚀 Total Products Created: {count}")
    print(f"💰 Potential Revenue (at $50/setup): ${count * 50}")

if __name__ == "__main__":
    generate_workflows()
