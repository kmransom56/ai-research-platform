#!/bin/bash
# AI Research Platform Status Checker

echo "📊 AI Research Platform Service Status"
echo "=" * 50

check_systemd_service() {
    local service_name=$1
    local service_type=$2
    
    if [ "$service_type" == "system" ]; then
        if systemctl is-active --quiet $service_name; then
            echo "✅ $service_name: Active"
        else
            echo "❌ $service_name: Inactive"
        fi
    else
        if systemctl --user is-active --quiet $service_name; then
            echo "✅ $service_name: Active"
        else
            echo "❌ $service_name: Inactive"
        fi
    fi
}

check_endpoint() {
    local name=$1
    local url=$2
    
    if curl -s --max-time 5 "$url" &> /dev/null; then
        echo "✅ $name: Accessible"
    else
        echo "❌ $name: Not accessible"
    fi
}

echo "🔧 Systemd Services:"
check_systemd_service "ollama-ai-platform" "system"
check_systemd_service "autogen-studio-ai-platform" "user"
check_systemd_service "webhook-server-ai-platform" "user"
check_systemd_service "chat-copilot-backend" "user"
check_systemd_service "chat-copilot-frontend" "user"

echo ""
echo "🌐 Service Endpoints:"
check_endpoint "Ollama API" "http://localhost:11434/api/version"
check_endpoint "AutoGen Studio" "http://100.123.10.72:8085"
check_endpoint "Webhook Server" "http://100.123.10.72:9001/health"
check_endpoint "Chat Copilot API" "https://100.123.10.72:40443/healthz"
check_endpoint "Chat Copilot Web" "http://100.123.10.72:10500"
check_endpoint "VS Code Web" "http://100.123.10.72:57081"

echo ""
echo "🦙 Ollama Models:"
ollama list 2>/dev/null || echo "❌ Ollama not accessible"
