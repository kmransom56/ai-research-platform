#!/bin/bash
# Environment Validation Script

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️ $message${NC}" ;;
    esac
}

echo "=== ENVIRONMENT VALIDATION ==="
echo

# Check .env file
if [[ -f "/home/keith/chat-copilot/.env" ]]; then
    print_status "SUCCESS" ".env file exists"
    
    # Check for required variables
    required_vars=(
        "AZURE_OPENAI_KEY"
        "RABBITMQ_USER"
        "RABBITMQ_PASSWORD"
        "POSTGRES_DB"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "VSCODE_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" /home/keith/chat-copilot/.env; then
            print_status "SUCCESS" "$var is set"
        else
            print_status "ERROR" "$var is missing"
        fi
    done
else
    print_status "ERROR" ".env file is missing"
fi

# Check build paths
if [[ -d "/home/keith/chat-copilot/webapp" ]]; then
    print_status "SUCCESS" "Webapp directory exists"
else
    print_status "ERROR" "Webapp directory is missing"
fi

echo
print_status "INFO" "Environment validation complete."
