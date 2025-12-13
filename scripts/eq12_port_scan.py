"""
EQ12 Port Scanner
- Lightweight TCP connect scanner using ThreadPoolExecutor
- Default: scans target 192.168.100.1 across ports 1-2000 plus common higher ports
- Writes JSON report to `logs/eq12_port_scan_<ts>.json`

Usage:
  python scripts\eq12_port_scan.py --targets 192.168.100.1
  python scripts\eq12_port_scan.py --targets 192.168.100.1 192.168.1.50 --ports 1-1024,3306,3389,5900
"""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime
import json
import os
import socket
import sys
from typing import List

DEFAULT_PORT_RANGES = ["1-2000"]
COMMON_PORTS = [22, 80, 443, 3389, 3306, 5432, 5900, 5985, 5986, 8080, 8443, 5000, 5001, 9000, 9001]


def parse_ports(specs: List[str]) -> List[int]:
    ports = set()
    for spec in specs:
        parts = spec.split(',')
        for p in parts:
            p = p.strip()
            if not p:
                continue
            if '-' in p:
                a,b = p.split('-',1)
                try:
                    a=int(a); b=int(b)
                    for x in range(max(1,a), min(65535,b)+1):
                        ports.add(x)
                except Exception:
                    continue
            else:
                try:
                    ports.add(int(p))
                except Exception:
                    continue
    return sorted(p for p in ports if 1 <= p <= 65535)


def scan_port(host: str, port: int, timeout: float=0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def ensure_logs():
    logs = os.path.join(os.path.dirname(__file__), os.pardir, 'logs')
    logs = os.path.abspath(logs)
    os.makedirs(logs, exist_ok=True)
    return logs


def save_report(report: dict) -> str:
    logs = ensure_logs()
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    path = os.path.join(logs, f'eq12_port_scan_{ts}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', nargs='+', help='Target IPs or hostnames', required=True)
    parser.add_argument('--ports', nargs='*', help='Port specs, e.g. 1-1024,3306,3389', default=DEFAULT_PORT_RANGES)
    parser.add_argument('--workers', type=int, default=200, help='Concurrency')
    parser.add_argument('--timeout', type=float, default=0.5, help='Connect timeout seconds')
    args = parser.parse_args(argv)

    port_list = parse_ports(args.ports + [','.join(str(p) for p in COMMON_PORTS)])
    # dedupe & sort
    port_list = sorted(set(port_list))

    report = {'generated_utc': datetime.datetime.utcnow().isoformat() + 'Z', 'targets': []}

    for t in args.targets:
        target_entry = {'target': t, 'open_ports': []}
        print(f'Scanning {t} {len(port_list)} ports...')
        sys.stdout.flush()
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(scan_port, t, p, args.timeout): p for p in port_list}
            for fut in concurrent.futures.as_completed(futures):
                p = futures[fut]
                try:
                    if fut.result():
                        print(f'Open: {t}:{p}')
                        target_entry['open_ports'].append(p)
                except Exception:
                    continue
        report['targets'].append(target_entry)
    path = save_report(report)
    print(json.dumps({'report': path}))

if __name__ == '__main__':
    main()
