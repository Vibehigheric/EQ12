#!/bin/bash

# EQ12 Founder Mode - Lenovo 10T8 Onboarding Script (Ubuntu Version)
# RUN THIS ON THE LENOVO MACHINE (WORKER NODE)

WORK_DIR="$HOME/EQ12_Worker"
REPO_URL="https://github.com/Ricoj100/EQ12_BROKEN_20251122_210342.git" # Adjust if private

echo -e "\e[36m🚀 INITIATING FOUNDER MODE ONBOARDING FOR LENOVO 10T8 (UBUNTU)...\e[0m"

# 1. Setup Workspace
if [ ! -d "$WORK_DIR" ]; then
    echo "Creating workspace at $WORK_DIR..."
    mkdir -p "$WORK_DIR"
fi
cd "$WORK_DIR"

# 2. Check Docker
echo "Checking Docker status..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is NOT installed. Installing now..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo usermod -aG docker $USER
    echo "⚠️ Docker installed. You may need to log out and back in for group changes to take effect."
else
    echo -e "\e[32m✅ Docker is ready.\e[0m"
fi

# 3. Sync Files (Simulated)
echo "⚠️ NOTE: Ensure 'src/products' is present in $WORK_DIR. (Use scp or git clone)"
# Example: git clone $REPO_URL .

# 4. Launch Portfolio
COMPOSE_FILE="$WORK_DIR/src/products/docker-compose.yaml"

if [ -f "$COMPOSE_FILE" ]; then
    echo -e "\e[35m🔥 Launching the 13-Product Portfolio...\e[0m"
    sudo docker-compose -f "$COMPOSE_FILE" up -d --build
    
    if [ $? -eq 0 ]; then
        echo -e "\e[32m✅ SUCCESS: Portfolio Deployed.\e[0m"
        sudo docker ps
    else
        echo "❌ Deployment Failed."
    fi
else
    echo "⚠️ docker-compose.yaml not found at $COMPOSE_FILE. Please sync the repo."
fi

echo -e "\e[36m🏁 FOUNDER MODE ONBOARDING COMPLETE.\e[0m"
