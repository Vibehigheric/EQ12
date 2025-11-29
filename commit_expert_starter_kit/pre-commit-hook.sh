#!/usr/bin/env bash
# ============================================================
# EQ12 Pre-Commit Hook - Automated Quality Control
# ============================================================
# Install: Copy to .git/hooks/pre-commit and chmod +x
# Purpose: Run checks before allowing commit
# ============================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== EQ12 Pre-Commit Validation ===${NC}"

# ============================================================
# CHECK 1: Prevent committing secrets
# ============================================================
echo -e "${YELLOW}[1/6] Checking for secrets...${NC}"

SECRET_PATTERNS=(
    "api_key"
    "API_KEY"
    "password"
    "secret"
    "token"
    "private_key"
    "-----BEGIN.*PRIVATE KEY"
    "aws_secret_access_key"
)

STAGED_FILES=$(git diff --cached --name-only)

for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        for pattern in "${SECRET_PATTERNS[@]}"; do
            if grep -i "$pattern" "$file" > /dev/null 2>&1; then
                echo -e "${RED}❌ SECURITY WARNING: Potential secret detected in $file${NC}"
                echo -e "${RED}   Pattern: $pattern${NC}"
                echo -e "${YELLOW}   If this is a false positive, add to .gitignore${NC}"
                exit 1
            fi
        done
    fi
done

echo -e "${GREEN}✅ No secrets detected${NC}"

# ============================================================
# CHECK 2: Prevent committing large files
# ============================================================
echo -e "${YELLOW}[2/6] Checking file sizes...${NC}"

MAX_SIZE_MB=10
MAX_SIZE_BYTES=$((MAX_SIZE_MB * 1024 * 1024))

for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        FILE_SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        if [ "$FILE_SIZE" -gt "$MAX_SIZE_BYTES" ]; then
            echo -e "${RED}❌ File too large: $file ($(($FILE_SIZE / 1024 / 1024)) MB)${NC}"
            echo -e "${YELLOW}   Maximum: ${MAX_SIZE_MB} MB${NC}"
            echo -e "${YELLOW}   Use Git LFS for large files${NC}"
            exit 1
        fi
    fi
done

echo -e "${GREEN}✅ All files under ${MAX_SIZE_MB} MB${NC}"

# ============================================================
# CHECK 3: Python code quality (if Python files staged)
# ============================================================
PYTHON_FILES=$(echo "$STAGED_FILES" | grep '\.py$' || true)

if [ -n "$PYTHON_FILES" ]; then
    echo -e "${YELLOW}[3/6] Checking Python code quality...${NC}"

    # Check if black is installed
    if command -v black > /dev/null 2>&1; then
        echo "  Running black formatter check..."
        if ! black --check $PYTHON_FILES; then
            echo -e "${YELLOW}  ⚠️ Python files not formatted with black${NC}"
            echo -e "${YELLOW}  Run: black <file.py> to format${NC}"
            # Don't fail, just warn
        else
            echo -e "${GREEN}  ✅ Black formatting OK${NC}"
        fi
    fi

    # Check for syntax errors
    for file in $PYTHON_FILES; do
        if ! python -m py_compile "$file"; then
            echo -e "${RED}❌ Python syntax error in $file${NC}"
            exit 1
        fi
    done

    echo -e "${GREEN}✅ Python files OK${NC}"
else
    echo -e "${YELLOW}[3/6] No Python files to check${NC}"
fi

# ============================================================
# CHECK 4: VB.NET code checks (if .vb files staged)
# ============================================================
VB_FILES=$(echo "$STAGED_FILES" | grep '\.vb$' || true)

if [ -n "$VB_FILES" ]; then
    echo -e "${YELLOW}[4/6] Checking VB.NET code...${NC}"

    for file in $VB_FILES; do
        # Check for uncommitted debug code
        if grep -i "console.writeline.*debug\|msgbox.*test\|stop" "$file" > /dev/null 2>&1; then
            echo -e "${YELLOW}  ⚠️ Possible debug code in $file${NC}"
            echo -e "${YELLOW}  Review before committing${NC}"
        fi

        # Check for proper transaction handling
        if grep -i "begintransaction\|begintrans" "$file" > /dev/null 2>&1; then
            if ! grep -i "commit\|rollback" "$file" > /dev/null 2>&1; then
                echo -e "${RED}❌ Transaction without Commit/Rollback in $file${NC}"
                exit 1
            fi
        fi
    done

    echo -e "${GREEN}✅ VB.NET files OK${NC}"
else
    echo -e "${YELLOW}[4/6] No VB.NET files to check${NC}"
fi

# ============================================================
# CHECK 5: SQL file checks
# ============================================================
SQL_FILES=$(echo "$STAGED_FILES" | grep '\.sql$' || true)

if [ -n "$SQL_FILES" ]; then
    echo -e "${YELLOW}[5/6] Checking SQL files...${NC}"

    for file in $SQL_FILES; do
        # Check for DROP TABLE without IF EXISTS
        if grep -i "drop table" "$file" | grep -v "if exists" > /dev/null 2>&1; then
            echo -e "${YELLOW}  ⚠️ DROP TABLE without IF EXISTS in $file${NC}"
            echo -e "${YELLOW}  Consider using: DROP TABLE IF EXISTS${NC}"
        fi

        # Check for BEGIN TRAN without COMMIT/ROLLBACK
        if grep -i "begin tran\|begin transaction" "$file" > /dev/null 2>&1; then
            if ! grep -i "commit\|rollback" "$file" > /dev/null 2>&1; then
                echo -e "${RED}❌ Transaction without COMMIT/ROLLBACK in $file${NC}"
                exit 1
            fi
        fi
    done

    echo -e "${GREEN}✅ SQL files OK${NC}"
else
    echo -e "${YELLOW}[5/6] No SQL files to check${NC}"
fi

# ============================================================
# CHECK 6: Commit message quality
# ============================================================
echo -e "${YELLOW}[6/6] Commit message will be validated...${NC}"
echo -e "${GREEN}✅ Pre-commit checks complete${NC}"

# All checks passed
exit 0
