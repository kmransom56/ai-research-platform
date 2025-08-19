#!/bin/bash
#
# Install Boot Services Script
# Sets up systemd services for automatic startup of AI Research Platform
#

# Set script directory and platform root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run with sudo privileges"
        echo "Usage: sudo $0 [install|uninstall|status|enable|disable|start|stop|restart]"
        exit 1
    fi
}

# Install systemd service
install_service() {
    log_info "Installing AI Research Platform systemd service..."
    
    # Copy service file to systemd directory
    cp "$PLATFORM_ROOT/ai-research-platform.service" /etc/systemd/system/
    
    # Set correct permissions
    chown root:root /etc/systemd/system/ai-research-platform.service
    chmod 644 /etc/systemd/system/ai-research-platform.service
    
    # Reload systemd daemon
    systemctl daemon-reload
    
    log_success "AI Research Platform service installed"
}

# Uninstall systemd service
uninstall_service() {
    log_info "Uninstalling AI Research Platform systemd service..."
    
    # Stop and disable service if running
    systemctl stop ai-research-platform.service 2>/dev/null || true
    systemctl disable ai-research-platform.service 2>/dev/null || true
    
    # Remove service file
    rm -f /etc/systemd/system/ai-research-platform.service
    
    # Reload systemd daemon
    systemctl daemon-reload
    systemctl reset-failed 2>/dev/null || true
    
    log_success "AI Research Platform service uninstalled"
}

# Enable service for boot startup
enable_service() {
    log_info "Enabling AI Research Platform for boot startup..."
    
    systemctl enable ai-research-platform.service
    
    if systemctl is-enabled ai-research-platform.service &>/dev/null; then
        log_success "AI Research Platform enabled for boot startup"
    else
        log_error "Failed to enable AI Research Platform service"
        return 1
    fi
}

# Disable service from boot startup
disable_service() {
    log_info "Disabling AI Research Platform from boot startup..."
    
    systemctl disable ai-research-platform.service
    
    if ! systemctl is-enabled ai-research-platform.service &>/dev/null; then
        log_success "AI Research Platform disabled from boot startup"
    else
        log_error "Failed to disable AI Research Platform service"
        return 1
    fi
}

# Start service
start_service() {
    log_info "Starting AI Research Platform service..."
    
    systemctl start ai-research-platform.service
    
    sleep 5
    
    if systemctl is-active ai-research-platform.service &>/dev/null; then
        log_success "AI Research Platform service started"
        systemctl status ai-research-platform.service --no-pager -l
    else
        log_error "Failed to start AI Research Platform service"
        systemctl status ai-research-platform.service --no-pager -l
        return 1
    fi
}

# Stop service
stop_service() {
    log_info "Stopping AI Research Platform service..."
    
    systemctl stop ai-research-platform.service
    
    sleep 3
    
    if ! systemctl is-active ai-research-platform.service &>/dev/null; then
        log_success "AI Research Platform service stopped"
    else
        log_error "Failed to stop AI Research Platform service"
        return 1
    fi
}

# Restart service
restart_service() {
    log_info "Restarting AI Research Platform service..."
    
    systemctl restart ai-research-platform.service
    
    sleep 5
    
    if systemctl is-active ai-research-platform.service &>/dev/null; then
        log_success "AI Research Platform service restarted"
        systemctl status ai-research-platform.service --no-pager -l
    else
        log_error "Failed to restart AI Research Platform service"
        systemctl status ai-research-platform.service --no-pager -l
        return 1
    fi
}

# Show service status
show_status() {
    log_info "AI Research Platform Service Status:"
    echo ""
    
    # Check if service file exists
    if [ -f "/etc/systemd/system/ai-research-platform.service" ]; then
        log_success "Service file installed: /etc/systemd/system/ai-research-platform.service"
    else
        log_warning "Service file not installed"
    fi
    
    # Check if service is enabled
    if systemctl is-enabled ai-research-platform.service &>/dev/null; then
        log_success "Service enabled for boot startup"
    else
        log_warning "Service not enabled for boot startup"
    fi
    
    # Check if service is active
    if systemctl is-active ai-research-platform.service &>/dev/null; then
        log_success "Service currently running"
    else
        log_warning "Service not currently running"
    fi
    
    echo ""
    systemctl status ai-research-platform.service --no-pager -l 2>/dev/null || log_warning "Service not found"
    
    echo ""
    log_info "Recent journal entries:"
    journalctl -u ai-research-platform.service --no-pager -l -n 20 2>/dev/null || log_warning "No journal entries found"
}

# Full installation with all steps
full_install() {
    log_info "Performing full installation of AI Research Platform boot services..."
    
    install_service
    enable_service
    
    log_info "Installation complete!"
    echo ""
    log_info "You can now:"
    echo "  - Start the service: sudo systemctl start ai-research-platform.service"
    echo "  - Check status: sudo systemctl status ai-research-platform.service"
    echo "  - View logs: sudo journalctl -u ai-research-platform.service -f"
    echo "  - The service will automatically start on boot"
    echo ""
    
    read -p "Would you like to start the service now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_service
    fi
}

# Check dependencies
check_dependencies() {
    log_info "Checking system dependencies for boot services..."
    
    local deps=("systemctl" "journalctl")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        log_success "All dependencies available"
        return 0
    else
        log_error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
}

# Main command handling
main() {
    check_sudo
    check_dependencies
    
    case "${1:-install}" in
        install)
            full_install
            ;;
        uninstall)
            uninstall_service
            ;;
        enable)
            enable_service
            ;;
        disable)
            disable_service
            ;;
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
        *)
            echo "Usage: sudo $0 {install|uninstall|enable|disable|start|stop|restart|status}"
            echo ""
            echo "Commands:"
            echo "  install   - Install and enable the systemd service (default)"
            echo "  uninstall - Remove the systemd service"
            echo "  enable    - Enable service for boot startup"
            echo "  disable   - Disable service from boot startup"
            echo "  start     - Start the service now"
            echo "  stop      - Stop the service now"
            echo "  restart   - Restart the service now"
            echo "  status    - Show service status and logs"
            echo ""
            echo "After installation, the AI Research Platform will:"
            echo "  - Start automatically on boot"
            echo "  - Restart automatically if it fails"
            echo "  - Start all registered services in proper sequence"
            exit 1
            ;;
    esac
}

main "$@"