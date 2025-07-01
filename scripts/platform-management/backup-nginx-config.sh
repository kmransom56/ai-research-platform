#!/bin/bash

# Nginx Proxy Manager configuration backup script
BACKUP_DIR="/home/keith/chat-copilot/config-backups-working/nginx-proxy-manager"
DATE=$(date +%Y%m%d-%H%M%S)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Backing up Nginx Proxy Manager configuration..."

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup configuration data
if [ -d "/home/keith/chat-copilot/data/nginx-proxy-manager" ]; then
    cp -r /home/keith/chat-copilot/data/nginx-proxy-manager/* "$BACKUP_DIR/$DATE/" 2>/dev/null || true
    log "✅ Nginx Proxy Manager configuration backed up to $BACKUP_DIR/$DATE"
else
    log "❌ Nginx Proxy Manager data directory not found"
fi

# Keep only last 5 backups
ls -t "$BACKUP_DIR" | tail -n +6 | xargs -I {} rm -rf "$BACKUP_DIR/{}" 2>/dev/null || true

log "Backup complete"
