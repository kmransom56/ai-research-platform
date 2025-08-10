#!/bin/bash

# AI Restaurant Network Management System
# Quick start script for non-technical users

set -e

echo "🍽️  AI RESTAURANT NETWORK MANAGEMENT SYSTEM"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Do not run this script as root!"
    echo "   Run as regular user: ./start-restaurant-network-system.sh"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    ! nc -z localhost "$1" >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to start on port $port..."
    while ! nc -z localhost "$port" >/dev/null 2>&1; do
        if [ $attempt -gt $max_attempts ]; then
            echo "❌ $service_name failed to start after $max_attempts attempts"
            return 1
        fi
        sleep 2
        ((attempt++))
    done
    echo "✅ $service_name is running on port $port"
}

# Check prerequisites
echo "🔍 Checking system requirements..."

# Check Docker
if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   sudo apt-get update && sudo apt-get install docker.io"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker:"
    echo "   sudo systemctl start docker"
    exit 1
fi

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3:"
    echo "   sudo apt-get install python3 python3-pip"
    exit 1
fi

# Check .NET (optional)
if ! command_exists dotnet; then
    echo "⚠️  .NET not found. Some features may be limited."
    echo "   Install .NET 8.0 for full functionality"
fi

# Check Node.js (optional)  
if ! command_exists node; then
    echo "⚠️  Node.js not found. Web interface may be limited."
    echo "   Install Node.js 18+ for full web features"
fi

echo "✅ System requirements check passed"
echo ""

# Check configuration
echo "🔧 Checking configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "📝 Creating .env from template..."
        cp .env.template .env
        echo "⚠️  Please edit .env file with your Meraki API key before continuing"
        echo "   Required: MERAKI_API_KEY=your_api_key_here"
        read -p "Press Enter after you've configured .env file..."
    else
        echo "❌ No .env configuration found. Please create .env file with:"
        echo "   MERAKI_API_KEY=your_api_key_here"
        echo "   NEO4J_PASSWORD=your_secure_password"
        exit 1
    fi
fi

# Source environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if API key is configured
if [ -z "$MERAKI_API_KEY" ] || [ "$MERAKI_API_KEY" = "your_api_key_here" ]; then
    echo "❌ Meraki API key not configured in .env file"
    echo "   Please set: MERAKI_API_KEY=your_actual_api_key"
    exit 1
fi

echo "✅ Configuration check passed"
echo ""

# Start Neo4j database
echo "🗄️  Starting Neo4j database..."

NEO4J_PASSWORD=${NEO4J_PASSWORD:-"password"}

if ! docker ps | grep -q restaurant-neo4j; then
    # Check if container exists but is stopped
    if docker ps -a | grep -q restaurant-neo4j; then
        echo "🔄 Starting existing Neo4j container..."
        docker start restaurant-neo4j
    else
        echo "🆕 Creating new Neo4j container..."
        docker run --name restaurant-neo4j \
            --restart unless-stopped \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/$NEO4J_PASSWORD \
            -e NEO4J_PLUGINS='["apoc"]' \
            -e NEO4J_server_memory_heap_initial__size=2g \
            -e NEO4J_server_memory_heap_max__size=4g \
            -v neo4j_restaurant_data:/data \
            -d neo4j:5.23-community
    fi
else
    echo "✅ Neo4j already running"
fi

wait_for_service 7474 "Neo4j"
echo ""

# Setup Python environment
echo "🐍 Setting up Python environment..."

