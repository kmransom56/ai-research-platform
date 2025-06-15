#!/bin/bash
# Emergency Reset System
# Resets everything to known good state

SCRIPT_DIR="/home/keith/chat-copilot"

echo "🚨 EMERGENCY RESET - Restoring to last known good configuration"
echo "This will:"
echo "  1. Stop all services"
echo "  2. Reset configuration files"
echo "  3. Restart services"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Reset cancelled"
    exit 0
fi

echo "🛑 Stopping all services..."
pkill -f "dotnet.*CopilotChatWebApi" || true
pkill -f "node.*webhook-server" || true
pkill -f "node.*port-scanner" || true
pkill -f "health-monitor" || true

echo "🔄 Resetting configurations..."

# Reset frontend .env
echo "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" > "/home/keith/chat-copilot/webapp/.env"

# Reset port scanner frontend
sed -i 's/localhost:10200/localhost:11010/g' "/home/keith/port-scanner-material-ui/src/index.html"
sed -i 's/localhost:4500/localhost:11010/g' "/home/keith/port-scanner-material-ui/src/index.html"

echo "🚀 Restarting platform..."
"$SCRIPT_DIR/startup-platform.sh"

echo "✅ Emergency reset complete!"
echo "🌐 Access: http://100.123.10.72:11000/control-panel.html"
