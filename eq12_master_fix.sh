#!/bin/bash
################################################################################
# EQ12 MASTER FIX SCRIPT - Complete Workspace Recovery
# Executes all repair operations in the correct order
#
# This script fixes:
# - WSL .bashrc freezing issues
# - VS Code Remote server corruption
# - Python interpreter conflicts
# - Pylance indexing death loop
# - Duplicate virtual environments
# - Corrupted workspace folders
# - Missing prompt templates
#
# Created: 2025-11-22
# Safe to run multiple times (idempotent)
################################################################################

set -e
set -u

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

WORKSPACE_ROOT="/workspaces/EQ12"
SCRIPTS_DIR="${WORKSPACE_ROOT}/scripts"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         EQ12 MASTER WORKSPACE RECOVERY SCRIPT                  ║"
echo "║                                                                ║"
echo "║  This will fix ALL known EQ12 workspace corruption issues      ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Confirm execution
read -p "⚠️  This will modify system files. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted by user${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 1: WSL SHELL CONFIGURATION FIX${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "${SCRIPTS_DIR}/fix_wsl_bashrc.sh" ]; then
    echo -e "${YELLOW}Running WSL .bashrc repair...${NC}"
    bash "${SCRIPTS_DIR}/fix_wsl_bashrc.sh"
    echo -e "${GREEN}✅ WSL .bashrc repaired${NC}"
else
    echo -e "${YELLOW}⚠️  WSL fix script not found, skipping...${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 2: VS CODE REMOTE SERVER CLEANUP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "${SCRIPTS_DIR}/cleanup_vscode_remote.sh" ]; then
    echo -e "${YELLOW}Running VS Code Remote cleanup...${NC}"
    bash "${SCRIPTS_DIR}/cleanup_vscode_remote.sh"
    echo -e "${GREEN}✅ VS Code Remote cleaned${NC}"
else
    echo -e "${YELLOW}⚠️  VS Code cleanup script not found, skipping...${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 3: WORKSPACE SANITY RESTORE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "${WORKSPACE_ROOT}/eq12_workspace_sanity_restore.sh" ]; then
    echo -e "${YELLOW}Running workspace sanity restore...${NC}"
    bash "${WORKSPACE_ROOT}/eq12_workspace_sanity_restore.sh"
    echo -e "${GREEN}✅ Workspace restored${NC}"
else
    echo -e "${YELLOW}⚠️  Workspace restore script not found, skipping...${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 4: PROMPT FOLDER INTEGRITY CHECK${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "${SCRIPTS_DIR}/eq12_prompt_repair.sh" ]; then
    echo -e "${YELLOW}Running prompt folder repair...${NC}"
    bash "${SCRIPTS_DIR}/eq12_prompt_repair.sh"
    echo -e "${GREEN}✅ Prompt folders validated${NC}"
else
    echo -e "${YELLOW}⚠️  Prompt repair script not found, skipping...${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 5: PYTHON ENVIRONMENT VALIDATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Checking Python configuration...${NC}"

# Check if .venv exists
if [ -d "${WORKSPACE_ROOT}/.venv" ]; then
    echo -e "${GREEN}✅ Python virtual environment found: .venv${NC}"

    # Activate and check Python version
    if [ -f "${WORKSPACE_ROOT}/.venv/bin/python" ]; then
        PYTHON_VERSION=$("${WORKSPACE_ROOT}/.venv/bin/python" --version 2>&1)
        echo -e "${GREEN}   Python: ${PYTHON_VERSION}${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .venv found${NC}"
    echo -e "${CYAN}   Creating Python 3.12 virtual environment...${NC}"

    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv "${WORKSPACE_ROOT}/.venv"
        source "${WORKSPACE_ROOT}/.venv/bin/activate"
        pip install --upgrade pip setuptools wheel

        # Install requirements if exists
        if [ -f "${WORKSPACE_ROOT}/requirements.txt" ]; then
            echo -e "${CYAN}   Installing requirements...${NC}"
            pip install -r "${WORKSPACE_ROOT}/requirements.txt"
        fi

        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${RED}❌ python3.12 not found. Please install Python 3.12${NC}"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 6: VS CODE CONFIGURATION VALIDATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check pyrightconfig.json
