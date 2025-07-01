#!/bin/bash

readonly PLATFORM_DIR="/home/keith/chat-copilot"

# Core AI Services
declare -A CORE_SERVICES=(
    ["chat-copilot-backend"]="11000|cd $PLATFORM_DIR/webapi && dotnet run --urls http://0.0.0.0:11000|/healthz"
    ["autogen-studio"]="11001|autogenstudio ui --port 11001 --host 0.0.0.0|/"
    ["webhook-server"]="11025|node $PLATFORM_DIR/webhook-server.js|/health"
    ["magentic-one"]="11003|python $PLATFORM_DIR/python/services/magentic_one_server.py|/health"
)

echo "Syntax test passed"
