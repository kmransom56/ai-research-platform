#!/bin/bash
# Automated Health Monitoring System for AI Research Platform
# Runs continuous health checks and takes corrective actions

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="/home/keith/chat-copilot/logs/health-monitoring"
readonly HEALTH_CHECK_SCRIPT="$SCRIPT_DIR/health-check.sh"
readonly MANAGE_SCRIPT="$SCRIPT_DIR/manage-platform.sh"
readonly CHECK_INTERVAL=300  # 5 minutes
readonly FAILURE_THRESHOLD=3  # Restart after 3 consecutive failures
readonly LOG_RETENTION_DAYS=7

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Create log directory
mkdir -p "$LOG_DIR"

# Initialize failure counters
declare -A failure_counts=()

log_message() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    local log_file="$LOG_DIR/health-monitor-$(date '+%Y%m%d').log"
    
    echo "[$timestamp] $message" | tee -a "$log_file"
}

print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️ $message${NC}" ;;
    esac
    log_message "$status: $message"
}

run_health_check() {
    local health_output
    local health_status
    
    print_status "INFO" "Running health check..."
    
    # Always capture output, even if exit code is non-zero
    health_output=$(bash "$HEALTH_CHECK_SCRIPT" 2>&1) || health_status=$?
    health_status=${health_status:-0}
    
    # Extract service count from health check output (strip color codes)
    local healthy_services_line=$(echo "$health_output" | grep "Healthy Services:" | sed 's/\x1b\[[0-9;]*m//g')
    local healthy_services=$(echo "$healthy_services_line" | grep -o "[0-9]\+/[0-9]\+" | head -1)
    local current_count=$(echo "$healthy_services" | cut -d'/' -f1)
    local total_count=$(echo "$healthy_services" | cut -d'/' -f2)
    
    if [ -n "$healthy_services" ]; then
        local health_percentage=$((current_count * 100 / total_count))
        print_status "INFO" "Platform Health: $healthy_services ($health_percentage%)"
        
        # Consider health check successful if >= 90%
        if [ $health_percentage -ge 90 ]; then
            print_status "SUCCESS" "Health check completed - platform healthy ($health_percentage%)"
            return 0
        elif [ $health_percentage -ge 75 ]; then
            print_status "WARNING" "Platform health degraded ($health_percentage%) - investigating..."
            investigate_failures
            return 1
        else
            print_status "ERROR" "Platform health critical ($health_percentage%) - immediate action required"
            investigate_failures
            return 1
        fi
    else
        print_status "ERROR" "Could not parse health check results"
        return 1
    fi
}

investigate_failures() {
    print_status "INFO" "Investigating service failures..."
    
    # Run detailed health check to identify specific failures
    local failed_services
    failed_services=$(bash "$HEALTH_CHECK_SCRIPT" 2>&1 | grep "❌" | wc -l)
    
    if [ "$failed_services" -gt 0 ]; then
        print_status "WARNING" "Found $failed_services failed services"
        
        # Attempt automatic restart for common issues
        attempt_auto_recovery
    fi
}

attempt_auto_recovery() {
    print_status "INFO" "Attempting automatic recovery..."
    
    # Check Docker services
    local docker_issues=$(docker ps --filter "status=exited" --format "table {{.Names}}" | grep -v NAMES | wc -l)
    
    if [ "$docker_issues" -gt 0 ]; then
        print_status "WARNING" "Found stopped Docker containers - restarting..."
        docker ps --filter "status=exited" --format "table {{.Names}}" | grep -v NAMES | while read container; do
            if [ -n "$container" ]; then
                print_status "INFO" "Restarting container: $container"
                docker start "$container" || print_status "ERROR" "Failed to restart $container"
            fi
        done
    fi
    
    # Check frontend service
    if ! pgrep -f "yarn start" > /dev/null; then
        print_status "WARNING" "Frontend service not running - attempting restart..."
        restart_frontend_service
    fi
    
    # Wait a moment for services to stabilize
    sleep 30
    
    # Re-run health check
    if run_health_check; then
        print_status "SUCCESS" "Auto-recovery successful"
    else
        print_status "ERROR" "Auto-recovery failed - manual intervention may be required"
        send_alert
    fi
}

restart_frontend_service() {
    print_status "INFO" "Restarting frontend service..."
    
    # Kill existing processes
    pkill -f "yarn start" || true
    
    # Start frontend
    cd /home/keith/chat-copilot/webapp
    nohup yarn start > "$LOG_DIR/frontend-$(date '+%Y%m%d').log" 2>&1 &
    
    print_status "INFO" "Frontend service restart initiated"
}

send_alert() {
    local alert_message="AI Research Platform health monitoring alert: Platform health issues detected at $(date)"
    
    # Log critical alert
    print_status "ERROR" "$alert_message"
    
    # Could be extended to send email, Slack, or other notifications
    echo "$alert_message" >> "$LOG_DIR/critical-alerts.log"
}

cleanup_old_logs() {
    print_status "INFO" "Cleaning up logs older than $LOG_RETENTION_DAYS days..."
    find "$LOG_DIR" -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete
}

show_monitoring_status() {
    echo -e "${BLUE}🔍 AI Research Platform - Health Monitoring Status${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo
    echo -e "Monitor Location: $LOG_DIR"
    echo -e "Check Interval: ${CHECK_INTERVAL}s ($(($CHECK_INTERVAL / 60)) minutes)"
    echo -e "Failure Threshold: $FAILURE_THRESHOLD consecutive failures"
    echo -e "Log Retention: $LOG_RETENTION_DAYS days"
    echo
    echo -e "${YELLOW}Recent Health Status:${NC}"
    if [ -f "$LOG_DIR/health-monitor-$(date '+%Y%m%d').log" ]; then
        tail -5 "$LOG_DIR/health-monitor-$(date '+%Y%m%d').log"
    else
        echo "No health monitoring logs found for today."
    fi
}

main() {
    case "${1:-monitor}" in
        "monitor")
            print_status "INFO" "Starting automated health monitoring..."
            print_status "INFO" "Check interval: ${CHECK_INTERVAL}s, Failure threshold: $FAILURE_THRESHOLD"
            
            while true; do
                if ! run_health_check; then
                    ((failure_counts[general]++))
                    if [ "${failure_counts[general]:-0}" -ge $FAILURE_THRESHOLD ]; then
                        print_status "ERROR" "Failure threshold reached - attempting recovery"
                        attempt_auto_recovery
                        failure_counts[general]=0
                    fi
                else
                    failure_counts[general]=0
                fi
                
                # Cleanup old logs daily
                if [ $(($(date +%s) % 86400)) -lt $CHECK_INTERVAL ]; then
                    cleanup_old_logs
                fi
                
                sleep $CHECK_INTERVAL
            done
            ;;
        "status")
            show_monitoring_status
            ;;
        "check")
            run_health_check
            ;;
        "recover")
            attempt_auto_recovery
            ;;
        "stop")
            print_status "INFO" "Stopping health monitoring..."
            pkill -f "automated-health-monitor.sh" || true
            ;;
        *)
            echo "Usage: $0 {monitor|status|check|recover|stop}"
            echo ""
            echo "  monitor  - Start continuous health monitoring (default)"
            echo "  status   - Show current monitoring status"
            echo "  check    - Run single health check"
            echo "  recover  - Attempt manual recovery"
            echo "  stop     - Stop health monitoring"
            exit 1
            ;;
    esac
}

# Handle signals for graceful shutdown
trap 'print_status "INFO" "Health monitoring stopped"; exit 0' SIGTERM SIGINT

main "$@"