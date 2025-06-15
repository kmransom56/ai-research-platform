#!/bin/bash
# Auto-start script for AI Research Platform

echo "🚀 Starting AI Research Platform Services..."

# Start AutoGen Studio
nohup uv run autogenstudio ui --port 11001 --host 0.0.0.0 > autogen-studio.log 2>&1 &
echo $! > pids/autogen-studio.pid
echo "✅ AutoGen Studio started on port 11001"

# Start Magentic-One Server  
nohup python3 magentic_one_server.py > magentic_one.log 2>&1 &
echo $! > pids/magentic-one.pid
echo "✅ Magentic-One started on port 11003"

# Start Chat Copilot Backend
cd webapi
ASPNETCORE_URLS=http://0.0.0.0:11000 nohup dotnet run --configuration Development > ../logs/webapi.log 2>&1 &
echo $! > ../pids/webapi.pid
cd ..
echo "✅ Chat Copilot Backend started on port 11000"

echo "🎉 All services started successfully!"
echo "📱 AutoGen Studio: http://100.123.10.72:11001"
echo "🤖 Magentic-One: http://100.123.10.72:11003" 
echo "💬 Chat Copilot: http://100.123.10.72:11000"