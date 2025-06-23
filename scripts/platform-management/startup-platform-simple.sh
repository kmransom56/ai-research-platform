#!/bin/bash
# AI Research Platform Simple Startup Script
# This script replaces the complex multi-service startup system
# Uses the new streamlined startup approach via ai-platform-restore.service
# Author: Automated Infrastructure Management
# Version: 4.0 - Simplified and Conflict-Free

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

readonly PLATFORM_DIR="/home/keith/chat-copilot"
readonly LOGS_DIR="$PLATFORM_DIR/logs"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

print_status() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "SUCCESS") echo -e "${GREEN}✅ [$timestamp] $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ [$timestamp] $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️ [$timestamp] $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️ [$timestamp] $message${NC}" ;;
    esac
}

print_header() {
    echo
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

show_startup_info() {
    print_header "AI RESEARCH PLATFORM STARTUP"
    
    print_status "INFO" "⚠️  IMPORTANT NOTICE ⚠️"
    echo
    echo "The AI Research Platform now uses a simplified startup system:"
    echo "• SystemD service: ai-platform-restore.service handles startup automatically"
    echo "• Manual startup: Use quick-restore.sh from latest backup"
    echo "• This script is now DEPRECATED and for reference only"
    echo
    
    print_status "INFO" "Current recommended startup methods:"
    echo "1. AUTOMATIC (after reboot): systemctl status ai-platform-restore.service"
    echo "2. MANUAL RESTORE: $PLATFORM_DIR/config-backups-working/latest/quick-restore.sh"
    echo "3. CONTAINERIZED: $PLATFORM_DIR/start-containerized-platform.sh start"
    echo
}

check_new_startup_system() {
    print_header "CHECKING NEW STARTUP SYSTEM"
    
    # Check if ai-platform-restore.service is enabled
    if systemctl is-enabled ai-platform-restore.service &>/dev/null; then
        print_status "SUCCESS" "ai-platform-restore.service is enabled"
    else
        print_status "ERROR" "ai-platform-restore.service is not enabled"
        print_status "INFO" "Run: sudo systemctl enable ai-platform-restore.service"
    fi
    
    # Check if quick-restore script exists
    if [[ -f "$PLATFORM_DIR/config-backups-working/latest/quick-restore.sh" ]]; then
        print_status "SUCCESS" "Quick restore script is available"
    else
        print_status "ERROR" "Quick restore script not found"
        print_status "INFO" "Run backup script to create restore point"
    fi
    
    # Check for conflicting services (should be disabled)
    local conflicting_services=(
        "ai-platform-gateways.service"
        "ai-platform-external.service" 
        "ai-platform-python.service"
        "ai-platform-services.service"
    )
    
    local conflicts_found=false
    for service in "${conflicting_services[@]}"; do
        if systemctl is-enabled "$service" &>/dev/null; then
            print_status "WARNING" "Conflicting service enabled: $service"
            conflicts_found=true
        fi
    done
    
    if [[ "$conflicts_found" == false ]]; then
        print_status "SUCCESS" "No conflicting services found"
    fi
}

run_quick_restore() {
    print_header "RUNNING QUICK RESTORE"
    
    if [[ -f "$PLATFORM_DIR/config-backups-working/latest/quick-restore.sh" ]]; then
        print_status "INFO" "Executing quick restore script..."
        bash "$PLATFORM_DIR/config-backups-working/latest/quick-restore.sh"
    else
        print_status "ERROR" "Quick restore script not found"
        exit 1
    fi
}

show_platform_status() {
    print_header "PLATFORM STATUS"
    
    if [[ -f "$PLATFORM_DIR/check-platform-status.sh" ]]; then
        bash "$PLATFORM_DIR/check-platform-status.sh"
    else
        print_status "WARNING" "Platform status script not found"
        
        # Basic status check
        print_status "INFO" "Checking basic services..."
        
        # Check backend
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:11000/healthz | grep -q "200"; then
            print_status "SUCCESS" "Backend API (11000) - HEALTHY"
        else
            print_status "ERROR" "Backend API (11000) - FAILED"
        fi
        
        # Check nginx
        if systemctl is-active nginx &>/dev/null; then
            print_status "SUCCESS" "Nginx - RUNNING"
        else
            print_status "ERROR" "Nginx - NOT RUNNING"
        fi
        
        # Check Docker
        if systemctl is-active docker &>/dev/null; then
            print_status "SUCCESS" "Docker - RUNNING"
        else
            print_status "ERROR" "Docker - NOT RUNNING"
        fi
    fi
}

show_help() {
    print_header "AI RESEARCH PLATFORM - STARTUP HELP"
    
    cat << 'EOF'
Usage: startup-platform.sh [COMMAND]

Commands:
  info           Show startup system information (default)
  check          Check new startup system status
  restore        Run quick restore manually
  status         Show platform status
  help           Show this help message

IMPORTANT: This platform now uses a simplified startup system.

NEW STARTUP METHODS:
1. AUTOMATIC (Recommended):
   - SystemD service handles startup after reboot
   - Service: ai-platform-restore.service
   - Check: systemctl status ai-platform-restore.service

2. MANUAL RESTORE:
   - Use: ./config-backups-working/latest/quick-restore.sh
   - This restores SSL certificates, nginx config, and starts services

3. CONTAINERIZED DEPLOYMENT:
   - Use: ./start-containerized-platform.sh start
   - For Docker-based deployments

DEPRECATED:
- Complex multi-service startup scripts (this file)
- Multiple conflicting systemd services
- Cron-based startup systems

For more information, see CLAUDE.md
EOF
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    local command=${1:-"info"}
    
    # Ensure we're in the right directory
    if [[ ! -d "$PLATFORM_DIR" ]]; then
        print_status "ERROR" "Platform directory not found: $PLATFORM_DIR"
        exit 1
    fi
    
    cd "$PLATFORM_DIR" || exit 1
    
    # Create logs directory if it doesn't exist
    mkdir -p "$LOGS_DIR"
    
    case "$command" in
        "info"|"")
            show_startup_info
            ;;
        "check")
            check_new_startup_system
            ;;
        "restore")
            run_quick_restore
            ;;
        "status")
            show_platform_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_status "ERROR" "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Handle cleanup on exit
cleanup() {
    print_status "INFO" "Cleaning up on exit..."
}

trap cleanup EXIT

# Run main function
main "$@"