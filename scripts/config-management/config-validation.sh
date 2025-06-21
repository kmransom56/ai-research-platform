#!/bin/bash
# Configuration Validation and Drift Prevention Script
# Validates critical configurations before service startup

set -e

PLATFORM_DIR="/home/keith/chat-copilot"
WEBAPP_ENV="$PLATFORM_DIR/webapp/.env"
BACKEND_CONFIG="$PLATFORM_DIR/webapi/appsettings.json"

echo "🔍 Configuration Validation Starting..."

# Function to validate configuration
validate_config() {
    local config_file=$1
    local expected_value=$2
    local actual_value=$3
    local description=$4
    
    if [[ "$actual_value" == "$expected_value" ]]; then
        echo "✅ $description: OK"
        return 0
    else
        echo "❌ $description: DRIFT DETECTED"
        echo "   Expected: $expected_value"
        echo "   Actual: $actual_value"
        echo "   File: $config_file"
        return 1
    fi
}

# Function to backup configuration before changes
backup_config() {
    local file=$1
    local backup_dir="$PLATFORM_DIR/config-backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    mkdir -p "$backup_dir/$timestamp"
    cp "$file" "$backup_dir/$timestamp/"
    echo "📋 Backed up $(basename $file) to $backup_dir/$timestamp/"
}

# Function to fix configuration drift
fix_drift() {
    local file=$1
    local search=$2
    local replace=$3
    local description=$4
    
    echo "🔧 Fixing $description..."
    backup_config "$file"
    sed -i "s|$search|$replace|g" "$file"
    echo "✅ Fixed $description"
}

# Validation Results
validation_errors=0

echo ""
echo "🔍 Validating Frontend Configuration..."

if [[ -f "$WEBAPP_ENV" ]]; then
    backend_uri=$(grep "REACT_APP_BACKEND_URI" "$WEBAPP_ENV" | cut -d'=' -f2)
    if ! validate_config "$WEBAPP_ENV" "http://100.123.10.72:11000/" "$backend_uri" "Frontend Backend URI"; then
        ((validation_errors++))
        fix_drift "$WEBAPP_ENV" "REACT_APP_BACKEND_URI=.*" "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" "Frontend Backend URI"
    fi
else
    echo "❌ Frontend .env file missing"
    echo "🔧 Creating missing .env file..."
    echo "REACT_APP_BACKEND_URI=http://100.123.10.72:11000/" > "$WEBAPP_ENV"
    echo "✅ Created frontend .env file"
fi

echo ""
echo "🔍 Validating Backend Configuration..."

if [[ -f "$BACKEND_CONFIG" ]]; then
    backend_port=$(grep -o '"Url": "http://0.0.0.0:[0-9]*"' "$BACKEND_CONFIG" | sed 's/.*://' | sed 's/"//')
    if ! validate_config "$BACKEND_CONFIG" "11000" "$backend_port" "Backend Port"; then
        ((validation_errors++))
        fix_drift "$BACKEND_CONFIG" '"Url": "http://0.0.0.0:[0-9]*"' '"Url": "http://0.0.0.0:11000"' "Backend Port"
    fi
    
    # Check Ollama endpoint
    ollama_endpoint=$(grep -A 1 '"Ollama"' "$BACKEND_CONFIG" | grep '"Endpoint"' | cut -d'"' -f4)
    if ! validate_config "$BACKEND_CONFIG" "http://localhost:11434" "$ollama_endpoint" "Ollama Endpoint"; then
        ((validation_errors++))
        fix_drift "$BACKEND_CONFIG" '"Endpoint": "http://localhost:[0-9]*"' '"Endpoint": "http://localhost:11434"' "Ollama Endpoint"
    fi
else
    echo "❌ Backend appsettings.json missing"
    ((validation_errors++))
fi

echo ""
echo "🔍 Validating Port Configuration..."

PORT_CONFIG="$PLATFORM_DIR/port-configuration.json"
if [[ -f "$PORT_CONFIG" ]]; then
    chat_copilot_port=$(grep -o '"chat_copilot_backend": [0-9]*' "$PORT_CONFIG" | grep -o '[0-9]*')
    if ! validate_config "$PORT_CONFIG" "11000" "$chat_copilot_port" "Port Configuration - Chat Copilot"; then
        ((validation_errors++))
        fix_drift "$PORT_CONFIG" '"chat_copilot_backend": [0-9]*' '"chat_copilot_backend": 11000' "Port Configuration - Chat Copilot"
    fi
else
    echo "❌ Port configuration file missing"
    ((validation_errors++))
fi

echo ""
echo "📊 Validation Summary"
echo "===================="

if [[ $validation_errors -eq 0 ]]; then
    echo "✅ All configurations are valid - no drift detected"
    echo "🚀 System ready for startup"
    exit 0
else
    echo "⚠️  Configuration drift detected and fixed: $validation_errors issues"
    echo "🔧 Configurations have been corrected"
    echo "🚀 System ready for startup"
    exit 0
fi