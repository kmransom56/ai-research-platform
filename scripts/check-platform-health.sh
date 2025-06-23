#!/bin/bash

# Platform Health Check Script
# Quickly verify all services are working

echo "🏥 AI Research Platform Health Check"
echo "===================================="

# Test key endpoints
echo "Testing HTTPS endpoints..."
endpoints=(
    "https://100.123.10.72:10443/hub|Hub"
    "https://100.123.10.72:10443/openwebui/|OpenWebUI"
    "https://100.123.10.72:10443/neo4j/|Neo4j"
    "https://100.123.10.72:10443/copilot/|Chat Copilot"
    "https://100.123.10.72:10443/fortinet/|Fortinet"
    "https://100.123.10.72:10443/ollama-api/|Ollama API"
)

for endpoint in "${endpoints[@]}"; do
    url=$(echo "$endpoint" | cut -d'|' -f1)
    name=$(echo "$endpoint" | cut -d'|' -f2)
    status=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout 5)
    
    if [ "$status" = "200" ] || [ "$status" = "301" ]; then
        echo "✅ $name: $status"
    else
        echo "❌ $name: $status"
    fi
done

echo ""
echo "🐳 Docker Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | head -10

echo ""
echo "🔧 System Services:"
systemctl is-active nginx ollama --quiet && echo "✅ Core services running" || echo "❌ Some services down"

echo ""
echo "📊 Ollama Models: $(ollama list | tail -n +2 | wc -l) models available"

echo ""
echo "💾 Latest Backup: $([ -L config-backups-working/latest ] && readlink config-backups-working/latest || 'No backup found')"