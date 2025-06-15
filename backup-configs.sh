#!/bin/bash

# Chat Copilot Configuration Backup Script
# This script creates local backups of critical configuration files

BACKUP_DIR="/home/keith/chat-copilot/config-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="config_backup_${TIMESTAMP}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create timestamped backup directory
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"

echo "Creating configuration backup: $BACKUP_PATH"

# Backup critical configuration files
echo "Backing up webapp/.env..."
cp -p /home/keith/chat-copilot/webapp/.env "$BACKUP_PATH/" 2>/dev/null || echo "Warning: webapp/.env not found"

echo "Backing up webapi/appsettings.json..."
cp -p /home/keith/chat-copilot/webapi/appsettings.json "$BACKUP_PATH/"

echo "Backing up webapi/appsettings.Azure.json..."
cp -p /home/keith/chat-copilot/webapi/appsettings.Azure.json "$BACKUP_PATH/" 2>/dev/null || echo "Warning: appsettings.Azure.json not found"

echo "Backing up scripts directory..."
cp -rp /home/keith/chat-copilot/scripts/ "$BACKUP_PATH/"

echo "Backing up startup scripts..."
cp -p /home/keith/chat-copilot/startup-platform.sh "$BACKUP_PATH/" 2>/dev/null || echo "Warning: startup-platform.sh not found"
cp -p /home/keith/chat-copilot/start-all-services.sh "$BACKUP_PATH/" 2>/dev/null || echo "Warning: start-all-services.sh not found"
cp -p /home/keith/chat-copilot/auto_startup_manager.py "$BACKUP_PATH/" 2>/dev/null || echo "Warning: auto_startup_manager.py not found"

echo "Backing up Docker configuration..."
cp -p /home/keith/chat-copilot/docker/docker-compose.yaml "$BACKUP_PATH/" 2>/dev/null || echo "Warning: docker-compose.yaml not found"

echo "Backing up CLAUDE.md..."
cp -p /home/keith/chat-copilot/CLAUDE.md "$BACKUP_PATH/" 2>/dev/null || echo "Warning: CLAUDE.md not found"

# Backup cron configuration
echo "Backing up cron configuration..."
crontab -l > "$BACKUP_PATH/crontab.txt" 2>/dev/null || echo "Warning: No crontab found"

# Backup systemd services
echo "Backing up systemd services..."
mkdir -p "$BACKUP_PATH/systemd"
cp -p /etc/systemd/system/chat-copilot-*.service "$BACKUP_PATH/systemd/" 2>/dev/null || echo "Warning: No chat-copilot systemd services found"

# Create a restore script
cat > "$BACKUP_PATH/restore.sh" << 'EOF'
#!/bin/bash
# Restore script for Chat Copilot configurations
# Usage: ./restore.sh

BACKUP_DIR="$(dirname "$0")"
CHAT_COPILOT_DIR="/home/keith/chat-copilot"

echo "Restoring configurations from: $BACKUP_DIR"

# Restore webapp/.env
if [ -f "$BACKUP_DIR/.env" ]; then
    echo "Restoring webapp/.env..."
    cp -p "$BACKUP_DIR/.env" "$CHAT_COPILOT_DIR/webapp/"
fi

# Restore webapi/appsettings.json
if [ -f "$BACKUP_DIR/appsettings.json" ]; then
    echo "Restoring webapi/appsettings.json..."
    cp -p "$BACKUP_DIR/appsettings.json" "$CHAT_COPILOT_DIR/webapi/"
fi

# Restore webapi/appsettings.Azure.json
if [ -f "$BACKUP_DIR/appsettings.Azure.json" ]; then
    echo "Restoring webapi/appsettings.Azure.json..."
    cp -p "$BACKUP_DIR/appsettings.Azure.json" "$CHAT_COPILOT_DIR/webapi/"
fi

# Restore scripts directory
if [ -d "$BACKUP_DIR/scripts" ]; then
    echo "Restoring scripts directory..."
    cp -rp "$BACKUP_DIR/scripts" "$CHAT_COPILOT_DIR/"
fi

# Restore startup scripts
if [ -f "$BACKUP_DIR/startup-platform.sh" ]; then
    echo "Restoring startup-platform.sh..."
    cp -p "$BACKUP_DIR/startup-platform.sh" "$CHAT_COPILOT_DIR/"
fi

if [ -f "$BACKUP_DIR/start-all-services.sh" ]; then
    echo "Restoring start-all-services.sh..."
    cp -p "$BACKUP_DIR/start-all-services.sh" "$CHAT_COPILOT_DIR/"
fi

if [ -f "$BACKUP_DIR/auto_startup_manager.py" ]; then
    echo "Restoring auto_startup_manager.py..."
    cp -p "$BACKUP_DIR/auto_startup_manager.py" "$CHAT_COPILOT_DIR/"
fi

# Restore Docker configuration
if [ -f "$BACKUP_DIR/docker-compose.yaml" ]; then
    echo "Restoring docker-compose.yaml..."
    cp -p "$BACKUP_DIR/docker-compose.yaml" "$CHAT_COPILOT_DIR/docker/"
fi

# Restore CLAUDE.md
if [ -f "$BACKUP_DIR/CLAUDE.md" ]; then
    echo "Restoring CLAUDE.md..."
    cp -p "$BACKUP_DIR/CLAUDE.md" "$CHAT_COPILOT_DIR/"
fi

# Restore cron configuration
if [ -f "$BACKUP_DIR/crontab.txt" ]; then
    echo "Restoring cron configuration..."
    echo "Note: You may need to manually restore crontab with: crontab $BACKUP_DIR/crontab.txt"
fi

# Restore systemd services
if [ -d "$BACKUP_DIR/systemd" ]; then
    echo "Restoring systemd services..."
    echo "Note: You may need to manually copy services to /etc/systemd/system/ with sudo"
fi

echo "Restore completed!"
EOF

chmod +x "$BACKUP_PATH/restore.sh"

# Create a summary file
echo "Configuration Backup Summary" > "$BACKUP_PATH/backup_summary.txt"
echo "============================" >> "$BACKUP_PATH/backup_summary.txt"
echo "Date: $(date)" >> "$BACKUP_PATH/backup_summary.txt"
echo "Backup Location: $BACKUP_PATH" >> "$BACKUP_PATH/backup_summary.txt"
echo "" >> "$BACKUP_PATH/backup_summary.txt"
echo "Files backed up:" >> "$BACKUP_PATH/backup_summary.txt"
find "$BACKUP_PATH" -type f -name "*.json" -o -name "*.env" -o -name "*.sh" -o -name "*.py" -o -name "*.md" | sort >> "$BACKUP_PATH/backup_summary.txt"

# Cleanup old backups (keep last 10)
echo "Cleaning up old backups (keeping last 10)..."
cd "$BACKUP_DIR"
ls -t | tail -n +11 | xargs rm -rf 2>/dev/null || true

echo ""
echo "Backup completed successfully!"
echo "Location: $BACKUP_PATH"
echo "To restore: $BACKUP_PATH/restore.sh"
echo ""
echo "Summary:"
cat "$BACKUP_PATH/backup_summary.txt"