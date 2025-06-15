#!/bin/bash
# Port Scanner Restart Script with Nmap Functionality

echo "🔍 Restarting Port Scanner with Nmap..."

# Kill existing process
PIDFILE="/home/keith/chat-copilot/pids/port-scanner.pid"
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping existing Port Scanner process (PID: $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 3
    fi
    rm -f "$PIDFILE"
fi

# Ensure logs directory exists
mkdir -p /home/keith/chat-copilot/logs

# Start new process
echo "Starting Port Scanner..."
cd /home/keith/port-scanner-material-ui
nohup node backend/server.js > /home/keith/chat-copilot/logs/port-scanner.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PIDFILE"

echo "✅ Port Scanner started with PID $NEW_PID"

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 5

# Test nmap functionality
if curl -s "http://100.123.10.72:11010/nmap-status" | jq -e '.installed' > /dev/null 2>&1; then
    echo "✅ Port Scanner with nmap functionality is running at http://100.123.10.72:11010"
    echo "📊 Dashboard: http://100.123.10.72:11010/"
    echo "🔍 Nmap Status: http://100.123.10.72:11010/nmap-status"
    echo "🧪 Nmap Scan: http://100.123.10.72:11010/nmap-scan"
else
    echo "⚠️ Service started but nmap functionality test failed"
    echo "Check logs: tail -f /home/keith/chat-copilot/logs/port-scanner.log"
fi