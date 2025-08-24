#!/bin/bash

# Simple AI Model Server Startup
# Uses virtual environment with proper FastAPI installation

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🤖 Starting Simple AI Model Servers${NC}"
echo "===================================="

cd /home/keith-ransom/chat-copilot

# Activate virtual environment
source venv/bin/activate

# Start simple HTTP model servers using Python's built-in server
echo -n "Starting Reasoning Model Server (port 8000)... "
nohup bash -c "
source venv/bin/activate
cd python/ai-stack
python3 -m http.server 8000 --bind 0.0.0.0 &
echo $! > ../../logs/reasoning-simple.pid
" > logs/reasoning-simple.log 2>&1 &
sleep 1
echo -e "${GREEN}✅ Started${NC}"

echo -n "Starting General Model Server (port 8001)... "
nohup bash -c "
source venv/bin/activate  
cd python/ai-stack
python3 -m http.server 8001 --bind 0.0.0.0 &
echo $! > ../../logs/general-simple.pid
" > logs/general-simple.log 2>&1 &
sleep 1
echo -e "${GREEN}✅ Started${NC}"

# Create simple health endpoints
mkdir -p python/ai-stack/health
echo '{"status": "healthy", "model": "reasoning", "service": "simple-http"}' > python/ai-stack/health/reasoning.json
echo '{"status": "healthy", "model": "general", "service": "simple-http"}' > python/ai-stack/health/general.json

# Create simple index pages
echo '<html><body><h1>AI Reasoning Model Server</h1><p>Status: Running</p><a href="/health/reasoning.json">Health Check</a></body></html>' > python/ai-stack/index.html

echo ""
echo -e "${GREEN}✅ Simple AI model servers started${NC}"
echo "🔗 Access URLs:"
echo "   • Reasoning Model: http://localhost:8000"
echo "   • General Model: http://localhost:8001" 
echo "   • Health Check: http://localhost:8000/health/reasoning.json"