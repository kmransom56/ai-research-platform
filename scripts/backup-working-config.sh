#!/bin/bash

# AI Research Platform - Working Configuration Backup Script
# Creates a comprehensive backup of the current working state

set -e

# Configuration
BACKUP_BASE_DIR="/home/keith/chat-copilot/config-backups-working"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_DIR="$BACKUP_BASE_DIR/$TIMESTAMP"

echo "🔄 Creating working configuration backup at: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to log actions
log() {
    echo "✅ $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$BACKUP_DIR/backup.log"
}

log "Starting backup process"

# 1. Backup Nginx configurations
log "Backing up Nginx configurations..."
mkdir -p "$BACKUP_DIR/nginx"
sudo cp -r /etc/nginx/sites-available/ "$BACKUP_DIR/nginx/"
sudo cp -r /etc/nginx/sites-enabled/ "$BACKUP_DIR/nginx/"
sudo cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx/"
sudo chown -R keith:keith "$BACKUP_DIR/nginx"

# 2. Backup SSL certificates and permissions
log "Backing up SSL certificates..."
mkdir -p "$BACKUP_DIR/ssl"
sudo cp -r /etc/ssl/tailscale/ "$BACKUP_DIR/ssl/" 2>/dev/null || true
sudo cp -r /var/lib/tailscale/certs/ "$BACKUP_DIR/ssl/tailscale-system/" 2>/dev/null || true
sudo chown -R keith:keith "$BACKUP_DIR/ssl"

# Store certificate permissions
sudo ls -la /etc/ssl/tailscale/ > "$BACKUP_DIR/ssl/permissions-etc-ssl.txt" 2>/dev/null || true
sudo ls -la /var/lib/tailscale/certs/ > "$BACKUP_DIR/ssl/permissions-var-lib.txt" 2>/dev/null || true

# 3. Backup Docker configurations and states
log "Backing up Docker configurations..."
mkdir -p "$BACKUP_DIR/docker"
cp docker-compose.yml "$BACKUP_DIR/docker/" 2>/dev/null || true
cp -r docker-configs/ "$BACKUP_DIR/docker/" 2>/dev/null || true

# Save current container states
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" > "$BACKUP_DIR/docker/container-states.txt"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" > "$BACKUP_DIR/docker/images.txt"

# 4. Backup application configurations
log "Backing up application configurations..."
mkdir -p "$BACKUP_DIR/app-configs"
cp webapi/appsettings.json "$BACKUP_DIR/app-configs/" 2>/dev/null || true
cp webapp/.env "$BACKUP_DIR/app-configs/" 2>/dev/null || true
cp -r nginx-configs/ "$BACKUP_DIR/app-configs/" 2>/dev/null || true

# 5. Backup service status and processes
log "Capturing service states..."
mkdir -p "$BACKUP_DIR/services"
systemctl status nginx > "$BACKUP_DIR/services/nginx-status.txt" 2>/dev/null || true
ps aux | grep -E "(dotnet|node|ollama)" > "$BACKUP_DIR/services/processes.txt" 2>/dev/null || true
netstat -tlnp > "$BACKUP_DIR/services/ports.txt" 2>/dev/null || true

# 6. Backup Ollama models
log "Backing up Ollama model list..."
ollama list > "$BACKUP_DIR/services/ollama-models.txt" 2>/dev/null || true

# 7. Create service startup commands log
log "Creating service startup log..."
cat > "$BACKUP_DIR/services/startup-commands.txt" << 'EOF'
# Commands to restore services after reboot

# 1. Start backend API
cd /home/keith/chat-copilot/webapi && dotnet run --urls http://0.0.0.0:11000 &

# 2. Start frontend
cd /home/keith/chat-copilot/webapp && REACT_APP_BACKEND_URI=http://100.123.10.72:11000/ yarn start &

# 3. Ensure Docker containers are running
docker ps --filter "status=exited" --format "{{.Names}}" | xargs -r docker start

# 4. Check nginx status
sudo systemctl status nginx
sudo systemctl reload nginx

