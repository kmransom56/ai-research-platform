
#!/bin/bash
# Comprehensive AI Research Platform Startup Script - ALL Services
# Standardized Port Range: 11000-12000

set -e

# Script configuration
PLATFORM_DIR="/home/keith/chat-copilot"
LOGS_DIR="$PLATFORM_DIR/logs"
PIDS_DIR="$PLATFORM_DIR/pids"

echo "🚀 Comprehensive AI Research Platform Startup Script"
echo "Current time: $(date)"
echo "User: $(whoami)"
echo "Working directory: $(pwd)"
echo "Platform directory: $PLATFORM_DIR"

# Create required directories
mkdir -p "$LOGS_DIR" "$PIDS_DIR"

# Function to wait for service with better error handling
wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    echo "⏳ Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 5 "$url" &> /dev/null; then
            echo "✅ $name is ready (attempt $attempt/$max_attempts)"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts - waiting for $name..."
        sleep 3
        ((attempt++))
    done
    echo "⚠️ $name not ready after $max_attempts attempts"
    return 1
}

# Function to start service with UV environment support
start_service() {
    local name=$1
    local command=$2
    local pidfile=$3
    local use_uv=${4:-false}
    
    echo "🚀 Starting $name..."
    
    # Kill existing process if running
    if [ -f "$pidfile" ]; then
        local old_pid=$(cat "$pidfile")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "   Stopping existing $name process (PID: $old_pid)..."
            kill "$old_pid" 2>/dev/null || true
            sleep 3
        fi
        rm -f "$pidfile"
    fi
    
    # Prepare command with UV if needed
    if [ "$use_uv" = "true" ]; then
        command="cd $PLATFORM_DIR && uv run $command"
    fi
    
    # Start new process
    local logfile="$LOGS_DIR/$(echo "$name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]').log"
    nohup bash -c "$command" > "$logfile" 2>&1 &
    local new_pid=$!
    echo $new_pid > "$pidfile"
    echo "✅ Started $name with PID $new_pid (log: $logfile)"
    sleep 2
}

# Function to start Docker service
start_docker_service() {
    local name=$1
    local compose_file=$2
    local health_url=$3
    
    echo "🐳 Starting Docker service: $name..."
    
    if [ -f "$compose_file" ]; then
        if docker-compose -f "$compose_file" ps | grep -q "Up"; then
            echo "✅ $name already running"
        else
            docker-compose -f "$compose_file" up -d
            echo "✅ $name Docker stack started"
            if [ -n "$health_url" ]; then
                wait_for_service "$name" "$health_url" 20
            fi
        fi
    else
        echo "⚠️ Docker compose file not found: $compose_file"
    fi
}

# ==============================================================================
# PHASE 1: SYSTEM PREREQUISITES
# ==============================================================================

echo ""
echo "🔧 PHASE 1: System Prerequisites"
echo "=================================="

# Wait for network
echo "🌐 Checking network connectivity..."
until ping -c 1 8.8.8.8 &> /dev/null; do
    echo "   Waiting for network..."
    sleep 2
done
echo "✅ Network is available"

# Check UV installation
if ! command -v uv &> /dev/null; then
    echo "⚠️ UV not found - installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi
echo "✅ UV package manager ready"

# Setup UV environment for AI services
echo "🐍 Setting up UV environment..."
cd "$PLATFORM_DIR"
if [ ! -d ".venv" ]; then
    uv venv --python 3.11
fi
source .venv/bin/activate
echo "✅ UV environment activated"

# ==============================================================================
# PHASE 2: INFRASTRUCTURE SERVICES
# ==============================================================================

echo ""
echo "🏗️  PHASE 2: Infrastructure Services"
echo "===================================="

# Wait for Ollama (critical dependency)
wait_for_service "Ollama LLM Server" "http://localhost:11434/api/version" 30

# Start Nginx Proxy Manager (if Docker available)
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    start_docker_service "Nginx Proxy Manager" \
        "$PLATFORM_DIR/docker-compose.nginx-proxy-manager.yml" \
        "http://100.123.10.72:11080"
