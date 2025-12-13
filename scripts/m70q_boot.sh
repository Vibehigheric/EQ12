#!/usr/bin/env bash
set -euo pipefail

EQ12_IP="192.168.100.2"
EQ12_USER="Ricoj100"

echo "[M70q BOOT] Starting M70q GodStack node pipeline..."

# 1) Wait for network
echo "[1/4] Waiting for network..."
for i in {1..30}; do
  if ping -c1 "$EQ12_IP" >/dev/null 2>&1; then
    echo "[1/4] Network up, EQ12 reachable."
    break
  fi
  sleep 2
done

# 2) Ensure Docker service is running
echo "[2/4] Ensuring Docker service is running..."
sudo systemctl start docker
sudo systemctl enable docker

# 3) Show Swarm status (for logging)
echo "[3/4] Docker node info:"
docker info --format 'Swarm: {{.Swarm.LocalNodeState}} / {{.Swarm.ControlAvailable}}' || true

# 4) Optionally maintain SSH reverse tunnel to EQ12 (if you still need it)
# Comment this block out if not needed.
echo "[4/4] (Optional) Starting SSH reverse tunnel to EQ12 for internet bridge..."
# You might manage this via systemd-ssh service instead; here is a simple nohup example:
if ! pgrep -f "ssh -N -R 8888:127.0.0.1:8888" >/dev/null 2>&1; then
  nohup ssh -N -R 8888:127.0.0.1:8888 "${EQ12_USER}@${EQ12_IP}" >/var/log/m70q_ssh_bridge.log 2>&1 &
  echo "[4/4] SSH reverse tunnel started."
else
  echo "[4/4] SSH reverse tunnel already running."
fi

echo "[M70q BOOT] M70q node pipeline complete."
