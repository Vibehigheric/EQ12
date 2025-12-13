"""
EQ12 Node Onboarder
- Uses PowerShell Remoting (WinRM) to copy and execute `bootstrap_node.ps1` on a remote Windows host
- Adds node metadata to `C:\EQ12\nodes\node_registry.json` (creates folder if missing)

Usage examples:
  python scripts\eq12_onboard_node.py --target 192.168.1.50 --user Administrator --password 'P@ssw0rd' --add-registry --role compute

Notes:
- This first version performs WinRM-based onboarding by invoking a PowerShell Invoke-Command call.
- It does not enable experimental SSH-based copy. Use `bootstrap_node.ps1` directly on the node if WinRM is not available.
- The script is conservative: it does not change network settings on the local host.
"""
from __future__ import annotations
import argparse
import getpass
import json
import logging
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime
from typing import Optional

LOG = logging.getLogger("eq12.onboard")

NODE_REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'nodes', 'node_registry.json'))
BOOTSTRAP_LOCAL = os.path.abspath(os.path.join(os.path.dirname(__file__), 'bootstrap_node.ps1'))


def ensure_nodes_dir():
    d = os.path.dirname(NODE_REGISTRY_PATH)
    os.makedirs(d, exist_ok=True)


def add_node_to_registry(entry: dict):
    ensure_nodes_dir()
    try:
        if os.path.exists(NODE_REGISTRY_PATH):
            with open(NODE_REGISTRY_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []
    # remove existing with same ip
    data = [e for e in data if e.get('ip') != entry.get('ip')]
    entry['added_utc'] = datetime.utcnow().isoformat() + 'Z'
    data.append(entry)
    with open(NODE_REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    LOG.info('Node added to registry: %s', NODE_REGISTRY_PATH)
    return NODE_REGISTRY_PATH


def build_powershell_invoke_command(target: str, username: str, password: str, remote_path: str = 'C:\\Windows\\Temp\\eq12_bootstrap.ps1', ps_args: Optional[str] = "-CreateEq12User -EnableSSH") -> List[str]:
    """Build the powershell.exe argument list that will invoke the bootstrap script on the remote target using Invoke-Command.
    The bootstrap script content is passed as a here-string argument to avoid quoting issues.
    Returns a list suitable for subprocess.run([...])
    """
    if not os.path.exists(BOOTSTRAP_LOCAL):
        raise FileNotFoundError(f"Local bootstrap script not found at {BOOTSTRAP_LOCAL}")

    with open(BOOTSTRAP_LOCAL, 'r', encoding='utf-8') as f:
        content = f.read()

    # Prepare a PowerShell command that creates a PSCredential and runs Invoke-Command with a here-string payload
    # Use @' ... '@ to avoid interpolation issues
    # We'll pass the cleartext password into ConvertTo-SecureString (this requires WinRM to accept this credential)
    ps_script = f"$content = @'\n{content}\n'@\n$secure = ConvertTo-SecureString '{password}' -AsPlainText -Force\n$cred = New-Object System.Management.Automation.PSCredential('{username}', $secure)\nInvoke-Command -ComputerName {target} -Credential $cred -ScriptBlock {{ param($c, $args) Set-Content -Path '{remote_path}' -Value $c -Force; & '{remote_path}' {ps_args} }} -ArgumentList $content\n"

    # Build command list
    cmd = [
        'powershell.exe',
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-Command', ps_script
    ]
    return cmd


def run_winrm_bootstrap(target: str, username: str, password: str, ps_args: Optional[str] = None) -> int:
    if ps_args is None:
        ps_args = "-CreateEq12User -EnableSSH"
    LOG.info('Running WinRM bootstrap against %s', target)
    cmd = build_powershell_invoke_command(target, username, password, ps_args=ps_args)
    LOG.debug('Powershell command: %s', cmd)
    p = subprocess.run(cmd)
    return p.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description='EQ12 Node Onboarder')
    parser.add_argument('--target', required=True, help='Target IP or hostname')
    parser.add_argument('--user', required=False, help='Username for remote (WinRM)')
    parser.add_argument('--password', required=False, help='Password for remote (WinRM)')
    parser.add_argument('--add-registry', action='store_true', help='Add node to C:\\EQ12\\nodes\\node_registry.json after successful bootstrap')
    parser.add_argument('--role', required=False, default='compute', help='Role to add to registry')
    parser.add_argument('--ps-args', required=False, default='-CreateEq12User -EnableSSH', help='Arguments to pass to remote bootstrap script')
    parser.add_argument('--no-run', action='store_true', help='Do not execute remote bootstrap; only prepare and print commands')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    target = args.target
    user = args.user
    password = args.password

    if not user:
        user = input('Remote username: ')
    if not password:
        password = getpass.getpass('Remote password: ')

    if args.no_run:
        try:
            cmd = build_powershell_invoke_command(target, user, password, ps_args=args.ps_args)
            print('Prepared PowerShell command (not executed).')
            print('\n'.join(cmd))
            sys.exit(0)
        except Exception as e:
            LOG.error('Failed to prepare command: %s', e)
            sys.exit(2)

    # Execute the remote bootstrap
    rc = run_winrm_bootstrap(target, user, password, ps_args=args.ps_args)
    if rc != 0:
        LOG.error('Remote bootstrap failed with return code %s', rc)
        sys.exit(rc)

    LOG.info('Remote bootstrap reported success (exit code %s).', rc)

    if args.add_registry:
        entry = {
            'name': f'node-{target}',
            'ip': target,
            'role': args.role,
            'status': 'online'
        }
        path = add_node_to_registry(entry)
        print(json.dumps({'registry': path, 'node': entry}))
    else:
        print(json.dumps({'result': 'bootstrap_executed', 'target': target}))

if __name__ == '__main__':
    main()
