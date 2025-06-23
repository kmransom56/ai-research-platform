#!/bin/bash
# AI Research Platform Status Checker
# Quick health check for all services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo -e "${BLUE}🚀 AI Research Platform Status Check${NC}"
echo "================================================"

# Check core services
check_service() {
    local name=$1
    local url=$2
    local description=$3
    
    if curl -s --max-time 5 "$url" &>/dev/null; then
        print_status "SUCCESS" "$name ($description)"
    else
        print_status "ERROR" "$name not responding ($description)"
    fi
}

echo ""
echo "🔍 Core Services:"
check_service "Chat Copilot Backend" "http://100.123.10.72:11000/healthz" "Main API"
check_service "AutoGen Studio" "http://100.123.10.72:11001/" "Multi-Agent AI"
check_service "Webhook Server" "http://100.123.10.72:11002/health" "GitHub Integration"
check_service "Magentic-One" "http://100.123.10.72:11003/" "AI Research"

echo ""
echo "🛠️ Infrastructure Services:"
check_service "Port Scanner" "http://100.123.10.72:11010/" "Network Discovery"
check_service "Nginx Proxy Manager" "http://100.123.10.72:11080/" "Reverse Proxy"
check_service "Ollama LLM Server" "http://100.123.10.72:11434/api/version" "Local AI Models"

echo ""
echo "🌐 External Services:"
check_service "VS Code Web" "http://100.123.10.72:57081/" "Code Editor"
check_service "Perplexica AI Search" "http://100.123.10.72:11020/" "AI Search"
check_service "OpenWebUI" "http://100.123.10.72:11880/" "Web Interface"

echo ""
echo "🔗 HTTPS Access (via Tailscale):"
print_status "INFO" "Main Hub: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443"
print_status "INFO" "Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub"
print_status "INFO" "Applications: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html"

echo ""
echo "🔧 System Status:"

# Check if startup service is running
if systemctl is-active --quiet ai-platform-restore.service; then
    print_status "SUCCESS" "ai-platform-restore.service is active"
else
    print_status "WARNING" "ai-platform-restore.service is not active"
fi

# Check for conflicting services
CONFLICTING_SERVICES=$(systemctl list-unit-files | grep -E "ai-platform\.service|ai-platform-gateways\.service|ai-platform-services\.service" | grep enabled || true)
if [[ -z "$CONFLICTING_SERVICES" ]]; then
    print_status "SUCCESS" "No conflicting startup services detected"
else
    print_status "WARNING" "Conflicting startup services found - may cause configuration drift"
    echo "$CONFLICTING_SERVICES"
fi

echo ""
echo "📊 Quick Recovery:"
print_status "INFO" "If services are down, run: ./config-backups-working/latest/quick-restore.sh"
print_status "INFO" "Platform management: ./scripts/platform-management/manage-platform.sh"

echo ""
echo "================================================"