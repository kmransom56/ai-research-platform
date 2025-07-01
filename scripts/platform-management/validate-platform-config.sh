#!/bin/bash
# Boot-time Platform Configuration Validator
# Run this after reboot to check if everything is properly configured

set -euo pipefail

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

echo "=== POST-REBOOT PLATFORM VALIDATION ==="
echo

# Check Docker service
if systemctl is-active --quiet docker; then
    print_status "SUCCESS" "Docker service is running"
else
    print_status "ERROR" "Docker service is not running"
fi

# Check systemd service
if systemctl is-enabled --quiet ai-platform-consolidated.service 2>/dev/null; then
    print_status "SUCCESS" "AI Platform service is enabled"
    if systemctl is-active --quiet ai-platform-consolidated.service; then
        print_status "SUCCESS" "AI Platform service is running"
    else
        print_status "WARNING" "AI Platform service is enabled but not running"
    fi
else
    print_status "ERROR" "AI Platform service is not enabled"
fi

# Check Docker containers
echo
print_status "INFO" "Docker container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check key services
echo
print_status "INFO" "Checking key service endpoints:"

# Check nginx-ssl
if docker ps | grep -q nginx-ssl; then
    print_status "SUCCESS" "nginx-ssl container is running"
else
    print_status "ERROR" "nginx-ssl container is not running"
fi

# Check compose services
if docker-compose -f /home/keith/chat-copilot/configs/docker-compose/docker-compose-full-stack.yml ps | grep -q "Up"; then
    print_status "SUCCESS" "Docker Compose services are running"
else
    print_status "WARNING" "Some Docker Compose services may not be running"
fi

echo
print_status "INFO" "Validation complete. Check any ERROR or WARNING items above."
