#!/bin/bash
# Configuration Change Monitor - Detect GitHub or other overwrites
# This script monitors critical configuration files for unauthorized changes

WATCH_DIR="/home/keith/chat-copilot"
LOG_FILE="$WATCH_DIR/logs/config-monitor.log"
ALERT_FILE="$WATCH_DIR/logs/config-alerts.log"

# Critical files to monitor for changes
CRITICAL_FILES=(
    "webapi/appsettings.json"
    "webapp/.env"
    "webapp/public/applications.html"
    "webapp/public/control-panel.html"
    "startup-platform.sh"
    "auto_startup_manager.py"
    "autogen_config.py"
    "manage-platform.sh"
)

# Expected port configurations (what should be in the files)
EXPECTED_PORTS=(
    "11000"  # Chat Copilot Backend
    "11001"  # AutoGen Studio  
    "11002"  # Webhook Server
    "11003"  # Magentic-One
    "11010"  # Port Scanner
    "11080"  # Nginx Proxy Manager
)

# Ports that should NOT appear (old ports)
FORBIDDEN_PORTS=(
    "10500"  # Old Chat Copilot port
    "40443"  # Old backend port
    "8085"   # Old AutoGen port
    "8086"   # Old Magentic-One port
    "9001"   # Old webhook port
    "10200"  # Old port scanner port
)

echo "🔍 Configuration Change Monitor Started at $(date)"
echo "Monitoring directory: $WATCH_DIR"
echo "Log file: $LOG_FILE"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to create alert
create_alert() {
    local severity=$1
    local message=$2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$severity] $message" | tee -a "$ALERT_FILE"
    log_message "🚨 ALERT [$severity]: $message"
}

# Function to check for forbidden ports in files
check_forbidden_ports() {
    local file=$1
    local found_issues=false
    
    for port in "${FORBIDDEN_PORTS[@]}"; do
        if grep -q "$port" "$file" 2>/dev/null; then
            create_alert "HIGH" "Forbidden port $port found in $file"
            found_issues=true
        fi
    done
    
    if [ "$found_issues" = true ]; then
        return 1
    fi
    return 0
}

# Function to validate file integrity
validate_file_integrity() {
    local file=$1
    local status="OK"
    
    if [ ! -f "$file" ]; then
        create_alert "CRITICAL" "Critical file missing: $file"
        return 1
    fi
    
    # Check for forbidden ports
    if ! check_forbidden_ports "$file"; then
        status="COMPROMISED"
    fi
    
    # File-specific validations
    case "$file" in
        "webapp/.env")
            if ! grep -q "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" "$file"; then
                create_alert "HIGH" "Frontend .env has incorrect backend URI"
                status="INCORRECT"
            fi
            ;;
        "webapi/appsettings.json")
            if ! grep -q '"Url": "http://0.0.0.0:11000"' "$file"; then
                create_alert "HIGH" "Backend appsettings.json has incorrect URL configuration"
                status="INCORRECT"
            fi
            ;;
        "startup-platform.sh")
            if ! grep -q "11000\|11001\|11002\|11003" "$file"; then
                create_alert "HIGH" "Startup script missing standardized ports"
                status="INCORRECT"
            fi
            ;;
    esac
    
    log_message "✅ File integrity check: $file - Status: $status"
    return 0
}

# Function to check for recent git changes
check_git_changes() {
    cd "$WATCH_DIR" || exit 1
    
    # Check if there are any uncommitted changes to critical files
    for file in "${CRITICAL_FILES[@]}"; do
        if [ -f "$file" ] && git status --porcelain "$file" | grep -q "^M"; then
            create_alert "MEDIUM" "Uncommitted changes detected in critical file: $file"
        fi
    done
    
    # Check for recent commits that might indicate external changes
    local recent_commits=$(git log --oneline --since="1 hour ago" --grep="bot\|action\|automated")
    if [ -n "$recent_commits" ]; then
        create_alert "MEDIUM" "Recent automated commits detected: $recent_commits"
    fi
    
    # Check remote for new commits
    git fetch origin main --quiet 2>/dev/null
    local behind_commits=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
    if [ "$behind_commits" -gt 0 ]; then
        create_alert "MEDIUM" "Local branch is $behind_commits commits behind origin/main"
    fi
}

# Function to check GitHub Actions status
check_github_actions() {
    # Look for recent workflow run files
    if [ -d ".github/workflows" ]; then
        local workflow_files=$(find .github/workflows -name "*.yml" -o -name "*.yaml")
        log_message "📋 Found GitHub workflows: $(echo "$workflow_files" | wc -l) files"
        
        # Check if any workflows modify configuration files
        for workflow in $workflow_files; do
            if grep -q "appsettings\|\.env\|config" "$workflow" 2>/dev/null; then
                create_alert "LOW" "Workflow $workflow may modify configuration files"
            fi
        done
    fi
}

# Function to create backup before any fixes
create_emergency_backup() {
    local backup_dir="$WATCH_DIR/emergency-backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/"
            log_message "📁 Emergency backup created: $backup_dir/$(basename "$file")"
        fi
    done
    
    echo "$backup_dir"
}

# Function to auto-fix configuration issues
auto_fix_config() {
    log_message "🔧 Starting automatic configuration fix..."
    
    # Create backup first
    local backup_dir=$(create_emergency_backup)
    
    # Fix frontend .env
    if [ -f "webapp/.env" ]; then
        echo "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" > "webapp/.env"
        log_message "✅ Fixed webapp/.env"
    fi
    
    # Re-copy corrected HTML files
    if [ -f "webapp/public/control-panel.html" ] && [ -f "webapi/wwwroot/control-panel.html" ]; then
        cp "webapp/public/control-panel.html" "webapi/wwwroot/control-panel.html"
        cp "webapp/public/applications.html" "webapi/wwwroot/applications.html"
        log_message "✅ Restored corrected HTML files"
    fi
    
    log_message "🎯 Auto-fix completed. Backup saved to: $backup_dir"
}

# Main monitoring loop
main() {
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$ALERT_FILE")"
    
    log_message "🚀 Starting configuration monitoring..."
    
    # Initial validation
    log_message "🔍 Performing initial validation..."
    local issues_found=false
    
    for file in "${CRITICAL_FILES[@]}"; do
        if ! validate_file_integrity "$file"; then
            issues_found=true
        fi
    done
    
    # Check git status
    check_git_changes
    
    # Check GitHub Actions
    check_github_actions
    
    # Generate summary report
    log_message "📊 Configuration Monitor Summary:"
    log_message "   Critical files monitored: ${#CRITICAL_FILES[@]}"
    log_message "   Expected ports: ${EXPECTED_PORTS[*]}"
    log_message "   Forbidden ports: ${FORBIDDEN_PORTS[*]}"
    
    if [ "$issues_found" = true ]; then
        create_alert "HIGH" "Configuration issues detected during initial scan"
        
        # Ask if auto-fix should be applied
        if [ "${1:-}" = "--auto-fix" ]; then
            auto_fix_config
        else
            log_message "💡 Run with --auto-fix to automatically correct issues"
        fi
    else
        log_message "✅ All configurations are correct"
    fi
    
    # If running in watch mode
    if [ "${1:-}" = "--watch" ]; then
        log_message "👀 Entering watch mode - monitoring for changes..."
        while true; do
            sleep 60  # Check every minute
            check_git_changes
            for file in "${CRITICAL_FILES[@]}"; do
                validate_file_integrity "$file" >/dev/null
            done
        done
    fi
}

# Run the monitor
main "$@"