fi

# ==============================================================================
# PHASE 3: CORE AI RESEARCH PLATFORM SERVICES
# ==============================================================================

echo ""
echo "🤖 PHASE 3: Core AI Research Platform Services"
echo "=============================================="

# Start Chat Copilot Backend (Port 11000)
start_service "Chat Copilot Backend" \
    "cd $PLATFORM_DIR/webapi && dotnet run --urls http://0.0.0.0:11000" \
    "$PIDS_DIR/chat-copilot-backend.pid"

# Start AutoGen Studio with UV (Port 11001) 
start_service "AutoGen Studio" \
    "python -m autogenstudio.ui --port 11001 --host 0.0.0.0" \
    "$PIDS_DIR/autogen-studio.pid" \
    "true"

# Start Webhook Server (Port 11002)
start_service "Webhook Server" \
    "node $PLATFORM_DIR/webhook-server.js" \
    "$PIDS_DIR/webhook-server.pid"

# Start Magentic-One Server with UV (Port 11003)
start_service "Magentic-One Server" \
    "python $PLATFORM_DIR/magentic_one_server.py" \
    "$PIDS_DIR/magentic-one.pid" \
    "true"

# ==============================================================================
# PHASE 4: NETWORK TOOLS & MONITORING
# ==============================================================================

echo ""
echo "🔍 PHASE 4: Network Tools & Monitoring"
echo "======================================"

# Start Port Scanner (Port 11010)
if [ -d "/home/keith/port-scanner-material-ui" ]; then
    start_service "Port Scanner" \
        "cd /home/keith/port-scanner-material-ui && node backend/server.js" \
        "$PIDS_DIR/port-scanner.pid"
else
    echo "⚠️ Port Scanner directory not found - skipping"
fi

# Start Health Monitor
start_service "Health Monitor" \
    "$PLATFORM_DIR/health-monitor.sh" \
    "$PIDS_DIR/health-monitor.pid"

# Start File Monitor (Configuration Protection)
if [ -f "$PLATFORM_DIR/file-monitor.sh" ]; then
    start_service "File Monitor" \
        "$PLATFORM_DIR/file-monitor.sh" \
        "$PIDS_DIR/file-monitor.pid"
fi

# ==============================================================================
# PHASE 5: EXTERNAL DOCKER SERVICES
# ==============================================================================

echo ""
echo "🐳 PHASE 5: External Docker Services"
echo "===================================="

# Start Fortinet Manager Stack
if [ -f "/home/keith/fortinet-manager/docker-compose.yml" ]; then
    start_docker_service "Fortinet Manager Stack" \
        "/home/keith/fortinet-manager/docker-compose.yml" \
        "http://100.123.10.72:3001"
fi

# Check VS Code Web (External Docker Container)
if curl -s --max-time 5 "http://100.123.10.72:57081" &> /dev/null; then
    echo "✅ VS Code Web already running"
else
    echo "⚠️ VS Code Web not responding - may need manual start"
fi

# Check Perplexica Search AI
if curl -s --max-time 5 "http://100.123.10.72:3999" &> /dev/null; then
    echo "✅ Perplexica Search AI already running"
else
    echo "⚠️ Perplexica Search AI not responding"
fi

# ==============================================================================
# PHASE 6: SERVICE HEALTH VERIFICATION
# ==============================================================================

echo ""
echo "🧪 PHASE 6: Service Health Verification"
echo "======================================="

# Give services time to initialize
sleep 5

# Test all endpoints systematically
declare -A services=(
    ["Chat Copilot Backend"]="http://100.123.10.72:11000/healthz"
    ["AutoGen Studio"]="http://100.123.10.72:11001"
    ["Webhook Server"]="http://100.123.10.72:11002/health"
    ["Magentic-One Server"]="http://100.123.10.72:11003/health"
    ["Port Scanner"]="http://100.123.10.72:11010/nmap-status"
    ["Nginx Proxy Manager"]="http://100.123.10.72:11080"
    ["Fortinet Manager"]="http://100.123.10.72:3001"
    ["VS Code Web"]="http://100.123.10.72:57081"
    ["Ollama LLM"]="http://localhost:11434/api/version"
)

