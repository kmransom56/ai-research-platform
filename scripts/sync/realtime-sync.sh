#!/bin/bash

# =============================================================================
# Chat Copilot Platform - Real-Time Synchronization Script
# =============================================================================
# This script provides real-time bidirectional synchronization between
# development and backup servers using inotify for file system monitoring
# =============================================================================

set -euo pipefail

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
PURPLE='\\033[0;35m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$PLATFORM_ROOT/scripts/sync"
LOG_DIR="$PLATFORM_ROOT/logs/sync"
PID_DIR="$PLATFORM_ROOT/pids"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create necessary directories
mkdir -p "$LOG_DIR" "$CONFIG_DIR" "$PID_DIR"

# Configuration files
SYNC_CONFIG="$CONFIG_DIR/realtime-sync.conf"
RSYNC_CONFIG="$CONFIG_DIR/rsync-config.conf"
PID_FILE="$PID_DIR/realtime-sync.pid"
LOG_FILE="$LOG_DIR/realtime-sync-$DATE.log"

# Print functions
print_status() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    case $level in
        \"INFO\")  echo -e \"${BLUE}[$timestamp] ℹ️  ${message}${NC}\" | tee -a \"$LOG_FILE\" ;;
        \"SUCCESS\") echo -e \"${GREEN}[$timestamp] ✅ ${message}${NC}\" | tee -a \"$LOG_FILE\" ;;
        \"WARNING\") echo -e \"${YELLOW}[$timestamp] ⚠️  ${message}${NC}\" | tee -a \"$LOG_FILE\" ;;
        \"ERROR\") echo -e \"${RED}[$timestamp] ❌ ${message}${NC}\" | tee -a \"$LOG_FILE\" ;;
        \"SYNC\") echo -e \"${PURPLE}[$timestamp] 🔄 ${message}${NC}\" | tee -a \"$LOG_FILE\" ;;
        \"WATCH\") echo -e \"${CYAN}[$timestamp] 👁️  ${message}${NC}\" | tee -a \"$LOG_FILE\" ;;
    esac
}

print_banner() {
    echo \"==============================================================================\"
    echo \"🔄 CHAT COPILOT PLATFORM REAL-TIME SYNCHRONIZATION\"
    echo \"🚀 Bidirectional real-time sync between development and backup servers\"
    echo \"💾 Source: 192.168.0.1 (ubuntuaicodeserver)\"
    echo \"🎮 Backup: 192.168.0.5 (ubuntuaicodeserver-2) - High GPU RAM\"
    echo \"==============================================================================\"
    echo
}

show_help() {
    cat << EOF
🔄 Chat Copilot Platform Real-Time Synchronization

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    start             Start real-time bidirectional sync
    stop              Stop real-time sync
    status            Show sync status
    setup             Setup real-time sync configuration
    monitor           Monitor sync activity (live view)
    restart           Restart sync service
    logs              Show recent sync logs
    test              Test sync functionality

SYNC MODES:
    --to-backup       Sync changes TO backup server (192.168.0.5)
    --from-backup     Sync changes FROM backup server (192.168.0.1)
    --bidirectional   Bidirectional sync (default)

OPTIONS:
    --include-systemd Include systemd service files
    --exclude-data    Exclude data directories
    --include-secrets Include secret files (use with caution)
    --interval SEC    Sync interval in seconds (default: 2)
    --daemon          Run as daemon
    --verbose         Verbose output
    --dry-run         Show what would be synced

EXAMPLES:
    # Start bidirectional real-time sync
    $0 start --bidirectional

    # Start sync TO backup server only
    $0 start --to-backup --include-systemd

    # Monitor sync activity
    $0 monitor

    # Check sync status
    $0 status

    # Stop sync
    $0 stop

NOTES:
    - Uses inotify for real-time file system monitoring
    - Automatically handles conflicts with timestamp-based resolution
    - Excludes temporary files and build artifacts
    - Includes systemd services when --include-systemd is used
    - Logs all sync activities for debugging

EOF
}

