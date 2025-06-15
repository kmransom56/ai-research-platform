#!/bin/bash
# AI Research Platform Robust Startup Script with UV
# Updated ports: 11000-12000 range | Python env: uv

set -e

echo "🚀 AI Research Platform Startup Script (UV Enhanced)"
echo "Current time: $(date)"
echo "User: $(whoami)"
echo "Working directory: $(pwd)"

# Function to wait for service
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=$3
    local attempt=1
    
    echo "⏳ Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 5 "$url" &> /dev/null; then
            echo "✅ $name is ready (attempt $attempt/$max_attempts)"
            return 0
        fi
        echo "Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    echo "⚠️ $name not ready after $max_attempts attempts"
    return 1
}

# Function to start service in background
start_service() {
    local name=$1
    local command=$2
    local pidfile=$3
    
    echo "🚀 Starting $name..."
    
    # Kill existing process if running
    if [ -f "$pidfile" ]; then
        local old_pid=$(cat "$pidfile")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "Stopping existing $name process..."
            kill "$old_pid" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$pidfile"
    fi
    
    # Start new process
    nohup $command > "/home/keith/chat-copilot/logs/$name.log" 2>&1 &
    local new_pid=$!
    echo $new_pid > "$pidfile"
    echo "✅ Started $name with PID $new_pid"
}

# Ensure UV is available
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create directories
mkdir -p /home/keith/chat-copilot/logs
mkdir -p /home/keith/chat-copilot/pids

# Wait for network
echo "🌐 Checking network connectivity..."
until ping -c 1 8.8.8.8 &> /dev/null; do
    echo "Waiting for network..."
    sleep 2
done
echo "✅ Network is available"

# Wait for Ollama
wait_for_service "Ollama" "http://localhost:11434/api/version" 30

# Setup UV environment if needed
if [ ! -f ".venv/pyvenv.cfg" ]; then
    echo "📦 Creating UV virtual environment..."
    uv venv
    echo "📥 Installing Python dependencies with UV..."
    uv add autogenstudio fastapi uvicorn
fi

# Start AutoGen Studio with UV
start_service "AutoGen Studio" \
    "uv run autogenstudio ui --port 11001 --host 0.0.0.0" \
    "/home/keith/chat-copilot/pids/autogen-studio.pid"

# Start Webhook Server (Node.js)
start_service "Webhook Server" \
    "node /home/keith/chat-copilot/webhook-server.js" \
    "/home/keith/chat-copilot/pids/webhook-server.pid"

# Start Magentic-One Server with UV
start_service "Magentic-One" \
    "uv run python /home/keith/chat-copilot/magentic_one_server.py" \
    "/home/keith/chat-copilot/pids/magentic-one.pid"

# Start Port Scanner
start_service "Port Scanner" \
    "/bin/bash -c 'cd /home/keith/port-scanner-material-ui && node backend/server.js'" \
    "/home/keith/chat-copilot/pids/port-scanner.pid"

# Start Fortinet Manager Docker Stack
echo "🚀 Starting Fortinet Manager Docker stack..."
if ! sudo docker-compose -f /home/keith/fortinet-manager/docker-compose.yml ps | grep -q "Up"; then
    sudo docker-compose -f /home/keith/fortinet-manager/docker-compose.yml up -d
    echo "✅ Fortinet Manager Docker stack started"
else
    echo "✅ Fortinet Manager Docker stack already running"
fi

# Wait for services to be ready
sleep 5

# Test endpoints with updated ports
echo "🧪 Testing service endpoints..."
wait_for_service "AutoGen Studio" "http://100.123.10.72:11001" 10
wait_for_service "Webhook Server" "http://100.123.10.72:11002/health" 10
wait_for_service "Magentic-One" "http://100.123.10.72:11003/health" 10
wait_for_service "Port Scanner" "http://100.123.10.72:11010/nmap-status" 10
wait_for_service "Fortinet Manager Frontend" "http://100.123.10.72:3001" 10
wait_for_service "Fortinet Manager Backend" "http://100.123.10.72:5000" 10

echo "🎉 AI Research Platform startup complete!"
echo "📊 Platform Status (Standardized Ports):"
echo "   🌐 Control Panel: http://100.123.10.72:11000/control-panel.html"
echo "   🔧 Nginx Proxy Manager: http://100.123.10.72:11080 (admin@example.com / changeme)"
echo "   🔗 Proxy Gateway HTTP: http://100.123.10.72:11081/"
echo "   🤖 AutoGen Studio: http://100.123.10.72:11001"
echo "   🌟 Magentic-One: http://100.123.10.72:11003"
echo "   💻 VS Code Web: http://100.123.10.72:57081"
echo "   🔗 Webhook Server: http://100.123.10.72:11002/health"
echo "   🔍 Port Scanner: http://100.123.10.72:11010"
echo "   🛡️ Fortinet Manager: http://100.123.10.72:3001"

# Create status file with corrected ports
cat > /home/keith/chat-copilot/platform-status.json << EOF
{
    "startup_time": "$(date -Iseconds)",
    "services": {
        "ollama": "$(curl -s http://localhost:11434/api/version &> /dev/null && echo 'running' || echo 'stopped')",
        "autogen_studio": "$(curl -s http://100.123.10.72:11001 &> /dev/null && echo 'running' || echo 'stopped')",
        "magentic_one": "$(curl -s http://100.123.10.72:11003/health &> /dev/null && echo 'running' || echo 'stopped')",
        "webhook_server": "$(curl -s http://100.123.10.72:11002/health &> /dev/null && echo 'running' || echo 'stopped')",
        "nginx_proxy_manager": "$(curl -s http://100.123.10.72:11080 &> /dev/null && echo 'running' || echo 'stopped')",
        "vscode_web": "$(curl -s http://100.123.10.72:57081 &> /dev/null && echo 'running' || echo 'stopped')",
        "port_scanner": "$(curl -s http://100.123.10.72:11010 &> /dev/null && echo 'running' || echo 'stopped')",
        "fortinet_manager": "$(curl -s http://100.123.10.72:3001 &> /dev/null && echo 'running' || echo 'stopped')"
    },
    "port_configuration": {
        "chat_copilot_backend": 11000,
        "autogen_studio": 11001,
        "webhook_server": 11002,
        "magentic_one": 11003,
        "port_scanner": 11010,
        "nginx_proxy_manager_web": 11080,
        "nginx_proxy_manager_http": 11081,
        "nginx_proxy_manager_https": 11082,
        "ollama": 11434
    },
    "python_environment": "uv",
    "configuration_version": "2.0-standardized"
}
EOF

echo "📋 Status saved to platform-status.json"
echo ""
echo "🔄 UV Environment Commands:"
echo "   📦 Add dependency: uv add <package>"
echo "   🐍 Run Python: uv run python"
echo "   🚀 Run script: uv run <command>"
echo ""
echo "✨ Configuration drift prevention: All ports standardized to 11000-12000 range"