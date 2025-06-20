#!/bin/bash
# AI Research Platform Startup Script - Clean & Maintainable
# Standardized Port Range: 11000-12000
# Author: Automated Infrastructure Management
# Version: 3.0

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

# Directories
readonly PLATFORM_DIR="/home/keith/chat-copilot"
readonly LOGS_DIR="$PLATFORM_DIR/logs"
readonly PIDS_DIR="$PLATFORM_DIR/pids"
readonly CONFIG_DIR="$PLATFORM_DIR/config"

# Timeouts and retries
readonly SERVICE_TIMEOUT=30
readonly SLEEP_INTERVAL=3
readonly MAX_STARTUP_TIME=300

# Tailscale configuration
readonly TAILSCALE_DOMAIN="ubuntuaicodeserver-1.tail5137b4.ts.net"
readonly TAILSCALE_NET="tail5137b4"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# =============================================================================
# SERVICE DEFINITIONS
# =============================================================================

# Core AI Services
declare -A CORE_SERVICES=(
    ["chat-copilot-backend"]="11000|cd $PLATFORM_DIR/webapi && dotnet run --urls http://0.0.0.0:11000|/healthz"
    ["autogen-studio"]="11001|autogenstudio ui --port 11001 --host 0.0.0.0|/"
    ["webhook-server"]="11002|node $PLATFORM_DIR/webhook-server.js|/health"
    ["magentic-one"]="11003|python $PLATFORM_DIR/magentic_one_server.py|/health"
)

# Infrastructure Services
declare -A INFRA_SERVICES=(
    ["port-scanner"]="11010|cd /home/keith/port-scanner-material-ui && node backend/server.js|/nmap-status"
)

# Docker Services
declare -A DOCKER_SERVICES=(
    ["nginx-proxy"]="11080|$PLATFORM_DIR/docker-compose.nginx-proxy-manager.yml|/"
    ["fortinet-manager"]="3001|/home/keith/fortinet-manager/docker-compose.yml|/"
    ["caddy-proxy"]="2019|$PLATFORM_DIR/docker-compose.caddy.yml|/config/"
    ["perplexica-stack"]="11020|/home/keith/perplexcia/compose.yaml|/"
)

# External Services (for health checks only)
declare -A EXTERNAL_SERVICES=(
    ["ollama"]="11434|localhost|/api/version"
    ["openwebui"]="11880|100.123.10.72|/api/config"
    ["vscode-web"]="57081|100.123.10.72|/"
)
# =============================================================================
# ENHANCED DOCKER SERVICE FUNCTION (Optional improvement)
# =============================================================================

start_docker_service_enhanced() {
    local name=$1
    local port=$2
    local compose_file=$3
    local health_path=$4

    # If port already bound on host OR another container is publishing it, assume service is up/managed elsewhere
    if is_port_in_use "$port" || is_docker_port_published "$port"; then
        log INFO "$name port $port already in use by another process or container – skipping docker-compose up."
        return 0
    fi

    log DEBUG "Starting Docker service: $name"

    if [[ ! -f "$compose_file" ]]; then
        log ERROR "Docker compose file not found: $compose_file"
        return 1
    fi

    # Check if services are already running
    if docker-compose -f "$compose_file" ps --services --filter "status=running" | grep -q .; then
        log INFO "$name stack already has running services"

        # Still do health check
        local health_url="http://100.123.10.72:${port}${health_path}"
        if wait_for_service "$name" "$health_url" 10; then
            log INFO "$name is healthy"
            return 0
        fi
    fi

    # Start the stack
    log INFO "Starting $name Docker stack..."
    if docker-compose -f "$compose_file" up -d; then
        log INFO "$name Docker stack started"

        # For Perplexica specifically, check both services
        if [[ "$name" == "perplexica-stack" ]]; then
            log INFO "Checking Perplexica services..."
            wait_for_service "SearXNG" "http://100.123.10.72:11021/searxng" 30
            wait_for_service "Perplexica" "http://100.123.10.72:11020/" 30
        else
            # Standard health check
            local health_url="http://100.123.10.72:${port}${health_path}"
            wait_for_service "$name" "$health_url" 30
        fi
    else
        # If failure due to port already allocated, assume service is already running
        if is_port_in_use "$port" || is_docker_port_published "$port"; then
            log INFO "$name appears to be already running (port $port bound). Skipping."
            return 0
        fi
        log ERROR "Failed to start $name"
        return 1
    fi
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
    INFO) echo -e "${GREEN}✅ [$timestamp] $message${NC}" ;;
    WARN) echo -e "${YELLOW}⚠️  [$timestamp] $message${NC}" ;;
    ERROR) echo -e "${RED}❌ [$timestamp] $message${NC}" ;;
    DEBUG) echo -e "${BLUE}🔍 [$timestamp] $message${NC}" ;;
    TITLE) echo -e "\n${BLUE}🚀 $message${NC}" ;;
    esac
}

