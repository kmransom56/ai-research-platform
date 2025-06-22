#!/bin/bash
# Install Complete AI Research Platform Auto-Startup Services

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

print_header "AI RESEARCH PLATFORM - COMPLETE AUTO-STARTUP INSTALLER"

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

# Create required directories
print_header "SETTING UP DIRECTORIES"

mkdir -p /home/keith/chat-copilot/{data,logs,pids,config}
chmod 755 /home/keith/chat-copilot/{data,logs,pids,config}

# Fix nginx-configs directory ownership if it exists
if [[ -d "/home/keith/chat-copilot/nginx-configs" ]]; then
    sudo chown -R keith:keith /home/keith/chat-copilot/nginx-configs
    chmod 755 /home/keith/chat-copilot/nginx-configs
    print_status "SUCCESS" "Fixed nginx-configs directory permissions"
else
    mkdir -p /home/keith/chat-copilot/nginx-configs
    chmod 755 /home/keith/chat-copilot/nginx-configs
    print_status "SUCCESS" "Created nginx-configs directory"
fi

print_status "SUCCESS" "Created required directories with proper permissions"

# Install systemd service files
print_header "INSTALLING SYSTEMD SERVICES"

# List of service files to install
services=(
    "ai-platform-services.service"
    "ai-platform-python.service" 
    "ai-platform-external.service"
    "ai-platform-gateways.service"
    "neo4j-genai.service"
    "genai-stack-services.service"
    "ai-platform.target"
)

for service in "${services[@]}"; do
    if [[ -f "$service" ]]; then
        sudo cp "$service" /etc/systemd/system/
        print_status "SUCCESS" "Installed $service"
    else
        print_status "WARNING" "$service not found, skipping"
    fi
done

# Reload systemd
sudo systemctl daemon-reload
print_status "SUCCESS" "Reloaded systemd daemon"

# Enable services
print_header "ENABLING SERVICES"

for service in "${services[@]}"; do
    if [[ -f "/etc/systemd/system/$service" ]]; then
        sudo systemctl enable "$service"
        print_status "SUCCESS" "Enabled $service"
    fi
done

# Ensure Docker service is enabled
sudo systemctl enable docker.service
print_status "SUCCESS" "Ensured Docker service is enabled"

print_header "SERVICE OVERVIEW"

print_status "INFO" "Installed AI Research Platform Services:"
echo
echo "🔧 Core Services (ai-platform-services.service):"
echo "   • Chat Copilot API (port 11000)"
echo "   • Chat Copilot WebApp (port 3000)"
echo
echo "🐍 Python Services (ai-platform-python.service):"
echo "   • AutoGen Studio (port 11001)"
echo "   • Webhook Server (port 11002)" 
echo "   • Magentic-One (port 11003)"
echo
echo "🌐 External Services (ai-platform-external.service):"
echo "   • Port Scanner (port 11010)"
echo "   • SearXNG (port 11021)"
echo "   • Perplexica (port 11020)"
echo "   • Ollama API (port 11434)"
echo
echo "🚪 Gateway Services (ai-platform-gateways.service):"
echo "   • Nginx Gateway (port 11080)"
echo "   • HTTP Gateway (port 11081)"
echo "   • HTTPS Gateway (port 11082)"
echo "   • Fortinet Manager (port 3001)"
echo "   • Bacula Backup (port 8081)"
echo
echo "🧠 GenAI Stack Services:"
echo "   • Neo4j Database (ports 7474, 7687)"
echo "   • GenAI Stack Apps (ports 8501-8505)"
echo

print_header "STARTUP ORDER"

print_status "INFO" "Service startup dependencies:"
echo "   1. Docker Service"
echo "   2. Core Services (Chat Copilot)"
echo "   3. External Services (Perplexica, SearXNG, etc.)"
echo "   4. Python Services (AutoGen, Magentic-One)"
echo "   5. Gateway Services (Nginx, HTTP/HTTPS)"
echo "   6. Neo4j Database"
echo "   7. GenAI Stack Applications"
echo

print_header "MANAGEMENT COMMANDS"

print_status "INFO" "Service management commands:"
echo "   • Start all: sudo systemctl start ai-platform.target"
echo "   • Stop all: sudo systemctl stop ai-platform.target"
echo "   • Status: sudo systemctl status ai-platform.target"
echo "   • Individual service: sudo systemctl start ai-platform-services.service"
echo "   • View logs: sudo journalctl -u ai-platform.target -f"
echo

print_header "INSTALLATION COMPLETE"

print_status "SUCCESS" "AI Research Platform auto-startup has been installed successfully!"
echo
print_status "INFO" "All 14+ applications will now start automatically at boot:"
echo "   ✅ copilot, copilotapi, autogen, magentic, webhook"
echo "   ✅ perplexica, searxng, portscanner, nginx"
echo "   ✅ gateway-http, gateway-https, fortinet, ollama-api, bacula"
echo "   ✅ neo4j, genai-stack (5 applications)"
echo
print_status "INFO" "Access through nginx reverse proxy at:"
echo "   🌐 https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/"
echo
print_status "WARNING" "Reboot your system to test full auto-startup functionality"
print_status "INFO" "Or start manually with: sudo systemctl start ai-platform.target"