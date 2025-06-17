#!/bin/bash
# Health Monitoring and Auto-Recovery System
# Continuously monitors services and auto-restarts them if they fail

SCRIPT_DIR="/home/keith/chat-copilot"
LOG_FILE="$SCRIPT_DIR/logs/health-monitor.log"
PIDFILE="$SCRIPT_DIR/pids/health-monitor.pid"

# Check if already running
if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
    echo "Health monitor already running (PID: $(cat $PIDFILE))"
    exit 1
fi

# Save PID
echo $$ > "$PIDFILE"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local restart_command=$3
    local pidfile=$4
    
    if curl -s --max-time 10 "$url" &> /dev/null; then
        return 0  # Healthy
    else
        log "⚠️ $name is unhealthy (URL: $url)"
        
        # Try to restart
        log "🔄 Attempting to restart $name..."
        
        # Kill existing process if pidfile exists
        if [ -f "$pidfile" ]; then
            local old_pid=$(cat "$pidfile" 2>/dev/null)
            if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
                kill "$old_pid" 2>/dev/null
                sleep 5
            fi
            rm -f "$pidfile"
        fi
        
        # Execute restart command
        eval "$restart_command"
        
        # Wait and check again
        sleep 10
        if curl -s --max-time 10 "$url" &> /dev/null; then
            log "✅ Successfully restarted $name"
            return 0
        else
            log "❌ Failed to restart $name"
            return 1
        fi
    fi
}

# Function to validate configuration before monitoring
validate_config() {
    log "🔍 Validating configuration before monitoring..."
    if [ -f "$SCRIPT_DIR/validate-config.sh" ]; then
        if "$SCRIPT_DIR/validate-config.sh" >> "$LOG_FILE" 2>&1; then
            log "✅ Configuration validation passed"
            return 0
        else
            log "❌ Configuration validation failed - fixing..."
            return 1
        fi
    else
        log "⚠️ Configuration validator not found"
        return 1
    fi
}

# Function to monitor critical services
monitor_services() {
    log "🔍 Starting service monitoring cycle..."
    
    # Define services to monitor
    # Format: "Name|Health_URL|Restart_Command|PID_File"
    local services=(
        "Chat Copilot Backend|http://100.123.10.72:11000/healthz|cd $SCRIPT_DIR/webapi && nohup dotnet run --urls http://0.0.0.0:11000 > $SCRIPT_DIR/logs/backend.log 2>&1 & echo \$! > $SCRIPT_DIR/pids/chat-copilot-backend.pid|$SCRIPT_DIR/pids/chat-copilot-backend.pid"
        "AutoGen Studio|http://100.123.10.72:11001|cd $SCRIPT_DIR && source .venv/bin/activate && nohup python -m autogenstudio.ui --port 11001 --host 0.0.0.0 > $SCRIPT_DIR/logs/autogen-studio.log 2>&1 & echo \$! > $SCRIPT_DIR/pids/autogen-studio.pid|$SCRIPT_DIR/pids/autogen-studio.pid"
        "Webhook Server|http://100.123.10.72:11002/health|cd $SCRIPT_DIR && nohup node webhook-server.js > $SCRIPT_DIR/logs/webhook-server.log 2>&1 & echo \$! > $SCRIPT_DIR/pids/webhook-server.pid|$SCRIPT_DIR/pids/webhook-server.pid"
        "Magentic-One Server|http://100.123.10.72:11003/health|cd $SCRIPT_DIR && source .venv/bin/activate && nohup python magentic_one_server.py > $SCRIPT_DIR/logs/magentic-one.log 2>&1 & echo \$! > $SCRIPT_DIR/pids/magentic-one.pid|$SCRIPT_DIR/pids/magentic-one.pid"
        "Port Scanner|http://100.123.10.72:11010/nmap-status|cd /home/keith/port-scanner-material-ui && nohup node backend/server.js > $SCRIPT_DIR/logs/port-scanner.log 2>&1 & echo \$! > $SCRIPT_DIR/pids/port-scanner.pid|$SCRIPT_DIR/pids/port-scanner.pid"
    )
    
    local failed_services=0
    
    for service_config in "${services[@]}"; do
        IFS='|' read -r name url restart_cmd pidfile <<< "$service_config"
        
        if ! check_service "$name" "$url" "$restart_cmd" "$pidfile"; then
            ((failed_services++))
        fi
    done
    
    if [ $failed_services -eq 0 ]; then
        log "✅ All services healthy"
    else
        log "⚠️ $failed_services services required intervention"
    fi
}

