#!/bin/bash
# Stop script for AI Research Platform

echo "🛑 Stopping AI Research Platform Services..."

# Stop AutoGen Studio
if [ -f "pids/autogen-studio.pid" ]; then
    kill $(cat pids/autogen-studio.pid) 2>/dev/null && echo "✅ AutoGen Studio stopped"
    rm -f pids/autogen-studio.pid
fi

# Stop Magentic-One
if [ -f "pids/magentic-one.pid" ]; then
    kill $(cat pids/magentic-one.pid) 2>/dev/null && echo "✅ Magentic-One stopped"
    rm -f pids/magentic-one.pid
fi

# Stop Chat Copilot Backend
if [ -f "pids/webapi.pid" ]; then
    kill $(cat pids/webapi.pid) 2>/dev/null && echo "✅ Chat Copilot Backend stopped"
    rm -f pids/webapi.pid
fi

# Clean up any remaining processes
pkill -f autogenstudio 2>/dev/null
pkill -f magentic_one_server 2>/dev/null
pkill -f "dotnet run" 2>/dev/null

echo "🎯 All services stopped!"