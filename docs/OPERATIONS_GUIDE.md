# 🔧 EQ12 Operations Guide

This guide covers the daily operations, maintenance, and troubleshooting of the EQ12 cluster.

## 🟢 Daily Startup Routine

1.  **Power On**: Ensure both EQ12 (Master) and M70q (Worker) are powered on.
2.  **Network Check**:
    ```powershell
    dotnet run --project src/EQ12.CommandCenter/EQ12.CommandCenter.vbproj network
    ```
    *   Ensure `Ethernet` (Cluster Link) is `Up` and has IP `192.168.100.2`.
    *   Ensure `Wi-Fi` (Internet) is `Up`.

3.  **Worker Connectivity**:
    ```powershell
    ssh ricoj100@192.168.100.3 "echo 'M70q Online'"
    ```

4.  **Start Orchestrator**:
    ```powershell
    # (Coming Soon)
    # python src/orchestrator/main.py
    ```

---

## 🔄 Deployment & Updates

### Deploying the Scraper to M70q
When you update the scraper code in `src/edgegod/`:

1.  **Run the Deploy Script**:
    ```powershell
    ./scripts/deploy_edgegod_scraper.ps1
    ```
    *   This will start the local proxy, copy files, build the Docker image on M70q, and restart the container.

### Updating the VB.NET Control Tower
1.  **Build the Solution**:
    ```powershell
    dotnet build EQ12.sln
    ```

---

## 🛠️ Troubleshooting

### 1. "M70q is not reachable"
*   **Check Physical Connection**: Is the Ethernet cable plugged in directly between EQ12 and M70q?
*   **Check IP Profile**:
    ```powershell
    dotnet run --project src/EQ12.CommandCenter/EQ12.CommandCenter.vbproj profile cluster
    ```
*   **Check M70q Power**: Is the device on?

### 2. "Docker build failed" (Proxy Issues)
*   The M70q needs the proxy to reach the internet during build.
*   Ensure `scripts/simple_proxy.py` is running on EQ12 (the deploy script handles this).
*   Check firewall rules on EQ12 to allow port 8888 from 192.168.100.3.

### 3. "SCP Permission Denied"
*   Ensure you are using the correct user: `ricoj100`.
*   Verify SSH keys or password.

---

## 📊 Monitoring

*   **Dashboard**: `dotnet run ... dashboard`
*   **Logs**: Check `logs/` directory for system logs.
*   **Docker Logs (M70q)**:
    ```powershell
    ssh ricoj100@192.168.100.3 "docker logs edgegod-scraper"
    ```
