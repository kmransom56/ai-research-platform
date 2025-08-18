#!/bin/bash
# Comprehensive Backup Server Sync Script
# Syncs Chat Copilot Platform with backup server at 192.168.0.5

set -euo pipefail

# Configuration
PLATFORM_ROOT="/home/keith/chat-copilot"
BACKUP_SERVER="keith-ransom@192.168.0.5"
BACKUP_SERVER_IP="192.168.0.5"
REMOTE_PATH="~/chat-copilot"

# Logging
LOG_DIR="$PLATFORM_ROOT/logs/sync"
LOG_FILE="$LOG_DIR/backup-sync.log"
PID_FILE="$PLATFORM_ROOT/pids/backup-sync.pid"

# Create directories
mkdir -p "$LOG_DIR" "$(dirname "$PID_FILE")" "$PLATFORM_ROOT/pids"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

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

# Check network connectivity
check_network() {
    log_msg "NETWORK" "Testing network connectivity to backup server..."
    
    # Ping test
    if ! ping -c 1 -W 3 "$BACKUP_SERVER_IP" >/dev/null 2>&1; then
        log_msg "ERROR" "Cannot ping backup server at $BACKUP_SERVER_IP"
        return 1
    fi
    
    # SSH test
    if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$BACKUP_SERVER" "echo 'Connection test successful'" >/dev/null 2>&1; then
        log_msg "ERROR" "Cannot SSH to backup server at $BACKUP_SERVER"
        return 1
    fi
    
    log_msg "SUCCESS" "Network connectivity to backup server verified"
    return 0
}

# Create backup server directory structure
setup_backup_server() {
    log_msg "SYNC" "Setting up directory structure on backup server..."
    
    ssh "$BACKUP_SERVER" "
        mkdir -p $REMOTE_PATH/{logs,pids,config-backups-working,scripts,webapi,webapp,python,network-agents}
        mkdir -p $REMOTE_PATH/logs/{sync,platform,ai-stack}
        mkdir -p $REMOTE_PATH/config-backups-working/latest
        echo '✅ Directory structure created on backup server'
    " || {
        log_msg "ERROR" "Failed to create directory structure on backup server"
        return 1
    }
    
    log_msg "SUCCESS" "Backup server directory structure ready"
}

# Sync critical configuration files
sync_configurations() {
    log_msg "SYNC" "Syncing critical configuration files..."
    
    local config_files=(
        ".env"
        "appsettings.json"
        "docker-compose.ai-stack.yml"
        "docker-compose.yml"
        "CLAUDE.md"
        "API_GATEWAY_USER_GUIDE.md"
        "COLLABORATION_GUIDE.md"
        "AI_STACK_SETUP.md"
        "platform-status.json"
        "port-configuration.json"
    )
    
    for file in "${config_files[@]}"; do
        if [[ -f "$PLATFORM_ROOT/$file" ]]; then
            if rsync -avz --timeout=30 "$PLATFORM_ROOT/$file" "$BACKUP_SERVER:$REMOTE_PATH/$file"; then
                log_msg "SUCCESS" "Synced: $file"
            else
                log_msg "WARNING" "Failed to sync: $file"
            fi
        fi
    done
}

# Sync entire project with exclusions
sync_full_project() {
    log_msg "SYNC" "Starting full project synchronization..."
    
    # Create rsync exclusion list
    local exclude_list=(
        "--exclude=logs/"
        "--exclude=pids/"
        "--exclude=*.log"
        "--exclude=*.pid"
        "--exclude=*.tmp"
        "--exclude=*.swp"
        "--exclude=*.swo"
        "--exclude=*~"
        "--exclude=*.pyc"
        "--exclude=*.pyo"
        "--exclude=__pycache__/"
        "--exclude=node_modules/"
        "--exclude=.git/"
        "--exclude=.venv/"
        "--exclude=venv/"
        "--exclude=build/"
        "--exclude=dist/"
        "--exclude=temp/"
        "--exclude=tmp/"
        "--exclude=.DS_Store"
        "--exclude=Thumbs.db"
        "--exclude=config-snapshots/"
        "--exclude=config-backups-auto/"
        "--exclude=runtime-data/"
        "--exclude=data/"
    )
    
    # Perform sync
    log_msg "SYNC" "Executing rsync with compression and progress..."
    
    if rsync -avz --progress --stats "${exclude_list[@]}" \
        --timeout=300 \
        --partial \
        --inplace \
        "$PLATFORM_ROOT/" "$BACKUP_SERVER:$REMOTE_PATH/"; then
        
        log_msg "SUCCESS" "Full project sync completed successfully"
        
        # Show sync statistics
        local sync_stats=$(rsync -avz --dry-run --stats "${exclude_list[@]}" "$PLATFORM_ROOT/" "$BACKUP_SERVER:$REMOTE_PATH/" 2>/dev/null | tail -15)
        log_msg "INFO" "Sync statistics:\n$sync_stats"
        
    else
        log_msg "ERROR" "Full project sync failed"
        return 1
    fi
}

