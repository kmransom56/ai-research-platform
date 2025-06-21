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