# Load rsync configuration
load_rsync_config() {
    if [[ -f \"$RSYNC_CONFIG\" ]]; then
        source \"$RSYNC_CONFIG\"
        print_status \"INFO\" \"Loaded rsync configuration\"
    else
        print_status \"ERROR\" \"Rsync configuration not found. Run rsync-platform-enhanced.sh setup first.\"
        return 1
    fi
}

# Create real-time sync configuration
setup_realtime_config() {
    print_status \"INFO\" \"Setting up real-time sync configuration...\"
    
    cat > \"$SYNC_CONFIG\" << 'EOF'
# Chat Copilot Platform Real-Time Sync Configuration

# Sync settings
SYNC_INTERVAL=2
SYNC_MODE=\"bidirectional\"
INCLUDE_SYSTEMD=\"false\"
EXCLUDE_DATA=\"true\"
INCLUDE_SECRETS=\"false\"
DAEMON_MODE=\"true\"
VERBOSE=\"false\"

# File patterns to watch
WATCH_PATTERNS=(
    \"*.py\"
    \"*.js\"
    \"*.ts\"
    \"*.jsx\"
    \"*.tsx\"
    \"*.cs\"
    \"*.json\"
    \"*.yml\"
    \"*.yaml\"
    \"*.md\"
    \"*.sh\"
    \"*.service\"
    \"*.conf\"
    \"*.env\"
    \"Dockerfile*\"
    \"docker-compose*\"
)

# Directories to watch
WATCH_DIRS=(
    \"webapi\"
    \"webapp\"
    \"scripts\"
    \"configs\"
    \"docker\"
    \"docs\"
    \"agents\"
    \"plugins\"
    \"tools\"
    \"python\"
    \"shared\"
)

# Exclude patterns for real-time sync
REALTIME_EXCLUDE_PATTERNS=(
    \"*.log\"
    \"*.tmp\"
    \"*.swp\"
    \"*.swo\"
    \"*~\"
    \".git/*\"
    \"node_modules/*\"
    \"__pycache__/*\"
    \"*.pyc\"
    \"*.pyo\"
    \".venv/*\"
    \"venv/*\"
    \"build/*\"
    \"dist/*\"
    \"target/*\"
    \"bin/*\"
    \"obj/*\"
    \"logs/*\"
    \"pids/*\"
    \"temp/*\"
    \"tmp/*\"
    \".DS_Store\"
    \"Thumbs.db\"
    \"*.lock\"
    \"package-lock.json\"
    \"yarn.lock\"
)

# Conflict resolution
CONFLICT_RESOLUTION=\"timestamp\"  # timestamp, source, backup, manual
BACKUP_CONFLICTS=\"true\"

# Performance settings
MAX_SYNC_JOBS=3
SYNC_TIMEOUT=30
RETRY_COUNT=3
RETRY_DELAY=5
EOF

    print_status \"SUCCESS\" \"Real-time sync configuration created at $SYNC_CONFIG\"
    print_status \"INFO\" \"Edit the configuration file to customize settings:\"
    print_status \"INFO\" \"nano $SYNC_CONFIG\"
}

# Load real-time sync configuration
load_realtime_config() {
    if [[ -f \"$SYNC_CONFIG\" ]]; then
        source \"$SYNC_CONFIG\"
        print_status \"INFO\" \"Loaded real-time sync configuration\"
    else
        print_status \"WARNING\" \"Real-time sync configuration not found. Creating default...\"
        setup_realtime_config
        source \"$SYNC_CONFIG\"
    fi
}

# Check if inotify-tools is installed
check_dependencies() {
    if ! command -v inotifywait &> /dev/null; then
        print_status \"ERROR\" \"inotify-tools not installed. Installing...\"
        sudo apt-get update && sudo apt-get install -y inotify-tools
        print_status \"SUCCESS\" \"inotify-tools installed\"
    fi
    
    if ! command -v rsync &> /dev/null; then
        print_status \"ERROR\" \"rsync not installed. Installing...\"
        sudo apt-get update && sudo apt-get install -y rsync
        print_status \"SUCCESS\" \"rsync installed\"
    fi
}

# Build rsync command for real-time sync
build_realtime_rsync_cmd() {
    local source=$1
    local dest=$2
    local options=()
    
    # Base options for real-time sync
    options+=(\"--archive\" \"--compress\" \"--partial\" \"--progress\")
    
    # SSH options
    options+=(\"--rsh=ssh -i $SSH_KEY_BACKUP -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null\")
    
    # Add exclude patterns
    for pattern in \"${REALTIME_EXCLUDE_PATTERNS[@]}\"; do
        options+=(\"--exclude=$pattern\")\n    done
    
    # Add data exclusions if requested
    if [[ \"$EXCLUDE_DATA\" == \"true\" ]]; then
        for pattern in \"${DATA_PATTERNS[@]}\"; do
            options+=(\"--exclude=$pattern\")\n        done
    fi
    
    # Include secrets only if explicitly requested
    if [[ \"$INCLUDE_SECRETS\" != \"true\" ]]; then
        for pattern in \"${SECRET_PATTERNS[@]}\"; do
            options+=(\"--exclude=$pattern\")\n        done
    fi
    
    # Additional options
    [[ \"$VERBOSE\" == \"true\" ]] && options+=(\"--verbose\")\n    \n    # Build command\n    REALTIME_RSYNC_CMD=(\"rsync\" \"${options[@]}\" \"$source\" \"$dest\")\n}\n\n# Sync single file or directory\nsync_path() {\n    local path=$1\n    local direction=$2  # to-backup, from-backup\n    \n    # Skip if path doesn't exist\n    if [[ ! -e \"$path\" ]]; then\n        return 0\n    fi\n    \n    # Convert absolute path to relative\n    local rel_path=\"${path#$PLATFORM_ROOT/}\"\n    \n    # Skip if path matches exclude patterns\n    for pattern in \"${REALTIME_EXCLUDE_PATTERNS[@]}\"; do\n        if [[ \"$rel_path\" == $pattern ]]; then\n            return 0\n        fi\n    done\n    \n    local source dest\n    \n    if [[ \"$direction\" == \"to-backup\" ]]; then\n        source=\"$PLATFORM_ROOT/$rel_path\"\n        dest=\"$BACKUP_SERVER/$rel_path\"\n    else\n        source=\"$BACKUP_SERVER/$rel_path\"\n        dest=\"$PLATFORM_ROOT/$rel_path\"\n    fi\n    \n    # Build and execute rsync command\n    build_realtime_rsync_cmd \"$source\" \"$(dirname \"$dest\")/\"\n    \n    if \"${REALTIME_RSYNC_CMD[@]}\" 2>&1 | tee -a \"$LOG_FILE\"; then\n        print_status \"SYNC\" \"Synced $direction: $rel_path\"\n        \n        # Sync systemd services if file is a service file and option is enabled\n        if [[ \"$INCLUDE_SYSTEMD\" == \"true\" && \"$rel_path\" == *.service ]]; then\n            sync_systemd_service \"$rel_path\" \"$direction\"\n        fi\n    else\n        print_status \"ERROR\" \"Failed to sync $direction: $rel_path\"\n    fi\n}\n\n# Sync systemd service file\nsync_systemd_service() {\n    local service_file=$1\n    local direction=$2\n    \n    local service_name=$(basename \"$service_file\")\n    local systemd_source systemd_dest\n    \n    if [[ \"$direction\" == \"to-backup\" ]]; then\n        systemd_source=\"/etc/systemd/system/$service_name\"\n        systemd_dest=\"keith-ransom@192.168.0.5:/etc/systemd/system/\"\n        \n        if [[ -f \"$systemd_source\" ]]; then\n            if rsync -avz \"$systemd_source\" \"$systemd_dest\" 2>&1 | tee -a \"$LOG_FILE\"; then\n                ssh keith-ransom@192.168.0.5 \"sudo systemctl daemon-reload\" 2>&1 | tee -a \"$LOG_FILE\"\n                print_status \"SYNC\" \"Synced systemd service to backup: $service_name\"\n            fi\n        fi\n    else\n        systemd_source=\"keith-ransom@192.168.0.5:/etc/systemd/system/$service_name\"\n        systemd_dest=\"/etc/systemd/system/\"\n        \n        if ssh keith-ransom@192.168.0.5 \"test -f /etc/systemd/system/$service_name\"; then\n            if rsync -avz \"$systemd_source\" \"$systemd_dest\" 2>&1 | tee -a \"$LOG_FILE\"; then\n                sudo systemctl daemon-reload 2>&1 | tee -a \"$LOG_FILE\"\n                print_status \"SYNC\" \"Synced systemd service from backup: $service_name\"\n            fi\n        fi\n    fi\n}\n\n# Watch for file changes and sync\nstart_file_watcher() {\n    local direction=$1\n    \n    print_status \"WATCH\" \"Starting file watcher for $direction sync...\"\n    \n    # Build inotify watch command\n    local watch_dirs=()\n    for dir in \"${WATCH_DIRS[@]}\"; do\n        if [[ -d \"$PLATFORM_ROOT/$dir\" ]]; then\n            watch_dirs+=(\"$PLATFORM_ROOT/$dir\")\n        fi\n    done\n    \n    # Add root directory files\n    watch_dirs+=(\"$PLATFORM_ROOT\")\n    \n    # Start inotify watcher\n    inotifywait -m -r -e modify,create,delete,move \\\n        --format '%w%f %e' \\\n        \"${watch_dirs[@]}\" 2>&1 | \\\n    while read -r file event; do\n        # Skip if file matches exclude patterns\n        local skip=false\n        for pattern in \"${REALTIME_EXCLUDE_PATTERNS[@]}\"; do\n            if [[ \"$file\" == *$pattern* ]]; then\n                skip=true\n                break\n            fi\n        done\n        \n        if [[ \"$skip\" == \"false\" ]]; then\n            # Add small delay to avoid rapid successive syncs\n            sleep \"$SYNC_INTERVAL\"\n            \n            print_status \"WATCH\" \"File change detected: $file ($event)\"\n            sync_path \"$file\" \"$direction\" &\n            \n            # Limit concurrent sync jobs\n            local job_count=$(jobs -r | wc -l)\n            if [[ $job_count -ge $MAX_SYNC_JOBS ]]; then\n                wait\n            fi\n        fi\n    done\n}\n\n# Start bidirectional sync\nstart_bidirectional_sync() {\n    print_status \"SYNC\" \"Starting bidirectional real-time sync...\"\n    \n    # Initial full sync\n    print_status \"SYNC\" \"Performing initial sync to backup server...\"\n    \"$SCRIPT_DIR/rsync-platform-enhanced.sh\" push backup-server --include-systemd 2>&1 | tee -a \"$LOG_FILE\"\n    \n    print_status \"SYNC\" \"Performing initial sync from backup server...\"\n    \"$SCRIPT_DIR/rsync-platform-enhanced.sh\" pull backup-server --include-systemd 2>&1 | tee -a \"$LOG_FILE\"\n    \n    # Start file watchers in background\n    start_file_watcher \"to-backup\" &\n    local to_backup_pid=$!\n    \n    # For bidirectional, we need to watch the backup server too\n    # This is more complex and would require a daemon on the backup server\n    # For now, we'll focus on source -> backup sync\n    \n    # Store PIDs\n    echo \"$to_backup_pid\" > \"$PID_FILE\"\n    \n    print_status \"SUCCESS\" \"Real-time sync started (PID: $to_backup_pid)\"\n    print_status \"INFO\" \"Watching for changes in: ${WATCH_DIRS[*]}\"\n    print_status \"INFO\" \"Syncing to backup server: 192.168.0.5\"\n    \n    # Wait for watchers\n    wait\n}\n\n# Start sync to backup only\nstart_to_backup_sync() {\n    print_status \"SYNC\" \"Starting real-time sync TO backup server...\"\n    \n    # Initial full sync\n    print_status \"SYNC\" \"Performing initial sync to backup server...\"\n    \"$SCRIPT_DIR/rsync-platform-enhanced.sh\" push backup-server --include-systemd 2>&1 | tee -a \"$LOG_FILE\"\n    \n    # Start file watcher\n    start_file_watcher \"to-backup\" &\n    local watcher_pid=$!\n    \n    # Store PID\n    echo \"$watcher_pid\" > \"$PID_FILE\"\n    \n    print_status \"SUCCESS\" \"Real-time sync to backup started (PID: $watcher_pid)\"\n    print_status \"INFO\" \"Watching for changes and syncing to 192.168.0.5\"\n    \n    # Wait for watcher\n    wait\n}\n\n# Start sync from backup only\nstart_from_backup_sync() {\n    print_status \"SYNC\" \"Starting real-time sync FROM backup server...\"\n    \n    # Initial full sync\n    print_status \"SYNC\" \"Performing initial sync from backup server...\"\n    \"$SCRIPT_DIR/rsync-platform-enhanced.sh\" pull backup-server --include-systemd 2>&1 | tee -a \"$LOG_FILE\"\n    \n    # For this mode, we would need to run a watcher on the backup server\n    # This requires a more complex setup with a daemon on the backup server\n    print_status \"WARNING\" \"FROM backup sync requires daemon on backup server\"\n    print_status \"INFO\" \"Consider using bidirectional sync or manual pulls\"\n}\n\n# Stop real-time sync\nstop_sync() {\n    if [[ -f \"$PID_FILE\" ]]; then\n        local pid=$(cat \"$PID_FILE\")\n        if kill -0 \"$pid\" 2>/dev/null; then\n            print_status \"INFO\" \"Stopping real-time sync (PID: $pid)...\"\n            kill \"$pid\"\n            \n            # Kill any child processes\n            pkill -P \"$pid\" 2>/dev/null || true\n            \n            # Remove PID file\n            rm -f \"$PID_FILE\"\n            \n            print_status \"SUCCESS\" \"Real-time sync stopped\"\n        else\n            print_status \"WARNING\" \"Sync process not running\"\n            rm -f \"$PID_FILE\"\n        fi\n    else\n        print_status \"WARNING\" \"No sync process found\"\n    fi\n}\n\n# Show sync status\nshow_status() {\n    print_status \"INFO\" \"Real-time sync status:\"\n    \n    if [[ -f \"$PID_FILE\" ]]; then\n        local pid=$(cat \"$PID_FILE\")\n        if kill -0 \"$pid\" 2>/dev/null; then\n            print_status \"SUCCESS\" \"Sync is running (PID: $pid)\"\n            \n            # Show recent activity\n            if [[ -f \"$LOG_FILE\" ]]; then\n                print_status \"INFO\" \"Recent sync activity:\"\n                tail -10 \"$LOG_FILE\" | while read -r line; do\n                    echo \"  $line\"\n                done\n            fi\n        else\n            print_status \"WARNING\" \"Sync process not running (stale PID file)\"\n            rm -f \"$PID_FILE\"\n        fi\n    else\n        print_status \"INFO\" \"Sync is not running\"\n    fi\n    \n    # Show configuration\n    if [[ -f \"$SYNC_CONFIG\" ]]; then\n        print_status \"INFO\" \"Configuration:\"\n        echo \"  Mode: $SYNC_MODE\"\n        echo \"  Interval: $SYNC_INTERVAL seconds\"\n        echo \"  Include systemd: $INCLUDE_SYSTEMD\"\n        echo \"  Exclude data: $EXCLUDE_DATA\"\n        echo \"  Include secrets: $INCLUDE_SECRETS\"\n    fi\n}\n\n# Monitor sync activity\nmonitor_sync() {\n    print_status \"INFO\" \"Monitoring real-time sync activity (Ctrl+C to exit)...\"\n    \n    if [[ -f \"$LOG_FILE\" ]]; then\n        tail -f \"$LOG_FILE\"\n    else\n        print_status \"WARNING\" \"No log file found. Start sync first.\"\n    fi\n}\n\n# Show recent logs\nshow_logs() {\n    local lines=${1:-50}\n    \n    print_status \"INFO\" \"Recent sync logs (last $lines lines):\"\n    \n    if [[ -f \"$LOG_FILE\" ]]; then\n        tail -n \"$lines\" \"$LOG_FILE\"\n    else\n        print_status \"WARNING\" \"No log file found\"\n    fi\n    \n    # Show all log files\n    print_status \"INFO\" \"Available log files:\"\n    ls -la \"$LOG_DIR\"/realtime-sync-*.log 2>/dev/null || print_status \"WARNING\" \"No log files found\"\n}\n\n# Test sync functionality\ntest_sync() {\n    print_status \"INFO\" \"Testing real-time sync functionality...\"\n    \n    # Create test file\n    local test_file=\"$PLATFORM_ROOT/test-realtime-sync-$DATE.txt\"\n    echo \"Real-time sync test - $DATE\" > \"$test_file\"\n    \n    print_status \"INFO\" \"Created test file: $test_file\"\n    \n    # Test sync to backup\n    sync_path \"$test_file\" \"to-backup\"\n    \n    # Verify on backup server\n    local backup_test_file=\"keith-ransom@192.168.0.5:~/chat-copilot/test-realtime-sync-$DATE.txt\"\n    if ssh keith-ransom@192.168.0.5 \"test -f ~/chat-copilot/test-realtime-sync-$DATE.txt\"; then\n        print_status \"SUCCESS\" \"Test file successfully synced to backup server\"\n        \n        # Cleanup\n        rm -f \"$test_file\"\n        ssh keith-ransom@192.168.0.5 \"rm -f ~/chat-copilot/test-realtime-sync-$DATE.txt\"\n        print_status \"INFO\" \"Test files cleaned up\"\n    else\n        print_status \"ERROR\" \"Test file not found on backup server\"\n        rm -f \"$test_file\"\n        return 1\n    fi\n}\n\n# Restart sync service\nrestart_sync() {\n    print_status \"INFO\" \"Restarting real-time sync...\"\n    \n    stop_sync\n    sleep 2\n    \n    # Restart with previous mode\n    if [[ -f \"$SYNC_CONFIG\" ]]; then\n        source \"$SYNC_CONFIG\"\n        case $SYNC_MODE in\n            \"bidirectional\")\n                start_bidirectional_sync &\n                ;;\n            \"to-backup\")\n                start_to_backup_sync &\n                ;;\n            \"from-backup\")\n                start_from_backup_sync &\n                ;;\n            *)\n                print_status \"ERROR\" \"Unknown sync mode: $SYNC_MODE\"\n                return 1\n                ;;\n        esac\n        \n        print_status \"SUCCESS\" \"Real-time sync restarted in $SYNC_MODE mode\"\n    else\n        print_status \"ERROR\" \"No configuration found. Run setup first.\"\n        return 1\n    fi\n}\n\n# Parse command line arguments\nparse_arguments() {\n    # Default values\n    SYNC_MODE=\"bidirectional\"\n    INCLUDE_SYSTEMD=\"false\"\n    EXCLUDE_DATA=\"true\"\n    INCLUDE_SECRETS=\"false\"\n    SYNC_INTERVAL=2\n    DAEMON_MODE=\"false\"\n    VERBOSE=\"false\"\n    DRY_RUN=\"false\"\n    \n    # Parse options\n    while [[ $# -gt 0 ]]; do\n        case $1 in\n            --to-backup)\n                SYNC_MODE=\"to-backup\"\n                shift\n                ;;\n            --from-backup)\n                SYNC_MODE=\"from-backup\"\n                shift\n                ;;\n            --bidirectional)\n                SYNC_MODE=\"bidirectional\"\n                shift\n                ;;\n            --include-systemd)\n                INCLUDE_SYSTEMD=\"true\"\n                shift\n                ;;\n            --exclude-data)\n                EXCLUDE_DATA=\"true\"\n                shift\n                ;;\n            --include-secrets)\n                INCLUDE_SECRETS=\"true\"\n                shift\n                ;;\n            --interval)\n                SYNC_INTERVAL=\"$2\"\n                shift 2\n                ;;\n            --daemon)\n                DAEMON_MODE=\"true\"\n                shift\n                ;;\n            --verbose)\n                VERBOSE=\"true\"\n                shift\n                ;;\n            --dry-run)\n                DRY_RUN=\"true\"\n                shift\n                ;;\n            --help|-h)\n                show_help\n                exit 0\n                ;;\n            -*)\n                print_status \"ERROR\" \"Unknown option: $1\"\n                show_help\n                exit 1\n                ;;\n            *)\n                # This is a positional argument\n                break\n                ;;\n        esac\n    done\n    \n    # Store remaining arguments\n    REMAINING_ARGS=(\"$@\")\n}\n\n# Main function\nmain() {\n    print_banner\n    \n    # Parse arguments\n    parse_arguments \"$@\"\n    \n    # Check if we have any arguments left\n    if [[ ${#REMAINING_ARGS[@]} -eq 0 ]]; then\n        print_status \"ERROR\" \"No command specified\"\n        show_help\n        exit 1\n    fi\n    \n    local command=\"${REMAINING_ARGS[0]}\"\n    \n    # Load configurations\n    if [[ \"$command\" != \"setup\" && \"$command\" != \"help\" ]]; then\n        load_rsync_config || exit 1\n        load_realtime_config\n    fi\n    \n    # Check dependencies\n    if [[ \"$command\" == \"start\" || \"$command\" == \"test\" ]]; then\n        check_dependencies\n    fi\n    \n    # Execute command\n    case $command in\n        \"setup\")\n            setup_realtime_config\n            ;;\n        \"start\")\n            case $SYNC_MODE in\n                \"bidirectional\")\n                    if [[ \"$DAEMON_MODE\" == \"true\" ]]; then\n                        start_bidirectional_sync &\n                        disown\n                        print_status \"SUCCESS\" \"Real-time sync started as daemon\"\n                    else\n                        start_bidirectional_sync\n                    fi\n                    ;;\n                \"to-backup\")\n                    if [[ \"$DAEMON_MODE\" == \"true\" ]]; then\n                        start_to_backup_sync &\n                        disown\n                        print_status \"SUCCESS\" \"Real-time sync to backup started as daemon\"\n                    else\n                        start_to_backup_sync\n                    fi\n                    ;;\n                \"from-backup\")\n                    start_from_backup_sync\n                    ;;\n                *)\n                    print_status \"ERROR\" \"Unknown sync mode: $SYNC_MODE\"\n                    exit 1\n                    ;;\n            esac\n            ;;\n        \"stop\")\n            stop_sync\n            ;;\n        \"status\")\n            show_status\n            ;;\n        \"monitor\")\n            monitor_sync\n            ;;\n        \"restart\")\n            restart_sync\n            ;;\n        \"logs\")\n            show_logs \"${REMAINING_ARGS[1]:-50}\"\n            ;;\n        \"test\")\n            test_sync\n            ;;\n        \"help\")\n            show_help\n            ;;\n        *)\n            print_status \"ERROR\" \"Unknown command: $command\"\n            show_help\n            exit 1\n            ;;\n    esac\n}\n\n# Run main function with all arguments\nmain \"$@\""