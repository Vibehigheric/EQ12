#!/usr/bin/env python3
import argparse
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[EQ12-ONBOARD] %(message)s')

def run_ssh_cmd(host, user, cmd):
    """Run a command via SSH and return the output."""
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{host}", cmd]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"SSH command failed on {host}: {e.stderr}")
        sys.exit(1)

def get_swarm_token(manager_host, manager_user, role="worker"):
    """Retrieve the swarm join token from the remote manager."""
    logging.info(f"Retrieving {role} token from manager {manager_host}...")
    cmd = f"sudo docker swarm join-token -q {role}"
    return run_ssh_cmd(manager_host, manager_user, cmd)

def onboard_node(target_host, target_user, manager_ip, token):
    """SSH into the node and join the swarm."""
    logging.info(f"Onboarding {target_user}@{target_host} to swarm manager {manager_ip}...")
    
    # Construct the join command
    join_cmd = f"sudo docker swarm join --token {token} {manager_ip}:2377"
    
    # Run SSH command
    run_ssh_cmd(target_host, target_user, join_cmd)
    logging.info(f"Successfully joined {target_host} to the swarm.")

def main():
    parser = argparse.ArgumentParser(description="Onboard a node to the EQ12 Docker Swarm.")
    parser.add_argument("target_host", help="IP address or hostname of the node to onboard")
    parser.add_argument("--target-user", default="eq12", help="SSH user for the target node (default: eq12)")
    parser.add_argument("--manager-host", default="192.168.1.80", help="IP/Hostname of the Swarm Manager (default: 192.168.1.80)")
    parser.add_argument("--manager-user", default="ricoj100", help="SSH user for the Swarm Manager (default: ricoj100)")
    parser.add_argument("--role", choices=["worker", "manager"], default="worker", help="Role of the new node")
    
    args = parser.parse_args()
    
    # 1. Get Token from Manager
    token = get_swarm_token(args.manager_host, args.manager_user, args.role)
    logging.info(f"Retrieved {args.role} token: {token}")
    
    # 2. Join Target Node to Swarm
    # Note: The target node needs to reach the manager IP. 
    # We assume manager_host is the IP reachable by the target node.
    onboard_node(args.target_host, args.target_user, args.manager_host, token)

if __name__ == "__main__":
    main()
