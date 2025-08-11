#!/bin/bash

# Simple Real-Time Sync for Chat Copilot Platform
# Watches for file changes and syncs to backup server

PLATFORM_ROOT="/home/keith/chat-copilot"
BACKUP_SERVER="keith-ransom@192.168.0.5"
LOG_FILE="$PLATFORM_ROOT/logs/sync/simple-realtime-$(date +%Y%m%d_%H%M%S).log"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to sync a file
sync_file() {
    local file="$1"
    local rel_path="${file#$PLATFORM_ROOT/}"
    
    # Skip temporary files
    case "$rel_path" in
        *.log|*.tmp|*.swp|*.swo|*~|*.pyc|*.pyo|*.lock) return 0 ;;
        .git/*|node_modules/*|__pycache__/*|.venv/*|venv/*|build/*|dist/*|logs/*|pids/*|temp/*|tmp/*) return 0 ;;
    esac
    
    # Sync file
    if rsync -avz --timeout=10 "$file" "$BACKUP_SERVER:~/chat-copilot/$rel_path" >/dev/null 2>&1; then
        log_message "🔄 Synced: $rel_path"
    else
        log_message "❌ Failed to sync: $rel_path"
    fi
}

# Test connection
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$BACKUP_SERVER" "echo 'connected'" >/dev/null 2>&1; then
    log_message "❌ Cannot connect to backup server"
    exit 1
fi

log_message "✅ Starting real-time sync to backup server"
log_message "👁️  Watching for file changes..."

# Watch for changes and sync
inotifywait -m -r -e modify,create,delete,move \
    --format '%w%f' \
    "$PLATFORM_ROOT/webapi" \
    "$PLATFORM_ROOT/webapp" \
    "$PLATFORM_ROOT/scripts" \
    "$PLATFORM_ROOT/configs" \
    "$PLATFORM_ROOT/docker" \
    "$PLATFORM_ROOT/docs" \
    "$PLATFORM_ROOT/agents" \
    "$PLATFORM_ROOT/plugins" \
    "$PLATFORM_ROOT/tools" \
    "$PLATFORM_ROOT/python" \
    "$PLATFORM_ROOT/shared" \
    2>/dev/null | while read file; do
    
    # Skip if file doesn't exist
    [[ -e "$file" ]] || continue
    
    log_message "👁️  Change detected: ${file#$PLATFORM_ROOT/}"
    
    # Small delay to avoid rapid syncs
    sleep 1
    
    # Sync in background
    sync_file "$file" &
    
    # Limit concurrent jobs
    while [[ $(jobs -r | wc -l) -ge 3 ]]; do
        sleep 0.1
    done
done