#!/usr/bin/env bash
# EQ12 Universal Ubuntu/Debian Node Setup
# Target: Ubuntu 22.04+, Debian 11+, Raspberry Pi OS
# Installs: OpenSSH, Docker Engine (Official), Python3, Utilities
# Configures: User permissions, /opt/eq12 workspace
# Usage: sudo bash setup_10t8_ubuntu.sh [username]

set -euo pipefail

# Configuration
TARGET_USER="${1:-$SUDO_USER}"
if [ -z "$TARGET_USER" ]; then TARGET_USER="eq12"; fi
EQ12_ROOT="/opt/eq12"

function log() { echo "[EQ12-SETUP] $*"; }

if [ "$(id -u)" -ne 0 ]; then
    log "Error: This script must be run as root (sudo)."
    exit 1
fi

log "Starting EQ12 Node Setup for user: $TARGET_USER"

# 1. System Update & Dependencies
log "Updating system packages..."
apt-get update -y

# Define base packages
PACKAGES=(
    ca-certificates
    curl
    gnupg
    lsb-release
    apt-transport-https
    git
    wget
    ufw
    jq
    net-tools
    nmap
    htop
    ncdu
    python3-pip
    python3-venv
    avahi-daemon
)

# Add software-properties-common only if available (Debian/Ubuntu specific)
if apt-cache show software-properties-common &>/dev/null; then
    PACKAGES+=(software-properties-common)
fi

apt-get install -y "${PACKAGES[@]}"

# 2. Docker Installation (Official)
if ! command -v docker &> /dev/null; then
    log "Installing Docker Engine..."
    mkdir -p /etc/apt/keyrings
    if [ -f /etc/apt/keyrings/docker.gpg ]; then rm /etc/apt/keyrings/docker.gpg; fi
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Detect Distro for Repo
    DISTRO=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
    CODENAME=$(lsb_release -cs)
    
    # Handle Raspbian/Debian specifically if needed, but usually 'debian' or 'ubuntu' works
    if [ "$DISTRO" == "raspbian" ]; then DISTRO="debian"; fi
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$DISTRO $CODENAME stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
    log "Docker already installed."
fi

# 3. User Configuration
if ! id "$TARGET_USER" &>/dev/null; then
    log "Creating user $TARGET_USER..."
    useradd -m -s /bin/bash "$TARGET_USER"
    passwd -l "$TARGET_USER" || true
    log "User created. Set password manually with: sudo passwd $TARGET_USER"
fi

log "Adding $TARGET_USER to docker group..."
usermod -aG docker "$TARGET_USER"

# 4. Workspace Setup
log "Configuring $EQ12_ROOT..."
mkdir -p "$EQ12_ROOT"
chown -R "$TARGET_USER:$TARGET_USER" "$EQ12_ROOT"
chmod 775 "$EQ12_ROOT"

# 5. Firewall (UFW) - Allow SSH and Docker Swarm ports
log "Configuring Firewall..."
ufw allow 22/tcp
ufw allow 2377/tcp # Swarm Management
ufw allow 7946/tcp # Swarm Node Comm
ufw allow 7946/udp
ufw allow 4789/udp # Overlay Network
# ufw enable # Uncomment to enable automatically (careful over SSH!)

log "=== Setup Complete ==="
log "Node is ready. Please relogin as $TARGET_USER to use Docker."


log "Enabling and starting Docker"
systemctl enable docker --now
usermod -aG docker "$TARGET_USER" || true

# Install Python3 + pip + venv ----------------------------------------------------------------
log "Installing Python3, pip, venv"
apt-get install -y python3 python3-venv python3-pip

# Optional: PostgreSQL -----------------------------------------------------------------------
# Default to false if not set
INSTALL_POSTGRES="${INSTALL_POSTGRES:-false}"
if [ "${INSTALL_POSTGRES}" = true ]; then
  log "Installing PostgreSQL"
  apt-get install -y postgresql postgresql-contrib
  systemctl enable postgresql --now
fi

# Basic security: UFW firewall -----------------------------------------------------------------
# Default to true if not set
ENABLE_UFW="${ENABLE_UFW:-true}"
if [ "${ENABLE_UFW}" = true ]; then
  log "Configuring UFW firewall: allow ssh, http (80), https (443)"
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow OpenSSH
  ufw allow 80/tcp
  ufw allow 443/tcp
  # allow Docker management ports if desired (commented by default)
  # ufw allow 2375/tcp
  ufw --force enable
fi

# Create basic directory layout ----------------------------------------------------------------
log "Creating EQ12 directories"
mkdir -p /opt/eq12 /opt/eq12/services /var/log/eq12
chown -R "$TARGET_USER":"$TARGET_USER" /opt/eq12

# Create a systemd template for docker-compose app (example) ----------------------------------
cat > /etc/systemd/system/eq12-compose@.service <<EOF
[Unit]
Description=EQ12 Compose instance %i
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/eq12/services/%i
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
log "Systemd template installed: eq12-compose@<service>.service"

# Final notes ---------------------------------------------------------------------------------
log "Setup complete. Next steps (as root or $TARGET_USER):"
cat <<EOF
- Place your service compose files under /opt/eq12/services/<service_name>/docker-compose.yml
  then enable with: sudo systemctl enable --now eq12-compose@<service_name>

- To run a quick test container as eq12 user:
  sudo -u $TARGET_USER docker run --rm hello-world

- If you want to SSH in with keys, copy your public key into /home/$TARGET_USER/.ssh/authorized_keys

- To add the node to EQ12 node registry remotely, run eq12_onboard_node.py from the EQ12 host.

EOF

log "EQ12 10T8 Ubuntu setup finished"
exit 0
