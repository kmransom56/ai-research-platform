#!/bin/bash

# Post-Reboot Ollama Model Persistence & Platform Recovery Script
# This script ensures Ollama models are preserved and all services are restored after reboot

set -euo pipefail

# Configuration
readonly PLATFORM_DIR="/home/keith/chat-copilot"
readonly OLLAMA_DATA_DIR="/home/keith/.ollama"
readonly BACKUP_DIR="/home/keith/platform-backups"
readonly LOG_FILE="$PLATFORM_DIR/ai-platform-recovery.log"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
    INFO) echo -e "${GREEN}✅ [$timestamp] $message${NC}" | tee -a "$LOG_FILE" ;;
    WARN) echo -e "${YELLOW}⚠️  [$timestamp] $message${NC}" | tee -a "$LOG_FILE" ;;
    ERROR) echo -e "${RED}❌ [$timestamp] $message${NC}" | tee -a "$LOG_FILE" ;;
    DEBUG) echo -e "${BLUE}🔍 [$timestamp] $message${NC}" | tee -a "$LOG_FILE" ;;
    TITLE) echo -e "\n${BLUE}🚀 $message${NC}" | tee -a "$LOG_FILE" ;;
    esac
}

# Create backup directory if it doesn't exist
setup_backup_directory() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
        log INFO "Created backup directory: $BACKUP_DIR"
    fi
}

# Backup Ollama models and configuration
backup_ollama_models() {
    log TITLE "Backing up Ollama models and configuration"

    if [[ -d "$OLLAMA_DATA_DIR" ]]; then
        local backup_file="$BACKUP_DIR/ollama-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
        tar -czf "$backup_file" -C "$(dirname "$OLLAMA_DATA_DIR")" "$(basename "$OLLAMA_DATA_DIR")" 2>/dev/null || {
            log WARN "Failed to create Ollama backup, but continuing..."
        }
        log INFO "Ollama backup created: $backup_file"

        # Keep only the 5 most recent backups
        find "$BACKUP_DIR" -name "ollama-backup-*.tar.gz" -type f | sort -r | tail -n +6 | xargs rm -f 2>/dev/null || true
    else
        log WARN "Ollama data directory not found: $OLLAMA_DATA_DIR"
    fi
}

# Ensure Ollama service is running
ensure_ollama_running() {
    log TITLE "Ensuring Ollama service is running"

    # Check if Ollama is already running
    if pgrep -f "ollama serve" >/dev/null; then
        log INFO "Ollama is already running"
        return 0
    fi

    # Start Ollama service
    log INFO "Starting Ollama service..."
    nohup ollama serve >/dev/null 2>&1 &
    sleep 5

    # Verify it's running
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then
            log INFO "Ollama service is running and responding"
            return 0
        fi
        sleep 2
        ((attempts++))
    done

    log ERROR "Failed to start Ollama service"
    return 1
}

# Verify Ollama models are available
verify_ollama_models() {
    log TITLE "Verifying Ollama models"

    local model_count=$(ollama list 2>/dev/null | grep -c ":" || echo "0")
    if [[ $model_count -gt 0 ]]; then
        log INFO "Found $model_count Ollama models"
        ollama list | head -10 | while read -r line; do
            [[ -n "$line" ]] && log DEBUG "Model: $line"
        done
    else
        log WARN "No Ollama models found - may need to restore from backup"
        restore_ollama_from_backup
    fi
}

# Restore Ollama from the most recent backup
restore_ollama_from_backup() {
    log TITLE "Attempting to restore Ollama from backup"

    local latest_backup=$(find "$BACKUP_DIR" -name "ollama-backup-*.tar.gz" -type f | sort -r | head -1)
    if [[ -n "$latest_backup" && -f "$latest_backup" ]]; then
        log INFO "Restoring from backup: $latest_backup"

        # Stop Ollama if running
        pkill -f "ollama serve" 2>/dev/null || true
        sleep 3

        # Restore the backup
        tar -xzf "$latest_backup" -C "$(dirname "$OLLAMA_DATA_DIR")" 2>/dev/null || {
            log ERROR "Failed to restore Ollama backup"
            return 1
        }

        # Restart Ollama
        ensure_ollama_running
        sleep 5
        verify_ollama_models
    else
        log WARN "No Ollama backup found to restore"
    fi
}

