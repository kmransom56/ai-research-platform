#!/bin/bash
# Start Complete Containerized AI Research Platform

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

# Function to handle different commands
handle_command() {
    local command=${1:-"help"}
    
    case "$command" in
        "start")
            start_platform
            ;;
        "start-build")
            start_platform_with_build
            ;;
        "stop")
            stop_platform
            ;;
        "logs")
            show_logs
            ;;
        "health")
            check_health
            ;;
        "clean")
            clean_platform
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

start_platform() {
    print_header "STARTING CONTAINERIZED AI RESEARCH PLATFORM"
    
    if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml up -d
        print_status "SUCCESS" "Full stack platform started"
    else
        print_status "ERROR" "configs/docker-compose/docker-compose-full-stack.yml not found"
        exit 1
    fi
    
    show_access_info
}

start_platform_with_build() {
    print_header "BUILDING AND STARTING CONTAINERIZED PLATFORM"
    
    if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml up -d --build
        print_status "SUCCESS" "Platform built and started"
    else
        print_status "ERROR" "configs/docker-compose/docker-compose-full-stack.yml not found"
        exit 1
    fi
    
    show_access_info
}

stop_platform() {
    print_header "STOPPING CONTAINERIZED PLATFORM"
    
    if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml down
        print_status "SUCCESS" "Platform stopped"
    else
        print_status "WARNING" "configs/docker-compose/docker-compose-full-stack.yml not found"
    fi
}

show_logs() {
    print_header "PLATFORM LOGS"
    
    if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml logs -f
    else
        print_status "ERROR" "configs/docker-compose/docker-compose-full-stack.yml not found"
        exit 1
    fi
}

check_health() {
    print_header "PLATFORM HEALTH CHECK"
    
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(ai-platform|copilot|neo4j|genai)"
}

clean_platform() {
    print_header "CLEANING PLATFORM"
    
    if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml down -v --remove-orphans
        docker system prune -f
        print_status "SUCCESS" "Platform cleaned"
    else
        print_status "WARNING" "configs/docker-compose/docker-compose-full-stack.yml not found"
    fi
}

show_access_info() {
    print_header "ACCESS INFORMATION"
    
    print_status "SUCCESS" "AI Research Platform is starting up!"
    echo
    print_status "INFO" "Access the platform at:"
    echo "   🌐 Main Hub: https://localhost:8443/"
    echo "   🎛️ Control Panel: https://localhost:8443/control-panel.html"
    echo "   📚 Applications: https://localhost:8443/applications.html"
    echo "   💬 Chat Copilot: https://localhost:8443/copilot/"
    echo "   🧠 GenAI Stack: https://localhost:8443/genai-stack/"
    echo "   🗄️ Neo4j Browser: https://localhost:8443/neo4j/"
    echo "   👥 AutoGen Studio: https://localhost:8443/autogen/"
    echo "   🔍 Perplexica: https://localhost:8443/perplexica/"
    echo
    print_status "INFO" "Services are starting up. Please wait 1-2 minutes for full availability."
    print_status "INFO" "Check service status with: $0 health"
    print_status "INFO" "View logs with: $0 logs"
}

show_help() {
    print_header "AI RESEARCH PLATFORM - CONTAINERIZED DEPLOYMENT"
    
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start          Start the platform (existing images)"
    echo "  start-build    Build and start the platform (rebuild images)"
    echo "  stop           Stop the platform"
    echo "  logs           View platform logs"
    echo "  health         Check platform health"
    echo "  clean          Stop and clean platform (removes volumes)"
    echo "  help           Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start-build    # First time setup"
    echo "  $0 start          # Normal startup"
    echo "  $0 stop           # Stop all services"
    echo "  $0 health         # Check running services"
    echo
}

# Check prerequisites
if ! command -v docker &> /dev/null; then
    print_status "ERROR" "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_status "ERROR" "Docker Compose is not available"
    exit 1
fi

# Handle the command
handle_command "${1:-help}"

print_header "AI RESEARCH PLATFORM - CONTAINERIZED STARTUP"

# Refresh HTML symlinks (control-panel, applications, index)
bash /home/keith/chat-copilot/scripts/platform-management/create-html-symlinks.sh || true