check_dependencies() {
    log TITLE "Checking System Dependencies"

    local deps=("curl" "docker" "docker-compose" "node" "python3" "dotnet")
    local missing=()

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &>/dev/null; then
            missing+=("$dep")
            log WARN "$dep not found"
        else
            log INFO "$dep available"
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log ERROR "Missing dependencies: ${missing[*]}"
        log INFO "Some services may not start properly"
    fi
}

setup_directories() {
    log TITLE "Setting Up Directory Structure"

    local dirs=("$LOGS_DIR" "$PIDS_DIR" "$CONFIG_DIR")
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log INFO "Created directory: $dir"
        fi
    done
}

wait_for_network() {
    log TITLE "Checking Network Connectivity"

    local timeout=60
    local count=0

    while ! ping -c 1 8.8.8.8 &>/dev/null; do
        if [ $count -ge $timeout ]; then
            log ERROR "Network timeout after ${timeout}s"
            exit 1
        fi
        log DEBUG "Waiting for network... ($count/$timeout)"
        sleep $SLEEP_INTERVAL
        ((count += SLEEP_INTERVAL))
    done

    log INFO "Network connectivity confirmed"
}

check_tailscale() {
    log TITLE "Checking Tailscale Status"

    if ! command -v tailscale &>/dev/null; then
        log WARN "Tailscale not installed"
        return 1
    fi

    if ! tailscale status &>/dev/null; then
        log WARN "Tailscale not connected - run 'tailscale up'"
        return 1
    fi

    local tailscale_ip=$(tailscale ip -4 2>/dev/null || echo "Unknown")
    log INFO "Tailscale connected - IP: $tailscale_ip"

    if tailscale status | grep -q "$TAILSCALE_DOMAIN"; then
        log INFO "Tailscale domain available: $TAILSCALE_DOMAIN"
        return 0
    else
        log WARN "Tailscale domain may not be available"
        return 1
    fi
}

setup_uv_environment() {
    log TITLE "Setting Up UV Python Environment"

    if ! command -v uv &>/dev/null; then
        log WARN "UV not found - installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.bashrc
    fi

    cd "$PLATFORM_DIR"
    if [[ ! -d ".venv" ]]; then
        uv venv --python 3.11
        log INFO "Created UV virtual environment"
    fi

    source .venv/bin/activate
    log INFO "UV environment activated"
}

# Utility: Check if a TCP port is already bound (LISTEN state)
is_port_in_use() {
    local port=$1
    # `ss` is shipped with iproute2 on most modern Linux distributions
    # We look for exact matches to ":<port>" at the end of the local address column.
    if ss -ltn | awk '{print $4}' | grep -q "[:.]$port$"; then
        return 0 # port is in use
    else
        return 1 # port is free
    fi
}

