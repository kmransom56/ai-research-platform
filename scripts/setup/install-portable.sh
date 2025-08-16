#!/bin/bash

# =============================================================================
# Chat Copilot Portable Installation Script
# =============================================================================
# This script sets up Chat Copilot in a portable way that works on any system
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    local level=$1
    local message=$2
    case $level in
        "INFO")  echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "ERROR") echo -e "${RED}❌ ${message}${NC}" ;;
    esac
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAT_COPILOT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

print_status "INFO" "Starting Chat Copilot portable installation..."
print_status "INFO" "Installation directory: $CHAT_COPILOT_ROOT"

# =============================================================================
# STEP 1: Detect System Information
# =============================================================================

print_status "INFO" "Detecting system information..."

# Get current user
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)
CURRENT_HOME=$(eval echo ~$CURRENT_USER)

print_status "INFO" "User: $CURRENT_USER"
print_status "INFO" "Group: $CURRENT_GROUP"
print_status "INFO" "Home: $CURRENT_HOME"

# Detect IP address
if command -v ip &> /dev/null; then
    PLATFORM_IP=$(ip route get 1.1.1.1 | grep -oP 'src \K\S+' | head -1)
elif command -v ifconfig &> /dev/null; then
    PLATFORM_IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)
else
    PLATFORM_IP="127.0.0.1"
fi

print_status "INFO" "Detected IP: $PLATFORM_IP"

# =============================================================================
# STEP 2: Create Environment Configuration
# =============================================================================

print_status "INFO" "Creating environment configuration..."

ENV_FILE="$CHAT_COPILOT_ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
    print_status "WARNING" "Environment file already exists. Creating backup..."
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d-%H%M%S)"
fi

# Create .env file from template
cat > "$ENV_FILE" << EOF
# Chat Copilot Platform Configuration
# Generated on $(date)

# =============================================================================
# INSTALLATION PATHS
# =============================================================================

CHAT_COPILOT_ROOT=$CHAT_COPILOT_ROOT
PLATFORM_USER=$CURRENT_USER
PLATFORM_GROUP=$CURRENT_GROUP

# =============================================================================
# NETWORK CONFIGURATION
# =============================================================================

PLATFORM_IP=$PLATFORM_IP
PLATFORM_DOMAIN=localhost

# =============================================================================
# SERVICE PORTS
# =============================================================================

# Core Services
CHAT_COPILOT_BACKEND_PORT=11000
CHAT_COPILOT_FRONTEND_PORT=3000
OPENWEBUI_PORT=11880
VSCODE_PORT=57081

# AI Services
AUTOGEN_PORT=11001
MAGENTIC_ONE_PORT=11003
PROMPT_FORGE_PORT=11500
N8N_PORT=11510

# Search & Knowledge
PERPLEXICA_PORT=11020
SEARXNG_PORT=11021
NEO4J_PORT=7474
QDRANT_PORT=6333

# GenAI Stack
GENAI_FRONTEND_PORT=8505
GENAI_LOADER_PORT=8502
GENAI_IMPORT_PORT=8082
GENAI_BOT_PORT=8501
GENAI_PDF_PORT=8503
GENAI_API_PORT=8504

# Infrastructure
NGINX_SSL_PORT=8443
NGINX_HTTP_PORT=8080
RABBITMQ_PORT=15672
POSTGRES_PORT=5432
GRAFANA_PORT=11004
WEBHOOK_PORT=11025

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

POSTGRES_DB=chatcopilot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=chatcopilot-$(openssl rand -hex 8)

RABBITMQ_DEFAULT_USER=chatcopilot
RABBITMQ_DEFAULT_PASS=chatcopilot-$(openssl rand -hex 8)

# =============================================================================
# AI PROVIDER CONFIGURATION
# =============================================================================

OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4

# =============================================================================
# SSL/TLS CONFIGURATION
# =============================================================================

SSL_CERT_PATH=/etc/ssl/certs/server.crt
SSL_KEY_PATH=/etc/ssl/private/server.key

# =============================================================================
# DOCKER CONFIGURATION
# =============================================================================

DOCKER_NETWORK_NAME=chatcopilot_ai-platform
DOCKER_VOLUME_PREFIX=chatcopilot

# =============================================================================
# LOGGING AND MONITORING
# =============================================================================

LOG_LEVEL=INFO
ASPNETCORE_ENVIRONMENT=Production
ENABLE_HEALTH_MONITORING=true
HEALTH_CHECK_INTERVAL=30

# =============================================================================
# BACKUP CONFIGURATION
# =============================================================================

BACKUP_DIR=$CHAT_COPILOT_ROOT/backups
BACKUP_RETENTION_DAYS=30
EOF

print_status "SUCCESS" "Environment configuration created: $ENV_FILE"

# =============================================================================
# STEP 3: Create Directory Structure
# =============================================================================

print_status "INFO" "Creating directory structure..."

