#!/bin/bash

# Open WebUI Service Management Script - AI Platform Integration
# This script provides easy commands to manage the Open WebUI service
# Part of: AI Research Platform - Complete Stack

SERVICE_NAME="ai-platform-open-webui"

# Colors for output - matching platform style
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[OPEN-WEBUI]${NC} $1"
}

# Function to show service status
show_status() {
    print_header "AI Platform - Open WebUI Service Status:"
    sudo systemctl status $SERVICE_NAME --no-pager
}

# Function to start service
start_service() {
    print_header "Starting AI Platform - Open WebUI service..."
    sudo systemctl start $SERVICE_NAME
    sleep 3
    show_status
}

# Function to stop service
stop_service() {
    print_header "Stopping AI Platform - Open WebUI service..."
    sudo systemctl stop $SERVICE_NAME
    show_status
}

# Function to restart service
restart_service() {
    print_header "Restarting AI Platform - Open WebUI service..."
    sudo systemctl restart $SERVICE_NAME
    sleep 3
    show_status
}

# Function to enable service at startup
enable_service() {
    print_header "Enabling AI Platform - Open WebUI service at startup..."
    sudo systemctl enable $SERVICE_NAME
    print_status "✅ Open WebUI will now start automatically at boot (as part of AI Platform)"
}

# Function to disable service at startup
disable_service() {
    print_header "Disabling AI Platform - Open WebUI service at startup..."
    sudo systemctl disable $SERVICE_NAME
    print_status "❌ Open WebUI will no longer start automatically at boot"
}

# Function to show logs
show_logs() {
    print_header "AI Platform - Open WebUI Service Logs (last 50 lines):"
    sudo journalctl -u $SERVICE_NAME -n 50 --no-pager
}

# Function to follow logs in real-time
follow_logs() {
    print_header "Following AI Platform - Open WebUI Service Logs (Press Ctrl+C to exit):"
    sudo journalctl -u $SERVICE_NAME -f
}

# Function to test connectivity
test_connection() {
    print_header "Testing Open WebUI connectivity..."
    if curl -s http://100.123.10.72:11880/ >/dev/null; then
        print_status "✅ Open WebUI is accessible at http://100.123.10.72:11880/"
    else
        print_error "❌ Open WebUI is not responding"
    fi
}

# Function to show help
show_help() {
    echo -e "${BLUE}AI Platform - Open WebUI Service Manager${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the AI Platform Open WebUI service"
    echo "  stop      - Stop the AI Platform Open WebUI service"
    echo "  restart   - Restart the AI Platform Open WebUI service"
    echo "  status    - Show service status"
    echo "  enable    - Enable service at startup (integrates with AI Platform)"
    echo "  disable   - Disable service at startup"
    echo "  logs      - Show recent service logs"
    echo "  follow    - Follow service logs in real-time"
    echo "  test      - Test if Open WebUI is responding"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs"
    echo ""
    echo "Service Name: $SERVICE_NAME"
    echo "Integration: AI Research Platform - Complete Stack"
}

# Main script logic
case "${1:-help}" in
start)
    start_service
    ;;
stop)
    stop_service
    ;;
restart)
    restart_service
    ;;
status)
    show_status
    ;;
enable)
    enable_service
    ;;
disable)
    disable_service
    ;;
logs)
    show_logs
    ;;
follow)
    follow_logs
    ;;
test)
    test_connection
    ;;
help | --help | -h)
    show_help
    ;;
*)
    print_error "Unknown command: $1"
    echo ""
    show_help
    exit 1
    ;;
esac