# Sync specific directories
sync_directory() {
    local dir="$1"
    local description="${2:-$dir}"
    
    if [[ ! -d "$PLATFORM_ROOT/$dir" ]]; then
        log_msg "WARNING" "Directory not found: $dir"
        return 1
    fi
    
    log_msg "SYNC" "Syncing $description..."
    
    if rsync -avz --timeout=60 --delete \
        "$PLATFORM_ROOT/$dir/" "$BACKUP_SERVER:$REMOTE_PATH/$dir/"; then
        log_msg "SUCCESS" "Synced: $description"
    else
        log_msg "ERROR" "Failed to sync: $description"
        return 1
    fi
}

# Sync working configuration backup
sync_working_backup() {
    log_msg "SYNC" "Creating and syncing working configuration backup..."
    
    # Run the backup script first
    if [[ -f "$PLATFORM_ROOT/scripts/backup-working-config.sh" ]]; then
        log_msg "INFO" "Creating local backup..."
        "$PLATFORM_ROOT/scripts/backup-working-config.sh"
        
        # Find the latest backup
        local latest_backup=$(ls -1t "$PLATFORM_ROOT/config-backups-working/" | head -1)
        
        if [[ -n "$latest_backup" ]]; then
            # Sync the latest backup
            if rsync -avz --timeout=120 \
                "$PLATFORM_ROOT/config-backups-working/$latest_backup/" \
                "$BACKUP_SERVER:$REMOTE_PATH/config-backups-working/latest/"; then
                
                log_msg "SUCCESS" "Working backup synced: $latest_backup"
                
                # Create metadata on backup server
                ssh "$BACKUP_SERVER" "
                    echo '{
                        \"backup_date\": \"$(date -Iseconds)\",
                        \"source_backup\": \"$latest_backup\",
                        \"source_server\": \"$(hostname)\",
                        \"source_ip\": \"$(hostname -I | awk '{print $1}')\",
                        \"backup_type\": \"working_configuration\"
                    }' > $REMOTE_PATH/config-backups-working/latest/backup_metadata.json
                "
            else
                log_msg "ERROR" "Failed to sync working backup"
                return 1
            fi
        else
            log_msg "WARNING" "No backup found to sync"
            return 1
        fi
    else
        log_msg "ERROR" "Backup script not found"
        return 1
    fi
}

# Check backup server status
check_backup_status() {
    log_msg "INFO" "Checking backup server status..."
    
    ssh "$BACKUP_SERVER" "
        echo '=== Backup Server Status ==='
        echo 'Hostname: '$(hostname)
        echo 'Uptime: '$(uptime | cut -d',' -f1)
        echo 'Disk Usage:'
        df -h | grep -E '/$|/home'
        echo
        echo '=== Chat Copilot Backup Status ==='
        if [[ -d $REMOTE_PATH ]]; then
            echo 'Backup directory exists: YES'
            echo 'Total size: '$(du -sh $REMOTE_PATH 2>/dev/null | cut -f1 || echo 'Unknown')
            echo 'Last modified: '$(stat -c %y $REMOTE_PATH 2>/dev/null | cut -d'.' -f1 || echo 'Unknown')
            echo
            echo 'Key files:'
            for file in .env docker-compose.ai-stack.yml CLAUDE.md; do
                if [[ -f $REMOTE_PATH/\$file ]]; then
                    echo '  ✅ '\$file
                else
                    echo '  ❌ '\$file
                fi
            done
            echo
            echo 'Recent backups:'
            ls -1t $REMOTE_PATH/config-backups-working/ 2>/dev/null | head -5 || echo '  No backups found'
        else
            echo 'Backup directory exists: NO'
        fi
        echo '==========================='
    " || {
        log_msg "ERROR" "Failed to check backup server status"
        return 1
    }
}

