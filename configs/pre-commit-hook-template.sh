#!/bin/sh
#
# EQ12 GitLeaks Pre-Commit Security Hook
# Professional-grade secret detection to prevent credential leaks
#
# Installation:
# 1. Copy this file to .git/hooks/pre-commit
# 2. Make executable: chmod +x .git/hooks/pre-commit (Linux/Mac)
# 3. Ensure GitLeaks is installed: winget install gitleaks
#
# Author: EQ12 Platform Security Team
# Version: 2.1.0

# Color codes for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# EQ12 Security Banner
echo "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo "${BLUE}🛡️  EQ12 SECURITY CHECKPOINT - Pre-Commit Secret Detection 🛡️${NC}"
echo "${BLUE}════════════════════════════════════════════════════════════════${NC}"

# Check if GitLeaks is installed
if ! command -v gitleaks &> /dev/null; then
    echo "${RED}❌ SECURITY ERROR: GitLeaks not installed!${NC}"
    echo "${YELLOW}📋 Install with: winget install gitleaks${NC}"
    echo "${YELLOW}🐧 Or on Linux: curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz | tar -xzC /usr/local/bin gitleaks${NC}"
    exit 1
fi

# Configuration
GITLEAKS_REPORT="gitleaks-precommit-report.json"
EQ12_LOG_DIR="C:/EQ12/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EQ12_LOG_FILE="${EQ12_LOG_DIR}/gitleaks_precommit_${TIMESTAMP}.log"

# Create log directory if it doesn't exist
if [ ! -d "$EQ12_LOG_DIR" ]; then
    mkdir -p "$EQ12_LOG_DIR" 2>/dev/null
fi

# Function to log security events
log_security_event() {
    local level=$1
    local message=$2
    local json_log=$(cat <<EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")",
  "level": "$level",
  "category": "SECURITY_HOOK",
  "message": "$message",
  "hook_type": "pre-commit",
  "eq12_version": "2.1.0",
  "repository": "$(pwd)"
}
EOF
)
    echo "$json_log" >> "$EQ12_LOG_FILE" 2>/dev/null
}

# Start security scan
echo "${BLUE}🔍 Scanning staged files for secrets and credentials...${NC}"
log_security_event "INFO" "Pre-commit security scan initiated"

# Run GitLeaks on staged files only
gitleaks protect --staged --report-path "$GITLEAKS_REPORT" --exit-code 1 --verbose

GITLEAKS_EXIT_CODE=$?

# Process results
if [ $GITLEAKS_EXIT_CODE -eq 0 ]; then
    # No secrets detected - allow commit
    echo "${GREEN}✅ SECURITY CHECK PASSED: No secrets detected${NC}"
    echo "${GREEN}🚀 Commit proceeding safely...${NC}"
    log_security_event "SUCCESS" "Pre-commit security scan passed - no secrets detected"
    
    # Clean up report file if empty
    if [ -f "$GITLEAKS_REPORT" ]; then
        rm -f "$GITLEAKS_REPORT"
    fi
    
    exit 0
    
else
    # Secrets detected - block commit
    echo ""
    echo "${RED}🚨 SECURITY ALERT: COMMIT BLOCKED!${NC}"
    echo "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo "${RED}GitLeaks detected secrets in your staged changes!${NC}"
    echo ""
    
    # Display findings if report exists
    if [ -f "$GITLEAKS_REPORT" ]; then
        echo "${YELLOW}📋 Security Findings:${NC}"
        echo "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
        
        # Try to pretty-print JSON report
        if command -v jq &> /dev/null; then
            jq -r '.[] | "🔥 File: \(.File)\n   Line: \(.StartLine)\n   Secret: \(.RuleID)\n   Match: \(.Match)\n"' "$GITLEAKS_REPORT" 2>/dev/null | head -20
        else
            cat "$GITLEAKS_REPORT" | head -20
        fi
        
        echo ""
        echo "${BLUE}📄 Full report saved to: $GITLEAKS_REPORT${NC}"
    fi
    
    echo "${YELLOW}🛠️  REMEDIATION OPTIONS:${NC}"
    echo "${YELLOW}────────────────────────────────────────────────────────────────${NC}"
    echo "${GREEN}1. 🔧 Auto-Fix (Recommended):${NC}"
    echo "   powershell -ExecutionPolicy Bypass -File scripts/eq12_gitleaks_autofix.ps1 -Action AutoFix"
    echo ""
    echo "${GREEN}2. 🔍 Preview Changes:${NC}"
    echo "   powershell -ExecutionPolicy Bypass -File scripts/eq12_gitleaks_autofix.ps1 -Action AutoFix -DryRun"
    echo ""
    echo "${GREEN}3. 📋 Manual Fix:${NC}"
    echo "   - Replace hardcoded secrets with: os.getenv('SECRET_NAME')"
    echo "   - Add secrets to .env file (and .env to .gitignore)"
    echo "   - Re-stage files: git add ."
    echo "   - Retry commit: git commit"
    echo ""
    echo "${GREEN}4. 🚨 Emergency Response:${NC}"
    echo "   powershell -ExecutionPolicy Bypass -File scripts/eq12_gitleaks_autofix.ps1 -Action Emergency"
    echo ""
    
    echo "${RED}⚠️  SECURITY NOTICE:${NC}"
    echo "${RED}────────────────────────────────────────────────────────────────${NC}"
    echo "• Any exposed API keys should be regenerated immediately"
    echo "• Check if secrets were previously committed: git log -p --all -S 'secret_text'"
    echo "• Consider running full security audit: EQ12 GitLeaks Full Security Audit"
    echo ""
    
    log_security_event "CRITICAL" "Pre-commit security scan FAILED - secrets detected in staged files"
    
    # Keep report for investigation
    echo "${BLUE}🔒 Security report preserved for analysis: $GITLEAKS_REPORT${NC}"
    
    exit 1
fi