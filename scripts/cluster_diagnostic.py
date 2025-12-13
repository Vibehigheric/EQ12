import os
import json
import logging
from datetime import datetime

# --- CONFIGURATION ---
LOG_DIR = "logs"
REPORT_FILE = os.path.join(LOG_DIR, "cluster_diagnostic_report.json")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_ssh(host, user):
    """Checks SSH connectivity."""
    cmd = f"ssh -o BatchMode=yes -o ConnectTimeout=5 {user}@{host} echo 'OK'"
    return os.system(cmd) == 0

def check_docker_context_size(path):
    """Estimates build context size (excluding ignored files is hard without docker CLI, 
       so we just check for massive folders that SHOULD be ignored)."""
    # This is a heuristic check
    large_folders = [".venv", ".venv_wsl", "node_modules", "EdgeGodParlays"]
    found_large = []
    for folder in large_folders:
        full_path = os.path.join(path, folder)
        if os.path.exists(full_path):
            # Check if it's in .dockerignore (simple check)
            with open(os.path.join(path, ".dockerignore"), "r") as f:
                content = f.read()
                if folder not in content and f"{folder}/" not in content:
                     found_large.append(folder)
    return found_large

def main():
    logging.info("Starting Cluster Diagnostic...")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "nodes": {
            "M70q": {"ip": "192.168.100.3", "status": "unknown"},
            "Pi5":  {"ip": "192.168.100.4", "status": "unknown"}
        },
        "build_context_issues": []
    }

    # Check Nodes
    for node, data in report["nodes"].items():
        if check_ssh(data["ip"], "ricoj100"):
            data["status"] = "online"
            logging.info(f"✔ {node} is ONLINE")
        else:
            data["status"] = "offline"
            logging.error(f"❌ {node} is OFFLINE")

    # Check Context
    issues = check_docker_context_size(".")
    if issues:
        report["build_context_issues"] = issues
        logging.warning(f"⚠ Potential Context Bloat: {issues} found but not clearly ignored.")
    else:
        logging.info("✔ Build Context looks clean (heuristic).")

    # Save Report
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    logging.info(f"Diagnostic complete. Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
