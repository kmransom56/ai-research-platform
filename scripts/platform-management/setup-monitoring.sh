#!/bin/bash
# Setup script for AI Research Platform automated monitoring

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SERVICE_FILE="/home/keith/chat-copilot/configs/ai-platform-health-monitor.service"
readonly SYSTEMD_SERVICE_FILE="/etc/systemd/system/ai-platform-health-monitor.service"

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

check_prerequisites() {
    print_status "INFO" "Checking prerequisites..."
    
    # Check if running as root for systemd service installation
    if [ "$EUID" -eq 0 ]; then
        print_status "SUCCESS" "Running as root - can install systemd service"
    else
        print_status "WARNING" "Not running as root - will skip systemd service installation"
    fi
    
    # Check if Docker is running
    if systemctl is-active --quiet docker; then
        print_status "SUCCESS" "Docker service is running"
    else
        print_status "ERROR" "Docker service is not running"
        return 1
    fi
    
    # Check health check script
    if [ -x "$SCRIPT_DIR/health-check.sh" ]; then
        print_status "SUCCESS" "Health check script found and executable"
    else
        print_status "ERROR" "Health check script not found or not executable"
        return 1
    fi
    
    # Check automated monitor script
    if [ -x "$SCRIPT_DIR/automated-health-monitor.sh" ]; then
        print_status "SUCCESS" "Automated health monitor script found and executable"
    else
        print_status "ERROR" "Automated health monitor script not found or not executable"
        return 1
    fi
}

create_log_directories() {
    print_status "INFO" "Creating log directories..."
    
    local log_dir="/home/keith/chat-copilot/logs/health-monitoring"
    mkdir -p "$log_dir"
    chown keith:keith "$log_dir" 2>/dev/null || true
    
    print_status "SUCCESS" "Log directory created: $log_dir"
}

install_systemd_service() {
    if [ "$EUID" -ne 0 ]; then
        print_status "WARNING" "Skipping systemd service installation (not root)"
        return 0
    fi
    
    print_status "INFO" "Installing systemd service..."
    
    if [ -f "$SERVICE_FILE" ]; then
        cp "$SERVICE_FILE" "$SYSTEMD_SERVICE_FILE"
        systemctl daemon-reload
        print_status "SUCCESS" "Systemd service installed"
        
        print_status "INFO" "Service commands available:"
        echo "  sudo systemctl start ai-platform-health-monitor"
        echo "  sudo systemctl stop ai-platform-health-monitor"
        echo "  sudo systemctl enable ai-platform-health-monitor"
        echo "  sudo systemctl status ai-platform-health-monitor"
    else
        print_status "ERROR" "Service file not found: $SERVICE_FILE"
        return 1
    fi
}

test_monitoring() {
    print_status "INFO" "Testing monitoring system..."
    
    # Test single health check
    if "$SCRIPT_DIR/automated-health-monitor.sh" check; then
        print_status "SUCCESS" "Health monitoring test passed"
    else
        print_status "ERROR" "Health monitoring test failed"
        return 1
    fi
    
    # Test cleanup script
    if "$SCRIPT_DIR/cleanup-config-snapshots.sh" analyze > /dev/null 2>&1; then
        print_status "SUCCESS" "Configuration cleanup test passed"
    else
        print_status "ERROR" "Configuration cleanup test failed"
        return 1
    fi
}

show_usage_instructions() {
    echo
    print_status "INFO" "Monitoring System Setup Complete!"
    echo
    echo -e "${BLUE}📋 Available Commands:${NC}"
    echo -e "   ${YELLOW}Health Monitoring:${NC}"
    echo -e "     ./automated-health-monitor.sh check      - Run single health check"
    echo -e "     ./automated-health-monitor.sh status     - Show monitoring status"
    echo -e "     ./automated-health-monitor.sh monitor    - Start continuous monitoring"
    echo -e "     ./automated-health-monitor.sh recover    - Attempt auto-recovery"
    echo -e "     ./automated-health-monitor.sh stop       - Stop monitoring"
    echo
    echo -e "   ${YELLOW}Configuration Cleanup:${NC}"
    echo -e "     ./cleanup-config-snapshots.sh analyze    - Analyze snapshots"
    echo -e "     ./cleanup-config-snapshots.sh cleanup    - Dry-run cleanup"
    echo -e "     ./cleanup-config-snapshots.sh cleanup-force - Actual cleanup"
    echo
    if [ "$EUID" -eq 0 ]; then
        echo -e "   ${YELLOW}Systemd Service:${NC}"
        echo -e "     sudo systemctl enable ai-platform-health-monitor   - Enable auto-start"
        echo -e "     sudo systemctl start ai-platform-health-monitor    - Start service"
        echo -e "     sudo systemctl status ai-platform-health-monitor   - Check status"
        echo
    fi
    echo -e "${BLUE}📁 Log Locations:${NC}"
    echo -e "   Health monitoring: /home/keith/chat-copilot/logs/health-monitoring/"
    echo -e "   Platform logs: /home/keith/chat-copilot/logs/"
    echo
    echo -e "${GREEN}🚀 The monitoring system is ready to use!${NC}"
}

main() {
    echo -e "${BLUE}🔧 AI Research Platform Monitoring Setup${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo
    
    if ! check_prerequisites; then
        print_status "ERROR" "Prerequisites check failed"
        exit 1
    fi
    
    create_log_directories
    
    if [ "$EUID" -eq 0 ]; then
        install_systemd_service
    fi
    
    if ! test_monitoring; then
        print_status "ERROR" "Monitoring system test failed"
        exit 1
    fi
    
    show_usage_instructions
}

main "$@"