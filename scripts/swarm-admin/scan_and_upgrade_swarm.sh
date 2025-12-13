#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODES_FILE="$SCRIPT_DIR/nodes.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required. Install with: sudo apt install jq"
  exit 1
fi

if [ ! -f "$NODES_FILE" ]; then
  echo "Could not find nodes file at $NODES_FILE"
  exit 1
fi

run_ssh() {
  local user="$1"
  local ip="$2"
  shift 2
  ssh -o BatchMode=yes -o ConnectTimeout=5 "${user}@${ip}" "$@"
}

echo "=== 🧠 EQ12 Swarm Scan & Upgrade ==="
echo "Using nodes from: $NODES_FILE"
echo

echo "=== 1) Network Reachability ==="
jq -c '.[]' "$NODES_FILE" | while read -r node; do
  name=$(echo "$node" | jq -r '.name')
  ip=$(echo "$node"   | jq -r '.ip')
  user=$(echo "$node" | jq -r '.user')

  echo
  echo "-> Checking ${name} (${ip})"
  if ping -c 1 -W 1 "$ip" >/dev/null 2>&1; then
    echo "   ✅ Reachable"
  else
    echo "   ❌ NOT reachable"
    continue
  fi

  if run_ssh "$user" "$ip" "echo ok" >/dev/null 2>&1; then
    echo "   ✅ SSH OK"
  else
    echo "   ❌ SSH failed (check keys / firewall)"
  fi

done

echo

echo "=== 2) Docker & OS Info ==="
jq -c '.[]' "$NODES_FILE" | while read -r node; do
  name=$(echo "$node" | jq -r '.name')
  ip=$(echo "$node"   | jq -r '.ip')
  user=$(echo "$node" | jq -r '.user')

  echo
  echo "-> Node: ${name} (${ip})"

  if ! run_ssh "$user" "$ip" "command -v docker" >/dev/null 2>&1; then
    echo "   ❌ Docker not installed"
    continue
  fi

  run_ssh "$user" "$ip" "docker version --format '{{.Server.Version}}' 2>/dev/null || docker version" \
    | sed 's/^/   Docker: /'

  run_ssh "$user" "$ip" "uname -a" | sed 's/^/   OS: /'
done

echo

echo "=== 3) Rolling Upgrade of Swarm Nodes ==="

MANAGER_DOCKER_OK=false
if docker info >/dev/null 2>&1; then
  MANAGER_DOCKER_OK=true
  echo "Manager docker detected locally."
else
  echo "⚠️ No local docker. Skipping swarm drain/activate control."
fi

jq -c '.[]' "$NODES_FILE" | while read -r node; do
  name=$(echo "$node"  | jq -r '.name')
  ip=$(echo "$node"    | jq -r '.ip')
  user=$(echo "$node"  | jq -r '.user')
  role=$(echo "$node"  | jq -r '.role')

  echo
  echo "-> Upgrading ${name} (${ip}) [role: ${role}]"

  if [ "$MANAGER_DOCKER_OK" = true ] && docker node ls >/dev/null 2>&1; then
    if docker node ls --format '{{.Hostname}}' | grep -q "^${name}$"; then
      echo "   Draining swarm node ${name}..."
      docker node update --availability drain "$name" || echo "   ⚠️ Could not drain ${name}"
    else
      echo "   (Node hostname may not match swarm node name; skipping drain)"
    fi
  fi

  echo "   Running apt update/upgrade + restarting docker..."
  run_ssh "$user" "$ip" "sudo apt update && sudo apt install -y docker.io || true"
  run_ssh "$user" "$ip" "sudo systemctl restart docker || sudo service docker restart || true"

  if [ "$MANAGER_DOCKER_OK" = true ] && docker node ls >/dev/null 2>&1; then
    if docker node ls --format '{{.Hostname}}' | grep -q "^${name}$"; then
      echo "   Setting swarm node ${name} back to active..."
      docker node update --availability active "$name" || echo "   ⚠️ Could not activate ${name}"
    fi
  fi

  echo "   ✅ Upgrade step finished for ${name}"
done

echo

echo "=== 4) Swarm / Service Health Check ==="
if [ "$MANAGER_DOCKER_OK" = true ] && docker node ls >/dev/null 2>&1; then
  echo "Nodes:"
  docker node ls
  echo
  echo "Services:"
  docker service ls
else
  echo "⚠️ No swarm manager docker detected locally; cannot summarize swarm state."
fi

echo

echo "✅ Cluster scan & upgrade complete."
