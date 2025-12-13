# Swarm Admin Toolkit

This folder mirrors the `~/swarm-admin` workspace you should create inside Ubuntu WSL on EQ12. It contains:

- `nodes.json` – inventory of the swarm nodes (EQ12 controller, M70Q worker, Raspberry Pi worker)
- `scan_and_upgrade_swarm.sh` – network probe plus rolling upgrade runner

## Usage (from Ubuntu WSL on EQ12)

```bash
cd ~/swarm-admin
chmod +x scan_and_upgrade_swarm.sh
./scan_and_upgrade_swarm.sh
```

### Pre-requisites

- WSL2 with an Ubuntu distro (`wsl --install`, `wsl --set-default-version 2`)
- `openssh-client`, `ping`, `jq` installed (`sudo apt install -y openssh-client net-tools iputils-ping jq`)
- SSH public key copied (`ssh-copy-id`) to each node (`192.168.1.52`, `192.168.1.80`, etc.)
- Docker installed on each node (use `curl -fsSL https://get.docker.com | sh` and `sudo usermod -aG docker $USER`)
- `docker swarm init --advertise-addr 192.168.1.144` run on the manager to populate `docker node ls`

## What the script does

1. Pings each IP and verifies SSH connectivity
2. Logs Docker version and OS info per host
3. If run on the swarm manager, drains each node, runs package upgrade, restarts Docker, then sets nodes back to active
4. Prints `docker node ls` and `docker service ls` as a health summary

After upgrades you can redeploy stacks with `docker stack deploy -c <compose>.yml <stack>` using additional helper scripts.
