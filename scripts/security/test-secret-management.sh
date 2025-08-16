#!/bin/bash
"""
Test Suite for Secret Management System
AI Research Platform
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}🧪 Secret Management System Test Suite${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="${3:-0}"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" >/dev/null 2>&1; then
        actual_exit_code=0
    else
        actual_exit_code=$?
    fi
    
    if [ "$actual_exit_code" -eq "$expected_exit_code" ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED (exit code: $actual_exit_code, expected: $expected_exit_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test 1: Secret scanner runs without errors
run_test "Secret Scanner Basic Run" \
    "python3 $SCRIPT_DIR/secret-scanner.py --stats-only"

# Test 2: Secret replacer dry run works
run_test "Secret Replacer Dry Run" \
    "python3 $SCRIPT_DIR/secret-replacer.py --dry-run"

# Test 3: Setup script shows help
run_test "Setup Script Help" \
    "$SCRIPT_DIR/setup-github-secrets.sh help"

# Test 4: Validate GitHub Actions workflow syntax
run_test "GitHub Actions Workflow Syntax" \
    "python3 -c 'import yaml; yaml.safe_load(open(\"$PROJECT_DIR/.github/workflows/secret-management.yml\"))'"

# Test 5: Environment templates are valid
run_test "Production Environment Template" \
    "[ -f $PROJECT_DIR/configs/env-templates/.env.production.template ]"

run_test "Development Environment Template" \
    "[ -f $PROJECT_DIR/configs/env-templates/.env.development.template ]"

run_test "Local Environment Template" \
    "[ -f $PROJECT_DIR/configs/env-templates/.env.local.template ]"

# Test 6: Secret detection patterns work
echo -e "${YELLOW}Testing: Secret Detection Patterns${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Create test file with known secrets
TEST_FILE=$(mktemp)
cat > "$TEST_FILE" << 'EOF'
{
  "apiKey": "sk-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "githubToken": "ghp_abc123def456ghi789jkl012mno345pqr678",
  "password": "super_secret_password_123"
}
EOF

# Run scanner on test file
SCANNER_OUTPUT=$(python3 "$SCRIPT_DIR/secret-scanner.py" "$TEST_FILE" --format json 2>/dev/null)
SECRETS_FOUND=$(echo "$SCANNER_OUTPUT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['total_matches'])" 2>/dev/null || echo "0")

# Clean up
rm "$TEST_FILE"

if [ "$SECRETS_FOUND" -gt 0 ]; then
    echo -e "${GREEN}✅ PASSED (found $SECRETS_FOUND secrets)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ FAILED (no secrets detected in test file)${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 7: Documentation files exist
run_test "Secret Management README" \
    "[ -f $PROJECT_DIR/SECRET_MANAGEMENT_README.md ]"

# Test 8: Configuration file validation
echo -e "${YELLOW}Testing: Configuration File Validation${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Check if main appsettings.json exists and is valid JSON
if [ -f "$PROJECT_DIR/webapi/appsettings.json" ]; then
    if python3 -c "import json; json.load(open('$PROJECT_DIR/webapi/appsettings.json'))" 2>/dev/null; then
        echo -e "${GREEN}✅ PASSED (appsettings.json is valid)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED (appsettings.json is invalid JSON)${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${YELLOW}⏭️  SKIPPED (appsettings.json not found)${NC}"
fi

# Test 9: Script permissions
run_test "Setup Script Executable" \
    "[ -x $SCRIPT_DIR/setup-github-secrets.sh ]"

run_test "Test Script Executable" \
    "[ -x $SCRIPT_DIR/test-secret-management.sh ]"

# Test 10: Python module imports
run_test "Python Dependencies Available" \
    "python3 -c 'import re, os, json, argparse, sys, pathlib, dataclasses, shutil, difflib, datetime, math'"

# Summary
echo ""
echo -e "${BLUE}📊 Test Results Summary${NC}"
echo -e "${BLUE}======================${NC}"
echo ""
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Secret management system is ready.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Set up GitHub repository secrets: ./scripts/security/setup-github-secrets.sh"
    echo "2. Run secret scanner: python3 scripts/security/secret-scanner.py"
    echo "3. Apply secret replacements: python3 scripts/security/secret-replacer.py --apply"
    echo "4. Commit and push to trigger GitHub Actions workflows"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    echo ""
    exit 1
fi