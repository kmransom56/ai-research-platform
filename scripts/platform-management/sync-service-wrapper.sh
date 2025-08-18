#!/bin/bash
# Service Wrapper for Real-time Backup Sync
# Handles systemd service environment specifics

set -euo pipefail

# Configuration
PLATFORM_ROOT="/home/keith/chat-copilot"
BACKUP_SERVER="keith-ransom@192.168.0.5" 
BACKUP_SERVER_IP="192.168.0.5"
LOG_DIR="$PLATFORM_ROOT/logs/sync"
LOG_FILE="$LOG_DIR/backup-sync.log"
PID_FILE="$PLATFORM_ROOT/pids/backup-sync.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Create directories
mkdir -p "$LOG_DIR" "$(dirname "$PID_FILE")" "$PLATFORM_ROOT/pids"

# Logging functions
log_msg() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${BLUE}[$timestamp] ℹ️  $message${NC}" | tee -a "$LOG_FILE" ;;
        "SUCCESS") echo -e "${GREEN}[$timestamp] ✅ $message${NC}" | tee -a "$LOG_FILE" ;;
        "WARNING") echo -e "${YELLOW}[$timestamp] ⚠️  $message${NC}" | tee -a "$LOG_FILE" ;;
        "ERROR") echo -e "${RED}[$timestamp] ❌ $message${NC}" | tee -a "$LOG_FILE" ;;
        "SYNC") echo -e "${PURPLE}[$timestamp] 🔄 $message${NC}" | tee -a "$LOG_FILE" ;;
        "NETWORK") echo -e "${CYAN}[$timestamp] 🌐 $message${NC}" | tee -a "$LOG_FILE" ;;
    esac
}

# Service-friendly network check
check_network_service() {
    log_msg "NETWORK" "Testing network connectivity for systemd service..."
    
    # Wait for network to be fully ready
    local retries=0
    local max_retries=12
    
    while [[ $retries -lt $max_retries ]]; do
        # Try SSH connection directly (more reliable than ping in systemd)
        if timeout 10 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
           -o BatchMode=yes -o PasswordAuthentication=no \
           "$BACKUP_SERVER" "echo 'Service connectivity test successful'" >/dev/null 2>&1; then
            
            log_msg "SUCCESS" "Network connectivity to backup server verified (attempt $((retries + 1)))"
            return 0
        fi
        
        retries=$((retries + 1))
        log_msg "WARNING" "Network connectivity attempt $retries/$max_retries failed, retrying in 5 seconds..."
        sleep 5
    done
    
    log_msg "ERROR" "Cannot establish SSH connection to backup server after $max_retries attempts"
    return 1
}

# Service-specific real-time sync start
start_service_sync() {
    # Check if already running
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log_msg "WARNING" "Real-time sync is already running (PID: $(cat "$PID_FILE"))"
        return 0
    fi
    
    log_msg "INFO" "Starting real-time sync service..."
    
    # Enhanced network check for service environment
    if ! check_network_service; then
        log_msg "ERROR" "Network connectivity check failed - will retry"
        return 1
    fi
    
    # Function to sync changed files
    sync_changed_file() {
        local file="$1"
        local rel_path="${file#$PLATFORM_ROOT/}"
        
        # Skip unwanted files
        case "$rel_path" in
            *.log|*.tmp|*.swp|*.swo|*~|*.pyc|*.pyo|*.lock|*.pid) return 0 ;;
            .git/*|node_modules/*|__pycache__/*|.venv/*|venv/*|build/*|dist/*|logs/*|pids/*|temp/*|tmp/*) return 0 ;;
        esac
        
        if [[ -e "$file" ]]; then
            # Create parent directory on remote if needed
            local parent_dir=$(dirname "$rel_path")
            if [[ "$parent_dir" != "." ]]; then
                ssh "$BACKUP_SERVER" "mkdir -p '$REMOTE_PATH/$parent_dir'" >/dev/null 2>&1 || true
            fi
            
            # Sync the file/directory with retry logic
            local sync_retries=0
            local max_sync_retries=3
            
            while [[ $sync_retries -lt $max_sync_retries ]]; do
                if timeout 30 rsync -avz --timeout=15 "$file" "$BACKUP_SERVER:~/chat-copilot/$rel_path" >/dev/null 2>&1; then
                    log_msg "SYNC" "Auto-synced: $rel_path"
                    return 0
                fi
                sync_retries=$((sync_retries + 1))
                sleep 2
            done
            
            log_msg "WARNING" "Auto-sync failed after $max_sync_retries attempts: $rel_path"
        fi
    }
    
    # Start monitoring
    log_msg "INFO" "Initializing inotifywait monitoring..."
    
    if command -v inotifywait >/dev/null 2>&1; then
        log_msg "SUCCESS" "Starting inotifywait real-time monitoring"
        
        # Use exec to replace the current process
        exec inotifywait -m -r -e modify,create,delete,move \
            --exclude '\.(log|tmp|swp|swo|pyc|pyo|lock|pid)$|/(logs|pids|\.git|node_modules|__pycache__|\.venv|venv|build|dist|temp|tmp)/' \
            "$PLATFORM_ROOT" | while read path action file; do
            
            case "$action" in
                "MODIFY"|"CREATE"|"MOVED_TO")
                    sync_changed_file "$path$file"
                    ;;
                "DELETE"|"MOVED_FROM")
                    local rel_path="${path}${file}"
                    rel_path="${rel_path#$PLATFORM_ROOT/}"
                    timeout 10 ssh "$BACKUP_SERVER" "rm -f '~/chat-copilot/$rel_path'" >/dev/null 2>&1 || true
                    log_msg "SYNC" "Auto-deleted: $rel_path"
                    ;;
            esac
        done
    else
        log_msg "ERROR" "inotifywait not available - cannot start real-time monitoring"
        return 1
    fi
}

# Stop sync service
stop_service_sync() {
    log_msg "INFO" "Stopping real-time sync service..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            rm -f "$PID_FILE"
            log_msg "SUCCESS" "Real-time sync stopped (PID: $pid)"
        else
            rm -f "$PID_FILE"
            log_msg "WARNING" "Sync process not running, cleaned PID file"
        fi
    else
        log_msg "INFO" "No PID file found"
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        start_service_sync
        ;;
    "stop")
        stop_service_sync
        ;;
    *)
        log_msg "ERROR" "Usage: $0 {start|stop}"
        exit 1
        ;;
esac