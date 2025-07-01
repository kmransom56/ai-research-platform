#!/bin/bash
# AI Research Platform - Comprehensive Backup & Restore Script
# Creates complete backup of all platform configurations and services

set -euo pipefail

# Configuration
BACKUP_BASE_DIR="/home/keith/platform-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE_DIR/platform_backup_$TIMESTAMP"
PLATFORM_ROOT="/home/keith/chat-copilot"
SCRIPTS_DIR="$PLATFORM_ROOT/scripts/platform-management"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Current service configuration (aligned with health-check.sh)
declare -A CURRENT_SERVICES=(
    ["Chat Copilot Backend"]="11000"
    ["AutoGen Studio"]="11001"
    ["Webhook Server"]="11025"
    ["Magentic-One"]="11003"
    ["Port Scanner"]="11010"
    ["Nginx Proxy Manager"]="8080"
    ["ntopng Network Monitor"]="8888"
    ["Neo4j Database"]="7474"
    ["GenAI Stack Frontend"]="8505"
    ["GenAI Stack API"]="8504"
    ["GenAI Stack Bot"]="8501"
    ["Perplexica"]="11020"
    ["SearXNG"]="11021"
    ["OpenWebUI"]="11880"
    ["Ollama"]="11434"
    ["VS Code Web"]="57081"
    ["Windmill"]="11006"
)

# Nginx proxy paths (aligned with nginx config)
declare -A NGINX_PATHS=(
    ["/vscode/"]="57081"
    ["/copilot/api/"]="11000"
    ["/copilot/"]="3000"
    ["/autogen/"]="11001"
    ["/magentic/"]="11003"
    ["/webhook/"]="11025"
    ["/perplexica/"]="11020"
    ["/searxng/"]="11021"
    ["/portscanner/"]="11010"
    ["/nginx/"]="8080"
    ["/gateway-admin/"]="11082"
    ["/openwebui/"]="11880"
    ["/neo4j/"]="7474"
    ["/genai-stack/"]="8505"
    ["/ollama-api/"]="11434"
)

backup_configurations() {
    log_info "🔄 Creating platform configuration backup..."

    mkdir -p "$BACKUP_DIR"/{configs,scripts,docker,html,logs,data}

    # 1. Backup all management scripts
    log_info "📁 Backing up management scripts..."
    cp -r "$SCRIPTS_DIR" "$BACKUP_DIR/scripts/"

    # 2. Backup nginx configuration
    log_info "🌐 Backing up nginx configuration..."
    sudo cp /etc/nginx/sites-available/ai-hub.conf "$BACKUP_DIR/configs/"
    sudo cp -r /etc/nginx/sites-available/ "$BACKUP_DIR/configs/nginx-sites/"

    # 3. Backup HTML control panels
    log_info "🎨 Backing up HTML control panels..."
    cp "$PLATFORM_ROOT/webapi/wwwroot/control-panel.html" "$BACKUP_DIR/html/webapi-control-panel.html"
    cp "$PLATFORM_ROOT/webapp/public/control-panel.html" "$BACKUP_DIR/html/webapp-control-panel.html"
    cp "$PLATFORM_ROOT/webapi/wwwroot/applications.html" "$BACKUP_DIR/html/webapi-applications.html" 2>/dev/null || true
    cp "$PLATFORM_ROOT/webapp/public/applications.html" "$BACKUP_DIR/html/webapp-applications.html" 2>/dev/null || true

    # 4. Backup Docker configurations
    log_info "🐳 Backing up Docker configurations..."
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" >"$BACKUP_DIR/docker/running-containers.txt"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" >"$BACKUP_DIR/docker/images.txt"
    docker network ls >"$BACKUP_DIR/docker/networks.txt"

    # Backup docker-compose files
    find "$PLATFORM_ROOT" -name "docker-compose*.yml" -exec cp {} "$BACKUP_DIR/docker/" \;
    find "$PLATFORM_ROOT" -name "compose.yaml" -exec cp {} "$BACKUP_DIR/docker/" \;

    # 5. Backup Python configuration scripts
    log_info "🐍 Backing up Python scripts..."
    cp -r "$PLATFORM_ROOT/python" "$BACKUP_DIR/scripts/" 2>/dev/null || true

    # 6. Generate current service configuration
    log_info "📊 Generating service configuration manifest..."
    cat >"$BACKUP_DIR/configs/service-manifest.txt" <<EOF
# AI Research Platform Service Configuration
# Generated: $(date)
# Total Services: ${#CURRENT_SERVICES[@]}

=== CURRENT SERVICES ===
EOF

    for service in "${!CURRENT_SERVICES[@]}"; do
        echo "$service: ${CURRENT_SERVICES[$service]}" >>"$BACKUP_DIR/configs/service-manifest.txt"
    done

    cat >>"$BACKUP_DIR/configs/service-manifest.txt" <<EOF

=== NGINX PROXY PATHS ===
EOF

    for path in "${!NGINX_PATHS[@]}"; do
        echo "$path -> ${NGINX_PATHS[$path]}" >>"$BACKUP_DIR/configs/service-manifest.txt"
    done

    # 7. Backup environment files and configurations
    log_info "⚙️ Backing up environment configurations..."
    cp "$PLATFORM_ROOT/.env" "$BACKUP_DIR/configs/" 2>/dev/null || true
    cp "$PLATFORM_ROOT/appsettings.json" "$BACKUP_DIR/configs/" 2>/dev/null || true
    cp -r "$PLATFORM_ROOT/config" "$BACKUP_DIR/configs/" 2>/dev/null || true

    # 8. Create restoration script
    create_restore_script

    # 9. Create verification script
    create_verification_script

    log_success "✅ Backup completed: $BACKUP_DIR"
    log_info "📦 Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
}

