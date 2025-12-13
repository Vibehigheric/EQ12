# 🌐 EQ12 Network Intelligence

The EQ12 cluster uses a sophisticated networking setup to ensure security, anonymity, and connectivity between nodes.

## 🔗 Network Topology

*   **Cluster Network (Ethernet)**:
    *   **Subnet**: `192.168.100.0/24`
    *   **EQ12 (Master)**: `192.168.100.2` (Static)
    *   **M70q (Worker)**: `192.168.100.3` (Static)
    *   **Purpose**: High-speed, isolated communication for database sync, Docker Swarm control, and SSH.

*   **Internet Network (Wi-Fi)**:
    *   **Interface**: `Wi-Fi`
    *   **Purpose**: External API access, scraping (via proxies), and cloud AI connectivity.

---

## 🛡️ Proxy Architecture

To allow the M70q (which is on an isolated subnet) to access the internet securely:

1.  **Local Proxy (EQ12)**:
    *   A Python-based `CONNECT` proxy runs on EQ12 at `192.168.100.2:8888`.
    *   Script: `scripts/simple_proxy.py`.

2.  **Remote Tunneling (M70q)**:
    *   Docker containers on M70q are configured to use `http_proxy=http://192.168.100.2:8888`.
    *   This routes all scraper traffic through EQ12, allowing for centralized IP management (e.g., VPN binding on EQ12).

---

## 🎮 Network Profiles

Managed via the VB.NET Control Tower:

### 1. Cluster Profile (`profile cluster`)
*   Sets Ethernet IP to `192.168.100.2`.
*   Enables communication with M70q.
*   **Use when**: Running the full cluster.

### 2. Home Profile (`profile home`)
*   Sets Ethernet to DHCP.
*   **Use when**: Connecting EQ12 directly to a router for updates or travel.

### 3. VPN Profile (`profile vpn_tokyo`)
*   (Future) Automates VPN connection and binds the proxy to the VPN interface.
