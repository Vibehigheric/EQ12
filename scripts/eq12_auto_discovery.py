"""
EQ12 Auto-Discovery Bot
- Argparse + logging
- Discovers IPv4 subnets from host adapters (via PowerShell Get-NetIPAddress)
- Performs ping sweep (concurrent) on selected subnets (default: private subnets only)
- Gathers ARP table and maps IP->MAC
- Performs TCP port checks (22, 3389) with socket connect
- Produces JSON report under `logs/eq12_auto_discovery_<ts>.json`

Usage examples:
  python scripts\eq12_auto_discovery.py --subnets 192.168.100.0/24
  python scripts\eq12_auto_discovery.py            # scans host private subnets

This script is intentionally dependency-light (stdlib only). Optional MAC vendor lookup may be enabled
with `--mac-lookup` if `requests` is available.
"""

from __future__ import annotations
import argparse
import concurrent.futures
import datetime
import ipaddress
import json
import logging
import os
import platform
import re
import socket
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

LOG = logging.getLogger("eq12.auto_discovery")

DEFAULT_PORTS = [22, 3389]


def run_powershell_json(cmd: str) -> Optional[dict]:
    """Run a PowerShell command and return parsed JSON if ConvertTo-Json used."""
    pwsh = "powershell.exe"
    full = f"{cmd} | ConvertTo-Json -Compress"
    try:
        p = subprocess.run([pwsh, "-NoProfile", "-Command", full], capture_output=True, text=True, timeout=20)
        out = p.stdout.strip()
        if not out:
            return None
        return json.loads(out)
    except Exception as e:
        LOG.debug("PowerShell JSON call failed: %s", e)
        return None


def get_host_ipv4_subnets() -> List[ipaddress.IPv4Network]:
    """Discover IPv4 addresses and prefix lengths from the host (Windows PowerShell Get-NetIPAddress).
    Falls back to parsing `ipconfig` if PowerShell not available.
    Only private networks are returned unless overridden.
    """
    nets: List[ipaddress.IPv4Network] = []
    if platform.system().lower().startswith("win"):
        try:
            out = run_powershell_json("Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '169.254.*' -and $_.PrefixLength -ne $null} | Select-Object IPAddress,PrefixLength,InterfaceAlias")
            if out:
                items = out if isinstance(out, list) else [out]
                for it in items:
                    ip = it.get("IPAddress")
                    prefix = int(it.get("PrefixLength", 24))
                    try:
                        net = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                        nets.append(net)
                    except Exception:
                        continue
        except Exception:
            LOG.debug("PowerShell based discovery failed, falling back to ipconfig")
    # Fallback: parse ipconfig
    if not nets:
        try:
            p = subprocess.run(["ipconfig"], capture_output=True, text=True)
            text = p.stdout
            for match in re.finditer(r"IPv4 Address[. ]*: ([0-9.]+)", text):
                ip = match.group(1)
                # we don't have prefix — assume /24
                try:
                    net = ipaddress.IPv4Network(f"{ip}/24", strict=False)
                    nets.append(net)
                except Exception:
                    continue
        except Exception:
            LOG.debug("Failed to run ipconfig fallback")
    # filter for private networks (RFC1918)
    private = [n for n in nets if n.is_private]
    # dedupe
    uniq = []
    for n in private:
        if not any(n == e for e in uniq):
            uniq.append(n)
    return uniq


def ping_addr(ip: str, timeout_ms: int = 300) -> bool:
    """Ping an IP using system ping. Returns True if reachable."""
    if platform.system().lower().startswith("win"):
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    else:
        # Linux / mac
        cmd = ["ping", "-c", "1", "-W", str(max(1, timeout_ms // 1000)), ip]
    try:
        p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.returncode == 0
    except Exception:
        return False


def ping_sweep(network: ipaddress.IPv4Network, workers: int = 100) -> List[str]:
    """Ping sweep a network, return list of alive IPs (skips network & broadcast)."""
    LOG.info("Ping sweeping %s", network)
    ips = [str(ip) for ip in network.hosts()]
    alive: List[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(ping_addr, ip): ip for ip in ips}
        for fut in concurrent.futures.as_completed(futs):
            ip = futs[fut]
            try:
                if fut.result():
                    alive.append(ip)
                    LOG.info("Alive: %s", ip)
            except Exception:
                continue
    return alive


def parse_arp_table() -> Dict[str, str]:
    """Return a mapping of IP -> MAC from `arp -a` output."""
    out = {}
    try:
        p = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        text = p.stdout
        # parse lines like:  192.168.100.1           00-11-22-33-44-55     dynamic
        for line in text.splitlines():
            m = re.search(r"([0-9]{1,3}(?:\.[0-9]{1,3}){3})\s+([0-9a-fA-F:-]{17}|[0-9a-fA-F-]{17})\s+\w+", line)
            if m:
                ip = m.group(1)
                mac = m.group(2).replace('-', ':').lower()
                out[ip] = mac
    except Exception:
        LOG.debug("Failed to parse arp -a")
    return out


def check_tcp_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def do_oui_lookup(mac: str) -> Optional[str]:
    """Simple online OUI lookup (optional). Uses https://api.macvendors.com if requests installed."""
    try:
        import requests
    except Exception:
        return None
    try:
        url = f"https://api.macvendors.com/{mac}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except Exception:
        return None
    return None


def ensure_logs_dir() -> str:
    logs = os.path.join(os.path.dirname(__file__), os.pardir, "logs")
    logs = os.path.abspath(logs)
    os.makedirs(logs, exist_ok=True)
    return logs


def save_report(report: dict) -> str:
    logs = ensure_logs_dir()
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(logs, f"eq12_auto_discovery_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return path


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="EQ12 Auto-Discovery Bot")
    parser.add_argument("--subnets", nargs="*", help="Subnet(s) to scan (CIDR). If omitted, uses host private subnets.")
    parser.add_argument("--ports", nargs="*", type=int, default=DEFAULT_PORTS, help="Ports to probe (default: 22,3389)")
    parser.add_argument("--workers", type=int, default=100, help="Concurrency for ping sweep")
    parser.add_argument("--mac-lookup", action="store_true", help="Attempt online OUI/MAC vendor lookup (optional)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if not args.quiet else logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")

    if args.subnets:
        networks = []
        for s in args.subnets:
            try:
                networks.append(ipaddress.IPv4Network(s, strict=False))
            except Exception:
                LOG.error("Invalid subnet: %s", s)
        if not networks:
            LOG.error("No valid subnets provided")
            sys.exit(1)
    else:
        networks = get_host_ipv4_subnets()
        if not networks:
            LOG.warning("No private host subnets discovered; please pass --subnets")
            sys.exit(1)

    final_report = {
        "generated_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "host": platform.node(),
        "scans": []
    }

    for net in networks:
        scan = {"network": str(net), "alive": []}
        alive = ping_sweep(net, workers=args.workers)
        scan["alive"] = []
        arp_map = parse_arp_table()
        for ip in alive:
            entry = {"ip": ip}
            mac = arp_map.get(ip)
            if mac:
                entry["mac"] = mac
                if args.mac_lookup:
                    vendor = do_oui_lookup(mac)
                    if vendor:
                        entry["vendor"] = vendor
            # port probes
            ports_info = {}
            for port in args.ports:
                ok = check_tcp_port(ip, port)
                ports_info[str(port)] = ok
            entry["ports"] = ports_info
            scan["alive"].append(entry)
        final_report["scans"].append(scan)

    report_path = save_report(final_report)
    LOG.info("Report saved to %s", report_path)
    print(json.dumps({"report": report_path}))


if __name__ == "__main__":
    main()
