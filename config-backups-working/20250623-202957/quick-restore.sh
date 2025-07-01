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
