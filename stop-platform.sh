#!/bin/bash
echo "🛑 Stopping AI Research Platform..."

# Stop services
if [ -f "/home/keith/chat-copilot/pids/autogen-studio.pid" ]; then
    kill $(cat "/home/keith/chat-copilot/pids/autogen-studio.pid") 2>/dev/null || true
    rm -f "/home/keith/chat-copilot/pids/autogen-studio.pid"
fi

if [ -f "/home/keith/chat-copilot/pids/webhook-server.pid" ]; then
    kill $(cat "/home/keith/chat-copilot/pids/webhook-server.pid") 2>/dev/null || true
    rm -f "/home/keith/chat-copilot/pids/webhook-server.pid"
fi

# Stop any running processes
pkill -f "autogenstudio" || true
pkill -f "webhook-server.js" || true

echo "✅ AI Research Platform stopped"
