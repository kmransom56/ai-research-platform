#!/bin/bash
# Auto-start script for AI Research Platform (using uv)

echo "🚀 Starting AI Research Platform Services with uv..."

# Ensure uv is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Create uv venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating uv virtual environment..."
    uv venv
    echo "📥 Installing dependencies with uv..."
    uv pip install autogenstudio fastapi uvicorn
fi

# Start AutoGen Studio with uv
echo "🤖 Starting AutoGen Studio..."
uv run autogenstudio ui --port 8085 --host 0.0.0.0 > autogen-studio.log 2>&1 &
echo $! > pids/autogen-studio.pid
echo "✅ AutoGen Studio started on port 8085"

# Start Magentic-One Server with uv
echo "🔮 Starting Magentic-One Server..."
uv run python magentic_one_server.py > magentic_one.log 2>&1 &
echo $! > pids/magentic-one.pid
echo "✅ Magentic-One started on port 8086"

# Start Chat Copilot Backend
echo "💬 Starting Chat Copilot Backend..."
cd webapi
ASPNETCORE_URLS=http://0.0.0.0:10500 nohup dotnet run --configuration Development > ../logs/webapi.log 2>&1 &
echo $! > ../pids/webapi.pid
cd ..
echo "✅ Chat Copilot Backend started on port 10500"

sleep 2
echo ""
echo "🎉 All services started successfully!"
echo "📱 AutoGen Studio: http://100.123.10.72:8085"
echo "🤖 Magentic-One: http://100.123.10.72:8086" 
echo "💬 Chat Copilot: http://100.123.10.72:10500"
echo ""
echo "💡 Use './stop-all-services.sh' to stop all services"