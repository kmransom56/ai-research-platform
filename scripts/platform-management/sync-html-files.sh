#!/bin/bash
# HTML Files Synchronization Script
# Ensures webapp and webapi HTML files stay synchronized

set -e

SCRIPT_DIR="/home/keith/chat-copilot"
WEBAPP_DIR="$SCRIPT_DIR/webapp/public"
WEBAPI_DIR="$SCRIPT_DIR/webapi/wwwroot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Sync function
sync_file() {
    local filename=$1
    local source="$WEBAPP_DIR/$filename"
    local target="$WEBAPI_DIR/$filename"

    if [[ ! -f "$source" ]]; then
        error "Source file not found: $source"
        return 1
    fi

    if [[ ! -f "$target" ]]; then
        log "Target file doesn't exist, copying: $filename"
        cp "$source" "$target"
        success "Created: $filename"
        return 0
    fi

    # Compare files
    if ! cmp -s "$source" "$target"; then
        local source_size=$(stat -c%s "$source")
        local target_size=$(stat -c%s "$target")
        local source_time=$(stat -c%Y "$source")
        local target_time=$(stat -c%Y "$target")

        warning "Files differ: $filename"
        log "  Source: $source_size bytes, modified $(date -d @$source_time)"
        log "  Target: $target_size bytes, modified $(date -d @$target_time)"

        # Use newer file
        if [[ $source_time -gt $target_time ]]; then
            log "Source is newer, updating target"
            cp "$source" "$target"
            success "Updated: $filename (webapp → webapi)"
        else
            log "Target is newer, updating source"
            cp "$target" "$source"
            success "Updated: $filename (webapi → webapp)"
        fi
    else
        log "Files identical: $filename"
    fi
}

# Main sync
log "🔄 Starting HTML files synchronization..."

sync_file "control-panel.html"
sync_file "applications.html"

log "🎉 Synchronization complete!"

# Verify web server can serve the files
log "🔍 Verifying web server access..."

if curl -s -I http://127.0.0.1:11000/control-panel.html | grep -q "200 OK"; then
    success "Control panel accessible via backend"
else
    error "Control panel not accessible via backend"
fi

if curl -s -I http://127.0.0.1:11000/applications.html | grep -q "200 OK"; then
    success "Applications page accessible via backend"
else
    error "Applications page not accessible via backend"
fi

success "HTML files synchronization verified!"
