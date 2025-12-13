#!/usr/bin/env bash
set -euo pipefail

EQ12_IP="192.168.100.2"

echo "[Pi5 BOOT] Starting Pi5 GodStack node pipeline..."

echo "[1/3] Waiting for network..."
for i in {1..30}; do
  if ping -c1 "$EQ12_IP" >/dev/null 2>&1; then
    echo "[1/3] Network up, EQ12 reachable."
    break
  fi
  sleep 2
done

echo "[2/3] Ensuring Docker is running..."
sudo systemctl start docker
sudo systemctl enable docker

echo "[3/3] Swarm node state:"
docker info --format 'Swarm: {{.Swarm.LocalNodeState}} / {{.Swarm.ControlAvailable}}' || true

echo "[Pi5 BOOT] Pi node pipeline complete."
