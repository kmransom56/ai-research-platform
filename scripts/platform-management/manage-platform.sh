#!/bin/bash
# User-Friendly Platform Management Interface - UPDATED
# Simple commands for users to manage the AI Research Platform
# Updated for new simplified startup system (v4.0)

SCRIPT_DIR="/home/keith/chat-copilot"
LOG_FILE="$SCRIPT_DIR/logs/management.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >>"$LOG_FILE"
}

# Function to display colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
    "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
    "ERROR") echo -e "${RED}❌ $message${NC}" ;;
    "WARNING") echo -e "${YELLOW}⚠️ $message${NC}" ;;
    "INFO") echo -e "${BLUE}ℹ️ $message${NC}" ;;
    "HEADER") echo -e "${PURPLE}🚀 $message${NC}" ;;
    esac
}

# Function to show platform status
show_status() {
    print_status "HEADER" "AI Research Platform Status"
    echo ""

    # Check ALL services with standardized ports
    local services=(
        "Chat Copilot Backend|http://100.123.10.72:11000/healthz"
        "AutoGen Studio|http://100.123.10.72:11001/"
        "Webhook Server|http://100.123.10.72:11002/health"
        "Magentic-One Server|http://100.123.10.72:11003/"
        "Port Scanner|http://100.123.10.72:11010/"
        "Nginx Proxy Manager|http://100.123.10.72:11080/"
        "Fortinet Manager|http://100.123.10.72:3001/"
        "Fortinet API|http://100.123.10.72:5000/api/v1/health"
        "Perplexica Search AI|http://100.123.10.72:11020"
        "SearXNG Search Engine|http://100.123.10.72:11021/"
        "OpenWebUI|http://100.123.10.72:11880/"
        "Ollama LLM Server|http://100.123.10.72:11434/api/version"
        "VS Code Web|http://100.123.10.72:57081/"
    )

    for service in "${services[@]}"; do
        IFS='|' read -r name url <<<"$service"
        if curl -s --max-time 5 "$url" &>/dev/null; then
            print_status "SUCCESS" "$name is running"
        else
            print_status "ERROR" "$name is not responding"
        fi
    done

    echo ""
    print_status "INFO" "🌐 SERVICE ENDPOINTS:"
    print_status "INFO" "   🏠 Chat Copilot: http://100.123.10.72:11000"
    print_status "INFO" "   🤖 AutoGen Studio: http://100.123.10.72:11001"
    print_status "INFO" "   🌟 Magentic-One: http://100.123.10.72:11003"
    print_status "INFO" "   🔍 Port Scanner: http://100.123.10.72:11010"
    print_status "INFO" "   🔧 Nginx Proxy Manager: http://100.123.10.72:11080"
    print_status "INFO" "   🛡️ Fortinet Manager: http://100.123.10.72:3001"
    print_status "INFO" "   🔌 Fortinet API: http://100.123.10.72:5000"
    print_status "INFO" "   💻 VS Code Web: http://100.123.10.72:57081"
    print_status "INFO" "   🌐 OpenWebUI: http://100.123.10.72:11880"
    echo ""
    print_status "INFO" "🔒 HTTPS ACCESS (via Caddy Proxy):"
    print_status "INFO" "   🌐 Main Hub: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443"
    print_status "INFO" "   🎛️ Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub"
    print_status "INFO" "   📋 Applications: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html"
    print_status "INFO" "   🤖 Chat Copilot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/copilot"
    print_status "INFO" "   🌟 AutoGen Studio: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/autogen"
    print_status "INFO" "   💫 Magentic-One: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/magentic"
    print_status "INFO" "   🔍 Perplexica: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/perplexica"
    print_status "INFO" "   🌐 OpenWebUI: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/openwebui"
    print_status "INFO" "   💻 VS Code: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/vscode/login"
    echo ""
    print_status "INFO" "🤖 AI RESEARCH SERVICES:"
    print_status "INFO" "   🔍 Perplexica: http://100.123.10.72:11020"
    print_status "INFO" "   🔍 SearXNG: http://100.123.10.72:11021"
    print_status "INFO" "   💬 OpenWebUI: http://100.123.10.72:11880"
}

# Function to start platform (UPDATED)
start_platform() {
    print_status "HEADER" "Starting AI Research Platform"
    log "User requested platform start"

    print_status "INFO" "Using new simplified startup system"
    
    # Check if ai-platform-restore.service is available
    if systemctl is-enabled ai-platform-restore.service &>/dev/null; then
        print_status "INFO" "Running ai-platform-restore.service..."
        sudo systemctl restart ai-platform-restore.service
        sleep 5
        
        if systemctl is-active ai-platform-restore.service &>/dev/null; then
            print_status "SUCCESS" "Platform started successfully via SystemD service"
        else
            print_status "WARNING" "SystemD service failed, trying manual restore..."
            start_manual_restore
        fi
    else
        print_status "INFO" "SystemD service not available, using manual restore..."
        start_manual_restore
    fi
    
    echo ""
    show_status
}

