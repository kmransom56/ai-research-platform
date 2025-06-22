#!/bin/bash
# Install GenAI Stack Auto-Startup Services

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

print_header "AI RESEARCH PLATFORM - GENAI STACK AUTO-STARTUP INSTALLER"

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

# Create data directory with proper permissions
print_header "SETTING UP DATA DIRECTORIES"

mkdir -p /home/keith/chat-copilot/data
chmod 755 /home/keith/chat-copilot/data
print_status "SUCCESS" "Created data directory with proper permissions"

# Install systemd service files
print_header "INSTALLING SYSTEMD SERVICES"

sudo cp neo4j-genai.service /etc/systemd/system/
sudo cp genai-stack-services.service /etc/systemd/system/
sudo cp ai-platform.target /etc/systemd/system/

print_status "SUCCESS" "Copied service files to /etc/systemd/system/"

# Reload systemd
sudo systemctl daemon-reload
print_status "SUCCESS" "Reloaded systemd daemon"

# Enable services
sudo systemctl enable neo4j-genai.service
sudo systemctl enable genai-stack-services.service
sudo systemctl enable ai-platform.target

print_status "SUCCESS" "Enabled GenAI Stack services for auto-startup"

# Ensure Docker service is enabled
sudo systemctl enable docker.service
print_status "SUCCESS" "Ensured Docker service is enabled"

print_header "TESTING SERVICE INSTALLATION"

# Test Neo4j service
print_status "INFO" "Testing Neo4j service..."
if sudo systemctl start neo4j-genai.service; then
    print_status "SUCCESS" "Neo4j service started successfully"
    
    # Wait for Neo4j to be ready
    print_status "INFO" "Waiting for Neo4j to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:7474 &> /dev/null; then
            print_status "SUCCESS" "Neo4j is responding on port 7474"
            break
        fi
        sleep 2
    done
else
    print_status "ERROR" "Failed to start Neo4j service"
    sudo journalctl -u neo4j-genai.service --no-pager -l
fi

print_header "INSTALLATION COMPLETE"

print_status "SUCCESS" "GenAI Stack auto-startup has been installed successfully!"
echo
print_status "INFO" "Services installed:"
echo "   • neo4j-genai.service - Neo4j Database"
echo "   • genai-stack-services.service - GenAI Stack Applications"
echo "   • ai-platform.target - Master target for all services"
echo
print_status "INFO" "Service management commands:"
echo "   • Start all: sudo systemctl start ai-platform.target"
echo "   • Stop all: sudo systemctl stop ai-platform.target"
echo "   • Status: sudo systemctl status ai-platform.target"
echo "   • View logs: sudo journalctl -u neo4j-genai.service -f"
echo
print_status "INFO" "Services will now start automatically at boot!"
echo
print_status "INFO" "Access URLs:"
echo "   • Neo4j Browser: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/neo4j/"
echo "   • GenAI Stack: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/"
echo
print_status "WARNING" "Reboot your system to test full auto-startup functionality"