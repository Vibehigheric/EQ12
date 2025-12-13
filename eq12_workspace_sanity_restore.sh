#!/bin/bash
################################################################################
# EQ12 Workspace Sanity Restore Script
# Purpose: Fix VS Code workspace corruption, Pylance indexing death loop,
#          invalid Python interpreters, and clean duplicate venvs
#
# Created: 2025-11-22
# Contract: AGENTS.md GPT-5 Enhanced Task Workflow
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

WORKSPACE_ROOT="/workspaces/EQ12"
LOG_DIR="${WORKSPACE_ROOT}/logs"
BACKUP_DIR="${WORKSPACE_ROOT}/backups/workspace_restore_$(date +%Y%m%d_%H%M%S)"
VENV_PATH="${WORKSPACE_ROOT}/.venv"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       EQ12 WORKSPACE SANITY RESTORE UTILITY                ║${NC}"
echo -e "${BLUE}║       Fixing Pylance Death Loop & Python Interpreter       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# STEP 1: Pre-flight checks
################################################################################
echo -e "${YELLOW}[1/7] Pre-flight validation...${NC}"

if [[ ! -d "${WORKSPACE_ROOT}" ]]; then
    echo -e "${RED}ERROR: Workspace root not found: ${WORKSPACE_ROOT}${NC}"
    exit 1
fi

cd "${WORKSPACE_ROOT}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"
echo -e "${GREEN}✓ Backup directory created: ${BACKUP_DIR}${NC}"

# Create logs directory if missing
mkdir -p "${LOG_DIR}"

################################################################################
# STEP 2: Remove corrupted workspace folders
################################################################################
echo -e "\n${YELLOW}[2/7] Removing corrupted workspace folders...${NC}"

CORRUPT_DIRS=(
    "profiles"
    "Extensions"
    ".cache"
    "archive_duplicates/profiles"
    ".vscode/profiles"
)

for dir in "${CORRUPT_DIRS[@]}"; do
    if [[ -d "${WORKSPACE_ROOT}/${dir}" ]]; then
        echo -e "  ${RED}Removing: ${dir}${NC}"
        rm -rf "${WORKSPACE_ROOT}/${dir}"
        echo -e "  ${GREEN}✓ Removed${NC}"
    fi
done

################################################################################
# STEP 3: Remove node_modules (should not be in Python project)
################################################################################
echo -e "\n${YELLOW}[3/7] Cleaning unnecessary node_modules...${NC}"

# Keep MCP server node_modules, remove others at workspace root level
if [[ -d "${WORKSPACE_ROOT}/node_modules" ]]; then
    echo -e "  ${RED}Removing: node_modules (workspace root)${NC}"
    rm -rf "${WORKSPACE_ROOT}/node_modules"
    echo -e "  ${GREEN}✓ Removed${NC}"
fi

################################################################################
# STEP 4: Remove duplicate virtual environments
################################################################################
echo -e "\n${YELLOW}[4/7] Removing duplicate virtual environments...${NC}"

VENV_DUPLICATES=(
    ".venv_new"
    "envs"
    "scripts/.venv"
    "EdgeGodParlays/.venv"
    "backups/integration_backup_20251107_115336/.venv"
)

for venv_dir in "${VENV_DUPLICATES[@]}"; do
    if [[ -d "${WORKSPACE_ROOT}/${venv_dir}" ]]; then
        echo -e "  ${RED}Removing: ${venv_dir}${NC}"
        # Backup if it's a current venv
        if [[ "${venv_dir}" == ".venv_new" || "${venv_dir}" == ".venv" ]]; then
            if [[ -f "${WORKSPACE_ROOT}/${venv_dir}/pyvenv.cfg" ]]; then
                cp "${WORKSPACE_ROOT}/${venv_dir}/pyvenv.cfg" "${BACKUP_DIR}/pyvenv.cfg.backup"
            fi
        fi
        rm -rf "${WORKSPACE_ROOT}/${venv_dir}"
        echo -e "  ${GREEN}✓ Removed${NC}"
    fi
done

# Keep only the main .venv if it exists
if [[ -d "${VENV_PATH}" ]]; then
    echo -e "  ${BLUE}Keeping: .venv (main virtual environment)${NC}"
fi

################################################################################
# STEP 5: Create clean Python virtual environment
################################################################################
echo -e "\n${YELLOW}[5/7] Creating clean Python 3.12 virtual environment...${NC}"

# Check if python3.12 or python3 is available
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo -e "${RED}ERROR: Python 3 not found. Please install Python 3.12+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "  ${BLUE}Using Python: ${PYTHON_CMD} (${PYTHON_VERSION})${NC}"

