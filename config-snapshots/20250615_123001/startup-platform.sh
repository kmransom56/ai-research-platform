
#!/bin/bash
# AI Research Platform Robust Startup Script

set -e

echo "🚀 AI Research Platform Startup Script"
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

# Create logs directory
mkdir -p /home/keith/chat-copilot/logs

# Wait for network
echo "🌐 Checking network connectivity..."
until ping -c 1 8.8.8.8 &> /dev/null; do
    echo "Waiting for network..."
    sleep 2
done
echo "✅ Network is available"

# Wait for Ollama
wait_for_service "Ollama" "http://localhost:11434/api/version" 30

# Start AutoGen Studio
start_service "AutoGen Studio" \
    "source /home/keith/chat-copilot/autogen-env/bin/activate && /home/keith/chat-copilot/autogen-env/bin/python -m autogenstudio.ui --port 11001 --host 0.0.0.0" \
    "/home/keith/chat-copilot/pids/autogen-studio.pid"

# Start Webhook Server
start_service "Webhook Server" \
    "node /home/keith/chat-copilot/webhook-server.js" \
    "/home/keith/chat-copilot/pids/webhook-server.pid"

# Start Magentic-One Server
start_service "Magentic-One" \
    "/bin/bash -c 'source /home/keith/chat-copilot/autogen-env/bin/activate && python /home/keith/chat-copilot/magentic_one_server.py'" \
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

# Test endpoints
echo "🧪 Testing service endpoints..."
wait_for_service "AutoGen Studio" "http://100.123.10.72:11001" 10
wait_for_service "Webhook Server" "http://100.123.10.72:11002/health" 10
wait_for_service "Magentic-One" "http://100.123.10.72:11003/health" 10
wait_for_service "Port Scanner" "http://100.123.10.72:11010/nmap-status" 10
wait_for_service "Fortinet Manager Frontend" "http://100.123.10.72:3001" 10
wait_for_service "Fortinet Manager Backend" "http://100.123.10.72:5000" 10

echo "🎉 AI Research Platform startup complete!"
echo "📊 Platform Status:"
echo "   🌐 Control Panel: http://100.123.10.72:11000/control-panel.html"
echo "   🔧 Nginx Proxy Manager: http://100.123.10.72:11080 (admin@example.com / changeme)"
echo "   🔗 Proxy Gateway HTTP: http://100.123.10.72:11081/"
echo "   🤖 AutoGen Studio: http://100.123.10.72:11001"
echo "   🌟 Magentic-One: http://100.123.10.72:11003"
echo "   💻 VS Code Web: http://100.123.10.72:57081"
echo "   🔗 Webhook Server: http://100.123.10.72:11002/health"
echo "   🔍 Port Scanner: http://100.123.10.72:11010"
echo "   🛡️ Fortinet Manager: http://100.123.10.72:3001"

# Create status file
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
    }
}
EOF

echo "📋 Status saved to platform-status.json"