create_restore_script() {
    log_info "📜 Creating restoration script..."

    cat >"$BACKUP_DIR/restore.sh" <<'EOF'
#!/bin/bash
# AI Research Platform - Restoration Script
# Restores all platform configurations from backup

set -euo pipefail

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="/home/keith/chat-copilot"
SCRIPTS_DIR="$PLATFORM_ROOT/scripts/platform-management"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

restore_platform() {
    log_info "🔄 Starting platform restoration..."
    
    # 1. Stop all services
    log_info "🛑 Stopping all platform services..."
    cd "$SCRIPTS_DIR" 2>/dev/null || { log_error "Scripts directory not found"; exit 1; }
    ./stop-platform.sh || log_warning "Some services may not have stopped cleanly"
    
    # 2. Restore management scripts
    log_info "📁 Restoring management scripts..."
    cp -r "$BACKUP_DIR/scripts/platform-management/"* "$SCRIPTS_DIR/"
    chmod +x "$SCRIPTS_DIR"/*.sh
    
    # 3. Restore nginx configuration
    log_info "🌐 Restoring nginx configuration..."
    sudo cp "$BACKUP_DIR/configs/ai-hub.conf" /etc/nginx/sites-available/
    sudo nginx -t && sudo systemctl reload nginx
    
    # 4. Restore HTML control panels
    log_info "🎨 Restoring HTML control panels..."
    cp "$BACKUP_DIR/html/webapi-control-panel.html" "$PLATFORM_ROOT/webapi/wwwroot/control-panel.html"
    cp "$BACKUP_DIR/html/webapp-control-panel.html" "$PLATFORM_ROOT/webapp/public/control-panel.html"
    
    # Update webapp container if running
    if docker ps | grep -q "chat-copilot-webapp"; then
        log_info "🐳 Updating webapp container with restored control panel..."
        docker cp "$PLATFORM_ROOT/webapp/public/control-panel.html" \
                  docker-chat-copilot-webapp-nginx-1:/usr/share/nginx/html/control-panel.html
    fi
    
    # 5. Restore Python scripts
    log_info "🐍 Restoring Python scripts..."
    cp -r "$BACKUP_DIR/scripts/python/"* "$PLATFORM_ROOT/python/" 2>/dev/null || true
    
    # 6. Restore environment configurations
    log_info "⚙️ Restoring environment configurations..."
    cp "$BACKUP_DIR/configs/.env" "$PLATFORM_ROOT/" 2>/dev/null || true
    cp "$BACKUP_DIR/configs/appsettings.json" "$PLATFORM_ROOT/" 2>/dev/null || true
    
    # 7. Start platform
    log_info "🚀 Starting platform services..."
    ./startup-platform-clean.sh
    
    # 8. Verify restoration
    log_info "🔍 Verifying restoration..."
    sleep 10
    ./health-check.sh
    
    log_success "✅ Platform restoration completed!"
    log_info "🌐 Access control panel: https://100.123.10.72:10443/hub"
}

# Check if running as backup restoration
if [[ "${1:-}" == "--restore" ]]; then
    restore_platform
else
    log_info "This is a restoration script generated with the backup."
    log_info "To restore the platform, run: $0 --restore"
    log_info "Backup contents:"
    find . -type f | head -20
fi
EOF

    chmod +x "$BACKUP_DIR/restore.sh"
}

create_verification_script() {
    log_info "✅ Creating verification script..."

    cat >"$BACKUP_DIR/verify.sh" <<'EOF'
#!/bin/bash
# AI Research Platform - Configuration Verification Script

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

verify_platform() {
    log_info "🔍 Verifying platform configuration alignment..."
    
    # Check all services from manifest
    log_info "📊 Checking service alignment..."
    
    # Expected services (from backup manifest)
    declare -A EXPECTED_SERVICES=(
        ["Chat Copilot Backend"]="11000"
        ["AutoGen Studio"]="11001" 
        ["Webhook Server"]="11025"
        ["Magentic-One"]="11003"
        ["Port Scanner"]="11010"
        ["Nginx Proxy Manager"]="8080"
        ["ntopng Network Monitor"]="8888"
        ["Neo4j Database"]="7474"
        ["GenAI Stack Frontend"]="8505"
        ["GenAI Stack API"]="8504"
        ["GenAI Stack Bot"]="8501"
        ["Perplexica"]="11020"
        ["SearXNG"]="11021"
        ["OpenWebUI"]="11880"
        ["Ollama"]="11434"
        ["VS Code Web"]="57081"
        ["Windmill"]="11006"
    )
    
    local healthy_count=0
    local total_count=${#EXPECTED_SERVICES[@]}
    
    for service in "${!EXPECTED_SERVICES[@]}"; do
        local port=${EXPECTED_SERVICES[$service]}
        local url="http://100.123.10.72:$port/"
        
        if [[ "$service" == "Webhook Server" ]]; then
            url="http://100.123.10.72:$port/health"
        elif [[ "$service" == "Ollama" ]]; then
            url="http://100.123.10.72:$port/api/version"
        fi
        
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
        
        if [[ "$status_code" =~ ^[2-3][0-9][0-9]$ ]]; then
            log_success "✅ $service ($port): $status_code"
            ((healthy_count++))
        else
            log_error "❌ $service ($port): $status_code"
        fi
    done
    
    log_info "📊 Health Summary: $healthy_count/$total_count services healthy"
    
    if [[ $healthy_count -eq $total_count ]]; then
        log_success "🎉 All services are healthy and properly configured!"
        return 0
    else
        log_warning "⚠️ Some services may need attention"
        return 1
    fi
}

verify_platform
EOF

    chmod +x "$BACKUP_DIR/verify.sh"
}

cleanup_obsolete() {
    log_info "🧹 Cleaning up obsolete configurations..."

    # Remove any remaining Fortinet or Caddy references from scripts
    find "$SCRIPTS_DIR" -name "*.sh" -exec grep -l -i "fortinet\|caddy" {} \; | while read -r file; do
        log_warning "Found obsolete references in: $file"
        # You may want to manually review these
    done

    # Stop and remove any obsolete containers
    log_info "🐳 Checking for obsolete containers..."
    docker ps -a --format "{{.Names}}" | grep -E "(fortinet|caddy)" | while read -r container; do
        log_info "Removing obsolete container: $container"
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
    done

    log_success "✅ Cleanup completed"
}

main() {
    case "${1:-backup}" in
    "backup")
        backup_configurations
        ;;
    "restore")
        if [[ -z "${2:-}" ]]; then
            log_error "Please specify backup directory to restore from"
            log_info "Usage: $0 restore /path/to/backup/directory"
            exit 1
        fi
        BACKUP_DIR="$2"
        if [[ ! -f "$BACKUP_DIR/restore.sh" ]]; then
            log_error "Invalid backup directory: $BACKUP_DIR"
            exit 1
        fi
        "$BACKUP_DIR/restore.sh" --restore
        ;;
    "cleanup")
        cleanup_obsolete
        ;;
    "verify")
        "$BACKUP_DIR/verify.sh" 2>/dev/null || {
            log_info "Running verification from current configuration..."
            # Run a quick health check
            cd "$SCRIPTS_DIR"
            ./health-check.sh
        }
        ;;
    *)
        log_info "AI Research Platform Backup & Restore Tool"
        log_info "Usage: $0 [backup|restore|cleanup|verify]"
        log_info ""
        log_info "Commands:"
        log_info "  backup  - Create comprehensive platform backup (default)"
        log_info "  restore - Restore from backup directory"
        log_info "  cleanup - Remove obsolete configurations and containers"
        log_info "  verify  - Verify platform configuration alignment"
        ;;
    esac
}

main "$@"
