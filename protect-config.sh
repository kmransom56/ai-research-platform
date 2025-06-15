#!/bin/bash
# Configuration Protection System
# Prevents unauthorized modification of critical configuration files

SCRIPT_DIR="/home/keith/chat-copilot"
LOG_FILE="$SCRIPT_DIR/logs/config-protection.log"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to create configuration templates
create_config_templates() {
    log "📝 Creating configuration templates..."
    
    local templates_dir="$SCRIPT_DIR/config-templates"
    mkdir -p "$templates_dir"
    
    # Frontend .env template
    cat > "$templates_dir/webapp.env.template" << 'EOF'
# Chat Copilot Frontend Configuration
# DO NOT MODIFY - This file is automatically managed
REACT_APP_BACKEND_URI=http://100.123.10.72:11000/
EOF
    
    # Port scanner frontend template
    cat > "$templates_dir/port-scanner-config.template" << 'EOF'
# Port Scanner Configuration Template
# API endpoints should use localhost:11010
# Replace any instances of:
# - localhost:10200 -> localhost:11010  
# - localhost:4500 -> localhost:11010
EOF
    
    # Webhook server configuration
    cat > "$templates_dir/webhook-config.template" << 'EOF'
# Webhook Server Configuration
# Port: 11002
# Health endpoint: /health
# Deploy endpoint: /deploy
EOF
    
    log "✅ Configuration templates created in $templates_dir"
}

# Function to set up file monitoring
setup_file_monitoring() {
    log "👁️ Setting up file monitoring..."
    
    # Create inotify monitoring script
    cat > "$SCRIPT_DIR/file-monitor.sh" << 'EOF'
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
EOF
    
    chmod +x "$SCRIPT_DIR/file-monitor.sh"
    log "✅ File monitoring script created"
}

# Function to create configuration backup system
setup_config_backup() {
    log "💾 Setting up configuration backup system..."
    
    # Create backup script
    cat > "$SCRIPT_DIR/backup-configs-auto.sh" << 'EOF'
#!/bin/bash
# Automatic Configuration Backup System

SCRIPT_DIR="/home/keith/chat-copilot"
BACKUP_DIR="$SCRIPT_DIR/config-backups-auto"
MAX_BACKUPS=20

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/config_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

# Backup critical files
cp "/home/keith/chat-copilot/webapp/.env" "$BACKUP_PATH/" 2>/dev/null || true
cp "/home/keith/chat-copilot/webapi/appsettings.json" "$BACKUP_PATH/" 2>/dev/null || true
cp "/home/keith/port-scanner-material-ui/src/index.html" "$BACKUP_PATH/" 2>/dev/null || true
cp "/home/keith/chat-copilot/startup-platform.sh" "$BACKUP_PATH/" 2>/dev/null || true

# Create metadata
cat > "$BACKUP_PATH/metadata.json" << EOL
{
    "timestamp": "$(date -Iseconds)",
    "backup_type": "automatic",
    "trigger": "config_protection_system"
}
EOL

# Cleanup old backups (keep only last MAX_BACKUPS)
cd "$BACKUP_DIR"
ls -t | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -rf

echo "Backup created: $BACKUP_PATH"
EOF
    
    chmod +x "$SCRIPT_DIR/backup-configs-auto.sh"
    log "✅ Automatic backup system created"
}