if [ ! -d "neo4j-env" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv neo4j-env
fi

source neo4j-env/bin/activate

# Install/update Python dependencies
if [ ! -f "neo4j-env/.installed" ] || [ requirements.txt -nt neo4j-env/.installed ]; then
    echo "📥 Installing Python dependencies..."
    
    # Create requirements if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        cat > requirements.txt << EOF
neo4j>=5.0.0
requests>=2.28.0
flask>=2.2.0
python-dotenv>=0.19.0
numpy>=1.21.0
speechrecognition>=3.10.0
pyttsx3>=2.90
asyncio-mqtt>=0.11.0
aiohttp>=3.8.0
dataclasses-json>=0.5.7
EOF
    fi
    
    pip install --upgrade pip
    pip install -r requirements.txt
    touch neo4j-env/.installed
else
    echo "✅ Python dependencies already installed"
fi

echo ""

# Start network agents
echo "🤖 Starting AI network agents..."

# Check if network-agents directory exists
if [ ! -d "network-agents" ]; then
    echo "❌ network-agents directory not found"
    echo "   Please run this script from the chat-copilot directory"
    exit 1
fi

cd network-agents

# Create logs directory
mkdir -p logs

# Function to start background service
start_service() {
    local script=$1
    local service_name=$2
    local log_file=$3
    
    if pgrep -f "$script" > /dev/null; then
        echo "✅ $service_name already running"
    else
        echo "🚀 Starting $service_name..."
        nohup python3 "$script" > "logs/$log_file" 2>&1 &
        sleep 2
    fi
}

# Start core services
start_service "landing-page-server.py" "Landing Page Server" "landing-page.log"
start_service "restaurant-equipment-voice-interface.py" "Restaurant Voice Interface" "restaurant-voice.log" 
start_service "speech-web-interface.py" "IT Voice Interface" "it-voice.log"
start_service "network_topology_dashboard.py" "Network Topology Dashboard" "topology.log"

# Wait for services to start
sleep 5

# Check service status
echo ""
echo "🔍 Checking service status..."

check_service() {
    local port=$1
    local service_name=$2
    local url=$3
    
    if nc -z localhost "$port" >/dev/null 2>&1; then
        echo "✅ $service_name - http://localhost:$port$url"
    else
        echo "❌ $service_name - Port $port not responding"
    fi
}

check_service 11040 "Landing Page Dashboard" ""
check_service 11032 "Restaurant Voice Interface" ""
check_service 11031 "IT Voice Interface" ""
check_service 11050 "Network Topology Dashboard" ""
check_service 7474 "Neo4j Database" ""

echo ""

# Initial data load (optional)
echo "📊 Network data loading..."

if [ ! -f ".initial_load_done" ]; then
    echo "🔄 Loading initial network topology from Meraki API..."
    echo "   This may take a few minutes..."
    
    if timeout 300 python3 load-real-meraki-topology.py > logs/initial-load.log 2>&1; then
        echo "✅ Initial network topology loaded successfully"
        touch .initial_load_done
        
        # Start endpoint discovery in background
        echo "🔍 Starting endpoint device discovery (running in background)..."
        nohup python3 discover-endpoint-devices.py > logs/endpoint-discovery.log 2>&1 &
    else
        echo "⚠️  Initial load timed out or failed. Check logs/initial-load.log"
        echo "   The system will work but may have limited data initially"
    fi
else
    echo "✅ Network topology already loaded (delete .initial_load_done to reload)"
fi

cd ..

# Health check
echo ""
echo "🏥 Running system health check..."

python3 -c "
import requests
import sys

services = [
    ('Landing Page', 'http://localhost:11040'),
    ('Restaurant Voice', 'http://localhost:11032'),
    ('IT Voice', 'http://localhost:11031'),
    ('Network Dashboard', 'http://localhost:11050'),
    ('Neo4j', 'http://localhost:7474')
]

healthy_services = 0
for name, url in services:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f'✅ {name}: Healthy')
            healthy_services += 1
        else:
            print(f'⚠️  {name}: HTTP {response.status_code}')
    except:
        print(f'❌ {name}: Not responding')

print(f'\\n📊 System Health: {healthy_services}/{len(services)} services healthy')

if healthy_services >= 3:
    print('\\n🎉 SYSTEM IS READY!')
    print('\\n🚀 ACCESS POINTS:')
    print('   🏠 Main Dashboard: http://localhost:11040')
    print('   🎤 Restaurant Voice: http://localhost:11032')
    print('   🗺️  Network Map: http://localhost:11050')
    print('\\n💡 Start with the Main Dashboard for easy access to all features')
else:
    print('\\n⚠️  System partially ready. Check service logs in network-agents/logs/')
    sys.exit(1)
" 2>/dev/null || echo "⚠️ Health check failed - services may still be starting"

echo ""
echo "📋 QUICK START GUIDE:"
echo "1. Open Main Dashboard: http://localhost:11040"
echo "2. Click 'Restaurant Voice Assistant' for voice commands"
echo "3. Try saying: 'Check store equipment status'"
echo "4. View Network Map for visual monitoring"
echo ""
echo "📚 Documentation:"
echo "   - Installation Guide: INSTALLATION_GUIDE.md"
echo "   - User Guide: USER_GUIDE_SIMPLE.md"
echo "   - Logs: network-agents/logs/"
echo ""
echo "🛑 To stop all services: ./stop-restaurant-network-system.sh"
echo ""
echo "✨ AI Restaurant Network Management System is now running!"