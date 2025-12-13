# 🌐 EQ12 Cluster Topology & Architecture (The "GodStack")

**Version**: 2.0 (Static Network & Island Mode Edition)
**Date**: 2025-12-12
**Status**: ACTIVE

---

## 1. 🏗️ High-Level Architecture

The EQ12 Cluster is a **hybrid distributed system** comprising x86_64 (Windows/Linux) and ARM64 (Pi) nodes. It utilizes a **Docker Swarm** orchestration layer over a **Static IP** network, with a specialized "Island Node" (M70q) bridging to the internet via an SSH Reverse Tunnel.

### Core Principles
1.  **Static Networking**: DHCP is banned for compute nodes. `eth0` is the source of truth.
2.  **Island Mode**: The M70q has no direct internet; it tunnels through EQ12.
3.  **Specialized Compute**:
    *   **EQ12**: Orchestration & Control Plane.
    *   **M70q**: Heavy Compute & Database (The "Gravity Well").
    *   **Pi**: Edge Inference (TPU).
    *   **VMs**: Scraping & Data Ingestion.

---

## 2. 🗺️ Network Map (Static IP Assignment)

| Node Name | Role | Hardware | IP Address (Static) | Interface | OS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EQ12** | **Manager** | Windows 11 (WSL2) | `192.168.100.1` | `eth0` | WSL2 / Ubuntu |
| **M70q** | **Worker** | Lenovo Tiny | `192.168.100.3` | `eth0` | Ubuntu 22.04 |
| **Pi5** | **Worker** | Raspberry Pi 5 | `192.168.1.80` | `wlan0/eth0` | Debian Bookworm |
| **VM-A** | **Worker** | Hyper-V VM | `192.168.1.94` | `eth0` | Ubuntu |
| **VM-B** | **Worker** | Hyper-V VM | `192.168.1.116` | `eth0` | Ubuntu |
| **VM-C** | **Worker** | Hyper-V VM | `192.168.1.126` | `eth0` | Ubuntu |

**Excluded Devices**:
*   LG TV (`192.168.1.246`) - Permanently ignored to prevent mDNS pollution.

---

## 3. 🌉 The "Island Bridge" (Connectivity)

The M70q (`192.168.100.3`) is an **Island Node**. It cannot reach the internet directly.
Connectivity is provided by the **EQ12 Bridge**:

*   **Mechanism**: SSH Reverse Tunnel (`ssh -R`)
*   **Port**: `8888` (HTTP Proxy)
*   **Flow**: `M70q -> localhost:8888 -> Tunnel -> EQ12 -> Internet`
*   **DNS**: Resolved via the tunnel or local Unbound cache.

---

## 4. 🐳 Docker Swarm Configuration

### Labels & Constraints
The scheduler uses node labels to pin workloads to the correct hardware.

| Label Key | Value | Target Node | Workload Type |
| :--- | :--- | :--- | :--- |
| `type` | `manager` | EQ12 | Orchestrator, Dashboard, Risk Engine |
| `type` | `worker` | M70q | Database, Redis, Parlay Engine |
| `type` | `pi` | Pi5 | TPU Inference, Light Models |
| `type` | `scraper` | VMs | Browser Automation, Data Fetching |

### Overlay Network
*   **Subnet**: `10.0.0.0/24` (Internal Swarm)
*   **Driver**: `overlay`
*   **MTU**: `1450` (Optimized for tunnel/VPN overhead)

---

## 5. 🚦 Service Routing Table

| Service | Host Node | Port | URL |
| :--- | :--- | :--- | :--- |
| **Portainer** | M70q | `9000` | `http://192.168.100.3:9000` |
| **Dashboard** | EQ12 | `3000` | `http://192.168.100.1:3000` |
| **Postgres** | M70q | `5432` | Internal Only |
| **Redis** | M70q | `6379` | Internal Only |
| **Inference** | Pi5 | `5000` | Internal Only |

---

## 6. 🛡️ DNS Strategy

*   **Primary Resolver**: `192.168.100.1` (EQ12 Manager)
*   **Secondary**: `1.1.1.1` (Cloudflare)
*   **Pi Accelerator**: Local `Unbound` instance for TPU latency reduction.
*   **Prefetching**: Python engines pre-resolve betting APIs (`the-odds-api.com`) to warm the cache.

---

## 7. ⚠️ Critical Operational Rules

1.  **Never DHCP**: If a node reboots and gets a new IP, the Swarm breaks. Static IPs are mandatory.
2.  **Tunnel First**: The M70q cannot pull Docker images if the SSH tunnel is down.
3.  **TPU Constraints**: Never deploy `prop-tensor` to a node without `type=pi`. It will crash.
4.  **Memory Limits**:
    *   Manager: 512MB Limit
    *   Pi: 2GB Limit
    *   M70q: 4GB Limit
