#!/bin/bash

# =============================================================================
# CONFIGURATION
# =============================================================================

# Directories
readonly PLATFORM_DIR="/home/keith/chat-copilot"

# Core AI Services
declare -A CORE_SERVICES=(
    ["webhook-server"]="11025|node $PLATFORM_DIR/runtime-data/webhook-server.js|/health"
)

# Test basic functionality
echo "🚀 Testing webhook server status..."
if curl -s "http://localhost:11025/health" >/dev/null 2>&1; then
    echo "✅ Webhook Server is running on port 11025"
else
    echo "❌ Webhook Server is not responding"
fi

echo "Script syntax and basic test completed"
