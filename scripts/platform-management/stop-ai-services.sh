#!/bin/bash

# Stop all AI services gracefully

echo "🛑 Stopping AI Research Platform Services"
echo "=========================================="

# Stop Python services by port
for port in 11000 9000 8000 8001 8002; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Stopping service on port $port (PID: $pid)"
        kill -TERM $pid 2>/dev/null
        sleep 2
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            kill -KILL $pid 2>/dev/null
        fi
    fi
done

# Stop Docker services
if [ -f docker-compose.ai-services-fixed.yml ]; then
    echo "Stopping Docker AI services..."
    docker-compose -f docker-compose.ai-services-fixed.yml down 2>/dev/null || true
fi

# Clean up PID files
rm -f logs/*.pid 2>/dev/null

echo "✅ All AI services stopped"