#!/bin/bash
# AI Research Platform Cleanup Script
# This script stops all competing services and frees up ports for platform startup

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

print_header() {
    echo
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

print_header "AI RESEARCH PLATFORM - COMPREHENSIVE CLEANUP"

# Stop all competing systemd services
print_status "INFO" "Stopping competing systemd services..."
sudo systemctl stop ai-platform-consolidated.service ai-platform-restore.service ollama-ai-platform.service ai-platform-validator.service ai-platform.service ai-platform-open-webui.service multifamily-valuation-app.service 2>/dev/null || true

# Disable auto-restart for these services
print_status "INFO" "Disabling auto-restart for competing services..."
sudo systemctl disable ai-platform-consolidated.service ai-platform-restore.service ollama-ai-platform.service ai-platform-validator.service ai-platform.service ai-platform-open-webui.service multifamily-valuation-app.service 2>/dev/null || true

# Stop all Docker containers
print_status "INFO" "Stopping all Docker containers..."
if docker ps -q | wc -l | grep -q "0"; then
    print_status "INFO" "No running containers found"
else
    docker stop $(docker ps -aq) 2>/dev/null || true
    print_status "SUCCESS" "All containers stopped"
fi

# Remove stopped containers
print_status "INFO" "Removing stopped containers..."
docker container prune -f 2>/dev/null || true

# Kill processes on critical ports
print_status "INFO" "Freeing up critical ports..."
critical_ports=(11000 11001 11002 11003 11007 11010 11020 11021 8501 8502 8503 8504 8505 3000 7474 7687 5432 6333 6379 4000)

for port in "${critical_ports[@]}"; do
    pids=$(sudo lsof -ti:$port 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        print_status "INFO" "Killing processes on port $port: $pids"
        sudo kill -9 $pids 2>/dev/null || true
        sleep 0.5
    fi
done

# Clean up Docker resources
print_status "INFO" "Cleaning up Docker networks and volumes..."
docker network prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true

# Clean up any orphaned Docker processes
print_status "INFO" "Cleaning up orphaned Docker processes..."
sudo pkill -f "docker-proxy" 2>/dev/null || true

# Wait for cleanup to complete
sleep 3

# Verify ports are free
print_status "INFO" "Verifying critical ports are free..."
conflicts_found=false
for port in 11001 11007 11020 8502 8505; do
    if sudo netstat -tulpn | grep -q ":$port "; then
        print_status "WARNING" "Port $port is still in use"
        conflicts_found=true
    fi
done

if $conflicts_found; then
    print_status "WARNING" "Some port conflicts may remain - manual intervention may be needed"
else
    print_status "SUCCESS" "All critical ports are now free"
fi

print_header "CLEANUP COMPLETED"
print_status "SUCCESS" "Platform is ready for startup"
print_status "INFO" "You can now run: ./start-ssl-platform.sh"