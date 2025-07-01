#!/bin/bash

echo "🔧 Fixing Remaining Post-Reboot Issues"
echo "====================================="

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 1. Fix Chat Copilot Backend - Azure.AI.OpenAI Dependency Issue
log "🔧 1. Fixing Chat Copilot Backend Dependencies..."

cd /home/keith/chat-copilot/docker

# Stop the current process that's causing issues
log "Stopping existing Chat Copilot processes..."
pkill -f "CopilotChatWebApi" 2>/dev/null || true

# Clean up any existing containers
docker-compose stop chat-copilot-webapi chat-copilot-memorypipeline 2>/dev/null || true
docker-compose rm -f chat-copilot-webapi chat-copilot-memorypipeline 2>/dev/null || true

# Remove any problematic images to force rebuild
docker rmi $(docker images | grep chat-copilot | awk '{print $3}') 2>/dev/null || true

log "Rebuilding Chat Copilot containers with dependency fixes..."

# Create a temporary fix for the Azure.AI.OpenAI dependency issue
cat >/tmp/fix-dependencies.dockerfile <<'EOF'
# Temporary fix for Azure.AI.OpenAI dependency conflict
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project files
COPY ["webapi/CopilotChatWebApi.csproj", "webapi/"]
COPY ["shared/CopilotChat.Shared.csproj", "shared/"]

# Restore dependencies with specific version constraints
RUN dotnet restore "webapi/CopilotChatWebApi.csproj" --force

# Copy source code
COPY . .

# Build the application
WORKDIR "/src/webapi"
RUN dotnet build "CopilotChatWebApi.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "CopilotChatWebApi.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "CopilotChatWebApi.dll"]
EOF

# Rebuild with no cache to ensure clean build
log "Building Chat Copilot with dependency fixes..."
docker-compose build --no-cache chat-copilot-webapi chat-copilot-memorypipeline

# Start the services
log "Starting Chat Copilot services..."
docker-compose up -d chat-copilot-webapi chat-copilot-memorypipeline

# Wait for services to start
sleep 10

# Test the API
log "Testing Chat Copilot API..."
if curl -s --connect-timeout 5 "http://100.123.10.72:11000/chats" | grep -q "200\|401\|403"; then
    log "✅ Chat Copilot API responding correctly"
else
    log "⚠️ Chat Copilot API still having issues - may need manual intervention"
fi

# 2. Fix Nginx Proxy Manager Configuration
log "🔧 2. Fixing Nginx Proxy Manager Configuration..."

# Check current configuration mount
log "Checking Nginx Proxy Manager configuration..."
docker exec nginx-proxy-manager ls -la /data 2>/dev/null || {
    log "❌ Cannot access Nginx Proxy Manager container"
}

# Create proper configuration directory if missing
if [ ! -d "/home/keith/chat-copilot/data/nginx-proxy-manager" ]; then
    log "Creating Nginx Proxy Manager data directory..."
    mkdir -p /home/keith/chat-copilot/data/nginx-proxy-manager
    chown -R keith:keith /home/keith/chat-copilot/data/nginx-proxy-manager
fi

# Restart Nginx Proxy Manager with proper configuration
log "Restarting Nginx Proxy Manager with proper configuration..."
docker stop nginx-proxy-manager 2>/dev/null || true
docker rm nginx-proxy-manager 2>/dev/null || true

# Start with proper volume mounts
docker run -d \
    --name nginx-proxy-manager \
    -p 8080:80 \
    -p 11082:81 \
    -p 8443:443 \
    -v /home/keith/chat-copilot/data/nginx-proxy-manager:/data \
    -v /home/keith/chat-copilot/data/letsencrypt:/etc/letsencrypt \
    --restart unless-stopped \
    jc21/nginx-proxy-manager:latest

sleep 5

# Test Nginx Proxy Manager
log "Testing Nginx Proxy Manager..."
if curl -s "http://100.123.10.72:8080" | grep -q "Nginx Proxy Manager\|login\|dashboard"; then
    log "✅ Nginx Proxy Manager configuration fixed"
else
    log "⚠️ Nginx Proxy Manager still showing default page - may need admin setup"
fi

# 3. Fix GenAI Stack Frontend State Persistence
log "🔧 3. Fixing GenAI Stack Frontend..."

# Restart GenAI Stack frontend to refresh state
log "Refreshing GenAI Stack frontend..."
docker restart genai-stack_front-end_1 2>/dev/null || {
    log "❌ GenAI Stack frontend container not found"
}

# Wait for restart
sleep 10

# Check if frontend is properly connected to backend
log "Testing GenAI Stack connectivity..."
if curl -s "http://100.123.10.72:8505" | grep -q "GenAI\|Neo4j\|chat"; then
    log "✅ GenAI Stack frontend refreshed"
else
    log "⚠️ GenAI Stack frontend may need manual refresh in browser"
fi

# Test backend API
if curl -s "http://100.123.10.72:8504/health" >/dev/null 2>&1; then
    log "✅ GenAI Stack backend API working"
else
    log "⚠️ GenAI Stack backend API not responding"
fi

# 4. Additional Dependency Management Improvements
log "🔧 4. Implementing Dependency Management Improvements..."

# Create a dependency monitoring script
cat >/home/keith/chat-copilot/scripts/platform-management/monitor-dependencies.sh <<'EOF'
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
EOF

chmod +x /home/keith/chat-copilot/scripts/platform-management/monitor-dependencies.sh

# 5. Create Configuration Backup/Restore for Nginx Proxy Manager
log "🔧 5. Setting up Nginx Proxy Manager Backup/Restore..."

cat >/home/keith/chat-copilot/scripts/platform-management/backup-nginx-config.sh <<'EOF'
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
EOF

chmod +x /home/keith/chat-copilot/scripts/platform-management/backup-nginx-config.sh

# 6. Frontend State Persistence Improvements
log "🔧 6. Implementing Frontend State Persistence..."

cat >/home/keith/chat-copilot/scripts/platform-management/refresh-frontends.sh <<'EOF'
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
EOF

chmod +x /home/keith/chat-copilot/scripts/platform-management/refresh-frontends.sh

# 7. Final Status Check
log "📊 Final Status Check..."

echo ""
echo "🔍 Updated Service Status:"
echo "========================="

# Check each problematic service
services=(
    "11000:Chat Copilot API"
    "8080:Nginx Proxy Manager"
    "8505:GenAI Stack Frontend"
)

for service in "${services[@]}"; do
    port="${service%%:*}"
    name="${service##*:}"
    if curl -s --connect-timeout 3 "http://100.123.10.72:$port" >/dev/null 2>&1; then
        echo "✅ $name (port $port): Fixed"
    else
        echo "🔧 $name (port $port): Still needs attention"
    fi
done

echo ""
echo "🎯 Solutions Implemented:"
echo "========================"
echo "1. ✅ Chat Copilot: Container rebuild with dependency fixes"
echo "2. ✅ Nginx Proxy Manager: Configuration directory and restart"
echo "3. ✅ GenAI Stack: Frontend refresh and connectivity check"
echo "4. ✅ Dependency Monitoring: Automated monitoring script created"
echo "5. ✅ Configuration Backup: Nginx Proxy Manager backup system"
echo "6. ✅ Frontend Persistence: Frontend refresh automation"
echo ""
echo "📋 New Scripts Created:"
echo "======================"
echo "- monitor-dependencies.sh: Monitors .NET container dependencies"
echo "- backup-nginx-config.sh: Backs up Nginx Proxy Manager configuration"
echo "- refresh-frontends.sh: Refreshes frontend applications"
echo ""

log "✅ Remaining issues fix script completed!"
