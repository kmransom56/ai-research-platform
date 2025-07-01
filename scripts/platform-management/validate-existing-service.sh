#!/bin/bash
# Validation script for ai-platform-restore.service

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

echo "=== AI PLATFORM RESTORE SERVICE VALIDATION ==="
echo

# Check service status
if systemctl is-enabled ai-platform-restore.service >/dev/null 2>&1; then
    print_status "SUCCESS" "ai-platform-restore.service is enabled"
else
    print_status "ERROR" "ai-platform-restore.service is not enabled"
fi

if systemctl is-active ai-platform-restore.service >/dev/null 2>&1; then
    print_status "SUCCESS" "ai-platform-restore.service is active"
else
    print_status "ERROR" "ai-platform-restore.service is not active"
fi

# Check Docker
if systemctl is-active docker >/dev/null 2>&1; then
    print_status "SUCCESS" "Docker service is running"
else
    print_status "ERROR" "Docker service is not running"
fi

# Check Docker containers
echo
print_status "INFO" "Current Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || print_status "WARNING" "Cannot connect to Docker daemon"

# Check service logs
echo
print_status "INFO" "Recent service logs:"
journalctl -u ai-platform-restore.service --no-pager -n 10 2>/dev/null || print_status "WARNING" "Cannot access service logs"

# Check if platform is accessible
echo
print_status "INFO" "Testing platform accessibility..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:11000 | grep -q "200\|302\|404"; then
    print_status "SUCCESS" "Platform backend is responding"
else
    print_status "WARNING" "Platform backend may not be accessible"
fi

echo
print_status "INFO" "Validation complete."
