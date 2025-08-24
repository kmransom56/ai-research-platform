#!/bin/bash
"""
Restart AI Research Platform
Graceful restart of all platform services
"""

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." &> /dev/null && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo -e "${BLUE}"
echo "🔄 AI Research Platform - Restart"
echo "=================================="
echo -e "${NC}"

cd "$PROJECT_ROOT"

# Stop platform services
log "Stopping platform services..."
if [ -x "scripts/platform-management/stop-platform.sh" ]; then
    scripts/platform-management/stop-platform.sh
else
    warning "Stop script not found, continuing with restart..."
fi

# Stop AI stack services
log "Stopping AI stack services..."
if [ -x "scripts/platform-management/manage-ai-stack.sh" ]; then
    scripts/platform-management/manage-ai-stack.sh stop-all 2>/dev/null || true
fi

# Wait a moment for services to stop
sleep 5

# Restart using startup script
log "Starting platform with startup script..."
if [ -x "scripts/startup/startup-complete-platform.sh" ]; then
    scripts/startup/startup-complete-platform.sh
else
    # Fallback to individual service starts
    log "Using fallback service start..."
    
    if [ -x "scripts/platform-management/manage-ai-stack.sh" ]; then
        scripts/platform-management/manage-ai-stack.sh start-all
    fi
fi

success "Platform restart completed!"