# Pull changes from backup server
pull_from_backup() {
    log_msg "SYNC" "Pulling changes from backup server..."
    
    # Create local backup before pulling
    local local_backup_dir="$PLATFORM_ROOT/backups/pre-pull-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$local_backup_dir"
    
    log_msg "INFO" "Creating local backup before pull..."
    rsync -a "$PLATFORM_ROOT/" "$local_backup_dir/" --exclude=backups/
    
    # Pull from backup server
    if rsync -avz --progress \
        --exclude=logs/ --exclude=pids/ --exclude=*.log --exclude=*.pid \
        "$BACKUP_SERVER:$REMOTE_PATH/" "$PLATFORM_ROOT/"; then
        
        log_msg "SUCCESS" "Successfully pulled changes from backup server"
        log_msg "INFO" "Local backup saved to: $local_backup_dir"
    else
        log_msg "ERROR" "Failed to pull from backup server"
        return 1
    fi
}

# Start real-time monitoring and sync
start_realtime_sync() {
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log_msg "WARNING" "Real-time sync is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    if ! check_network; then
        log_msg "ERROR" "Cannot start real-time sync - network check failed"
        return 1
    fi
    
    log_msg "INFO" "Starting real-time sync monitoring..."
    
    # Function to sync changed files
    sync_changed_file() {
        local file="$1"
        local rel_path="${file#$PLATFORM_ROOT/}"
        
        # Skip unwanted files
        case "$rel_path" in
            *.log|*.tmp|*.swp|*.swo|*~|*.pyc|*.pyo|*.lock|*.pid) return 0 ;;
            .git/*|node_modules/*|__pycache__/*|.venv/*|venv/*|build/*|dist/*|logs/*|pids/*|temp/*|tmp/*) return 0 ;;
        esac
        
        if [[ -f "$file" ]]; then
            if rsync -avz --timeout=10 "$file" "$BACKUP_SERVER:$REMOTE_PATH/$rel_path" >/dev/null 2>&1; then
                log_msg "SYNC" "Auto-synced: $rel_path"
            else
                log_msg "WARNING" "Auto-sync failed: $rel_path"
            fi
        fi
    }
    
    # Start monitoring in background
    (
        echo $$ > "$PID_FILE"
        
        if command -v inotifywait >/dev/null 2>&1; then
            log_msg "INFO" "Using inotifywait for real-time monitoring"
            
            inotifywait -m -r -e modify,create,delete,move \
                --exclude '\.(log|tmp|swp|swo|pyc|pyo|lock|pid)$' \
                --exclude '/(logs|pids|\.git|node_modules|__pycache__|\.venv|venv|build|dist|temp|tmp)/' \
                "$PLATFORM_ROOT" | while read path action file; do
                
                if [[ "$action" == "MODIFY" || "$action" == "CREATE" ]]; then
                    sync_changed_file "$path$file"
                fi
            done
        else
            log_msg "WARNING" "inotifywait not available, using periodic sync (every 30 seconds)"
            
            while true; do
                sleep 30
                sync_configurations
            done
        fi
    ) &
    
    local sync_pid=$!
    echo $sync_pid > "$PID_FILE"
    
    log_msg "SUCCESS" "Real-time sync started (PID: $sync_pid)"
}

# Stop real-time sync
stop_realtime_sync() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log_msg "INFO" "Stopping real-time sync (PID: $pid)..."
            kill "$pid"
            rm -f "$PID_FILE"
            log_msg "SUCCESS" "Real-time sync stopped"
        else
            log_msg "WARNING" "Real-time sync process not found"
            rm -f "$PID_FILE"
        fi
    else
        log_msg "WARNING" "No real-time sync PID file found"
    fi
}

# Check real-time sync status
check_realtime_status() {
    if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        local pid=$(cat "$PID_FILE")
        log_msg "SUCCESS" "Real-time sync is running (PID: $pid)"
        
        # Show recent sync activity
        if [[ -f "$LOG_FILE" ]]; then
            log_msg "INFO" "Recent sync activity:"
            tail -10 "$LOG_FILE" | grep -E "(Auto-synced|Synced)" || echo "  No recent activity"
        fi
    else
        log_msg "INFO" "Real-time sync is not running"
    fi
}

# Validate sync integrity
validate_sync() {
    log_msg "INFO" "Validating sync integrity..."
    
    local validation_script=$(cat << 'EOF'
#!/bin/bash
echo "=== Backup Server Validation ==="
cd ~/chat-copilot 2>/dev/null || { echo "Chat Copilot directory not found"; exit 1; }

echo "Checking key files..."
key_files=(.env docker-compose.ai-stack.yml CLAUDE.md)
for file in "${key_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file ($(stat -c%s "$file") bytes)"
    else
        echo "❌ $file (missing)"
    fi
done

echo
echo "Checking directory structure..."
dirs=(webapi webapp python scripts network-agents)
for dir in "${dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "✅ $dir ($count files)"
    else
        echo "❌ $dir (missing)"
    fi
done

echo
echo "Recent sync timestamps:"
find . -name "*.md" -o -name "*.yml" -o -name "*.json" | head -5 | xargs ls -lt 2>/dev/null | head -5

echo "=== Validation Complete ==="
EOF
    )
    
    ssh "$BACKUP_SERVER" "$validation_script" || {
        log_msg "ERROR" "Validation failed"
        return 1
    }
    
    log_msg "SUCCESS" "Sync integrity validation completed"
}

# Show usage information
show_usage() {
    cat << EOF
🔄 Chat Copilot Platform - Backup Server Sync

USAGE:
    $0 <command> [options]

COMMANDS:
    check           - Test network connectivity to backup server
    setup           - Setup directory structure on backup server
    sync-config     - Sync critical configuration files only
    sync-full       - Sync entire project (excluding logs, temp files)
    sync-working    - Create and sync working configuration backup
    sync-dir <dir>  - Sync specific directory
    pull            - Pull changes from backup server to local
    status          - Check backup server status and contents
    validate        - Validate sync integrity
    
    realtime-start  - Start real-time file monitoring and sync
    realtime-stop   - Stop real-time sync
    realtime-status - Check real-time sync status
    
    help            - Show this help message

EXAMPLES:
    $0 check                    # Test connection
    $0 setup                    # Setup backup server
    $0 sync-full                # Full project sync
    $0 sync-config              # Sync configs only
    $0 sync-working             # Sync working backup
    $0 sync-dir python          # Sync python directory
    $0 realtime-start           # Start real-time sync
    $0 status                   # Check backup status
    $0 validate                 # Validate sync

CONFIGURATION:
    Backup Server: $BACKUP_SERVER
    Remote Path: $REMOTE_PATH
    Log File: $LOG_FILE

NOTES:
    - Requires SSH key authentication to backup server
    - Uses rsync for efficient file transfer
    - Excludes logs, temp files, and development artifacts
    - Real-time sync requires inotify-tools for optimal performance

EOF
}

# Main execution
main() {
    local command="${1:-help}"
    
    # Create log entry for command execution
    log_msg "INFO" "Executing command: $command"
    
    case "$command" in
        "check")
            check_network
            ;;
        "setup")
            check_network && setup_backup_server
            ;;
        "sync-config")
            check_network && sync_configurations
            ;;
        "sync-full")
            check_network && setup_backup_server && sync_full_project
            ;;
        "sync-working")
            check_network && sync_working_backup
            ;;
        "sync-dir")
            local dir="$2"
            if [[ -z "$dir" ]]; then
                log_msg "ERROR" "Directory name required for sync-dir command"
                echo "Usage: $0 sync-dir <directory_name>"
                exit 1
            fi
            check_network && sync_directory "$dir"
            ;;
        "pull")
            check_network && pull_from_backup
            ;;
        "status")
            check_network && check_backup_status
            ;;
        "validate")
            check_network && validate_sync
            ;;
        "realtime-start")
            start_realtime_sync
            ;;
        "realtime-stop")
            stop_realtime_sync
            ;;
        "realtime-status")
            check_realtime_status
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_msg "ERROR" "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              Chat Copilot Platform Backup Sync              ║"
echo "║                    Backup Server: 192.168.0.5               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we have the required commands
for cmd in rsync ssh; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_msg "ERROR" "Required command not found: $cmd"
        echo "Please install $cmd and try again"
        exit 1
    fi
done

# Run main function
main "$@"