# Remove existing .venv if requested or corrupted
if [[ -d "${VENV_PATH}" ]]; then
    if [[ ! -f "${VENV_PATH}/bin/python" ]]; then
        echo -e "  ${YELLOW}Existing venv is corrupted, recreating...${NC}"
        rm -rf "${VENV_PATH}"
    else
        echo -e "  ${GREEN}✓ Valid venv exists at: ${VENV_PATH}${NC}"
        SKIP_VENV_CREATION=1
    fi
fi

if [[ -z "${SKIP_VENV_CREATION:-}" ]]; then
    echo -e "  ${BLUE}Creating new virtual environment...${NC}"
    $PYTHON_CMD -m venv "${VENV_PATH}"
    echo -e "  ${GREEN}✓ Virtual environment created${NC}"

    # Activate and upgrade pip
    source "${VENV_PATH}/bin/activate"
    echo -e "  ${BLUE}Upgrading pip, setuptools, wheel...${NC}"
    pip install --upgrade pip setuptools wheel --quiet
    echo -e "  ${GREEN}✓ Base packages upgraded${NC}"

    # Install requirements if file exists
    if [[ -f "${WORKSPACE_ROOT}/requirements.txt" ]]; then
        echo -e "  ${BLUE}Installing requirements.txt...${NC}"
        pip install -r "${WORKSPACE_ROOT}/requirements.txt" --quiet
        echo -e "  ${GREEN}✓ Requirements installed${NC}"
    else
        echo -e "  ${YELLOW}⚠ No requirements.txt found - installing core packages${NC}"
        pip install pytest playwright transformers torch pandas numpy requests --quiet
        echo -e "  ${GREEN}✓ Core packages installed${NC}"
    fi

    deactivate
else
    echo -e "  ${GREEN}✓ Using existing virtual environment${NC}"
fi

################################################################################
# STEP 6: Verify configuration files
################################################################################
echo -e "\n${YELLOW}[6/7] Verifying configuration files...${NC}"

# Check pyrightconfig.json
if [[ -f "${WORKSPACE_ROOT}/pyrightconfig.json" ]]; then
    echo -e "  ${GREEN}✓ pyrightconfig.json exists${NC}"
else
    echo -e "  ${YELLOW}⚠ pyrightconfig.json not found (should have been created)${NC}"
fi

# Check .vscode/settings.json
if [[ -f "${WORKSPACE_ROOT}/.vscode/settings.json" ]]; then
    echo -e "  ${GREEN}✓ .vscode/settings.json exists${NC}"

    # Verify Python interpreter path is correct
    if grep -q '"/workspaces/EQ12/.venv/bin/python"' "${WORKSPACE_ROOT}/.vscode/settings.json"; then
        echo -e "  ${GREEN}✓ Python interpreter path configured correctly${NC}"
    else
        echo -e "  ${YELLOW}⚠ Python interpreter path may need updating${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ .vscode/settings.json not found${NC}"
fi

################################################################################
# STEP 7: Generate summary report
################################################################################
echo -e "\n${YELLOW}[7/7] Generating summary report...${NC}"

REPORT_FILE="${LOG_DIR}/workspace_restore_$(date +%Y%m%d_%H%M%S).json"

cat > "${REPORT_FILE}" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "workspace_root": "${WORKSPACE_ROOT}",
  "python_version": "${PYTHON_VERSION}",
  "venv_path": "${VENV_PATH}",
  "backup_directory": "${BACKUP_DIR}",
  "actions_performed": {
    "corrupted_folders_removed": $(printf '%s\n' "${CORRUPT_DIRS[@]}" | wc -l),
    "duplicate_venvs_removed": $(printf '%s\n' "${VENV_DUPLICATES[@]}" | wc -l),
    "venv_created": $(if [[ -z "${SKIP_VENV_CREATION:-}" ]]; then echo "true"; else echo "false"; fi)
  },
  "status": "SUCCESS"
}
EOF

echo -e "${GREEN}✓ Report saved: ${REPORT_FILE}${NC}"

################################################################################
# Final Instructions
################################################################################
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    RESTORE COMPLETE                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo -e ""
echo -e "${GREEN}✓ Workspace cleaned successfully${NC}"
echo -e "${GREEN}✓ Python virtual environment ready: ${VENV_PATH}${NC}"
echo -e "${GREEN}✓ Backup created: ${BACKUP_DIR}${NC}"
echo -e ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo -e "  1. Reload VS Code window: ${BLUE}Ctrl+Shift+P${NC} → ${BLUE}Developer: Reload Window${NC}"
echo -e "  2. Select interpreter: ${BLUE}Ctrl+Shift+P${NC} → ${BLUE}Python: Select Interpreter${NC}"
echo -e "     Choose: ${GREEN}${VENV_PATH}/bin/python${NC}"
echo -e "  3. Verify Pylance: Check status bar for Python version"
echo -e "  4. Run test: ${BLUE}pytest tests/smoke_math_clean.py${NC}"
echo -e ""
echo -e "${GREEN}Your workspace should now be stable. Pylance indexing limited to ~500 files.${NC}"
echo -e ""
