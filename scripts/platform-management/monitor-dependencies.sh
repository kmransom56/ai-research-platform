#!/bin/bash

# Dependency monitoring script for .NET containers
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Checking .NET container dependencies..."

# Check Chat Copilot containers
if docker ps | grep -q "chat-copilot-webapi"; then
    log "✅ Chat Copilot WebAPI container running"
else
    log "❌ Chat Copilot WebAPI container not running"
    # Auto-restart if needed
    cd /home/keith/chat-copilot/docker
    docker-compose up -d chat-copilot-webapi
fi

# Check for dependency conflicts in logs
docker logs chat-copilot-webapi 2>&1 | tail -20 | grep -i "error\|exception\|failed" || {
    log "✅ No recent errors in Chat Copilot logs"
}

log "Dependency check complete"
