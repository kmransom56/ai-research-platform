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
