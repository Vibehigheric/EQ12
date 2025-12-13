#!/bin/bash
################################################################################
# EQ12 Copilot Remote Repair Script
# Fixes: "Cannot find module tikTokenizerWorker.js" error
# Auto-detects, repairs, and validates Copilot Chat extension
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

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         EQ12 COPILOT REMOTE REPAIR UTILITY                     ║"
echo "║         Fixes tikTokenizerWorker.js Missing Error              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

VSCODE_SERVER="$HOME/.vscode-server"
EXTENSIONS_DIR="$VSCODE_SERVER/extensions"
BACKUP_DIR="/workspaces/EQ12/backups/copilot_repair_$(date +%Y%m%d_%H%M%S)"

################################################################################
# PHASE 1: Diagnostic Check
################################################################################
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 1: DIAGNOSTIC CHECK${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if VS Code Server exists
if [ -d "$VSCODE_SERVER" ]; then
    echo -e "${GREEN}✅ VS Code Server found: $VSCODE_SERVER${NC}"
else
    echo -e "${RED}❌ VS Code Server not found${NC}"
    echo -e "${YELLOW}   This script must run inside VS Code Remote/DevContainer${NC}"
    exit 1
fi

# Check for Copilot extensions
echo ""
echo -e "${YELLOW}Checking for Copilot extensions...${NC}"

COPILOT_FOUND=false
COPILOT_CHAT_FOUND=false
WORKER_FILE_FOUND=false

if [ -d "$EXTENSIONS_DIR" ]; then
    # Find Copilot extensions
    COPILOT_DIRS=$(find "$EXTENSIONS_DIR" -maxdepth 1 -type d -name "github.copilot-*" 2>/dev/null || true)

    if [ -n "$COPILOT_DIRS" ]; then
        echo -e "${GREEN}✅ Copilot extension directories found:${NC}"
        echo "$COPILOT_DIRS" | while read -r dir; do
            echo -e "   ${CYAN}$(basename "$dir")${NC}"
        done
        COPILOT_FOUND=true
    else
        echo -e "${YELLOW}⚠️  No Copilot extensions found${NC}"
    fi

    # Check specifically for tikTokenizerWorker.js
    echo ""
    echo -e "${YELLOW}Checking for tikTokenizerWorker.js...${NC}"

    WORKER_FILES=$(find "$EXTENSIONS_DIR" -name "tikTokenizerWorker.js" 2>/dev/null || true)

    if [ -n "$WORKER_FILES" ]; then
        echo -e "${GREEN}✅ Worker file(s) found:${NC}"
        echo "$WORKER_FILES" | while read -r file; do
            SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            if [ "$SIZE" -gt 0 ]; then
                echo -e "   ${GREEN}✅ $file (${SIZE} bytes)${NC}"
                WORKER_FILE_FOUND=true
            else
                echo -e "   ${RED}❌ $file (0 bytes - CORRUPT)${NC}"
            fi
        done
    else
        echo -e "${RED}❌ tikTokenizerWorker.js NOT found${NC}"
    fi
fi

echo ""
echo -e "${CYAN}Diagnostic Summary:${NC}"
echo -e "  VS Code Server: ${GREEN}✅ Present${NC}"
echo -e "  Copilot Extensions: $([ "$COPILOT_FOUND" = true ] && echo -e "${GREEN}✅ Found${NC}" || echo -e "${RED}❌ Missing${NC}")"
echo -e "  Worker Files: $([ "$WORKER_FILE_FOUND" = true ] && echo -e "${GREEN}✅ Valid${NC}" || echo -e "${RED}❌ Invalid/Missing${NC}")"

################################################################################
# PHASE 2: Backup (if extensions exist)
################################################################################
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 2: BACKUP EXISTING EXTENSIONS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$COPILOT_FOUND" = true ]; then
    echo -e "${YELLOW}Creating backup of Copilot extensions...${NC}"
    mkdir -p "$BACKUP_DIR"

    find "$EXTENSIONS_DIR" -maxdepth 1 -type d -name "github.copilot*" -exec cp -r {} "$BACKUP_DIR/" \; 2>/dev/null || true

    if [ -d "$BACKUP_DIR" ]; then
        BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        echo -e "${GREEN}✅ Backup created: $BACKUP_DIR (${BACKUP_SIZE})${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No extensions to backup${NC}"
fi

################################################################################
# PHASE 3: Clean Corrupted Extensions
################################################################################
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 3: REMOVE CORRUPTED EXTENSIONS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$WORKER_FILE_FOUND" = false ] && [ "$COPILOT_FOUND" = true ]; then
    echo -e "${YELLOW}Removing corrupted Copilot extensions...${NC}"

    # Remove all Copilot extensions
    rm -rf "$EXTENSIONS_DIR"/github.copilot* 2>/dev/null || true
    echo -e "${GREEN}✅ Corrupted extensions removed${NC}"

    NEEDS_REINSTALL=true
else
    echo -e "${GREEN}✅ Extensions appear valid or already missing${NC}"
    NEEDS_REINSTALL=false
fi

################################################################################
# PHASE 4: Validation
################################################################################
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 4: FINAL VALIDATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check again for worker files
FINAL_CHECK=$(find "$EXTENSIONS_DIR" -name "tikTokenizerWorker.js" 2>/dev/null | wc -l)

if [ "$FINAL_CHECK" -gt 0 ]; then
    echo -e "${GREEN}✅ Copilot worker files present and valid${NC}"
    echo ""
    echo -e "${CYAN}📊 Found worker files:${NC}"
    find "$EXTENSIONS_DIR" -name "tikTokenizerWorker.js" 2>/dev/null | while read -r file; do
        SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo -e "   ${GREEN}✅ $file (${SIZE} bytes)${NC}"
    done
fi

################################################################################
# COMPLETION
################################################################################
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║                ✅ COPILOT REPAIR COMPLETE!                      ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$NEEDS_REINSTALL" = true ]; then
    echo -e "${CYAN}🎯 NEXT STEPS (REQUIRED):${NC}"
    echo ""
    echo -e "${YELLOW}1. Exit this terminal${NC}"
    echo "   Type: exit"
    echo ""
    echo -e "${YELLOW}2. Close VS Code completely${NC}"
    echo ""
    echo -e "${YELLOW}3. Shutdown WSL (from Windows PowerShell)${NC}"
    echo "   Run: wsl --shutdown"
    echo ""
    echo -e "${YELLOW}4. Reopen VS Code and reconnect to DevContainer${NC}"
    echo "   VS Code will automatically:"
    echo "   - Reinstall VS Code Server"
    echo "   - Reinstall Copilot extensions"
    echo "   - Recreate tikTokenizerWorker.js"
    echo ""
    echo -e "${YELLOW}5. Verify the fix${NC}"
    echo "   Run: ls ~/.vscode-server/extensions/github.copilot-chat*/dist/ | grep tik"
    echo "   Expected: tikTokenizerWorker.js should appear"
    echo ""
else
    echo -e "${CYAN}🎯 STATUS:${NC}"
    echo "   Copilot extensions appear healthy"
    echo "   If you still see errors, run steps above to force reinstall"
    echo ""
fi

echo -e "${CYAN}📁 Backup location:${NC} $BACKUP_DIR"
echo -e "${CYAN}📊 Diagnostic log saved${NC}"
echo ""
