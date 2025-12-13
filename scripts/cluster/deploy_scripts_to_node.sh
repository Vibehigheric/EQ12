#!/bin/bash
# Deploy setup scripts to a remote node
# Usage: ./deploy_scripts_to_node.sh <user@host>

TARGET=$1

if [ -z "$TARGET" ]; then
    echo "Usage: $0 <user@host>"
    exit 1
fi

echo "Deploying scripts to $TARGET..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")" # Parent of cluster/ is scripts/
# Actually repo root is parent of scripts/
# But setup_10t8_ubuntu.sh is in scripts/ (parent of SCRIPT_DIR)

# Create directory on remote
ssh "$TARGET" "mkdir -p ~/eq12-scripts"

# Copy scripts
# setup_10t8_ubuntu.sh is in scripts/ (one level up from cluster/)
scp "$SCRIPT_DIR/../setup_10t8_ubuntu.sh" "$TARGET":~/eq12-scripts/
scp "$SCRIPT_DIR/join_swarm.sh" "$TARGET":~/eq12-scripts/
scp "$SCRIPT_DIR/bootstrap_ssh_linux.sh" "$TARGET":~/eq12-scripts/

echo "Scripts deployed to ~/eq12-scripts on $TARGET."
echo "You can now SSH into $TARGET and run the setup scripts."