if [ -f "${WORKSPACE_ROOT}/pyrightconfig.json" ]; then
    echo -e "${GREEN}✅ pyrightconfig.json exists${NC}"
else
    echo -e "${YELLOW}⚠️  pyrightconfig.json missing${NC}"
fi

# Check .vscode/settings.json
if [ -f "${WORKSPACE_ROOT}/.vscode/settings.json" ]; then
    echo -e "${GREEN}✅ .vscode/settings.json exists${NC}"
else
    echo -e "${YELLOW}⚠️  .vscode/settings.json missing${NC}"
fi

# Check .devcontainer
if [ -f "${WORKSPACE_ROOT}/.devcontainer/devcontainer.json" ]; then
    echo -e "${GREEN}✅ DevContainer configuration exists${NC}"
else
    echo -e "${YELLOW}⚠️  DevContainer configuration missing${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 7: FINAL CLEANUP AND VERIFICATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Clean Python cache
echo -e "${YELLOW}Cleaning Python cache files...${NC}"
find "${WORKSPACE_ROOT}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${WORKSPACE_ROOT}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${WORKSPACE_ROOT}" -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Python cache cleaned${NC}"

# Verify critical directories exist
REQUIRED_DIRS=("scripts" "tests" "configs" "logs" "dashboard" "data")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "${WORKSPACE_ROOT}/${dir}" ]; then
        echo -e "${GREEN}✅ Directory exists: ${dir}${NC}"
    else
        echo -e "${YELLOW}⚠️  Creating directory: ${dir}${NC}"
        mkdir -p "${WORKSPACE_ROOT}/${dir}"
    fi
done

# Create __init__.py files
echo ""
echo -e "${YELLOW}Ensuring __init__.py files exist...${NC}"
for dir in "${REQUIRED_DIRS[@]}"; do
    INIT_FILE="${WORKSPACE_ROOT}/${dir}/__init__.py"
    if [ ! -f "${INIT_FILE}" ]; then
        touch "${INIT_FILE}"
        echo -e "${GREEN}   Created: ${dir}/__init__.py${NC}"
    fi
done

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║                 ✅ EQ12 RECOVERY COMPLETE!                      ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}🎯 NEXT STEPS:${NC}"
echo ""
echo -e "${YELLOW}1. RESTART VS CODE COMPLETELY${NC}"
echo "   - Close all VS Code windows"
echo "   - Reopen ONLY /workspaces/EQ12"
echo ""
echo -e "${YELLOW}2. SELECT PYTHON INTERPRETER${NC}"
echo "   - Press Ctrl+Shift+P"
echo "   - Type: Python: Select Interpreter"
echo "   - Choose: /workspaces/EQ12/.venv/bin/python"
echo ""
echo -e "${YELLOW}3. VERIFY PYLANCE${NC}"
echo "   - Open a .py file"
echo "   - Check status bar (should show Python version)"
echo "   - Verify autocomplete works"
echo ""
echo -e "${YELLOW}4. IF STILL HAVING ISSUES:${NC}"
echo "   - Run: code --disable-extensions"
echo "   - Reinstall Python extension only"
echo "   - Reload window"
echo ""
echo -e "${CYAN}📊 DIAGNOSTIC INFO:${NC}"
echo "   Workspace: ${WORKSPACE_ROOT}"
echo "   Python: ${WORKSPACE_ROOT}/.venv/bin/python"
echo "   Config: ${WORKSPACE_ROOT}/pyrightconfig.json"
echo ""
echo -e "${GREEN}For additional help, see: /workspaces/EQ12/AGENTS.md${NC}"
echo ""
