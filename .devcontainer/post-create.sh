#!/bin/bash

# EQ12 DevContainer Post-Create Setup Script
# Runs after container is created to install dependencies and configure environment

set -e

echo "========================================"
echo "EQ12 DevContainer Setup"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install essential system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    vim \
    htop \
    tmux \
    jq \
    postgresql-client \
    redis-tools \
    sqlite3

# Install Python development tools
echo -e "${YELLOW}Installing Python development tools...${NC}"
pip install --upgrade pip setuptools wheel

# Install core EQ12 Python packages
echo -e "${YELLOW}Installing EQ12 Python packages...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install essential packages if requirements.txt doesn't exist
    pip install \
        requests>=2.31.0 \
        beautifulsoup4>=4.12.0 \
        lxml>=4.9.0 \
        pandas>=2.0.0 \
        numpy>=1.24.0 \
        python-dotenv>=1.0.0 \
        fastapi>=0.104.0 \
        uvicorn>=0.24.0 \
        pytest>=7.4.0 \
        black>=23.0.0 \
        flake8>=6.0.0 \
        mypy>=1.5.0 \
        jupyter>=1.0.0 \
        notebook>=7.0.0 \
        ipykernel>=6.25.0
fi

# Install Node.js packages if package.json exists
if [ -f "package.json" ]; then
    echo -e "${YELLOW}Installing Node.js packages...${NC}"
    npm install
fi

# Configure Git
echo -e "${YELLOW}Configuring Git...${NC}"
git config --global core.autocrlf input
git config --global core.filemode true
git config --global init.defaultBranch main

# Set up Python virtual environment (optional, for isolation)
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
fi

# Create necessary directories
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p configs
mkdir -p dashboard
mkdir -p tests

# Set proper permissions
echo -e "${YELLOW}Setting permissions...${NC}"
find scripts -name "*.py" -type f -exec chmod +x {} \;
find . -name "*.sh" -type f -exec chmod +x {} \;

# Install Jupyter kernel
echo -e "${YELLOW}Installing Jupyter kernel...${NC}"
python -m ipykernel install --user --name=eq12 --display-name="Python (EQ12)"

# Verify installations
echo -e "${YELLOW}Verifying installations...${NC}"
echo "Python version: $(python --version)"
echo "pip version: $(pip --version)"
echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"

# Test essential imports
echo -e "${YELLOW}Testing Python imports...${NC}"
python -c "import requests, pandas, numpy, fastapi; print('✓ Core packages installed successfully')"

# Display success message
echo ""
echo -e "${GREEN}========================================"
echo -e "EQ12 DevContainer Setup Complete!"
echo -e "========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Run tests: pytest tests/"
echo "  3. Start development server: uvicorn main:app --reload"
echo "  4. Launch Jupyter: jupyter lab --ip=0.0.0.0 --port=8888"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
