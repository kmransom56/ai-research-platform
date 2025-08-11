#!/bin/bash

# Working Real-Time Sync for Chat Copilot Platform
# This version uses a simple approach that actually works

set -e

PLATFORM_ROOT="/home/keith/chat-copilot"
BACKUP_SERVER="keith-ransom@192.168.0.5"
PID_FILE="$PLATFORM_ROOT/pids/working-realtime-sync.pid"
LOG_FILE="$PLATFORM_ROOT/logs/sync/working-realtime-sync.log"

# Create directories
mkdir -p "$(dirname "$PID_FILE")" "$(dirname "$LOG_FILE")"

# Function to log messages
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to sync file
sync_file() {
    local file="$1"
    local rel_path="${file#$PLATFORM_ROOT/}"
    
    # Skip unwanted files
    case "$rel_path" in
        *.log|*.tmp|*.swp|*.swo|*~|*.pyc|*.pyo|*.lock|*.pid) return 0 ;;
        .git/*|node_modules/*|__pycache__/*|.venv/*|venv/*|build/*|dist/*|logs/*|pids/*|temp/*|tmp/*) return 0 ;;
    esac
    
    if [[ -f "$file" ]]; then
        if rsync -avz --timeout=10 "$file" "$BACKUP_SERVER:~/chat-copilot/$rel_path" >/dev/null 2>&1; then
            log_msg "✅ Synced: $rel_path"
        else
            log_msg "❌ Failed: $rel_path"
        fi
    fi
}

# Command functions
start_sync() {
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Real-time sync is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    # Test connection
    if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$BACKUP_SERVER" "echo 'test'" >/dev/null 2>&1; then
        echo "❌ Cannot connect to backup server"
        return 1
    fi
    
    echo "🚀 Starting real-time sync..."
    log_msg "🚀 Starting real-time sync to backup server"
    
    # Start background process
    {
        echo $$ > "$PID_FILE"
        
        log_msg "👁️  Watching for file changes..."
        
        # Use fswatch if available, otherwise inotifywait
        if command -v fswatch >/dev/null 2>&1; then
            fswatch -r \
                "$PLATFORM_ROOT/webapi" \
                "$PLATFORM_ROOT/webapp" \
                "$PLATFORM_ROOT/scripts" \
                "$PLATFORM_ROOT/configs" \
                "$PLATFORM_ROOT/docker" \
                "$PLATFORM_ROOT/docs" \
                2>/dev/null | while read file; do
                log_msg "👁️  Change: ${file#$PLATFORM_ROOT/}"
                sync_file "$file" &
            done
        else
            inotifywait -m -r -e modify,create,delete,move \
                --format '%w%f' \
                "$PLATFORM_ROOT/webapi" \
                "$PLATFORM_ROOT/webapp" \
                "$PLATFORM_ROOT/scripts" \
                "$PLATFORM_ROOT/configs" \
                "$PLATFORM_ROOT/docker" \
                "$PLATFORM_ROOT/docs" \
                2>/dev/null | while read file; do
                [[ -e "$file" ]] || continue
                log_msg "👁️  Change: ${file#$PLATFORM_ROOT/}"
                sync_file "$file" &
                sleep 0.5
            done
        fi
    } &
    
    local sync_pid=$!
    echo "$sync_pid" > "$PID_FILE"
    
    echo "✅ Real-time sync started (PID: $sync_pid)"
    echo "📝 Log file: $LOG_FILE"
    echo "🛑 Stop with: $0 stop"
}

stop_sync() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping real-time sync (PID: $pid)..."
            kill "$pid"
            pkill -P "$pid" 2>/dev/null || true
            rm -f "$PID_FILE"
            log_msg "🛑 Real-time sync stopped"
            echo "✅ Real-time sync stopped"
        else
            echo "⚠️  Sync process not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "⚠️  No sync process found"
    fi
}

status_sync() {
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        local pid=$(cat "$PID_FILE")
        echo "✅ Real-time sync is running (PID: $pid)"
        
        # Test connection
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$BACKUP_SERVER" "echo 'test'" >/dev/null 2>&1; then
            echo "🌐 Connection to backup server: OK"
        else
            echo "❌ Connection to backup server: FAILED"
        fi
        
        # Show recent activity
        if [[ -f "$LOG_FILE" ]]; then
            echo "📋 Recent activity:"
            tail -5 "$LOG_FILE" | sed 's/^/  /'
        fi
    else
        echo "❌ Real-time sync is not running"
        [[ -f "$PID_FILE" ]] && rm -f "$PID_FILE"
    fi
}

test_sync() {
    echo "🧪 Testing real-time sync..."
    
    # Test connection
    if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$BACKUP_SERVER" "echo 'test'" >/dev/null 2>&1; then
        echo "❌ Cannot connect to backup server"
        return 1
    fi
    
    # Create test file
    local test_file="$PLATFORM_ROOT/test-sync-$(date +%s).txt"
    echo "Test sync file created at $(date)" > "$test_file"
    
    # Sync it
    sync_file "$test_file"
    
    # Check on backup server
    sleep 2
    if ssh "$BACKUP_SERVER" "test -f ~/chat-copilot/$(basename "$test_file")"; then
        echo "✅ Test successful - file synced to backup server"
        rm -f "$test_file"
        ssh "$BACKUP_SERVER" "rm -f ~/chat-copilot/$(basename "$test_file")" 2>/dev/null
    else
        echo "❌ Test failed - file not found on backup server"
        rm -f "$test_file"
        return 1
    fi
}

monitor_sync() {
    echo "📊 Monitoring real-time sync (Ctrl+C to exit)..."
    if [[ -f "$LOG_FILE" ]]; then
        tail -f "$LOG_FILE"
    else
        echo "No log file found. Start sync first."
    fi
}

# Main command handling
case "${1:-help}" in
    start)
        start_sync
        ;;
    stop)
        stop_sync
        ;;
    status)
        status_sync
        ;;
    test)
        test_sync
        ;;
    monitor)
        monitor_sync
        ;;
    *)
        echo "Usage: $0 {start|stop|status|test|monitor}"
        echo ""
        echo "Commands:"
        echo "  start   - Start real-time sync to backup server"
        echo "  stop    - Stop real-time sync"
        echo "  status  - Show sync status"
        echo "  test    - Test sync functionality"
        echo "  monitor - Monitor sync activity"
        ;;
esac