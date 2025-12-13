# EQ12 Deployment Guide

## EdgeGod Scraper Deployment (M70q)

This guide explains how to deploy the `edgegod-scraper` to the offline M70q node (`192.168.100.3`).

### Prerequisites
- **Host**: EQ12 (Windows)
- **Target**: M70q (Ubuntu)
- **User**: `ricoj100`
- **Network**: 192.168.100.x subnet active.

### The "One-Click" Deployer

We have created a PowerShell automation script that handles the entire pipeline:
1.  Starts a temporary HTTP/HTTPS Proxy on EQ12 (Port 8888).
2.  SCPs the source code from `src/edgegod` to M70q.
3.  Triggers a remote `docker build` on M70q (using the proxy for internet access).
4.  Restarts the `edgegod-scraper` container.

### Usage

Run the following command in PowerShell:

```powershell
.\scripts\deploy_edgegod_scraper.ps1
```

### Troubleshooting

- **SCP Permission Denied**: Ensure you are using user `ricoj100`.
- **Proxy Failed**: Check if port 8888 is in use. The script tries to kill existing jobs, but you might need to manually stop python processes.
- **Docker Build Failed**: Check the output for network errors. The proxy must be running on EQ12 and reachable from M70q.

### Architecture

- **Proxy**: `scripts/proxy_server.py` (Python `socket` + `select` implementation of HTTP CONNECT).
- **Orchestrator**: `scripts/deploy_edgegod_scraper.ps1`.