# Returns 0 if a Docker container is already publishing the given host TCP port
is_docker_port_published() {
    local port=$1
    if docker ps --format '{{.Ports}}' | grep -E "[:.]${port}->" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# SERVICE MANAGEMENT
# =============================================================================

wait_for_service() {
    local name=$1
    local url=$2
    local max_attempts=${3:-$SERVICE_TIMEOUT}

    log DEBUG "Waiting for $name to be ready..."

    for ((i = 1; i <= max_attempts; i++)); do
        if curl -s --max-time 5 "$url" &>/dev/null; then
            log INFO "$name is ready (attempt $i/$max_attempts)"
            return 0
        fi

        if [ $i -lt $max_attempts ]; then
            log DEBUG "Attempt $i/$max_attempts - waiting for $name..."
            sleep $SLEEP_INTERVAL
        fi
    done

    log WARN "$name not ready after $max_attempts attempts"
    return 1
}

start_process_service() {
    local name=$1
    local port=$2
    local command=$3
    local health_path=$4
    local use_uv=${5:-false}

    # Health-check URL used in several places below
    local health_url="http://100.123.10.72:${port}${health_path}"

    # Skip start if something is already listening on the desired port *and* looks healthy
    if is_port_in_use "$port"; then
        log INFO "$name appears to be running already on port $port"
        if wait_for_service "$name" "$health_url" 5; then
            log INFO "$name is healthy – skipping start"
            return 0
        else
            log WARN "$name port $port is busy but health-check failed. Will not attempt automatic restart to avoid conflicts."
            return 1
        fi
    fi

    log DEBUG "Starting $name..."

    local pidfile="$PIDS_DIR/${name}.pid"
    local logfile="$LOGS_DIR/${name}.log"

    # Stop existing process
    if [[ -f "$pidfile" ]]; then
        local old_pid=$(cat "$pidfile" 2>/dev/null || echo "")
        if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
            log DEBUG "Stopping existing $name process (PID: $old_pid)"
            kill "$old_pid" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$pidfile"
    fi

    # Prepare command
    if [ "$use_uv" = "true" ]; then
        command="cd $PLATFORM_DIR && source .venv/bin/activate && $command"
    fi

    # Start new process
    nohup bash -c "$command" >"$logfile" 2>&1 &
    local new_pid=$!
    echo $new_pid >"$pidfile"

    log INFO "Started $name (PID: $new_pid, Port: $port)"

    # Health check
    if wait_for_service "$name" "$health_url" 20; then
        log INFO "$name is healthy"
    else
        log WARN "$name may not be responding properly"
    fi
}

start_docker_service() {
    local name=$1
    local port=$2
    local compose_file=$3
    local health_path=$4

    # If port already bound on host OR another container is publishing it, assume service is up/managed elsewhere
    if is_port_in_use "$port" || is_docker_port_published "$port"; then
        log INFO "$name port $port already in use by another process or container – skipping docker-compose up."
        return 0
    fi

    log DEBUG "Starting Docker service: $name"

    if [[ ! -f "$compose_file" ]]; then
        log ERROR "Docker compose file not found: $compose_file"
        return 1
    fi

    if docker-compose -f "$compose_file" ps | grep -q "Up"; then
        log INFO "$name already running"
    else
        if docker-compose -f "$compose_file" up -d; then
            log INFO "$name Docker stack started"

            local health_url="http://100.123.10.72:${port}${health_path}"
            wait_for_service "$name" "$health_url" 30
        else
            # If failure due to port already allocated, assume service is already running
            if is_port_in_use "$port" || is_docker_port_published "$port"; then
                log INFO "$name appears to be already running (port $port bound). Skipping."
                return 0
            fi
            log ERROR "Failed to start $name"
            return 1
        fi
    fi
}

check_external_service() {
    local name=$1
    local port=$2
    local host=$3
    local health_path=$4

    local url="http://${host}:${port}${health_path}"

    if curl -s --max-time 5 "$url" &>/dev/null; then
        log INFO "$name is running (Port: $port)"
    else
        log WARN "$name not responding ($url)"
    fi
}

# =============================================================================
# SERVICE STARTUP ORCHESTRATION
# =============================================================================

start_core_services() {
    log TITLE "Starting Core AI Services"

    for service_name in "${!CORE_SERVICES[@]}"; do
        IFS='|' read -r port command health_path <<<"${CORE_SERVICES[$service_name]}"

        # Determine if service needs UV environment
        local use_uv=false
        case $service_name in
        "autogen-studio" | "magentic-one") use_uv=true ;;
        esac

        start_process_service "$service_name" "$port" "$command" "$health_path" "$use_uv"
    done
}

