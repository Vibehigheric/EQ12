"""
EQ12 SWARM DEPLOYER
Reads the manifest and 'spins up' the agent architecture.
(Simulation Mode: Creates the directory structure and config files for each agent)
"""
import yaml
import os
import json

MANIFEST_PATH = "config/agent_swarm_manifest.yaml"
AGENTS_ROOT = "src/agents"

def deploy_swarm():
    print("🐝 Deploying EQ12 Agent Swarm...")
    
    with open(MANIFEST_PATH, "r") as f:
        manifest = yaml.safe_load(f)

    # 1. Deploy Master
    master = manifest["master"]
    deploy_agent("master", master["name"], master)

    # 2. Deploy Core
    for agent in manifest["core_assistants"]:
        deploy_agent("core", agent["name"], agent)

    # 3. Deploy Workers
    for agent in manifest["workers"]:
        deploy_agent("workers", agent["name"], agent)

    print(f"✅ Swarm Deployed. Structure created in {AGENTS_ROOT}")

def deploy_agent(category, name, config):
    # Create Folder
    agent_dir = os.path.join(AGENTS_ROOT, category, name)
    os.makedirs(agent_dir, exist_ok=True)
    
    # Create Config
    with open(os.path.join(agent_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)
    
    # Create 'Brain' (Placeholder)
    with open(os.path.join(agent_dir, "brain.py"), "w") as f:
        f.write(f"# Brain for {name}\n")
        f.write("def think():\n    print('I am alive.')\n")

    print(f"   - [Created] {category}/{name}")

if __name__ == "__main__":
    deploy_swarm()