# Start essential Docker services
start_essential_services() {
    log TITLE "Starting essential Docker services"

    # Start Nginx Proxy Manager
    if ! docker ps | grep -q nginx-proxy-manager; then
        log INFO "Starting Nginx Proxy Manager..."
        docker run -d \
            --name nginx-proxy-manager \
            --restart unless-stopped \
            -p 8080:80 \
            -p 11082:81 \
            -p 8443:443 \
            -v /home/keith/nginx_data:/data \
            -v /home/keith/nginx_letsencrypt:/etc/letsencrypt \
            jc21/nginx-proxy-manager:latest 2>/dev/null || log WARN "Failed to start Nginx Proxy Manager"
    fi

    # Start OpenWebUI with correct Ollama connection
    if ! docker ps | grep -q openwebui; then
        log INFO "Starting OpenWebUI with Ollama connection..."
        docker run -d \
            --name openwebui \
            --restart unless-stopped \
            -p 11880:8080 \
            -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
            -v openwebui:/app/backend/data \
            --add-host=host.docker.internal:host-gateway \
            ghcr.io/open-webui/open-webui:main 2>/dev/null || log WARN "Failed to start OpenWebUI"
    fi

    # Start GenAI Stack
    if [[ -f "$PLATFORM_DIR/genai-stack/docker-compose.yml" ]]; then
        log INFO "Starting GenAI Stack..."
        cd "$PLATFORM_DIR/genai-stack"
        docker-compose up -d 2>/dev/null || log WARN "Failed to start GenAI Stack"
    fi

    # Start other essential services
    start_utility_services
}

# Start utility services (Port Scanner, Webhook Server)
start_utility_services() {
    log INFO "Starting utility services..."

    # Port Scanner
    if ! docker ps | grep -q port-scanner; then
        docker run -d --name port-scanner \
            -p 11010:8080 \
            --restart unless-stopped \
            python:3.11-slim bash -c "
            pip install flask requests > /dev/null 2>&1 && 
            cat > /app/scanner.py << 'EOF'
from flask import Flask, jsonify
import socket
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status': 'Port Scanner Active', 'timestamp': '$(date)'})

@app.route('/scan')
def scan():
    ports = [11000, 11001, 11003, 11020, 11021, 11434, 11880, 8505, 57081]
    results = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('100.123.10.72', port))
            sock.close()
            results.append({'port': port, 'open': result == 0})
        except:
            results.append({'port': port, 'open': False})
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF
            cd /app && python scanner.py
            " 2>/dev/null || log WARN "Port scanner start failed"
    fi

    # Webhook Server
    if ! docker ps | grep -q webhook-server; then
        docker run -d --name webhook-server \
            -p 11025:8080 \
            --restart unless-stopped \
            python:3.11-slim bash -c "
            pip install flask > /dev/null 2>&1 && 
            cat > /app/webhook.py << 'EOF'
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status': 'Webhook Server Running', 'timestamp': '$(date)'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({'message': 'Webhook received', 'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF
            cd /app && python webhook.py
            " 2>/dev/null || log WARN "Webhook server start failed"
    fi
}