# 5. Verify Ollama is running
sudo systemctl status ollama || ollama serve &

# 6. Test key endpoints
curl -k -s -o /dev/null -w "%{http_code}" https://100.123.10.72:10443/hub
curl -k -s -o /dev/null -w "%{http_code}" https://100.123.10.72:10443/openwebui/
curl -k -s -o /dev/null -w "%{http_code}" https://100.123.10.72:10443/neo4j/
EOF

# 8. Create restoration metadata
log "Creating restoration metadata..."
cat > "$BACKUP_DIR/restore-info.json" << EOF
{
  "backup_date": "$(date -Iseconds)",
  "backup_user": "$(whoami)",
  "backup_host": "$(hostname)",
  "platform_directory": "$(pwd)",
  "key_services": {
    "nginx_enabled": true,
    "backend_port": 11000,
    "frontend_port": 3000,
    "ssl_domain": "100.123.10.72:10443",
    "ollama_models": $(ollama list | wc -l)
  }
}
EOF

# 9. Create quick restore script
log "Creating quick restore script..."
cat > "$BACKUP_DIR/quick-restore.sh" << 'EOF'
#!/bin/bash
# Quick restore script - run this after reboot to restore working state

BACKUP_DIR="$(dirname "$0")"
cd /home/keith/chat-copilot

echo "🔄 Restoring working configuration from backup..."

# Restore SSL certificates with proper permissions
echo "Restoring SSL certificates..."
sudo mkdir -p /etc/ssl/tailscale
sudo cp -r "$BACKUP_DIR/ssl/tailscale/"* /etc/ssl/tailscale/ 2>/dev/null || true
sudo chmod 644 /etc/ssl/tailscale/*.crt 2>/dev/null || true
sudo chmod 640 /etc/ssl/tailscale/*.key 2>/dev/null || true
sudo chgrp www-data /etc/ssl/tailscale/*.key 2>/dev/null || true

# Restore nginx configuration
echo "Restoring nginx configuration..."
sudo cp "$BACKUP_DIR/nginx/sites-available/ai-hub.conf" /etc/nginx/sites-available/
sudo nginx -t && sudo systemctl reload nginx

# Start application services
echo "Starting application services..."
cd webapi && dotnet run --urls http://0.0.0.0:11000 > /tmp/backend.log 2>&1 &
sleep 5
cd ../webapp && REACT_APP_BACKEND_URI=http://100.123.10.72:11000/ yarn start > /tmp/frontend.log 2>&1 &

# Start Docker containers
echo "Starting Docker containers..."
docker start $(docker ps -aq --filter "status=exited") 2>/dev/null || true

# Wait and test
sleep 10
echo "Testing services..."
curl -k -s -o /dev/null -w "Hub: %{http_code}\n" https://100.123.10.72:10443/hub
curl -k -s -o /dev/null -w "OpenWebUI: %{http_code}\n" https://100.123.10.72:10443/openwebui/
curl -k -s -o /dev/null -w "Neo4j: %{http_code}\n" https://100.123.10.72:10443/neo4j/

echo "✅ Restore complete! Check the URLs above for 200 status codes."
EOF

chmod +x "$BACKUP_DIR/quick-restore.sh"

# 10. Create symlink to latest backup
log "Creating symlink to latest backup..."
rm -f "$BACKUP_BASE_DIR/latest"
ln -sf "$TIMESTAMP" "$BACKUP_BASE_DIR/latest"

# Final summary
log "Backup completed successfully!"
echo ""
echo "📦 Backup Summary:"
echo "   Location: $BACKUP_DIR"
echo "   Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo ""
echo "🚀 To restore after reboot:"
echo "   cd $BACKUP_BASE_DIR/latest"
echo "   ./quick-restore.sh"
echo ""
echo "🔗 Quick access:"
echo "   $BACKUP_BASE_DIR/latest/quick-restore.sh"

# Save backup info to main directory
echo "$TIMESTAMP" > "$BACKUP_BASE_DIR/last-backup.txt"
echo "Last backup: $(date)" >> /home/keith/chat-copilot/CLAUDE.md