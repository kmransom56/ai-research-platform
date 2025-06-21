#!/bin/bash
# File monitoring for configuration drift prevention

SCRIPT_DIR="/home/keith/chat-copilot"
LOG_FILE="$SCRIPT_DIR/logs/file-monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Monitor critical files
monitor_files() {
    local files=(
        "/home/keith/chat-copilot/webapp/.env"
        "/home/keith/port-scanner-material-ui/src/index.html"
        "/home/keith/chat-copilot/webapi/appsettings.json"
        "/home/keith/chat-copilot/startup-platform.sh"
    )
    
    log "🔍 Starting file monitoring for configuration drift"
    
    # Use inotifywait if available
    if command -v inotifywait &> /dev/null; then
        for file in "${files[@]}"; do
            if [ -f "$file" ]; then
                log "👁️ Monitoring: $file"
                (inotifywait -m -e modify,move,delete "$file" 2>/dev/null | while read path action file; do
                    log "⚠️ DETECTED: $action on $path$file"
                    # Trigger validation
                    "$SCRIPT_DIR/validate-config.sh" >> "$LOG_FILE" 2>&1
                done) &
            fi
        done
    else
        log "⚠️ inotifywait not available - using periodic checks"
        # Fallback to periodic checking
        while true; do
            "$SCRIPT_DIR/validate-config.sh" >> "$LOG_FILE" 2>&1
            sleep 300  # Check every 5 minutes
        done &
    fi
}

# Start monitoring if run directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    monitor_files
    wait
fi
