#!/bin/bash

# AI Services Startup Script - Fixed Configuration
# Starts all AI services with proper configuration and error handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting AI Research Platform - Fixed Configuration${NC}"
echo "======================================================="
echo "$(date)"
echo ""

# Set working directory
cd /home/keith-ransom/chat-copilot

# Source environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Loaded environment variables${NC}"
fi

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✅ Created logs directory${NC}"

echo ""
echo -e "${BLUE}🔧 Starting Core Services${NC}"
echo "=========================="

# 1. Start Chat Copilot Backend
echo -n "Starting Chat Copilot Backend... "
if ! pgrep -f "dotnet.*11000" > /dev/null; then
    cd webapi
    nohup dotnet run --urls http://0.0.0.0:11000 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    sleep 5
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:11000/healthz | grep -q "200"; then
        echo -e "${GREEN}✅ Started (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Started but not responding yet${NC}"
    fi
else
    echo -e "${GREEN}✅ Already running${NC}"
fi

# 2. Start AI Gateway
echo -n "Starting AI Gateway... "
if ! pgrep -f "gunicorn.*9000" > /dev/null; then
    cd python/ai-stack
    nohup gunicorn -w 2 -b 0.0.0.0:9000 \
        --access-logfile ../../logs/ai-gateway-access.log \
        --error-logfile ../../logs/ai-gateway-error.log \
        --daemon --pid ../../logs/ai-gateway.pid \
        api_gateway:app
    cd ../..
    sleep 3
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/health | grep -q "200"; then
        echo -e "${GREEN}✅ Started${NC}"
    else
        echo -e "${YELLOW}⚠️  Starting...${NC}"
    fi
else
    echo -e "${GREEN}✅ Already running${NC}"
fi

# 3. Start simple model servers (CPU-based for reliability)
echo -n "Starting AI Model Servers... "
cd python/ai-stack

# Start reasoning model server
if ! pgrep -f "python.*8000" > /dev/null; then
    nohup python3 -c "
import os
os.environ['MODEL_TYPE'] = 'reasoning'
import transformers_api
import asyncio
asyncio.run(transformers_api.start_server('reasoning'))
" > ../../logs/reasoning-model.log 2>&1 &
fi

# Start general model server  
if ! pgrep -f "python.*8001" > /dev/null; then
    nohup python3 -c "
import os
os.environ['MODEL_TYPE'] = 'general'
import transformers_api
import asyncio
asyncio.run(transformers_api.start_server('general'))
" > ../../logs/general-model.log 2>&1 &
fi

cd ../..
echo -e "${GREEN}✅ Started model servers${NC}"

echo ""
echo -e "${BLUE}🐳 Starting Docker Services${NC}"
echo "============================="

# Start lightweight AI services
if command -v docker-compose > /dev/null; then
    echo -n "Starting Docker AI services... "
    docker-compose -f docker-compose.ai-services-fixed.yml up -d 2>/dev/null || true
    echo -e "${GREEN}✅ Docker services started${NC}"
fi

echo ""
echo -e "${BLUE}🧪 Testing Services${NC}"
echo "==================="

# Test function
test_service() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    echo -n "Testing $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
    
    if [[ "$response" == "$expected" ]]; then
        echo -e "${GREEN}✅ OK ($response)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $response${NC}"
        return 1
    fi
}

# Test core services
test_service "Backend API" "http://localhost:11000/healthz" "200"
test_service "AI Gateway" "http://localhost:9000/health" "200"
test_service "Neo4j Database" "http://localhost:7474" "200"
test_service "Grafana" "http://localhost:11002" "302"
test_service "Open WebUI" "http://localhost:11880" "200"

# Test AI model services (may take time to load)
echo ""
echo -e "${BLUE}🤖 AI Model Services (may take time to load)${NC}"
test_service "Reasoning Model" "http://localhost:8000/health" "200"
test_service "General Model" "http://localhost:8001/health" "200"

echo ""
echo -e "${BLUE}📊 Service Status Summary${NC}"
echo "========================="

# Show running processes
echo "Python services:"
ps aux | grep -E "python.*11[0-9][0-9][0-9]|python.*[89][0-9][0-9][0-9]|gunicorn.*9000|dotnet.*11000" | grep -v grep | head -10

echo ""
echo "Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | head -8

echo ""
echo -e "${GREEN}🎉 AI Services Startup Complete!${NC}"
echo ""
echo "📋 Access URLs:"
echo "• Backend API: http://localhost:11000"
echo "• AI Gateway: http://localhost:9000"  
echo "• Neo4j: http://localhost:7474"
echo "• Grafana: http://localhost:11002"
echo "• Open WebUI: http://localhost:11880"
echo "• Reasoning AI: http://localhost:8000"
echo "• General AI: http://localhost:8001"
echo ""
echo "📁 Logs location: ./logs/"
echo "🔧 To stop services: ./scripts/platform-management/stop-ai-services.sh"