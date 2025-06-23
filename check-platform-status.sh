#!/bin/bash
# Platform Status Checker - verify all services are running properly

echo "🔍 AI Research Platform Status Check"
echo "===================================="

# Check Backend API
echo "Backend API (11000):"
if curl -s -o /dev/null -w "%{http_code}" "http://100.123.10.72:11000/healthz" | grep -q "200"; then
    echo "  ✅ Chat Copilot Backend - HEALTHY"
else
    echo "  ❌ Chat Copilot Backend - FAILED"
fi

# Check Frontend
echo "Frontend (3000):"
if curl -s "http://localhost:3000" | grep -q "Chat Copilot"; then
    echo "  ✅ React Frontend - HEALTHY"
else
    echo "  ❌ React Frontend - FAILED"
fi

# Check HTTPS Proxy
echo "HTTPS Proxy (10443):"
if curl -k -s "https://100.123.10.72:10443/copilot/" | grep -q "Chat Copilot"; then
    echo "  ✅ HTTPS Proxy - HEALTHY"
else
    echo "  ❌ HTTPS Proxy - FAILED"
fi

# Check ntopng
echo "ntopng (8888):"
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8888" | grep -q "302"; then
    echo "  ✅ ntopng Network Monitor - HEALTHY"
else
    echo "  ❌ ntopng Network Monitor - FAILED"
fi

# Check Ollama
echo "Ollama (11434):"
if curl -s "http://localhost:11434/api/tags" | grep -q "models"; then
    echo "  ✅ Ollama LLM Service - HEALTHY"
else
    echo "  ❌ Ollama LLM Service - FAILED"
fi

# Check SSL Certificates
echo "SSL Certificates:"
if [ -f "/etc/ssl/tailscale/ubuntuaicodeserver-1.tail5137b4.ts.net.crt" ]; then
    echo "  ✅ SSL Certificates - PRESENT"
else
    echo "  ❌ SSL Certificates - MISSING"
fi

# Check Nginx
echo "Nginx:"
if sudo nginx -t 2>/dev/null; then
    echo "  ✅ Nginx Configuration - VALID"
else
    echo "  ❌ Nginx Configuration - INVALID"
fi

echo ""
echo "🔗 Quick Access URLs:"
echo "  • Main Platform: https://100.123.10.72:10443/"
echo "  • Chat Copilot: https://100.123.10.72:10443/copilot/"
echo "  • Control Panel: https://100.123.10.72:10443/hub"
echo "  • Applications: https://100.123.10.72:10443/applications.html"
echo "  • ntopng Monitor: https://100.123.10.72:10443/ntopng"
echo ""
echo "🛠️  If issues found:"
echo "  • Restore: /home/keith/chat-copilot/config-backups-working/latest/quick-restore.sh"
echo "  • Logs: tail -f /tmp/backend.log /tmp/frontend.log"