# Function to create configuration restore functionality
create_restore_system() {
    log "🔄 Creating configuration restore system..."
    
    cat > "$SCRIPT_DIR/restore-config.sh" << 'EOF'
#!/bin/bash
# Configuration Restore System
# Quickly restore known good configurations

SCRIPT_DIR="/home/keith/chat-copilot"
BACKUP_DIR="$SCRIPT_DIR/config-backups-auto"

usage() {
    echo "Usage: $0 [backup_name|latest]"
    echo "Available backups:"
    ls -1 "$BACKUP_DIR" 2>/dev/null | grep "config_" | sort -r | head -10
}

restore_config() {
    local backup_name=$1
    
    if [ "$backup_name" = "latest" ]; then
        backup_name=$(ls -1 "$BACKUP_DIR" | grep "config_" | sort -r | head -1)
    fi
    
    local backup_path="$BACKUP_DIR/$backup_name"
    
    if [ ! -d "$backup_path" ]; then
        echo "❌ Backup not found: $backup_name"
        usage
        exit 1
    fi
    
    echo "🔄 Restoring configuration from: $backup_name"
    
    # Stop services
    echo "🛑 Stopping services..."
    pkill -f "dotnet.*CopilotChatWebApi" || true
    pkill -f "node.*webhook-server" || true
    pkill -f "node.*port-scanner" || true
    
    # Restore files
    [ -f "$backup_path/.env" ] && cp "$backup_path/.env" "/home/keith/chat-copilot/webapp/"
    [ -f "$backup_path/appsettings.json" ] && cp "$backup_path/appsettings.json" "/home/keith/chat-copilot/webapi/"
    [ -f "$backup_path/index.html" ] && cp "$backup_path/index.html" "/home/keith/port-scanner-material-ui/src/"
    [ -f "$backup_path/startup-platform.sh" ] && cp "$backup_path/startup-platform.sh" "/home/keith/chat-copilot/"
    
    echo "✅ Configuration restored from $backup_name"
    echo "🚀 Restart services with: ./startup-platform.sh"
}

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

restore_config "$1"
EOF
    
    chmod +x "$SCRIPT_DIR/restore-config.sh"
    log "✅ Configuration restore system created"
}

# Function to setup cron jobs for protection
setup_protection_cron() {
    log "⏰ Setting up protection cron jobs..."
    
    # Create cron entry for configuration validation
    local cron_entry="*/15 * * * * $SCRIPT_DIR/validate-config.sh >> $SCRIPT_DIR/logs/cron-validation.log 2>&1"
    local backup_entry="0 */6 * * * $SCRIPT_DIR/backup-configs-auto.sh >> $SCRIPT_DIR/logs/cron-backup.log 2>&1"
    
    # Add to user crontab if not already present
    (crontab -l 2>/dev/null | grep -v "$SCRIPT_DIR/validate-config.sh"; echo "$cron_entry") | crontab -
    (crontab -l 2>/dev/null | grep -v "$SCRIPT_DIR/backup-configs-auto.sh"; echo "$backup_entry") | crontab -
    
    log "✅ Protection cron jobs configured:"
    log "   - Configuration validation: every 15 minutes"
    log "   - Automatic backups: every 6 hours"
}

# Function to create emergency reset
create_emergency_reset() {
    log "🚨 Creating emergency reset system..."
    
    cat > "$SCRIPT_DIR/emergency-reset.sh" << 'EOF'
#!/bin/bash
# Emergency Reset System
# Resets everything to known good state

SCRIPT_DIR="/home/keith/chat-copilot"

echo "🚨 EMERGENCY RESET - Restoring to last known good configuration"
echo "This will:"
echo "  1. Stop all services"
echo "  2. Reset configuration files"
echo "  3. Restart services"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Reset cancelled"
    exit 0
fi

echo "🛑 Stopping all services..."
pkill -f "dotnet.*CopilotChatWebApi" || true
pkill -f "node.*webhook-server" || true
pkill -f "node.*port-scanner" || true
pkill -f "health-monitor" || true

echo "🔄 Resetting configurations..."

# Reset frontend .env
echo "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" > "/home/keith/chat-copilot/webapp/.env"

# Reset port scanner frontend
sed -i 's/localhost:10200/localhost:11010/g' "/home/keith/port-scanner-material-ui/src/index.html"
sed -i 's/localhost:4500/localhost:11010/g' "/home/keith/port-scanner-material-ui/src/index.html"

echo "🚀 Restarting platform..."
"$SCRIPT_DIR/startup-platform.sh"

echo "✅ Emergency reset complete!"
echo "🌐 Access: http://100.123.10.72:11000/control-panel.html"
EOF
    
    chmod +x "$SCRIPT_DIR/emergency-reset.sh"
    log "✅ Emergency reset system created"
}

# Main protection setup
main() {
    log "🛡️ Setting up configuration protection system..."
    
    create_config_templates
    setup_file_monitoring
    setup_config_backup
    create_restore_system
    setup_protection_cron
    create_emergency_reset
    
    log "✅ Configuration protection system fully deployed!"
    log "📋 Available commands:"
    log "   - ./validate-config.sh - Validate and fix configurations"
    log "   - ./backup-configs-auto.sh - Create backup"
    log "   - ./restore-config.sh latest - Restore latest backup"
    log "   - ./emergency-reset.sh - Emergency reset to known good state"
    log "   - ./health-monitor.sh - Start continuous monitoring"
}

# Run setup
main "$@"