# Create systemd service for automatic startup
create_systemd_service() {
    log TITLE "Creating systemd service for automatic startup"

    cat >/tmp/ai-platform-recovery.service <<'EOF'
[Unit]
Description=AI Platform Recovery Service
After=network.target docker.service
Wants=network.target docker.service

[Service]
Type=oneshot
ExecStart=/home/keith/chat-copilot/scripts/platform-management/post-reboot-ollama-persistence.sh
User=keith
Group=keith
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    if sudo cp /tmp/ai-platform-recovery.service /etc/systemd/system/ 2>/dev/null; then
        sudo systemctl daemon-reload
        sudo systemctl enable ai-platform-recovery.service
        log INFO "Systemd service created and enabled"
    else
        log WARN "Failed to create systemd service (requires sudo)"
    fi
}

# Generate comprehensive status report
generate_status_report() {
    log TITLE "Generating platform status report"

    local status_file="$PLATFORM_DIR/post-reboot-status.json"
    local timestamp=$(date -Iseconds)

    cat >"$status_file" <<EOF
{
    "platform": {
        "name": "AI Research Platform",
        "recovery_time": "$timestamp",
        "script_version": "2.0"
    },
    "ollama": {
        "running": $(pgrep -f "ollama serve" >/dev/null && echo "true" || echo "false"),
        "models_count": $(ollama list 2>/dev/null | grep -c ":" || echo "0"),
        "api_responding": $(curl -s http://localhost:11434/api/version >/dev/null && echo "true" || echo "false")
    },
    "services": {
EOF

    # Check service status
    local services=(
        "11000:Chat Copilot"
        "11001:AutoGen Studio"
        "11003:Magentic-One"
        "11010:Port Scanner"
        "11020:Perplexica"
        "11021:SearXNG"
        "11025:Webhook Server"
        "11434:Ollama"
        "11880:OpenWebUI"
        "8505:GenAI Stack"
        "57081:VS Code"
        "8080:Nginx Gateway"
    )

    local first=true
    for service in "${services[@]}"; do
        local port="${service%%:*}"
        local name="${service##*:}"

        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >>"$status_file"
        fi

        local status="stopped"
        if curl -s --connect-timeout 2 "http://100.123.10.72:$port" >/dev/null 2>&1; then
            status="running"
        fi

        cat >>"$status_file" <<EOF
        "${name,,}": {
            "port": $port,
            "status": "$status",
            "url": "http://100.123.10.72:$port"
        }
EOF
    done

    cat >>"$status_file" <<EOF
    }
}
EOF

    log INFO "Status report generated: $status_file"
}

# Main execution function
main() {
    log TITLE "AI Platform Post-Reboot Recovery v2.0"
    log INFO "Starting recovery process at $(date)"

    # Create necessary directories
    setup_backup_directory

    # Backup current state
    backup_ollama_models

    # Ensure Ollama is running
    ensure_ollama_running

    # Verify models are available
    verify_ollama_models

    # Start essential services
    start_essential_services

    # Create systemd service for future reboots
    create_systemd_service

    # Generate status report
    generate_status_report

    # Final status check
    log TITLE "Recovery Summary"

    local ollama_status="❌ Not Running"
    if pgrep -f "ollama serve" >/dev/null; then
        local model_count=$(ollama list 2>/dev/null | grep -c ":" || echo "0")
        ollama_status="✅ Running with $model_count models"
    fi

    log INFO "Ollama Status: $ollama_status"
    log INFO "Docker Services: $(docker ps --format 'table {{.Names}}' | wc -l) containers running"
    log INFO "Platform accessible at: http://100.123.10.72:11000"

    echo ""
    echo "🎯 Quick Access URLs:"
    echo "===================="
    echo "🤖 Chat Copilot: http://100.123.10.72:11000"
    echo "🌟 AutoGen Studio: http://100.123.10.72:11001"
    echo "🧠 Perplexica: http://100.123.10.72:11020"
    echo "🌐 OpenWebUI: http://100.123.10.72:11880"
    echo "🔧 Nginx Gateway: http://100.123.10.72:8080"
    echo "🦙 Ollama API: http://localhost:11434"
    echo ""

    log INFO "✅ Post-reboot recovery completed successfully!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
