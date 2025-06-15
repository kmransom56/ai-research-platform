#!/bin/bash
echo "📊 AI Research Platform Status"
echo "=" * 40

check_service() {
    local name=$1
    local url=$2
    if curl -s --max-time 3 "$url" &> /dev/null; then
        echo "✅ $name: Running"
    else
        echo "❌ $name: Stopped"
    fi
}

check_service "Ollama" "http://localhost:11434/api/version"
check_service "AutoGen Studio" "http://100.123.10.72:8085"
check_service "Webhook Server" "http://100.123.10.72:9001/health"
check_service "VS Code Web" "http://100.123.10.72:57081"
check_service "Chat Copilot" "http://100.123.10.72:10500"

echo ""
echo "📋 Process Information:"
ps aux | grep -E "(autogenstudio|webhook-server|ollama)" | grep -v grep || echo "No platform processes found"

if [ -f "/home/keith/chat-copilot/platform-status.json" ]; then
    echo ""
    echo "📊 Last Startup Status:"
    cat "/home/keith/chat-copilot/platform-status.json"
fi
