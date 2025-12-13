# EQ12 DNS Optimization Pack v1.0

This directory contains the configuration files for the EQ12 DNS Optimization Pack.

## Deployment Instructions

### 1. Cluster-Wide Policy
- File: `dns_policy.conf`
- Target: `/etc/eq12/dns_policy.conf` (All Linux Nodes)

### 2. EQ12 Manager (If Linux/WSL)
- File: `00-manager-dns.yaml`
- Target: `/etc/netplan/00-manager-dns.yaml`
- Apply: `sudo netplan apply`
- **Note**: If Manager is Windows, use PowerShell `Set-DnsClientServerAddress` instead.

### 3. Raspberry Pi (Unbound)
- File: `unbound.conf`
- Target: `/etc/unbound/unbound.conf`
- Install: `sudo apt install unbound -y`
- Restart: `sudo systemctl restart unbound`

### 4. M70q Ubuntu (Worker)
- File: `01-dns.yaml`
- Target: `/etc/netplan/01-dns.yaml`
- Apply: `sudo netplan apply`

### 5. Host Pinning
- File: `hosts_append.txt`
- Action: Append content to `/etc/hosts` (Linux) or `C:\Windows\System32\drivers\etc\hosts` (Windows).

## Scripts
- `scripts/dns_stress_test.sh`: Run to verify DNS performance.
- `scripts/verify_dns_cluster.sh`: Run to check DNS config on all nodes.

## Code Integration
- `src/core/dns_prefetcher.py`: Prefetch logic.
- `src/core/dns_health.py`: Health check logic.
- Engines (`Parlay`, `Risk`, `PropTensor`) have been updated to use `prefetch_dns()`.
