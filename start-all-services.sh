#!/bin/bash

# AI Research Platform - Complete Service Startup
echo "🚀 Starting AI Research Platform - All Services"

# Stop any existing services first
echo "🔄 Stopping existing services..."
docker compose -f docker-compose.simple.yml down 2>/dev/null
docker compose -f docker-compose.portable.yml down 2>/dev/null
pkill -f "dotnet run" 2>/dev/null
pkill -f "webhook-server" 2>/dev/null

# Start infrastructure services
echo "🏗️ Starting infrastructure services..."
docker compose -f docker-compose.simple.yml up -d postgres rabbitmq qdrant neo4j grafana vscode

# Wait for infrastructure
echo "⏳ Waiting for infrastructure to be ready..."
sleep 15

# Start Ollama if not running
if ! curl -s http://localhost:11434 > /dev/null; then
    echo "🤖 Starting Ollama..."
    sudo systemctl start ollama
    sleep 10
fi

# Start OpenWebUI
echo "🌐 Starting OpenWebUI..."
docker compose -f docker-compose.simple.yml up -d openwebui

# Start Chat Copilot Backend
echo "🔧 Starting Chat Copilot Backend..."
cd webapi && nohup dotnet run --urls http://0.0.0.0:11000 > ../logs/backend.log 2>&1 &
cd ..

# Start Webhook Server
echo "📡 Starting Webhook Server..."
cd runtime-data && nohup node webhook-server.js > ../logs/webhook.log 2>&1 &
cd ..

# Start GenAI Stack
echo "🧠 Starting GenAI Stack..."
cd genai-stack && docker compose up -d &
cd ..

# Start additional Python services
echo "🐍 Starting Python AI services..."

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install requirements if needed
if [ ! -f ".venv/requirements_installed" ]; then
    pip install -r requirements.txt
    touch .venv/requirements_installed
fi

# Start AutoGen Studio on different port
echo "🤖 Starting AutoGen Studio..."
cd python/autogen-studio
nohup python3 -m autogenstudio.ui --port 11001 > ../../logs/autogen.log 2>&1 &
cd ../..

# Wait and verify services
echo "⏳ Waiting for services to start..."
sleep 20

echo "✅ Service Status Check:"
curl -s -o /dev/null -w "Backend (11000): %{http_code}\n" http://localhost:11000/healthz
curl -s -o /dev/null -w "OpenWebUI (11880): %{http_code}\n" http://localhost:11880
curl -s -o /dev/null -w "Webhook (11025): %{http_code}\n" http://localhost:11025/health
curl -s -o /dev/null -w "Neo4j (7474): %{http_code}\n" http://localhost:7474
curl -s -o /dev/null -w "Grafana (11002): %{http_code}\n" http://localhost:11002
curl -s -o /dev/null -w "Ollama (11434): %{http_code}\n" http://localhost:11434
curl -s -o /dev/null -w "VS Code (57081): %{http_code}\n" http://localhost:57081

echo "🎉 AI Research Platform startup complete!"
echo "📊 Access the platform:"
echo "   - Chat Copilot: http://localhost:11000"
echo "   - OpenWebUI: http://localhost:11880"
echo "   - VS Code: http://localhost:57081"
echo "   - Neo4j: http://localhost:7474"
echo "   - Grafana: http://localhost:11002"