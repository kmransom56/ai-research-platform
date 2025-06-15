#!/bin/bash
# Configuration Validation and Auto-Fix System
# This script ensures all configurations are correct and fixes drift automatically

set -e

SCRIPT_DIR="/home/keith/chat-copilot"
LOG_FILE="$SCRIPT_DIR/logs/config-validation.log"
CONFIG_ERRORS=0

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check and fix configuration
check_and_fix_config() {
    local file=$1
    local expected_content=$2
    local description=$3
    
    log "Checking $description..."
    
    if [ ! -f "$file" ]; then
        log "❌ MISSING: $file"
        echo "$expected_content" > "$file"
        log "✅ FIXED: Created $file"
        return 0
    fi
    
    if ! grep -q "$expected_content" "$file"; then
        log "❌ INCORRECT: $description"
        # Backup current file
        cp "$file" "$file.backup.$(date +%s)"
        
        # Fix the configuration
        if [[ "$file" == *".env"* ]]; then
            echo "$expected_content" > "$file"
        else
            # For other files, we need more sophisticated handling
            log "⚠️ Manual fix required for $file"
            ((CONFIG_ERRORS++))
            return 1
        fi
        log "✅ FIXED: $description"
    else
        log "✅ OK: $description"
    fi
    return 0
}

# Function to validate service ports
validate_service_ports() {
    log "🔍 Validating service port configurations..."
    
    # Check frontend .env file
    check_and_fix_config \
        "/home/keith/chat-copilot/webapp/.env" \
        "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" \
        "Frontend backend URI configuration"
    
    # Check port scanner frontend
    local port_scanner_html="/home/keith/port-scanner-material-ui/src/index.html"
    if [ -f "$port_scanner_html" ]; then
        if grep -q "localhost:10200\|localhost:4500" "$port_scanner_html"; then
            log "❌ Port scanner frontend uses wrong ports"
            sed -i 's/localhost:10200/localhost:11010/g' "$port_scanner_html"
            sed -i 's/localhost:4500/localhost:11010/g' "$port_scanner_html"
            log "✅ FIXED: Port scanner frontend ports"
        else
            log "✅ OK: Port scanner frontend ports"
        fi
    fi
    
    # Validate backend appsettings.json
    local backend_config="/home/keith/chat-copilot/webapi/appsettings.json"
    if [ -f "$backend_config" ]; then
        if ! grep -q '"Url": "http://0.0.0.0:11000"' "$backend_config"; then
            log "❌ Backend port configuration incorrect"
            ((CONFIG_ERRORS++))
        else
            log "✅ OK: Backend port configuration"
        fi
    fi
}

# Function to validate startup script
validate_startup_script() {
    log "🔍 Validating startup script..."
    
    local startup_script="/home/keith/chat-copilot/startup-platform.sh"
    if [ -f "$startup_script" ]; then
        # Check if port scanner is configured correctly
        if grep -q "port-scanner-material-ui.*server.js" "$startup_script"; then
            log "✅ OK: Startup script port scanner configuration"
        else
            log "❌ Startup script missing port scanner configuration"
            ((CONFIG_ERRORS++))
        fi
        
        # Check if webhook server uses correct port
        if grep -q "11002" "$startup_script"; then
            log "✅ OK: Webhook server port in startup script"
        else
            log "❌ Webhook server port incorrect in startup script"
            ((CONFIG_ERRORS++))
        fi
    else
        log "❌ MISSING: Startup script not found"
        ((CONFIG_ERRORS++))
    fi
}

# Function to check process health
check_process_health() {
    log "🔍 Checking process health..."
    
    # Define expected processes and their health check URLs
    declare -A services=(
        ["Chat Copilot Backend"]="http://100.123.10.72:11000/healthz"
        ["Webhook Server"]="http://100.123.10.72:11002/health"
        ["Port Scanner"]="http://100.123.10.72:11010/nmap-status"
    )
    
    for service in "${!services[@]}"; do
        local url="${services[$service]}"
        if curl -s --max-time 5 "$url" &> /dev/null; then
            log "✅ HEALTHY: $service"
        else
            log "⚠️ UNHEALTHY: $service (URL: $url)"
            # Could add auto-restart logic here
        fi
    done
}

# Function to create configuration snapshot
create_config_snapshot() {
    log "📸 Creating configuration snapshot..."
    
    local snapshot_dir="$SCRIPT_DIR/config-snapshots/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$snapshot_dir"
    
    # Copy critical configuration files
    [ -f "/home/keith/chat-copilot/webapp/.env" ] && cp "/home/keith/chat-copilot/webapp/.env" "$snapshot_dir/"
    [ -f "/home/keith/chat-copilot/webapi/appsettings.json" ] && cp "/home/keith/chat-copilot/webapi/appsettings.json" "$snapshot_dir/"
    [ -f "/home/keith/port-scanner-material-ui/src/index.html" ] && cp "/home/keith/port-scanner-material-ui/src/index.html" "$snapshot_dir/"
    [ -f "/home/keith/chat-copilot/startup-platform.sh" ] && cp "/home/keith/chat-copilot/startup-platform.sh" "$snapshot_dir/"
    
    # Create metadata
    cat > "$snapshot_dir/metadata.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "validation_run": true,
    "config_errors": $CONFIG_ERRORS,
    "system_info": {
        "hostname": "$(hostname)",
        "user": "$(whoami)",
        "git_commit": "$(cd $SCRIPT_DIR && git rev-parse HEAD 2>/dev/null || echo 'unknown')"
    }
}
EOF
    
    log "✅ Configuration snapshot saved to: $snapshot_dir"
}

# Main validation routine
main() {
    log "🔍 Starting configuration validation..."
    log "=========================================="
    
    validate_service_ports
    validate_startup_script
    check_process_health
    create_config_snapshot
    
    log "=========================================="
    if [ $CONFIG_ERRORS -eq 0 ]; then
        log "✅ ALL CONFIGURATIONS VALID - System ready for users"
        exit 0
    else
        log "❌ FOUND $CONFIG_ERRORS CONFIGURATION ISSUES"
        log "🔧 Some issues require manual intervention"
        log "📋 Check log file: $LOG_FILE"
        exit 1
    fi
}

# Run validation
main "$@"