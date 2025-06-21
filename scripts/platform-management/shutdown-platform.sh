#!/bin/bash
# AI Research Platform Graceful Shutdown Script

set -e

PLATFORM_DIR="/home/keith/chat-copilot"
PIDS_DIR="$PLATFORM_DIR/pids"

echo "🛑 Shutting down AI Research Platform..."
echo "Current time: $(date)"

# Function to stop service by PID file
stop_service() {
    local name=$1
    local pidfile=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $name (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null || true
            
            # Wait for graceful shutdown
            local attempts=0
            while kill -0 "$pid" 2>/dev/null && [ $attempts -lt 10 ]; do
                sleep 1
                ((attempts++))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "   Force killing $name..."
                kill -KILL "$pid" 2>/dev/null || true
            fi
            
            echo "✅ Stopped $name"
        fi
        rm -f "$pidfile"
    else
        echo "⚠️ No PID file for $name"
    fi
}

echo ""
echo "🛑 Stopping Caddy Reverse Proxy..."
cd "$PLATFORM_DIR"
if docker-compose -f docker-compose.caddy.yml ps | grep -q "Up"; then
    docker-compose -f docker-compose.caddy.yml down
    echo "✅ Caddy stopped"
else
    echo "⚠️ Caddy not running"
fi

echo ""
echo "🛑 Stopping Core AI Services..."
stop_service "Chat Copilot Backend" "$PIDS_DIR/chat-copilot-backend.pid"
stop_service "AutoGen Studio" "$PIDS_DIR/autogen-studio.pid"
stop_service "Webhook Server" "$PIDS_DIR/webhook-server.pid"
stop_service "Magentic-One Server" "$PIDS_DIR/magentic-one.pid"

echo ""
echo "🛑 Stopping Network Tools..."
stop_service "Port Scanner" "$PIDS_DIR/port-scanner.pid"
stop_service "Health Monitor" "$PIDS_DIR/health-monitor.pid"
stop_service "File Monitor" "$PIDS_DIR/file-monitor.pid"

echo ""
echo "🛑 Stopping Docker Services..."
if [ -f "$PLATFORM_DIR/docker-compose.nginx-proxy-manager.yml" ]; then
    docker-compose -f "$PLATFORM_DIR/docker-compose.nginx-proxy-manager.yml" down 2>/dev/null || true
fi

if [ -f "/home/keith/fortinet-manager/docker-compose.yml" ]; then
    cd /home/keith/fortinet-manager
    docker-compose down 2>/dev/null || true
fi

echo ""
echo "🛑 Cleaning up..."
# Clean up any remaining PID files
rm -f "$PIDS_DIR"/*.pid 2>/dev/null || true

echo ""
echo "✅ AI Research Platform shutdown complete!"
echo "   To restart: ./startup-platform.sh"
echo "   To start at boot: sudo systemctl start ai-platform"
