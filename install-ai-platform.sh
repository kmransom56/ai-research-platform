#!/bin/bash
# Install AI Research Platform - Consolidated Installation Script

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

show_help() {
    print_header "AI RESEARCH PLATFORM - INSTALLATION OPTIONS"
    
    echo "Usage: $0 [OPTION]"
    echo
    echo "Installation Options:"
    echo "  simple      Install simplified auto-startup service (recommended)"
    echo "  complete    Install complete multi-service auto-startup"
    echo "  genai       Install GenAI Stack services"
    echo "  help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 simple     # Single consolidated service"
    echo "  $0 complete   # Full multi-service installation"
    echo "  $0 genai      # Add GenAI Stack to existing installation"
    echo
}

install_simple() {
    print_header "INSTALLING SIMPLIFIED AI PLATFORM SERVICE"
    
    if [[ -f "configs/installation/install-ai-platform-simple.sh" ]]; then
        chmod +x configs/installation/install-ai-platform-simple.sh
        ./configs/installation/install-ai-platform-simple.sh
    else
        print_status "ERROR" "Simple installation script not found"
        exit 1
    fi
}

install_complete() {
    print_header "INSTALLING COMPLETE AI PLATFORM SERVICES"
    
    if [[ -f "configs/installation/install-ai-platform-startup.sh" ]]; then
        chmod +x configs/installation/install-ai-platform-startup.sh
        ./configs/installation/install-ai-platform-startup.sh
    else
        print_status "ERROR" "Complete installation script not found"
        exit 1
    fi
}

install_genai() {
    print_header "INSTALLING GENAI STACK SERVICES"
    
    if [[ -f "configs/installation/install-genai-startup.sh" ]]; then
        chmod +x configs/installation/install-genai-startup.sh
        ./configs/installation/install-genai-startup.sh
    else
        print_status "ERROR" "GenAI installation script not found"
        exit 1
    fi
}

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
    print_status "ERROR" "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if user is in docker group
if groups | grep -q docker; then
    print_status "SUCCESS" "User is in docker group"
else
    print_status "WARNING" "User is not in docker group. Run: sudo usermod -aG docker \$USER && logout"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status "SUCCESS" "Docker Compose is available"
else
    print_status "ERROR" "Docker Compose is not available. Please install docker-compose."
    exit 1
fi

# Handle command line arguments
case "${1:-help}" in
    "simple")
        install_simple
        ;;
    "complete") 
        install_complete
        ;;
    "genai")
        install_genai
        ;;
    "help"|*)
        show_help
        ;;
esac

print_header "INSTALLATION GUIDE"

print_status "INFO" "Available installation scripts:"
echo "   📁 configs/installation/install-ai-platform-simple.sh"
echo "   📁 configs/installation/install-ai-platform-startup.sh" 
echo "   📁 configs/installation/install-genai-startup.sh"
echo
print_status "INFO" "Available startup scripts:"
echo "   🚀 ./start-ssl-platform.sh (Production SSL)"
echo "   🐳 ./start-containerized-platform.sh (Full containerization)"
echo "   ⚡ cd docker && docker-compose up (Development)"
echo
print_status "INFO" "Configuration files organized in:"
echo "   📁 configs/systemd/ (Service files)"
echo "   📁 configs/docker-compose/ (Container orchestration)"
echo "   📁 configs/nginx/ (Web server configurations)"
echo "   📁 docs/deployment/ (Deployment guides)"