start_infrastructure_services() {
    log TITLE "Starting Infrastructure Services"

    for service_name in "${!INFRA_SERVICES[@]}"; do
        IFS='|' read -r port command health_path <<<"${INFRA_SERVICES[$service_name]}"
        start_process_service "$service_name" "$port" "$command" "$health_path"
    done
}

start_docker_services() {
    log TITLE "Starting Docker Services"

    for service_name in "${!DOCKER_SERVICES[@]}"; do
        IFS='|' read -r port compose_file health_path <<<"${DOCKER_SERVICES[$service_name]}"
        start_docker_service "$service_name" "$port" "$compose_file" "$health_path"
    done
}

check_external_services() {
    log TITLE "Checking External Services"

    for service_name in "${!EXTERNAL_SERVICES[@]}"; do
        IFS='|' read -r port host health_path <<<"${EXTERNAL_SERVICES[$service_name]}"
        check_external_service "$service_name" "$port" "$host" "$health_path"
    done
}

# =============================================================================
# HEALTH MONITORING
# =============================================================================

generate_status_report() {
    log TITLE "Generating Platform Status Report"

    local status_file="$PLATFORM_DIR/platform-status.json"
    local tailscale_available=false
    local tailscale_ip="N/A"

    if check_tailscale; then
        tailscale_available=true
        tailscale_ip=$(tailscale ip -4 2>/dev/null || echo "N/A")
    fi

    cat >"$status_file" <<EOF
{
    "platform": {
        "name": "AI Research Platform",
        "version": "3.0",
        "startup_time": "$(date -Iseconds)",
        "port_range": "11000-12000"
    },
    "tailscale": {
        "available": $tailscale_available,
        "domain": "$TAILSCALE_DOMAIN",
        "ip": "$tailscale_ip"
    },
    "services": {
EOF

    # Add service status
    local first=true
    for category in "CORE_SERVICES" "INFRA_SERVICES" "DOCKER_SERVICES" "EXTERNAL_SERVICES"; do
        declare -n services_ref=$category

        if [ "$first" = true ]; then
            first=false
        else
            echo "," >>"$status_file"
        fi

        echo "        \"${category,,}\": {" >>"$status_file"

        local service_first=true
        for service_name in "${!services_ref[@]}"; do
            IFS='|' read -r port _ health_path <<<"${services_ref[$service_name]}"

            if [ "$service_first" = true ]; then
                service_first=false
            else
                echo "," >>"$status_file"
            fi

            local host="100.123.10.72"
            if [[ "$category" == "EXTERNAL_SERVICES" ]]; then
                IFS='|' read -r port host health_path <<<"${services_ref[$service_name]}"
            fi

            local status="stopped"
            if curl -s --max-time 5 "http://${host}:${port}${health_path}" &>/dev/null; then
                status="running"
            fi

            cat >>"$status_file" <<EOF
            "$service_name": {
                "port": $port,
                "status": "$status",
                "local_url": "http://${host}:${port}",
                "tailscale_url": "https://${service_name}.${TAILSCALE_DOMAIN}/"
            }
EOF
        done

        echo "        }" >>"$status_file"
    done

    cat >>"$status_file" <<EOF
    }
}
EOF

    log INFO "Status report generated: $status_file"
}
# =============================================================================
# UPDATED ACCESS INFORMATION DISPLAY
# =============================================================================