# Function to check for configuration drift
check_config_drift() {
    log "🔍 Checking for configuration drift..."
    
    # Check if critical files have been modified unexpectedly
    local webapp_env="/home/keith/chat-copilot/webapp/.env"
    if [ -f "$webapp_env" ]; then
        if ! grep -q "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" "$webapp_env"; then
            log "❌ Configuration drift detected in webapp/.env"
            echo "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" > "$webapp_env"
            log "✅ Fixed webapp/.env configuration"
        fi
    fi
    
    # Check port scanner configuration
    local port_scanner_html="/home/keith/port-scanner-material-ui/src/index.html"
    if [ -f "$port_scanner_html" ]; then
        if grep -q "localhost:10200\|localhost:4500" "$port_scanner_html"; then
            log "❌ Configuration drift detected in port scanner frontend"
            sed -i 's/localhost:10200/localhost:11010/g' "$port_scanner_html"
            sed -i 's/localhost:4500/localhost:11010/g' "$port_scanner_html"
            log "✅ Fixed port scanner frontend configuration"
        fi
    fi
}

# Function to create health report
create_health_report() {
    local report_file="$SCRIPT_DIR/health-report.json"
    local timestamp=$(date -Iseconds)
    
    # Test all services
    local backend_status="stopped"
    local autogen_status="stopped"
    local webhook_status="stopped"
    local magentic_status="stopped"
    local port_scanner_status="stopped"
    
    curl -s --max-time 5 "http://100.123.10.72:11000/healthz" &> /dev/null && backend_status="running"
    curl -s --max-time 5 "http://100.123.10.72:11001" &> /dev/null && autogen_status="running"
    curl -s --max-time 5 "http://100.123.10.72:11002/health" &> /dev/null && webhook_status="running"
    curl -s --max-time 5 "http://100.123.10.72:11003/health" &> /dev/null && magentic_status="running"
    curl -s --max-time 5 "http://100.123.10.72:11010/nmap-status" &> /dev/null && port_scanner_status="running"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$timestamp",
    "overall_status": "$([ "$backend_status" = "running" ] && [ "$autogen_status" = "running" ] && [ "$webhook_status" = "running" ] && [ "$magentic_status" = "running" ] && [ "$port_scanner_status" = "running" ] && echo "healthy" || echo "degraded")",
    "services": {
        "chat_copilot_backend": {
            "status": "$backend_status",
            "port": 11000,
            "url": "http://100.123.10.72:11000",
            "health_check": "http://100.123.10.72:11000/healthz"
        },
        "autogen_studio": {
            "status": "$autogen_status",
            "port": 11001,
            "url": "http://100.123.10.72:11001",
            "health_check": "http://100.123.10.72:11001"
        },
        "webhook_server": {
            "status": "$webhook_status",
            "port": 11002,
            "url": "http://100.123.10.72:11002",
            "health_check": "http://100.123.10.72:11002/health"
        },
        "magentic_one_server": {
            "status": "$magentic_status",
            "port": 11003,
            "url": "http://100.123.10.72:11003",
            "health_check": "http://100.123.10.72:11003/health"
        },
        "port_scanner": {
            "status": "$port_scanner_status",
            "url": "http://100.123.10.72:11010",
            "health_check": "http://100.123.10.72:11010/nmap-status"
        }
    },
    "monitoring": {
        "last_check": "$timestamp",
        "log_file": "$LOG_FILE"
    }
}
EOF
}

# Cleanup function
cleanup() {
    log "🛑 Health monitor shutting down..."
    rm -f "$PIDFILE"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main monitoring loop
main() {
    log "🚀 Starting health monitor for AI Research Platform"
    log "PID: $$"
    log "Log file: $LOG_FILE"
    
    # Initial configuration validation
    validate_config
    
    # Monitor loop
    while true; do
        monitor_services
        check_config_drift
        create_health_report
        
        # Wait 60 seconds before next check
        sleep 60
    done
}

# Start monitoring if run directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi