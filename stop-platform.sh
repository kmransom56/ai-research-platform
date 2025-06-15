#!/bin/bash
# Comprehensive AI Research Platform Stop Script - ALL Services
# Safely stops all platform services in proper order

echo "🛑 Stopping Comprehensive AI Research Platform"
echo "=============================================="
echo "Timestamp: $(date)"

PLATFORM_DIR="/home/keith/chat-copilot"
PIDS_DIR="$PLATFORM_DIR/pids"

# Function to stop service by PID file
stop_service_by_pid() {
    local name=$1
    local pidfile=$2
    local process_pattern=$3
    
    echo "🛑 Stopping $name..."
    
    # Stop via PID file first
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "   Sending SIGTERM to PID $pid..."
            kill "$pid" 2>/dev/null || true
            sleep 3
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "   Force killing PID $pid..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$pidfile"
    fi
    
    # Kill any remaining processes by pattern
    if [ -n "$process_pattern" ]; then
        pkill -f "$process_pattern" 2>/dev/null || true
        sleep 1
        # Force kill remaining
        pkill -9 -f "$process_pattern" 2>/dev/null || true
    fi
    
    echo "✅ $name stopped"
}

# Function to stop Docker services
stop_docker_service() {
    local name=$1
    local compose_file=$2
    
    echo "🐳 Stopping Docker service: $name..."
    
    if [ -f "$compose_file" ]; then
        docker-compose -f "$compose_file" down 2>/dev/null || true
        echo "✅ $name Docker service stopped"
    else
        echo "⚠️ Docker compose file not found: $compose_file"
    fi
}

# ==============================================================================
# PHASE 1: STOP MONITORING SERVICES FIRST
# ==============================================================================

echo ""
echo "📊 PHASE 1: Stopping Monitoring Services"
echo "========================================"

stop_service_by_pid "Health Monitor" "$PIDS_DIR/health-monitor.pid" "health-monitor.sh"
stop_service_by_pid "File Monitor" "$PIDS_DIR/file-monitor.pid" "file-monitor.sh"

# ==============================================================================
# PHASE 2: STOP CORE AI RESEARCH PLATFORM SERVICES
# ==============================================================================

echo ""
echo "🤖 PHASE 2: Stopping Core AI Services"
echo "====================================="

stop_service_by_pid "Magentic-One Server" "$PIDS_DIR/magentic-one.pid" "magentic_one_server.py"
stop_service_by_pid "AutoGen Studio" "$PIDS_DIR/autogen-studio.pid" "autogenstudio"
stop_service_by_pid "Webhook Server" "$PIDS_DIR/webhook-server.pid" "webhook-server.js"
stop_service_by_pid "Chat Copilot Backend" "$PIDS_DIR/chat-copilot-backend.pid" "dotnet.*webapi"

# ==============================================================================
# PHASE 3: STOP NETWORK TOOLS
# ==============================================================================

echo ""
echo "🔍 PHASE 3: Stopping Network Tools"
echo "================================="

stop_service_by_pid "Port Scanner" "$PIDS_DIR/port-scanner.pid" "port-scanner.*server.js"

# ==============================================================================
# PHASE 4: STOP DOCKER SERVICES
# ==============================================================================

echo ""
echo "🐳 PHASE 4: Stopping Docker Services"
echo "==================================="

# Stop Nginx Proxy Manager
if [ -f "$PLATFORM_DIR/docker-compose.nginx-proxy-manager.yml" ]; then
    stop_docker_service "Nginx Proxy Manager" "$PLATFORM_DIR/docker-compose.nginx-proxy-manager.yml"
fi

# Stop Fortinet Manager Stack
if [ -f "/home/keith/fortinet-manager/docker-compose.yml" ]; then
    stop_docker_service "Fortinet Manager Stack" "/home/keith/fortinet-manager/docker-compose.yml"
fi

# ==============================================================================
# PHASE 5: CLEANUP PROCESSES & FILES
# ==============================================================================

echo ""
echo "🧹 PHASE 5: Cleanup Processes & Files"
echo "===================================="

# Kill any remaining AI platform processes
echo "🔍 Cleaning up remaining processes..."

# AutoGen and Python processes
pkill -f "autogenstudio" 2>/dev/null || true
pkill -f "magentic_one" 2>/dev/null || true
pkill -f "python.*autogen" 2>/dev/null || true

# Node.js processes
pkill -f "webhook-server" 2>/dev/null || true
pkill -f "port-scanner" 2>/dev/null || true

# .NET processes
pkill -f "dotnet.*webapi" 2>/dev/null || true

# Force kill if needed
sleep 2
pkill -9 -f "autogenstudio" 2>/dev/null || true
pkill -9 -f "magentic_one" 2>/dev/null || true
pkill -9 -f "webhook-server" 2>/dev/null || true

# Clean up PID files
echo "🗑️ Cleaning up PID files..."
rm -f "$PIDS_DIR"/*.pid 2>/dev/null || true

# Clean up log rotation
echo "📝 Rotating logs..."
if [ -d "$PLATFORM_DIR/logs" ]; then
    # Create backup directory for logs
    backup_dir="$PLATFORM_DIR/logs/backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Move current logs to backup
    for logfile in "$PLATFORM_DIR/logs"/*.log; do
        if [ -f "$logfile" ]; then
            mv "$logfile" "$backup_dir/" 2>/dev/null || true
        fi
    done
    
    echo "✅ Logs backed up to: $backup_dir"
fi

# ==============================================================================
# PHASE 6: SYSTEM CLEANUP
# ==============================================================================

echo ""
echo "🔧 PHASE 6: System Cleanup"
echo "========================="

# Stop systemd user services if they exist
echo "⚙️ Stopping systemd services..."
systemctl --user stop autogen-studio-ai-platform 2>/dev/null || true
systemctl --user stop webhook-server-ai-platform 2>/dev/null || true
systemctl --user stop chat-copilot-backend 2>/dev/null || true
systemctl --user stop chat-copilot-frontend 2>/dev/null || true

# Clean up temporary files
echo "🗑️ Cleaning temporary files..."
rm -f "$PLATFORM_DIR/platform-status.json" 2>/dev/null || true
rm -f "$PLATFORM_DIR/last-status-check.json" 2>/dev/null || true

# Deactivate UV environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🐍 Deactivating UV environment..."
    deactivate 2>/dev/null || true
fi

# ==============================================================================
# FINAL STATUS CHECK
# ==============================================================================

echo ""
echo "✅ AI Research Platform Shutdown Complete"
echo "========================================"

# Check for any remaining processes
remaining_procs=$(pgrep -f "autogenstudio|magentic_one|webhook-server|dotnet.*webapi" 2>/dev/null | wc -l)
if [ "$remaining_procs" -gt 0 ]; then
    echo "⚠️ Warning: $remaining_procs AI platform processes still running"
    echo "   Use 'pkill -9 -f \"autogenstudio|magentic_one|webhook-server\"' to force kill"
else
    echo "✅ All AI platform processes stopped cleanly"
fi

# Check port availability
echo ""
echo "🔍 Checking key ports are released:"
for port in 11000 11001 11002 11003 11010; do
    if ss -tuln | grep -q ":$port "; then
        echo "⚠️ Port $port still in use"
    else
        echo "✅ Port $port released"
    fi
done

echo ""
echo "📝 Shutdown Summary:"
echo "   • All AI platform services stopped"
echo "   • Docker services stopped"
echo "   • PID files cleaned"
echo "   • Logs rotated and backed up"
echo "   • System resources released"
echo ""
echo "🚀 Ready for restart with: ./startup-platform.sh"
echo "⏰ Shutdown completed at: $(date)"
