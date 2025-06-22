#!/bin/bash
# Update nginx configuration for GenAI Stack integration

echo "🔧 Adding GenAI Stack services to nginx configuration..."

# Backup current configuration
sudo cp /etc/nginx/sites-available/ai-hub.conf /etc/nginx/sites-available/ai-hub.conf.backup
echo "✅ Backup created: /etc/nginx/sites-available/ai-hub.conf.backup"

# Add GenAI Stack services to nginx config
sudo sed -i '/location \/bacula\//a\\n    # Neo4j GenAI Stack Services\n    location /neo4j/           { proxy_pass http://127.0.0.1:7474/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }\n    location /genai-stack/loader/  { proxy_pass http://127.0.0.1:8502/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }\n    location /genai-stack/import/  { proxy_pass http://127.0.0.1:8081/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }\n    location /genai-stack/bot/     { proxy_pass http://127.0.0.1:8501/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }\n    location /genai-stack/pdf/     { proxy_pass http://127.0.0.1:8503/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }\n    location /genai-stack/api/     { proxy_pass http://127.0.0.1:8504/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }\n    location /genai-stack/         { proxy_pass http://127.0.0.1:8505/;   include /etc/nginx/sites-available/04-proxy-settings.conf; }' /etc/nginx/sites-available/ai-hub.conf

echo "✅ GenAI Stack services added to nginx configuration"

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded successfully"
    echo ""
    echo "🎉 GenAI Stack services are now available at:"
    echo "   • Neo4j Browser: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/neo4j/"
    echo "   • GenAI Stack Frontend: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/"
    echo "   • Support Bot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/bot/"
    echo "   • PDF Reader: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/pdf/"
    echo "   • API Docs: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/api/"
    echo "   • Data Loader: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/loader/"
else
    echo "❌ Nginx configuration has errors. Restoring backup..."
    sudo cp /etc/nginx/sites-available/ai-hub.conf.backup /etc/nginx/sites-available/ai-hub.conf
    echo "🔄 Backup restored. Please check the configuration manually."
fi