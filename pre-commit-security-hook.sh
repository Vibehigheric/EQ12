# Pre-commit security hook for EQ12
# Prevents accidental commit of sensitive data
# Save as .git/hooks/pre-commit and chmod +x

#!/bin/bash

echo "🔍 EQ12 Security Pre-commit Check..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Flag for issues found
ISSUES_FOUND=false

# Check 1: Scan for API keys and tokens
echo "Checking for API keys and tokens..."
if git diff --cached --name-only | xargs grep -l "sk-[a-zA-Z0-9]" 2>/dev/null; then
    echo -e "${RED}❌ OpenAI API key detected in staged files!${NC}"
    ISSUES_FOUND=true
fi

if git diff --cached --name-only | xargs grep -l "[0-9]*:.*" | xargs grep -l "token" 2>/dev/null; then
    echo -e "${RED}❌ Bot token detected in staged files!${NC}"
    ISSUES_FOUND=true
fi

if git diff --cached --name-only | xargs grep -l "AKIA[0-9A-Z]" 2>/dev/null; then
    echo -e "${RED}❌ AWS access key detected in staged files!${NC}"
    ISSUES_FOUND=true
fi

# Check 2: Verify sensitive directories/files aren't staged
SENSITIVE_PATHS=(
    "keys/"
    ".env"
    "credentials.json"
    "secrets.json"
    "logs/"
    "data/"
    "*.db"
    "*.sqlite"
)

for path in "${SENSITIVE_PATHS[@]}"; do
    if git diff --cached --name-only | grep -q "$path"; then
        echo -e "${RED}❌ Sensitive path detected: $path${NC}"
        ISSUES_FOUND=true
    fi
done

# Check 3: Verify .gitignore is protecting sensitive files
if [ ! -f ".gitignore" ]; then
    echo -e "${RED}❌ No .gitignore file found!${NC}"
    ISSUES_FOUND=true
else
    REQUIRED_IGNORES=("keys/" "*.key" ".env" "credentials.*" "logs/")
    for ignore in "${REQUIRED_IGNORES[@]}"; do
        if ! grep -q "^$ignore" .gitignore; then
            echo -e "${YELLOW}⚠️ .gitignore missing: $ignore${NC}"
        fi
    done
fi

# Check 4: Validate credential manager usage
if git diff --cached --name-only | xargs grep -l "OPENAI_API_KEY\s*=" 2>/dev/null | grep -v "credential_manager"; then
    echo -e "${YELLOW}⚠️ Direct API key usage detected. Consider using credential manager.${NC}"
fi

# Check 5: Scan for personal information patterns
PERSONAL_PATTERNS=(
    "password\s*=\s*[\"'][^\"']+[\"']"
    "email.*@.*\.com"
    "phone.*[0-9]{10}"
    "ssn.*[0-9]{3}-[0-9]{2}-[0-9]{4}"
)

for pattern in "${PERSONAL_PATTERNS[@]}"; do
    if git diff --cached | grep -i "$pattern" >/dev/null; then
        echo -e "${YELLOW}⚠️ Potential personal information detected: $pattern${NC}"
    fi
done

# Results
if [ "$ISSUES_FOUND" = true ]; then
    echo -e "${RED}"
    echo "╔════════════════════════════════════════╗"
    echo "║          COMMIT BLOCKED!               ║"
    echo "║                                        ║"
    echo "║  Sensitive data detected in commit.    ║"
    echo "║  Remove secrets before committing.     ║"
    echo "║                                        ║"
    echo "║  Use: eq12_credential_manager.py       ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Security check passed. Proceeding with commit.${NC}"
    exit 0
fi
