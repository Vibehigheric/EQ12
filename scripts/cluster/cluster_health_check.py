#!/usr/bin/env python3
import subprocess
import json
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='[EQ12-HEALTH] %(message)s')

def run_ssh_cmd(host, user, cmd):
    """Run a command via SSH and return the output."""
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{host}", cmd]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"SSH command failed on {host}: {e.stderr}")
        return None

def check_swarm_nodes(manager_host, manager_user):
    """Get list of nodes from the Swarm Manager."""
    logging.info(f"Checking Swarm nodes via {manager_host}...")
    cmd = "sudo docker node ls --format '{{json .}}'"
    output = run_ssh_cmd(manager_host, manager_user, cmd)
    
    if not output:
        return []

    nodes = []
    for line in output.splitlines():
        try:
            nodes.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return nodes

def check_services(manager_host, manager_user):
    """Get list of services from the Swarm Manager."""
    logging.info(f"Checking Swarm services via {manager_host}...")
    cmd = "sudo docker service ls --format '{{json .}}'"
    output = run_ssh_cmd(manager_host, manager_user, cmd)
    
    if not output:
        return []

    services = []
    for line in output.splitlines():
        try:
            services.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return services

def main():
    manager_host = "192.168.1.80"
    manager_user = "ricoj100"
    
    print(f"=== EQ12 Cluster Health Check ({datetime.now()}) ===")
    
    # 1. Check Nodes
    nodes = check_swarm_nodes(manager_host, manager_user)
    print(f"\nNodes ({len(nodes)}):")
    print(f"{'ID':<20} {'HOSTNAME':<20} {'STATUS':<10} {'AVAILABILITY':<15} {'MANAGER'}")
    print("-" * 80)
    for node in nodes:
        manager_status = node.get('ManagerStatus', 'Worker')
        print(f"{node['ID']:<20} {node['Hostname']:<20} {node['Status']:<10} {node['Availability']:<15} {manager_status}")

    # 2. Check Services
    services = check_services(manager_host, manager_user)
    print(f"\nServices ({len(services)}):")
    print(f"{'ID':<20} {'NAME':<20} {'MODE':<15} {'REPLICAS'}")
    print("-" * 80)
    for service in services:
        print(f"{service['ID']:<20} {service['Name']:<20} {service['Mode']:<15} {service['Replicas']}")

    if not nodes:
        logging.error("Could not retrieve node list. Is the manager reachable?")
        sys.exit(1)

    print("\n=== Health Check Complete ===")

if __name__ == "__main__":
    main()
