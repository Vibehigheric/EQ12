# 🌐 EQ12 Cluster Manual: "The GodStack"

**Version**: 1.0 (Quantum Edge Edition)
**Date**: 2025-12-12
**Status**: ACTIVE

---

## 🎯 Objective
Connect three distinct hardware nodes into a single, unified Docker Swarm cluster ("The GodStack") capable of high-performance scraping, inference, and orchestration.

## 🖥️ Hardware Roles

| Node Name | Hardware | Role | IP Address | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **EQ12** | Windows 11 | **Manager** | `192.168.100.2` | `node.role == manager` |
| **M70q** | Lenovo Tiny (Ubuntu) | **Worker (Gravity Well)** | `192.168.100.3` | `node.labels.type == worker` |
| **Pi5** | Raspberry Pi 5 | **Worker (Quantum Tunneler)** | `192.168.100.4` | `node.labels.type == pi` |

---

## 🚀 Phase 1: Network Configuration (The "Overlay")

### 1.1 Windows (EQ12) Setup
Ensure your Windows machine has a static IP on the cluster interface.
```powershell
# Run as Administrator
New-NetIPAddress -InterfaceAlias "Ethernet 2" -IPAddress 192.168.100.2 -PrefixLength 24
```

### 1.2 Ubuntu (M70q) Setup
Configure Netplan to force the static IP.
```bash
# /etc/netplan/00-installer-config.yaml
network:
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.100.3/24
      routes:
        - to: default
          via: 192.168.100.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
  version: 2
```
Apply: `sudo netplan apply`

### 1.3 Pi Setup
Similar to Ubuntu, ensure static IP `192.168.100.4`.

---

## 🤝 Phase 2: Swarm Initialization

### 2.1 Initialize Manager (EQ12)
**Prerequisite**: Docker Desktop must be running.
```powershell
docker swarm init --advertise-addr 192.168.100.2
```
*Copy the join token output.*

### 2.2 Join Workers (M70q & Pi)
Run this on both the M70q and the Pi:
```bash
docker swarm join --token <TOKEN> 192.168.100.2:2377
```

### 2.3 Label Nodes (Critical for "GodStack")
Back on **EQ12**, label the nodes so the scheduler knows where to put tasks.

```powershell
# List nodes to get IDs
docker node ls

# Label M70q (Replace <M70q_NODE_ID>)
docker node update --label-add type=worker <M70q_NODE_ID>

# Label Pi (Replace <Pi_NODE_ID>)
docker node update --label-add type=pi <Pi_NODE_ID>
```

---

## ⚡ Phase 3: Deploy "The GodStack"

Now that the nodes are joined and labeled, deploy the optimized stack.

```powershell
# Deploy from EQ12
docker stack deploy -c eq12_stack.yml eq12
```

### Verification
```powershell
docker service ls
docker stack ps eq12
```

---

## 🛠️ Troubleshooting

**Issue**: Nodes can't see each other.
**Fix**: Check Windows Firewall. Allow port `2377` (TCP), `7946` (TCP/UDP), and `4789` (UDP).

**Issue**: "No such node" error during labeling.
**Fix**: Ensure the node has actually joined with `docker node ls`.

**Issue**: Services stuck in `Pending`.
**Fix**: Check constraints. If a service needs `type=pi` but the Pi is offline, it will hang.
