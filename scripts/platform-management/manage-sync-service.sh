#!/bin/bash
# Chat Copilot Real-time Sync Service Management
# Manages the systemd service for real-time backup synchronization

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/chat-copilot-sync.service"
SERVICE_NAME="chat-copilot-sync"
PLATFORM_ROOT="/home/keith/chat-copilot"

log_msg() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${BLUE}[$timestamp] ℹ️  $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}[$timestamp] ✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}[$timestamp] ⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}[$timestamp] ❌ $message${NC}" ;;
    esac
}

install_service() {
    log_msg "INFO" "Installing Chat Copilot sync service..."
    
    if [[ ! -f "$SERVICE_FILE" ]]; then
        log_msg "ERROR" "Service file not found: $SERVICE_FILE"
        return 1
    fi
    
    # Copy service file to systemd directory
    sudo cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME.service"
    
    log_msg "SUCCESS" "Service installed and enabled"
}

uninstall_service() {
    log_msg "INFO" "Uninstalling Chat Copilot sync service..."
    
    # Stop and disable service
    sudo systemctl stop "$SERVICE_NAME.service" 2>/dev/null || true
    sudo systemctl disable "$SERVICE_NAME.service" 2>/dev/null || true
    
    # Remove service file
    sudo rm -f "/etc/systemd/system/$SERVICE_NAME.service"
    sudo systemctl daemon-reload
    
    log_msg "SUCCESS" "Service uninstalled"
}

start_service() {
    log_msg "INFO" "Starting Chat Copilot sync service..."
    
    if ! systemctl is-enabled "$SERVICE_NAME.service" >/dev/null 2>&1; then
        log_msg "WARNING" "Service not installed. Installing first..."
        install_service
    fi
    
    sudo systemctl start "$SERVICE_NAME.service"
    sleep 2
    
    if systemctl is-active "$SERVICE_NAME.service" >/dev/null 2>&1; then
        log_msg "SUCCESS" "Service started successfully"
    else
        log_msg "ERROR" "Failed to start service"
        return 1
    fi
}

stop_service() {
    log_msg "INFO" "Stopping Chat Copilot sync service..."
    
    sudo systemctl stop "$SERVICE_NAME.service" 2>/dev/null || true
    
    # Also stop any manual sync processes
    "$PLATFORM_ROOT/sync-with-backup-server.sh" realtime-stop 2>/dev/null || true
    
    log_msg "SUCCESS" "Service stopped"
}

restart_service() {
    log_msg "INFO" "Restarting Chat Copilot sync service..."
    
    stop_service
    sleep 2
    start_service
}

status_service() {
    log_msg "INFO" "Checking Chat Copilot sync service status..."
    
    echo
    echo "=== System Service Status ==="
    if systemctl is-enabled "$SERVICE_NAME.service" >/dev/null 2>&1; then
        echo "✅ Service is installed and enabled"
        
        if systemctl is-active "$SERVICE_NAME.service" >/dev/null 2>&1; then
            echo "✅ Service is running"
            
            # Show service info
            echo
            echo "Service Details:"
            systemctl status "$SERVICE_NAME.service" --no-pager -l
        else
            echo "❌ Service is not running"
            
            # Show recent logs
            echo
            echo "Recent Logs:"
            journalctl -u "$SERVICE_NAME.service" --no-pager -l -n 10
        fi
    else
        echo "❌ Service is not installed"
    fi
    
    echo
    echo "=== Manual Sync Status ==="
    "$PLATFORM_ROOT/sync-with-backup-server.sh" realtime-status
    
    echo
    echo "=== Network Connectivity ==="
    "$PLATFORM_ROOT/sync-with-backup-server.sh" check
}

show_logs() {
    log_msg "INFO" "Showing Chat Copilot sync service logs..."
    
    echo "=== Service Logs (last 50 lines) ==="
    journalctl -u "$SERVICE_NAME.service" --no-pager -l -n 50
    
    echo
    echo "=== Manual Sync Logs ==="
    if [[ -f "$PLATFORM_ROOT/logs/sync/backup-sync.log" ]]; then
        tail -20 "$PLATFORM_ROOT/logs/sync/backup-sync.log"
    else
        echo "No manual sync logs found"
    fi
}

show_usage() {
    echo "Chat Copilot Real-time Sync Service Management"
    echo
    echo "USAGE:"
    echo "    $0 <command>"
    echo
    echo "COMMANDS:"
    echo "    install    - Install systemd service"
    echo "    uninstall  - Uninstall systemd service"
    echo "    start      - Start sync service"
    echo "    stop       - Stop sync service"
    echo "    restart    - Restart sync service"
    echo "    status     - Show service status"
    echo "    logs       - Show service logs"
    echo "    help       - Show this help"
    echo
    echo "EXAMPLES:"
    echo "    $0 install     # Install and enable service"
    echo "    $0 start       # Start real-time sync"
    echo "    $0 status      # Check if sync is running"
    echo "    $0 logs        # View sync logs"
}

main() {
    local command="${1:-help}"
    
    case "$command" in
        "install")
            install_service
            ;;
        "uninstall")
            uninstall_service
            ;;
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            status_service
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_msg "ERROR" "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Check for required commands
for cmd in systemctl journalctl; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_msg "ERROR" "Required command not found: $cmd"
        exit 1
    fi
done

# Header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Chat Copilot Real-time Sync Service Manager         ║"
echo "║                   Service: $SERVICE_NAME                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

main "$@"