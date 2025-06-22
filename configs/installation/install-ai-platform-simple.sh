#!/bin/bash
# Install AI Research Platform with Simplified Service Management

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

print_header "AI RESEARCH PLATFORM - SIMPLIFIED AUTO-STARTUP INSTALLER"

# Check if running as user (not root)
if [[ $EUID -eq 0 ]]; then
    print_status "ERROR" "Please run this script as a regular user, not root"
    exit 1
fi

# Check prerequisites
print_header "CHECKING PREREQUISITES"

# Check Docker
if command -v docker &> /dev/null; then
    print_status "SUCCESS" "Docker is installed"
else
    print_status "ERROR" "Docker is not installed"
    exit 1
fi

# Check if user is in docker group
if groups | grep -q docker; then
    print_status "SUCCESS" "User is in docker group"
else
    print_status "ERROR" "User is not in docker group. Run: sudo usermod -aG docker \$USER && logout"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status "SUCCESS" "Docker Compose is available"
else
    print_status "ERROR" "Docker Compose is not available"
    exit 1
fi

# Check environment file
if [[ -f ".env" ]]; then
    print_status "SUCCESS" "Environment file found"
else
    print_status "WARNING" "No .env file found. Copy from .env.template and configure"
fi

# Install consolidated service
print_header "INSTALLING SYSTEMD SERVICE"

if [[ -f "scripts/platform-management/ai-platform-consolidated.service" ]]; then
    sudo cp scripts/platform-management/ai-platform-consolidated.service /etc/systemd/system/
    print_status "SUCCESS" "Installed ai-platform-consolidated.service"
else
    print_status "ERROR" "Service file not found"
    exit 1
fi

# Reload systemd and enable service
sudo systemctl daemon-reload
print_status "SUCCESS" "Reloaded systemd daemon"

sudo systemctl enable ai-platform-consolidated.service
print_status "SUCCESS" "Enabled AI Platform service"

# Ensure Docker service is enabled
sudo systemctl enable docker.service
print_status "SUCCESS" "Ensured Docker service is enabled"

print_header "SERVICE OVERVIEW"

print_status "INFO" "Installed AI Research Platform Service:"
echo
echo "🔧 Complete Platform Service (ai-platform-consolidated.service):"
echo "   • Uses production SSL startup script"
echo "   • Nginx reverse proxy on port 8443"
echo "   • All services accessible via HTTPS"
echo "   • Automatic Docker container management"
echo

print_header "MANAGEMENT COMMANDS"

print_status "INFO" "Service management commands:"
echo "   • Start platform: sudo systemctl start ai-platform-consolidated"
echo "   • Stop platform: sudo systemctl stop ai-platform-consolidated"
echo "   • Status check: sudo systemctl status ai-platform-consolidated"
echo "   • View logs: sudo journalctl -u ai-platform-consolidated -f"
echo "   • Manual start: ./start-ssl-platform.sh"
echo

print_header "INCLUDED SERVICES"

print_status "INFO" "All services accessible through reverse proxy:"
echo "   🌐 Main Hub: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/"
echo "   💬 Chat Copilot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/copilot/"
echo "   👥 AutoGen Studio: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/autogen/"
echo "   🏭 Magentic-One: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/magentic/"
echo "   🔍 Perplexica: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/perplexica/"
echo "   🕵️ SearXNG: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/searxng/"
echo "   🧠 GenAI Stack: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/genai-stack/"
echo "   🗄️ Neo4j: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/neo4j/"
echo "   💻 VS Code Web: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/vscode/"
echo

print_header "INSTALLATION COMPLETE"

print_status "SUCCESS" "AI Research Platform simplified auto-startup has been installed!"
echo
print_status "INFO" "Single service manages all platform components"
print_status "WARNING" "Reboot your system to test full auto-startup functionality"
print_status "INFO" "Or start manually with: sudo systemctl start ai-platform-consolidated"