# Function to start via manual restore
start_manual_restore() {
    local restore_script="$SCRIPT_DIR/config-backups-working/latest/quick-restore.sh"
    
    if [ -f "$restore_script" ]; then
        print_status "INFO" "Running quick restore script..."
        if bash "$restore_script" >>"$LOG_FILE" 2>&1; then
            print_status "SUCCESS" "Platform started via manual restore"
        else
            print_status "ERROR" "Manual restore failed - check logs"
            print_status "INFO" "Log file: $LOG_FILE"
        fi
    else
        print_status "ERROR" "Quick restore script not found"
        print_status "INFO" "Run backup script to create restore point first"
    fi
}

# Function to stop platform
stop_platform() {
    print_status "HEADER" "Stopping AI Research Platform"
    log "User requested platform stop"

    print_status "INFO" "Stopping services..."

    # Use comprehensive stop script
    if [ -f "$SCRIPT_DIR/stop-platform.sh" ]; then
        "$SCRIPT_DIR/stop-platform.sh" >>"$LOG_FILE" 2>&1
        print_status "SUCCESS" "All services stopped via stop-platform.sh"
    else
        # Fallback - stop known processes manually
        pkill -f "dotnet.*webapi" && print_status "SUCCESS" "Stopped Chat Copilot Backend"
        pkill -f "autogenstudio" && print_status "SUCCESS" "Stopped AutoGen Studio"
        pkill -f "magentic_one" && print_status "SUCCESS" "Stopped Magentic-One"
        pkill -f "webhook-server" && print_status "SUCCESS" "Stopped Webhook Server"
        pkill -f "port-scanner" && print_status "SUCCESS" "Stopped Port Scanner"
        pkill -f "health-monitor" && print_status "SUCCESS" "Stopped Health Monitor"
    fi

    # Stop Docker services
    if docker-compose -f "$SCRIPT_DIR/docker-compose.nginx-proxy-manager.yml" down &>/dev/null; then
        print_status "SUCCESS" "Stopped Docker services"
    fi

    print_status "SUCCESS" "Platform stopped"
}

# Function to restart platform
restart_platform() {
    print_status "HEADER" "Restarting AI Research Platform"
    stop_platform
    sleep 5
    start_platform
}

# Function to validate configuration
validate_configuration() {
    print_status "HEADER" "Validating Platform Configuration"

    if [ -f "$SCRIPT_DIR/validate-config.sh" ]; then
        "$SCRIPT_DIR/validate-config.sh"
    else
        print_status "ERROR" "Configuration validator not found"
        return 1
    fi
}

# Function to show logs
show_logs() {
    local service=$1
    print_status "HEADER" "Platform Logs"

    if [ -z "$service" ]; then
        echo "Available logs:"
        ls -la "$SCRIPT_DIR/logs/" 2>/dev/null | grep -E "\.(log)$" | awk '{print "  " $9}'
        echo ""
        echo "Usage: $0 logs [service_name]"
        echo "Example: $0 logs port-scanner"
        return 0
    fi

    local log_file="$SCRIPT_DIR/logs/$service.log"
    if [ -f "$log_file" ]; then
        print_status "INFO" "Showing last 50 lines of $service logs:"
        echo ""
        tail -50 "$log_file"
    else
        print_status "ERROR" "Log file not found: $log_file"
    fi
}

# Function to backup configuration
backup_config() {
    print_status "HEADER" "Creating Configuration Backup"

    if [ -f "$SCRIPT_DIR/backup-configs-auto.sh" ]; then
        "$SCRIPT_DIR/backup-configs-auto.sh"
        print_status "SUCCESS" "Configuration backup created"
    else
        print_status "ERROR" "Backup script not found"
    fi
}

# Function to restore configuration
restore_config() {
    local backup_name=${1:-"latest"}
    print_status "HEADER" "Restoring Configuration"

    if [ -f "$SCRIPT_DIR/restore-config.sh" ]; then
        "$SCRIPT_DIR/restore-config.sh" "$backup_name"
    else
        print_status "ERROR" "Restore script not found"
    fi
}

# Function to enable monitoring
enable_monitoring() {
    print_status "HEADER" "Enabling Health Monitoring"

    if [ -f "$SCRIPT_DIR/health-monitor.sh" ]; then
        # Start health monitor in background
        nohup "$SCRIPT_DIR/health-monitor.sh" >"$SCRIPT_DIR/logs/health-monitor.log" 2>&1 &
        local monitor_pid=$!
        echo $monitor_pid >"$SCRIPT_DIR/pids/health-monitor.pid"
        print_status "SUCCESS" "Health monitoring enabled (PID: $monitor_pid)"
        print_status "INFO" "Monitor logs: $SCRIPT_DIR/logs/health-monitor.log"
    else
        print_status "ERROR" "Health monitor not found"
    fi
}

