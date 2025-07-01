#!/bin/bash

echo "🔍 AI Platform Startup Validation"
echo "=================================="

# Check systemd services
echo "📋 Checking systemd services..."
echo "Conflicting services status:"
for service in ai-platform-consolidated ai-platform-restore ai-platform-validator ai-platform ollama-ai-platform; do
    status=$(systemctl is-active $service.service 2>/dev/null || echo "inactive")
    enabled=$(systemctl is-enabled $service.service 2>/dev/null || echo "disabled")
    echo "  $service: $status ($enabled)"
done

echo ""
echo "🐳 Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -1
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(chat-copilot|openwebui|genai|nginx|rabbitmq|qdrant|n8n)" || echo "No matching containers found"

echo ""
echo "🌐 Testing service endpoints..."
services=(
    "http://localhost:3000"
    "http://localhost:3080/healthz"
    "http://localhost:11880"
    "http://localhost:8505"
    "http://localhost:11082"
    "http://localhost:5678"
)

for service in "${services[@]}"; do
    if curl -s -o /dev/null -w "%{http_code}" "$service" --connect-timeout 5 | grep -q "200"; then
        echo "✅ $service - OK"
    else
        echo "❌ $service - FAILED"
    fi
done

echo ""
echo "📊 Container Summary:"
total_containers=$(docker ps -q | wc -l)
running_containers=$(docker ps --filter "status=running" -q | wc -l)
echo "  Total containers: $total_containers"
echo "  Running containers: $running_containers"

echo ""
echo "🎯 Validation complete"
echo "📝 If services are failing, run: cd /home/keith/chat-copilot/docker && docker-compose up -d"