display_access_information() {
    log TITLE "Platform Access Information"

    echo -e "\n${GREEN}🏠 LOCAL ACCESS (via Caddy SSL):${NC}"
    echo "   🤖 Chat Copilot: https://copilot.$TAILSCALE_DOMAIN"
    echo "   🌟 AutoGen Studio: https://autogen.$TAILSCALE_DOMAIN"
    echo "   💫 Magentic-One: https://magentic.$TAILSCALE_DOMAIN"
    echo "   🔗 Webhook Server: https://webhook.$TAILSCALE_DOMAIN"
    echo "   🔍 Port Scanner: https://portscanner.$TAILSCALE_DOMAIN"

    echo -e "\n${BLUE}🛠️ INFRASTRUCTURE:${NC}"
    echo "   🔧 Nginx Proxy: https://nginx.$TAILSCALE_DOMAIN"
    echo "   🦙 Ollama LLM: https://ollama.$TAILSCALE_DOMAIN"
    echo "   💻 VS Code Web: https://vscode.$TAILSCALE_DOMAIN"

    echo -e "\n${GREEN}🔍 SEARCH & AI:${NC}"
    echo "   🧠 Perplexica: https://perplexica.$TAILSCALE_DOMAIN"
    echo "   🔎 SearXNG: https://searxng.$TAILSCALE_DOMAIN"
    echo "   🌐 OpenWebUI: https://openwebui.$TAILSCALE_DOMAIN"

    echo -e "\n${YELLOW}🔗 DIRECT ACCESS (HTTP):${NC}"
    echo "   🤖 Chat Copilot: http://$TAILSCALE_DOMAIN:11000"
    echo "   🌟 AutoGen Studio: http://$TAILSCALE_DOMAIN:11001"
    echo "   💫 Magentic-One: http://$TAILSCALE_DOMAIN:11003"

    if check_tailscale; then
        echo -e "\n${GREEN}📱 TAILSCALE ACCESS:${NC}"
        echo "   🌐 Main Hub: https://$TAILSCALE_DOMAIN"
        echo "   🤖 All Services: https://{subdomain}.$TAILSCALE_DOMAIN"
        echo -e "\n${YELLOW}📱 Mobile Setup:${NC}"
        echo "   1. Install Tailscale app"
        echo "   2. Connect with same account"
        echo "   3. Bookmark: https://$TAILSCALE_DOMAIN"
    else
        echo -e "\n${YELLOW}📱 TAILSCALE SETUP:${NC}"
        echo "   Install: curl -fsSL https://tailscale.com/install.sh | sh"
        echo "   Connect: sudo tailscale up"
    fi

    echo -e "\n${GREEN}📁 MANAGEMENT:${NC}"
    echo "   📝 Logs: $LOGS_DIR"
    echo "   🔢 PIDs: $PIDS_DIR"
    echo "   📊 Status: $PLATFORM_DIR/platform-status.json"
}
# =============================================================================
# MAIN EXECUTION
# =============================================================================

cleanup() {
    log INFO "Cleaning up on exit..."
    # Add any cleanup tasks here
}

main() {
    trap cleanup EXIT

    log TITLE "AI Research Platform Startup v3.0"
    log INFO "Timestamp: $(date)"
    log INFO "User: $(whoami)"
    log INFO "Platform Directory: $PLATFORM_DIR"

    # Phase 1: Prerequisites
    check_dependencies
    setup_directories
    wait_for_network
    setup_uv_environment

    # Phase 2: Service Startup
    start_core_services
    start_infrastructure_services
    start_docker_services

    # Phase 3: Health Checks
    sleep 5 # Allow services to initialize
    check_external_services

    # Phase 4: Reporting
    generate_status_report
    display_access_information

    log INFO "✅ AI Research Platform startup complete!"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
