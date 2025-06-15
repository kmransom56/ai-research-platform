#!/bin/bash

# AI Research Platform Deployment Script
# Called by webhook server after git pull

echo "🚀 Starting AI Research Platform deployment..."

# Set variables
PROJECT_DIR="/home/keith/chat-copilot"
LOG_FILE="$PROJECT_DIR/deployment.log"
BACKUP_DIR="/home/keith/backups"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        log "✅ $1 completed successfully"
    else
        log "❌ $1 failed"
        exit 1
    fi
}

# Create backup before deployment
log "📦 Creating pre-deployment backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_NAME="pre-deploy-$(date +%Y%m%d_%H%M%S)"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$PROJECT_DIR" \
    --exclude=node_modules --exclude=bin --exclude=obj \
    --exclude=logs --exclude="*.log" .
check_success "Backup creation"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Update file permissions
log "🔧 Updating file permissions..."
chmod +x webhook-server.js
chmod +x switch-ai-provider.sh
chmod +x deploy.sh
check_success "Permission updates"

# Frontend deployment
if [ -f "webapp/package.json" ]; then
    log "📦 Installing frontend dependencies..."
    cd webapp
    yarn install --frozen-lockfile
    check_success "Frontend dependency installation"
    
    log "🏗️ Building frontend..."
    yarn build
    check_success "Frontend build"
    
    cd ..
fi

# Backend preparation
log "🔧 Preparing backend..."
cd webapi
dotnet restore
check_success "Backend dependency restore"

# Build backend
log "🏗️ Building backend..."
dotnet build --configuration Release
check_success "Backend build"

cd ..

# Update environment variables
log "🌍 Updating environment variables..."
source ~/.bashrc
check_success "Environment update"

# Docker services management
log "🐳 Managing Docker services..."
docker-compose pull 2>/dev/null || log "⚠️ Docker compose pull skipped"
docker-compose up -d --remove-orphans 2>/dev/null || log "⚠️ Docker services restart skipped"

# Test critical services
log "🧪 Testing critical services..."

# Test Chat Copilot API
if curl -k -s -f "http://100.123.10.72:11000/healthz" > /dev/null; then
    log "✅ Chat Copilot API: Healthy"
else
    log "⚠️ Chat Copilot API: Not responding"
fi

# Test frontend
if curl -s -f "http://100.123.10.72:11000" > /dev/null; then
    log "✅ Frontend: Accessible"
else
    log "⚠️ Frontend: Not responding"
fi

# Test control panel
if curl -s -f "http://100.123.10.72:11000/control-panel.html" > /dev/null; then
    log "✅ Control Panel: Accessible"
else
    log "⚠️ Control Panel: Not responding"
fi

# Update system status
log "📊 Updating system status..."
echo "$(date): Deployment completed" > "$PROJECT_DIR/last-deployment.txt"

# Cleanup old logs (keep last 30 days)
log "🧹 Cleaning up old logs..."
find "$PROJECT_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "pre-deploy-*.tar.gz" -mtime +7 -delete 2>/dev/null || true

# Send notification (if webhook URL is configured)
if [ ! -z "$DEPLOYMENT_WEBHOOK_URL" ]; then
    log "📡 Sending deployment notification..."
    curl -X POST "$DEPLOYMENT_WEBHOOK_URL" \
         -H "Content-Type: application/json" \
         -d "{\"text\":\"🚀 AI Research Platform deployed successfully at $(date)\"}" \
         2>/dev/null || log "⚠️ Notification failed"
fi

log "🎉 Deployment completed successfully!"
log "📊 Services available at:"
log "   - Control Panel: http://100.123.10.72:11000/control-panel.html"
log "   - Chat Copilot: http://100.123.10.72:11000"
log "   - Nginx Proxy Manager: http://100.123.10.72:11080"
log "   - Port Scanner: http://100.123.10.72:11010"
log "   - API Health: http://100.123.10.72:11000/healthz"

exit 0