# Function to disable monitoring
disable_monitoring() {
    print_status "HEADER" "Disabling Health Monitoring"

    if [ -f "$SCRIPT_DIR/pids/health-monitor.pid" ]; then
        local monitor_pid=$(cat "$SCRIPT_DIR/pids/health-monitor.pid")
        if kill "$monitor_pid" 2>/dev/null; then
            print_status "SUCCESS" "Health monitoring disabled"
            rm -f "$SCRIPT_DIR/pids/health-monitor.pid"
        else
            print_status "WARNING" "Health monitor process not found"
        fi
    else
        print_status "INFO" "Health monitor was not running"
    fi
}

# Function to emergency reset
emergency_reset() {
    print_status "HEADER" "Emergency Reset"

    echo -e "${RED}⚠️ WARNING: This will reset all configurations to defaults!${NC}"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" = "yes" ]; then
        if [ -f "$SCRIPT_DIR/emergency-reset.sh" ]; then
            "$SCRIPT_DIR/emergency-reset.sh"
        else
            print_status "ERROR" "Emergency reset script not found"
        fi
    else
        print_status "INFO" "Emergency reset cancelled"
    fi
}

# Function to show help
show_help() {
    echo -e "${PURPLE}🚀 AI Research Platform Management${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  status                    - Show platform status"
    echo "  start                     - Start the platform"
    echo "  stop                      - Stop the platform"
    echo "  restart                   - Restart the platform"
    echo "  validate                  - Validate configuration"
    echo "  logs [service]            - Show logs"
    echo "  backup                    - Create configuration backup"
    echo "  restore [backup_name]     - Restore configuration"
    echo "  monitor-enable            - Enable health monitoring"
    echo "  monitor-disable           - Disable health monitoring"
    echo "  emergency-reset           - Emergency reset to defaults"
    echo "  help                      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 status                 - Check if services are running"
    echo "  $0 start                  - Start all services"
    echo "  $0 logs port-scanner      - Show port scanner logs"
    echo "  $0 restore latest         - Restore latest backup"
    echo ""
    echo "Useful URLs (Port Range: 11000-12000):"
    echo "  🔒 HTTPS (Recommended):"
    echo "  • 🌐 Main Hub: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443"
    echo "  • 🎛️ Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub"
    echo "  • 📋 Applications: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html"
    echo "  • 🤖 Chat Copilot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/copilot"
    echo "  • 🌟 AutoGen Studio: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/autogen"
    echo "  • 💫 Magentic-One: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/magentic"
    echo "  • 🔍 Perplexica: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/perplexica"
    echo "  • 🌐 OpenWebUI: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/openwebui"
    echo "  • 💻 VS Code: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/vscode/login"
    echo ""
    echo "  📡 HTTP (Direct):"
    echo "  • 🏠 Chat Copilot: http://100.123.10.72:11000"
    echo "  • 🤖 AutoGen Studio: http://100.123.10.72:11001"
    echo "  • 🔗 Webhook Server: http://100.123.10.72:11002/health"
    echo "  • 🌟 Magentic-One: http://100.123.10.72:11003"
    echo "  • 🔍 Port Scanner: http://100.123.10.72:11010"
    echo "  • 🔧 Nginx Proxy Manager: http://100.123.10.72:11080"
    echo "  • 🛡️ Fortinet Manager: http://100.123.10.72:3001"
    echo "  • 🔌 Fortinet API: http://100.123.10.72:5000"
    echo "  • 💻 VS Code Web: http://100.123.10.72:57081"
    echo "  • 🌐 OpenWebUI: http://100.123.10.72:11880"
    echo "  • 🦙 Ollama LLM: http://100.123.10.72:11434"
}

# Main command handler
main() {
    # Create logs directory
    mkdir -p "$SCRIPT_DIR/logs"

    case "${1:-help}" in
    "status")
        show_status
        ;;
    "start")
        start_platform
        ;;
    "stop")
        stop_platform
        ;;
    "restart")
        restart_platform
        ;;
    "validate")
        validate_configuration
        ;;
    "logs")
        show_logs "$2"
        ;;
    "backup")
        backup_config
        ;;
    "restore")
        restore_config "$2"
        ;;
    "monitor-enable")
        enable_monitoring
        ;;
    "monitor-disable")
        disable_monitoring
        ;;
    "emergency-reset")
        emergency_reset
        ;;
    "help" | "--help" | "-h")
        show_help
        ;;
    *)
        print_status "ERROR" "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
    esac
}

# Run main function
main "$@"