echo "Testing service endpoints..."
for service_name in "${!services[@]}"; do
    url="${services[$service_name]}"
    if curl -s --max-time 5 "$url" &> /dev/null; then
        echo "✅ $service_name - OK"
    else
        echo "❌ $service_name - FAILED ($url)"
    fi
done

# ==============================================================================
# PHASE 7: PLATFORM STATUS REPORT
# ==============================================================================

echo ""
echo "📊 PHASE 7: Platform Status Report"
echo "=================================="

echo "🎉 AI Research Platform Startup Complete!"
echo ""
echo "🌐 SERVICE ENDPOINTS:"
echo "   🏠 Chat Copilot: http://100.123.10.72:11000/control-panel.html"
echo "   🤖 AutoGen Studio: http://100.123.10.72:11001"
echo "   🌟 Magentic-One: http://100.123.10.72:11003"
echo "   🔗 Webhook Server: http://100.123.10.72:11002/health"
echo "   🔍 Port Scanner: http://100.123.10.72:11010"
echo ""
echo "🔧 INFRASTRUCTURE:"
echo "   🔧 Nginx Proxy Manager: http://100.123.10.72:11080"
echo "   🔗 Proxy Gateway HTTP: http://100.123.10.72:11081"
echo "   🔒 Proxy Gateway HTTPS: http://100.123.10.72:11082"
echo ""
echo "🛠️ DEVELOPMENT TOOLS:"
echo "   💻 VS Code Web: http://100.123.10.72:57081"
echo "   🛡️ Fortinet Manager: http://100.123.10.72:3001"
echo "   🔍 Perplexica Search: http://100.123.10.72:3999"
echo ""
echo "🦙 AI BACKEND:"
echo "   🦙 Ollama LLM Server: http://localhost:11434"

# Create comprehensive status file
cat > "$PLATFORM_DIR/platform-status.json" << EOF
{
    "platform": "AI Research Platform",
    "version": "2.0",
    "startup_time": "$(date -Iseconds)",
    "port_range": "11000-12000",
    "environment": "UV Python + Docker",
    "services": {
        "core_ai": {
            "chat_copilot_backend": {
                "port": 11000,
                "status": "$(curl -s http://100.123.10.72:11000/healthz &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:11000"
            },
            "autogen_studio": {
                "port": 11001,
                "status": "$(curl -s http://100.123.10.72:11001 &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:11001"
            },
            "webhook_server": {
                "port": 11002,
                "status": "$(curl -s http://100.123.10.72:11002/health &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:11002"
            },
            "magentic_one": {
                "port": 11003,
                "status": "$(curl -s http://100.123.10.72:11003/health &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:11003"
            }
        },
        "network_tools": {
            "port_scanner": {
                "port": 11010,
                "status": "$(curl -s http://100.123.10.72:11010 &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:11010"
            }
        },
        "infrastructure": {
            "nginx_proxy_manager": {
                "ports": [11080, 11081, 11082],
                "status": "$(curl -s http://100.123.10.72:11080 &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:11080"
            },
            "ollama": {
                "port": 11434,
                "status": "$(curl -s http://localhost:11434/api/version &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://localhost:11434"
            }
        },
        "development": {
            "vscode_web": {
                "port": 57081,
                "status": "$(curl -s http://100.123.10.72:57081 &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:57081"
            },
            "fortinet_manager": {
                "port": 3001,
                "status": "$(curl -s http://100.123.10.72:3001 &> /dev/null && echo 'running' || echo 'stopped')",
                "url": "http://100.123.10.72:3001"
            }
        }
    }
}
EOF

echo ""
echo "📋 Comprehensive status saved to platform-status.json"
echo "📝 Service logs available in: $LOGS_DIR"
echo "🔢 Process IDs saved in: $PIDS_DIR"
echo ""
echo "✅ AI Research Platform is ready for use!"