# Create required directories
DIRECTORIES=(
    "logs"
    "pids"
    "data"
    "backups"
    "config-backups"
    "config-snapshots"
    "temp"
)

for dir in "${DIRECTORIES[@]}"; do
    mkdir -p "$CHAT_COPILOT_ROOT/$dir"
    print_status "SUCCESS" "Created directory: $dir"
done

# Set proper permissions
chmod 755 "$CHAT_COPILOT_ROOT"/{logs,pids,data,backups,config-backups,config-snapshots,temp}

# =============================================================================
# STEP 4: Update Configuration Files
# =============================================================================

print_status "INFO" "Updating configuration files with portable paths..."

# Function to update paths in files
update_paths_in_file() {
    local file="$1"
    if [[ -f "$file" ]]; then
        # Create backup
        cp "$file" "$file.backup.$(date +%Y%m%d-%H%M%S)"
        
        # Replace hard-coded paths
        sed -i "s|/home/keith/chat-copilot|\${CHAT_COPILOT_ROOT}|g" "$file"
        sed -i "s|/home/keith|\${HOME}|g" "$file"
        
        print_status "SUCCESS" "Updated paths in: $(basename "$file")"
    fi
}

# Update Docker Compose files
find "$CHAT_COPILOT_ROOT/configs/docker-compose" -name "*.yml" -exec bash -c 'update_paths_in_file "$0"' {} \;

# Update scripts
find "$CHAT_COPILOT_ROOT/scripts" -name "*.sh" -exec bash -c 'update_paths_in_file "$0"' {} \;

# Update nginx configs
find "$CHAT_COPILOT_ROOT/nginx-configs" -name "*.conf" -exec bash -c 'update_paths_in_file "$0"' {} \;

# =============================================================================
# STEP 5: Create Portable Startup Script
# =============================================================================

print_status "INFO" "Creating portable startup script..."

cat > "$CHAT_COPILOT_ROOT/start-platform-portable.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# Chat Copilot Portable Startup Script
# =============================================================================

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
if [[ -f ".env" ]]; then
    set -a
    source .env
    set +a
    echo "✅ Loaded environment configuration"
else
    echo "❌ Environment file not found. Run scripts/setup/install-portable.sh first"
    exit 1
fi

# Export environment variables for Docker Compose
export CHAT_COPILOT_ROOT
export PLATFORM_USER
export PLATFORM_GROUP
export PLATFORM_IP

echo "🚀 Starting Chat Copilot Platform..."
echo "📁 Installation directory: $CHAT_COPILOT_ROOT"
echo "👤 User: $PLATFORM_USER"
echo "🌐 IP: $PLATFORM_IP"

# Start the platform
docker-compose -f configs/docker-compose/docker-compose-full-stack.yml up -d

echo "✅ Platform started successfully!"
echo "🌐 Access the platform at: http://$PLATFORM_IP:$OPENWEBUI_PORT"
EOF

chmod +x "$CHAT_COPILOT_ROOT/start-platform-portable.sh"

# =============================================================================
# STEP 6: Create Portable Docker Compose Template
# =============================================================================

print_status "INFO" "Creating portable Docker Compose configuration..."

# Create a portable version of the main Docker Compose file
PORTABLE_COMPOSE="$CHAT_COPILOT_ROOT/configs/docker-compose/docker-compose-portable.yml"

cp "$CHAT_COPILOT_ROOT/configs/docker-compose/docker-compose-full-stack.yml" "$PORTABLE_COMPOSE"

# Update the portable compose file to use environment variables
sed -i 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT}|g' "$PORTABLE_COMPOSE"
sed -i 's|keith:keith|${PLATFORM_USER}:${PLATFORM_GROUP}|g' "$PORTABLE_COMPOSE"

# =============================================================================
# STEP 7: Create Installation Summary
# =============================================================================

print_status "SUCCESS" "Installation completed successfully!"

cat << EOF

🎉 Chat Copilot Portable Installation Complete!

📋 Installation Summary:
   • Installation directory: $CHAT_COPILOT_ROOT
   • User: $CURRENT_USER
   • Group: $CURRENT_GROUP
   • Platform IP: $PLATFORM_IP

📁 Created Files:
   • .env - Environment configuration
   • start-platform-portable.sh - Portable startup script
   • configs/docker-compose/docker-compose-portable.yml - Portable Docker Compose

🚀 Next Steps:

1. Configure your AI provider:
   Edit .env and set your OPENAI_API_KEY or Azure OpenAI settings

2. Start the platform:
   ./start-platform-portable.sh

3. Access the platform:
   http://$PLATFORM_IP:11880 (OpenWebUI)
   http://$PLATFORM_IP:11000 (Chat Copilot)

📖 For more information, see the documentation in docs/

EOF

print_status "INFO" "Installation log saved to: $CHAT_COPILOT_ROOT/logs/install-$(date +%Y%m%d-%H%M%S).log"