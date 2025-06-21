#!/bin/bash
# Configuration Monitor - Prevents drift by monitoring critical files
# Runs continuously to detect and fix configuration changes

set -e

PLATFORM_DIR="/home/keith/chat-copilot"
MONITOR_INTERVAL=30 # seconds
LOG_FILE="$PLATFORM_DIR/logs/config-monitor.log"

# Files to monitor
WATCH_FILES=(
    "$PLATFORM_DIR/webapp/.env"
    "$PLATFORM_DIR/webapi/appsettings.json"
    "$PLATFORM_DIR/port-configuration.json"
)

# Expected values
declare -A EXPECTED_VALUES
EXPECTED_VALUES["$PLATFORM_DIR/webapp/.env:REACT_APP_BACKEND_URI"]="http://100.123.10.72:11000/"
EXPECTED_VALUES["$PLATFORM_DIR/webapi/appsettings.json:Kestrel.Endpoints.Http.Url"]="http://0.0.0.0:11000"
EXPECTED_VALUES["$PLATFORM_DIR/webapi/appsettings.json:Ollama.Endpoint"]="http://localhost:11434"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_and_fix_drift() {
    local file=$1
    local key=$2
    local expected=$3
    
    case "$file" in
        *.env)
            local actual=$(grep "^$key=" "$file" 2>/dev/null | cut -d'=' -f2 || echo "")
            ;;
        *.json)
            case "$key" in
                "Kestrel.Endpoints.Http.Url")
                    local actual=$(grep -o '"Url": "[^"]*"' "$file" 2>/dev/null | cut -d'"' -f4 || echo "")
                    ;;
                "Ollama.Endpoint")
                    local actual=$(grep -A 1 '"Ollama"' "$file" 2>/dev/null | grep '"Endpoint"' | cut -d'"' -f4 || echo "")
                    ;;
            esac
            ;;
    esac
    
    if [[ "$actual" != "$expected" ]]; then
        log_message "🚨 DRIFT DETECTED in $file"
        log_message "   Key: $key"
        log_message "   Expected: $expected"
        log_message "   Actual: $actual"
        
        # Create backup
        local backup_file="${file}.backup.$(date +%s)"
        cp "$file" "$backup_file"
        log_message "📋 Backup created: $backup_file"
        
        # Fix the drift
        case "$file" in
            *.env)
                sed -i "s|^$key=.*|$key=$expected|g" "$file"
                ;;
            *.json)
                case "$key" in
                    "Kestrel.Endpoints.Http.Url")
                        sed -i "s|\"Url\": \"[^\"]*\"|\"Url\": \"$expected\"|g" "$file"
                        ;;
                    "Ollama.Endpoint")
                        sed -i "/\"Ollama\"/,/}/ s|\"Endpoint\": \"[^\"]*\"|\"Endpoint\": \"$expected\"|g" "$file"
                        ;;
                esac
                ;;
        esac
        
        log_message "🔧 Fixed drift in $file"
        return 1
    fi
    return 0
}

# Create logs directory
mkdir -p "$(dirname "$LOG_FILE")"

log_message "🔍 Configuration Monitor Started"
log_message "   Monitoring interval: ${MONITOR_INTERVAL}s"
log_message "   Watched files: ${#WATCH_FILES[@]}"

# Main monitoring loop
while true; do
    drift_detected=false
    
    for file in "${WATCH_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            for key_value in "${!EXPECTED_VALUES[@]}"; do
                if [[ "$key_value" =~ ^$file: ]]; then
                    key="${key_value#*:}"
                    expected="${EXPECTED_VALUES[$key_value]}"
                    
                    if ! check_and_fix_drift "$file" "$key" "$expected"; then
                        drift_detected=true
                    fi
                fi
            done
        else
            log_message "⚠️ Watched file missing: $file"
        fi
    done
    
    if [[ "$drift_detected" == "false" ]]; then
        # Only log every 10 minutes when everything is OK
        if (( $(date +%s) % 600 < $MONITOR_INTERVAL )); then
            log_message "✅ All configurations stable"
        fi
    fi
    
    sleep "$MONITOR_INTERVAL"
done