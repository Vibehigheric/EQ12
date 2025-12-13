EQ12 Auto-Discovery Bot

Purpose
- Discover new nodes attached to the EQ12 system by scanning local IPv4 subnets.
- Produce a JSON report listing alive IPs, MACs (if available), and common service ports (SSH/RDP).

Files
- `scripts/eq12_auto_discovery.py` - main Python script
- `scripts/bootstrap_node.ps1` - Windows bootstrap helper to enable PSRemoting/OpenSSH
- `logs/` - script writes `eq12_auto_discovery_<timestamp>.json` here

Quick Usage
- Scan a specific subnet (fast):

```powershell
python scripts\eq12_auto_discovery.py --subnets 192.168.100.0/24
```

- Scan host private subnets (default):

```powershell
python scripts\eq12_auto_discovery.py
```

- Probe additional ports and enable MAC vendor lookup (optional):

```powershell
python scripts\eq12_auto_discovery.py --subnets 192.168.100.0/24 --ports 22 3389 80 --mac-lookup
```

Notes & Safety
- The script uses ping sweeps and short TCP connect attempts (non-destructive).
- If you want to reach a freshly-started device that uses a different subnet, either configure a temporary static IP on EQ12's Ethernet adapter or change the device's IP to the same subnet.
- MAC vendor lookup requires network access and `requests` library; the script will skip lookup if `requests` is not installed.

Next Steps
- Integrate into EQ12 scheduler, add automatic OUI DB or local cache, add WinRM probe for Windows nodes and SSH handshake for Linux nodes.
