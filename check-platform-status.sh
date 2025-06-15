#!/bin/bash
# Comprehensive AI Research Platform Status Checker - ALL Services
# Port Range: 11000-12000

echo "📊 Comprehensive AI Research Platform Status Check"
echo "================================================="
echo "Timestamp: $(date)"
echo "Port Range: 11000-12000"
echo ""

# Check if process is running via PID file
check_pid_service() {
    local name=$1
    local pidfile=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "✅ $name: Running (PID: $pid)"
            return 0
        else
            echo "❌ $name: Not running (stale PID file)"
            return 1
        fi
    else
        echo "❌ $name: Not running (no PID file)"
        return 1
    fi
}

# Check systemd service
check_systemd_service() {
    local service_name=$1
    local service_type=${2:-user}
    
    if [ "$service_type" == "system" ]; then
        if systemctl is-active --quiet $service_name; then
            echo "✅ $service_name: Active (system)"
        else
            echo "❌ $service_name: Inactive (system)"
        fi
    else
        if systemctl --user is-active --quiet $service_name; then
            echo "✅ $service_name: Active (user)"
        else
            echo "❌ $service_name: Inactive (user)"
        fi
    fi
}

# Check HTTP endpoint
check_endpoint() {
    local name=$1
    local url=$2
    local port=$3
    
    if curl -s --max-time 5 "$url" &> /dev/null; then
        echo "✅ $name: Accessible (Port $port)"
    else
        echo "❌ $name: Not accessible (Port $port)"
    fi
}

# Check Docker service
check_docker_service() {
    local name=$1
    local container_pattern=$2
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_pattern"; then
        echo "✅ $name: Running (Docker)"
    else
        echo "❌ $name: Not running (Docker)"
    fi
}

# ==============================================================================
# CORE AI RESEARCH PLATFORM SERVICES (11000-11099)
# ==============================================================================

echo "🤖 CORE AI RESEARCH PLATFORM SERVICES"
echo "======================================"

check_endpoint "Chat Copilot Backend" "http://100.123.10.72:11000/healthz" "11000"
check_pid_service "Chat Copilot Backend (PID)" "/home/keith/chat-copilot/pids/chat-copilot-backend.pid"

check_endpoint "AutoGen Studio" "http://100.123.10.72:11001" "11001"
check_pid_service "AutoGen Studio (PID)" "/home/keith/chat-copilot/pids/autogen-studio.pid"

check_endpoint "Webhook Server" "http://100.123.10.72:11002/health" "11002"
check_pid_service "Webhook Server (PID)" "/home/keith/chat-copilot/pids/webhook-server.pid"

check_endpoint "Magentic-One Server" "http://100.123.10.72:11003/health" "11003"
check_pid_service "Magentic-One Server (PID)" "/home/keith/chat-copilot/pids/magentic-one.pid"

echo ""

# ==============================================================================
# NETWORK TOOLS & MONITORING (11100-11199)
# ==============================================================================

echo "🔍 NETWORK TOOLS & MONITORING"
echo "============================="

check_endpoint "Port Scanner" "http://100.123.10.72:11010/nmap-status" "11010"
check_pid_service "Port Scanner (PID)" "/home/keith/chat-copilot/pids/port-scanner.pid"

check_pid_service "Health Monitor" "/home/keith/chat-copilot/pids/health-monitor.pid"
check_pid_service "File Monitor" "/home/keith/chat-copilot/pids/file-monitor.pid"

echo ""

# ==============================================================================
# INFRASTRUCTURE SERVICES
# ==============================================================================

echo "🏗️ INFRASTRUCTURE SERVICES"
echo "=========================="

check_endpoint "Nginx Proxy Manager" "http://100.123.10.72:11080" "11080"
check_endpoint "Nginx HTTP Gateway" "http://100.123.10.72:11081" "11081"
check_endpoint "Nginx HTTPS Gateway" "http://100.123.10.72:11082" "11082"

check_endpoint "Ollama LLM Server" "http://localhost:11434/api/version" "11434"

echo ""

