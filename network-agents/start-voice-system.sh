#!/bin/bash

# 🎤 AI Network Management System - Easy Startup Script
# This script starts all voice interfaces for maximum user adoption

echo "🚀 STARTING AI NETWORK MANAGEMENT SYSTEM"
echo "========================================"

# Check if Neo4j is running
echo "🔍 Checking Neo4j database..."
if ! nc -z localhost 7687 2>/dev/null; then
    echo "❌ Neo4j is not running. Please start Neo4j first:"
    echo "   docker start ai-platform-neo4j-final"
    echo "   Or check: docker ps"
    exit 1
fi
echo "✅ Neo4j database is running"

# Create virtual environment if it doesn't exist
if [ ! -d "neo4j-env" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv neo4j-env
    source neo4j-env/bin/activate
    pip install neo4j flask requests aiohttp asyncio
else
    echo "✅ Virtual environment exists"
fi

# Kill any existing processes on our ports
echo "🔄 Stopping any existing services..."
pkill -f "python3.*speech-web-interface.py" 2>/dev/null || true
pkill -f "python3.*restaurant-equipment-voice-interface.py" 2>/dev/null || true  
pkill -f "python3.*landing-page-server.py" 2>/dev/null || true

sleep 2

echo ""
echo "🎤 STARTING VOICE INTERFACES..."
echo "==============================="

# Start Network Management Interface
echo "🌐 Starting Network Management Interface (Port 11030)..."
source neo4j-env/bin/activate && python3 speech-web-interface.py > /tmp/network-interface.log 2>&1 &
NETWORK_PID=$!

sleep 3

# Start Restaurant Operations Interface  
echo "🍴 Starting Restaurant Operations Interface (Port 11032)..."
source neo4j-env/bin/activate && python3 restaurant-equipment-voice-interface.py > /tmp/restaurant-interface.log 2>&1 &
RESTAURANT_PID=$!

sleep 3

# Start Landing Page
echo "🚀 Starting Landing Page (Port 11040)..."
python3 landing-page-server.py > /tmp/landing-page.log 2>&1 &
LANDING_PID=$!

sleep 3

echo ""
echo "✅ SYSTEM READY!"
echo "================"
echo ""
echo "📱 MAIN ACCESS POINT:"
echo "   🌐 http://localhost:11040"
echo "   Choose Restaurant Operations OR Network Management"
echo ""
echo "🍴 RESTAURANT OPERATIONS (Store Managers):"
echo "   🌐 http://localhost:11032"
echo "   Commands: 'How are our POS systems?', 'Check kitchen equipment'"
echo ""
echo "🌐 NETWORK MANAGEMENT (IT Teams):"
echo "   🌐 http://localhost:11030" 
echo "   Commands: 'How many devices?', 'Check network health'"
echo ""
echo "🛠 ADVANCED ACCESS:"
echo "   Neo4j Browser: http://localhost:7474 (neo4j/password)"
echo ""
echo "📊 SYSTEM STATUS:"

# Check if services started successfully
sleep 5

if curl -s http://localhost:11030 >/dev/null 2>&1; then
    echo "   ✅ Network Interface: Running"
else
    echo "   ❌ Network Interface: Failed to start"
fi

if curl -s http://localhost:11032 >/dev/null 2>&1; then
    echo "   ✅ Restaurant Interface: Running"
else
    echo "   ❌ Restaurant Interface: Failed to start"
fi

if curl -s http://localhost:11040 >/dev/null 2>&1; then
    echo "   ✅ Landing Page: Running"
else
    echo "   ❌ Landing Page: Failed to start"
fi

echo ""
echo "💡 QUICK START GUIDE:"
echo "   1. Open: http://localhost:11040"
echo "   2. Choose your interface (Restaurant or Network)"
echo "   3. Click the microphone button"
echo "   4. Speak your question naturally"
echo "   5. Listen to the response"
echo ""
echo "📞 SUPPORT:"
echo "   Logs: /tmp/*-interface.log"
echo "   Status: curl http://localhost:11040/status"
echo "   Help: curl http://localhost:11040/help"
echo ""
echo "🎉 READY FOR ENTERPRISE USE!"
echo "   7,816 devices across 4,458 restaurant locations"
echo "   Voice-controlled troubleshooting for maximum adoption"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and monitor processes
trap 'echo ""; echo "🛑 Stopping all services..."; kill $NETWORK_PID $RESTAURANT_PID $LANDING_PID 2>/dev/null; exit 0' INT

# Monitor the processes
while true; do
    sleep 30
    
    # Check if any process died and restart it
    if ! kill -0 $NETWORK_PID 2>/dev/null; then
        echo "⚠️  Network interface stopped, restarting..."
        source neo4j-env/bin/activate && python3 speech-web-interface.py > /tmp/network-interface.log 2>&1 &
        NETWORK_PID=$!
    fi
    
    if ! kill -0 $RESTAURANT_PID 2>/dev/null; then
        echo "⚠️  Restaurant interface stopped, restarting..."
        source neo4j-env/bin/activate && python3 restaurant-equipment-voice-interface.py > /tmp/restaurant-interface.log 2>&1 &
        RESTAURANT_PID=$!
    fi
    
    if ! kill -0 $LANDING_PID 2>/dev/null; then
        echo "⚠️  Landing page stopped, restarting..."
        python3 landing-page-server.py > /tmp/landing-page.log 2>&1 &
        LANDING_PID=$!
    fi
done