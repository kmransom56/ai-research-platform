#!/bin/bash

# AI Provider Switching Script for Chat Copilot
# Usage: ./switch-ai-provider.sh [openai|azure]

WEBAPI_DIR="/home/keith/chat-copilot/webapi"
BACKUP_DIR="$WEBAPI_DIR/config-backups"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

function switch_to_openai() {
    echo "🔄 Switching to OpenAI..."
    
    # Backup current config
    cp "$WEBAPI_DIR/appsettings.json" "$BACKUP_DIR/appsettings.json.$(date +%Y%m%d_%H%M%S)"
    
    # Update to use OpenAI
    cat > "$WEBAPI_DIR/appsettings.json.tmp" << 'EOF'
{
  "KernelMemory": {
    "TextGeneratorType": "OpenAI",
    "DataIngestion": {
      "EmbeddingGeneratorTypes": ["OpenAI"]
    },
    "Retrieval": {
      "EmbeddingGeneratorType": "OpenAI"
    }
  }
}
EOF
    
    # Use jq to merge if available, otherwise manual update
    if command -v jq &> /dev/null; then
        jq -s '.[0] * .[1]' "$WEBAPI_DIR/appsettings.json" "$WEBAPI_DIR/appsettings.json.tmp" > "$WEBAPI_DIR/appsettings.json.new"
        mv "$WEBAPI_DIR/appsettings.json.new" "$WEBAPI_DIR/appsettings.json"
        rm "$WEBAPI_DIR/appsettings.json.tmp"
    else
        echo "⚠️  Manual configuration required - jq not available"
        echo "Update TextGeneratorType to 'OpenAI' in appsettings.json"
    fi
    
    echo "✅ Switched to OpenAI"
    echo "🔑 Using OPENAI_API_KEY environment variable"
}

function switch_to_azure() {
    echo "🔄 Switching to Azure OpenAI..."
    
    # Backup current config
    cp "$WEBAPI_DIR/appsettings.json" "$BACKUP_DIR/appsettings.json.$(date +%Y%m%d_%H%M%S)"
    
    # Copy Azure configuration
    cp "$WEBAPI_DIR/appsettings.Azure.json" "$WEBAPI_DIR/appsettings.json"
    
    echo "✅ Switched to Azure OpenAI"
    echo "🔑 Using endpoint: https://selfhostapikey.openai.azure.com/"
    echo "📋 Deployment: gpt-4o"
}

function test_connection() {
    echo "🧪 Testing Chat Copilot backend..."
    
    # Check if backend is running
    if curl -k -s -f "https://100.123.10.72:40443/healthz" > /dev/null; then
        echo "✅ Backend is healthy"
    else
        echo "❌ Backend not responding - restart required"
        echo "Run: cd $WEBAPI_DIR && dotnet run --urls 'https://100.123.10.72:40443'"
    fi
}

function show_status() {
    echo "📊 Current AI Provider Status:"
    echo "----------------------------"
    
    if grep -q '"TextGeneratorType": "OpenAI"' "$WEBAPI_DIR/appsettings.json"; then
        echo "Current Provider: 🟢 OpenAI"
        echo "API Key: $(echo $OPENAI_API_KEY | head -c 20)..."
    elif grep -q '"TextGeneratorType": "AzureOpenAI"' "$WEBAPI_DIR/appsettings.json"; then
        echo "Current Provider: 🔵 Azure OpenAI"
        echo "Endpoint: $AZURE_OPENAI_ENDPOINT"
        echo "Deployment: $AZURE_OPENAI_DEPLOYMENT"
    else
        echo "Current Provider: ❓ Unknown"
    fi
    
    echo ""
    test_connection
}

# Main script logic
case "$1" in
    "openai")
        switch_to_openai
        test_connection
        ;;
    "azure")
        switch_to_azure
        test_connection
        ;;
    "status")
        show_status
        ;;
    "test")
        test_connection
        ;;
    *)
        echo "🤖 AI Provider Switching Script"
        echo "Usage: $0 [openai|azure|status|test]"
        echo ""
        echo "Commands:"
        echo "  openai  - Switch to OpenAI (primary)"
        echo "  azure   - Switch to Azure OpenAI (backup)"
        echo "  status  - Show current provider status"
        echo "  test    - Test backend connection"
        echo ""
        show_status
        ;;
esac