# ==============================================================================
# DEVELOPMENT TOOLS
# ==============================================================================

echo "🛠️ DEVELOPMENT TOOLS"
echo "==================="

check_endpoint "VS Code Web" "http://100.123.10.72:57081" "57081"
check_endpoint "Chat Copilot Frontend (Dev)" "http://100.123.10.72:3000" "3000"

echo ""

# ==============================================================================
# EXTERNAL SERVICES & DOCKER CONTAINERS
# ==============================================================================

echo "🐳 EXTERNAL SERVICES & DOCKER"
echo "============================="

check_endpoint "Fortinet Manager Frontend" "http://100.123.10.72:3001" "3001"
check_endpoint "Fortinet Manager Backend" "http://100.123.10.72:5000" "5000"

echo ""
echo "🤖 AI RESEARCH SERVICES"
echo "======================"

check_endpoint "Perplexica Search AI" "http://100.123.10.72:3999" "3999"
check_endpoint "SearXNG Search Engine" "http://100.123.10.72:4000" "4000"
check_endpoint "OpenWebUI" "http://100.123.10.72:8080/api/config" "8080"

# Check Docker containers
if command -v docker &> /dev/null; then
    echo ""
    echo "📋 Docker Container Status:"
    check_docker_service "Nginx Proxy Manager" "nginx-proxy-manager"
    check_docker_service "Fortinet Manager Stack" "fortinet"
    check_docker_service "Perplexica Search AI" "perplexica-app"
    check_docker_service "SearXNG Search Engine" "perplexica-searxng"
    check_docker_service "OpenWebUI" "open-webui"
    check_docker_service "VS Code Web" "openvscode"
fi

echo ""

# ==============================================================================
# SYSTEMD SERVICES
# ==============================================================================

echo "🔧 SYSTEMD SERVICES"
echo "=================="

check_systemd_service "ollama-ai-platform" "system"
check_systemd_service "autogen-studio-ai-platform" "user"
check_systemd_service "webhook-server-ai-platform" "user"
check_systemd_service "chat-copilot-backend" "user"
check_systemd_service "chat-copilot-frontend" "user"

echo ""

# ==============================================================================
# AI MODELS & CAPABILITIES
# ==============================================================================

echo "🦙 AI MODELS & CAPABILITIES"
echo "=========================="

if curl -s --max-time 5 "http://localhost:11434/api/version" &> /dev/null; then
    echo "Available Ollama Models:"
    ollama list 2>/dev/null | head -10
else
    echo "❌ Ollama not accessible - cannot list models"
fi

echo ""

# ==============================================================================
# PLATFORM SUMMARY
# ==============================================================================

echo "📋 PLATFORM SUMMARY"
echo "==================="

# Count running services
running_count=0
total_count=0

# Core services
for port in 11000 11001 11002 11003; do
    ((total_count++))
    if curl -s --max-time 2 "http://100.123.10.72:$port" &> /dev/null; then
        ((running_count++))
    fi
done

# Infrastructure
for port in 11080 11434; do
    ((total_count++))
    if curl -s --max-time 2 "http://100.123.10.72:$port" &> /dev/null || curl -s --max-time 2 "http://localhost:$port" &> /dev/null; then
        ((running_count++))
    fi
done

echo "📊 Service Status: $running_count/$total_count core services running"
echo "🔗 Main Control Panel: http://100.123.10.72:11000/control-panel.html"
echo "⏰ Status check completed at: $(date)"

# Create status summary file
cat > /home/keith/chat-copilot/last-status-check.json << EOF
{
    "timestamp": "$(date -Iseconds)",
    "running_services": $running_count,
    "total_services": $total_count,
    "platform_health": "$([ $running_count -ge $((total_count * 2 / 3)) ] && echo "healthy" || echo "degraded")",
    "main_endpoints": {
        "control_panel": "http://100.123.10.72:11000/control-panel.html",
        "autogen_studio": "http://100.123.10.72:11001",
        "magentic_one": "http://100.123.10.72:11003"
    }
}
EOF

echo "📝 Status summary saved to last-status-check.json"
