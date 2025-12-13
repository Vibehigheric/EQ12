import socket
import subprocess
import json
import platform
import ipaddress
from concurrent.futures import ThreadPoolExecutor

CLUSTER_SUBNET = "192.168.100.0/24"
MASTER_IP = "192.168.100.2"
WORKER_IP_START = "192.168.100.3"

def ping_host(ip):
    """
    Pings a host to check if it is reachable.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', str(ip)]
    try:
        subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(ip), True
    except subprocess.CalledProcessError:
        return str(ip), False

def scan_subnet(subnet):
    """
    Scans the subnet for active hosts.
    """
    print(f"🔍 Scanning subnet {subnet}...")
    network = ipaddress.ip_network(subnet)
    active_hosts = []
    
    # Limit scan to first 20 IPs for speed in this example
    hosts_to_scan = list(network.hosts())[:20] 

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(ping_host, hosts_to_scan)
        
    for ip, is_active in results:
        if is_active:
            print(f"✅ Found active host: {ip}")
            active_hosts.append(ip)
            
    return active_hosts

def identify_node(ip):
    """
    Attempts to identify the node type via SSH banner or hostname.
    """
    try:
        # Simple hostname check (requires SSH keys to be set up)
        result = subprocess.check_output(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=2", f"ricoj100@{ip}", "hostname"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return result
    except:
        return "Unknown"

def main():
    print("🚀 EQ12 Cluster Auto-Discovery Tool")
    print("===================================")
    
    active_ips = scan_subnet(CLUSTER_SUBNET)
    
    cluster_map = []
    
    for ip in active_ips:
        role = "Unknown"
        if ip == MASTER_IP:
            role = "Master (Windows)"
        elif ip == WORKER_IP_START:
            role = "Worker (M70q)"
        
        hostname = identify_node(ip)
        
        node_info = {
            "ip": ip,
            "role": role,
            "hostname": hostname,
            "status": "Online"
        }
        cluster_map.append(node_info)
        
    print("\n📊 Cluster Map:")
    print(json.dumps(cluster_map, indent=2))
    
    # Save to report
    with open("reports/cluster_status.json", "w") as f:
        json.dump(cluster_map, f, indent=2)
    print("\n✅ Report saved to reports/cluster_status.json")

if __name__ == "__main__":
    main()
