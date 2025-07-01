#!/bin/bash

# Frontend refresh script for web applications
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Refreshing frontend applications..."

# Refresh GenAI Stack frontend
if docker ps | grep -q "genai-stack_front-end"; then
    log "Refreshing GenAI Stack frontend..."
    docker restart genai-stack_front-end_1
    sleep 5
fi

# Check Chat Copilot frontend
if curl -s "http://100.123.10.72:11000" | grep -q "Chat Copilot"; then
    log "✅ Chat Copilot frontend accessible"
else
    log "⚠️ Chat Copilot frontend may need refresh"
fi

# Check other frontends
services=("11880:OpenWebUI" "11001:AutoGen" "11020:Perplexica" "8505:GenAI Stack")
for service in "${services[@]}"; do
    port="${service%%:*}"
    name="${service##*:}"
    if curl -s --connect-timeout 3 "http://100.123.10.72:$port" >/dev/null 2>&1; then
        log "✅ $name frontend responding"
    else
        log "⚠️ $name frontend not responding"
    fi
done

log "Frontend refresh complete"
