#!/bin/bash
# Quality check script - Run all code quality tools

set -e

echo "🔍 Starting Code Quality Checks..."
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter
PASSED=0
FAILED=0

# Function to run check
run_check() {
    local name=$1
    local command=$2
    
    echo -e "${BLUE}→${NC} Running $name..."
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name passed"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $name failed"
        ((FAILED++))
    fi
    echo ""
}

# Black formatting check
run_check "Black (Code Formatting)" "black --check ."

# isort import check
run_check "isort (Import Sorting)" "isort --check-only ."

# Flake8 linting
run_check "Flake8 (Linting)" "flake8 ."

# Pylint (optional, may fail)
echo -e "${BLUE}→${NC} Running Pylint (Code Analysis)..."
if pylint gravity_tse app --disable=all --enable=E,F > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Pylint passed"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Pylint had warnings (not critical)"
fi
echo ""

# mypy type checking
echo -e "${BLUE}→${NC} Running mypy (Type Checking)..."
if mypy gravity_tse app --ignore-missing-imports > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} mypy passed"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} mypy had issues (not critical)"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix issues.${NC}"
    exit 1
fi
