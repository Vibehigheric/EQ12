EQ12 — Lenovo 10T8 Setup Summary
=================================

Purpose
-------
This document explains how to prepare the Lenovo ThinkCentre 10T8 as an EQ12 cluster node and how to run the automated join script `scripts/eq12_cluster_join.ps1`.

Prerequisites
-------------
- The 10T8 is connected to the same LAN as the EQ12 controller (Ethernet to same switch/router).
- SSH access to the 10T8 (username with sudo privileges, e.g., `ricoj100`).
- Windows EQ12 controller has `ssh` and `scp` available (OpenSSH client installed). Run PowerShell as Administrator when required.
- If using key auth, have the private key available on the controller.

Quick steps
-----------
1. (Optional) Ensure the 10T8 has a static IP or is reachable on the LAN (we used `192.168.100.2` in examples).
2. From the EQ12 controller run (PowerShell):

```powershell
# example: passwordless SSH using private key
.\scripts\eq12_cluster_join.ps1 -Host 192.168.100.2 -User ricoj100 -KeyPath C:\keys\pi_key -Roles "worker,ai"

# or with password-based SSH (you'll be prompted by ssh):
.\scripts\eq12_cluster_join.ps1 -Host 192.168.100.2 -User ricoj100 -Roles "worker"
```

What the script does
--------------------
- Tests SSH connectivity
- Installs Docker Engine (from Docker upstream repo) on Ubuntu/Debian systems
- Creates `eq12` user and `/opt/eq12` directory
- Writes `/tmp/eq12_node_info.json` on the remote host and scp's it back to `./nodes/<host>_eq12_node_info.json`
- Appends a node entry into `nodes/node_registry.json` for the controller

After joining
------------
- Review `nodes/node_registry.json` and confirm the node entry
- SSH to the node and verify: `docker run --rm hello-world` (or `sudo -u eq12 docker run --rm hello-world`)
- Deploy your EQ12 workloads into `/opt/eq12/services/` and enable via `systemctl enable --now eq12-compose@<service>` if the node uses the `eq12-compose` systemd template

Notes & Safety
--------------
- The script assumes `sudo` is available and the connecting user can run `sudo` without an interactive password prompt where necessary. If your sudo is password-protected, you may need to perform some steps manually.
- The script creates and uses `nodes/node_registry.json` in the repo root. Back up your registry file before running in production.
- If the remote host uses a non-debian OS or a limited environment, the script will skip package installs and still try to collect node info.

Support
-------
If any step fails, paste the output here and I will diagnose the failure and provide a fix.
