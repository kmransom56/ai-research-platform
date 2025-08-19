#!/bin/bash
#
# Comprehensive Service Startup Script
# Starts all AI Research Platform services at boot or on-demand
# Uses the comprehensive service registry for intelligent startup sequencing
#

# Set script directory and platform root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_AI_STACK="$PLATFORM_ROOT/python/ai-stack"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="$PLATFORM_ROOT/logs/startup-all-services.log"
mkdir -p "$PLATFORM_ROOT/logs"

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if service is running on port
check_service_port() {
    local port=$1
    local timeout=${2:-5}
    
    if timeout "$timeout" bash -c "</dev/tcp/localhost/$port"; then
        return 0
    else
        return 1
    fi
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    log_info "Waiting for $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_service_port "$port" 2; then
            log_success "$service_name is ready (attempt $attempt/$max_attempts)"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 2
        ((attempt++))
    done
    
    log_warning "$service_name not ready after $max_attempts attempts"
    return 1
}

# Start a Python service
start_python_service() {
    local service_name=$1
    local script_name=$2
    local port=$3
    local work_dir=$4
    local extra_args=${5:-""}
    
    log_info "Starting $service_name..."
    
    if check_service_port "$port"; then
        log_success "$service_name already running on port $port"
        return 0
    fi
    
    cd "$work_dir" || {
        log_error "Cannot change to directory: $work_dir"
        return 1
    }
    
    # Create PID directory
    mkdir -p "$PLATFORM_ROOT/pids"
    
    # Start the service in background
    nohup python3 "$script_name" $extra_args > "$PLATFORM_ROOT/logs/$service_name.log" 2>&1 &
    local pid=$!
    echo $pid > "$PLATFORM_ROOT/pids/$service_name.pid"
    
    # Wait for service to be ready
    if wait_for_service "$service_name" "$port" 20; then
        log_success "$service_name started successfully (PID: $pid)"
        return 0
    else
        log_error "Failed to start $service_name"
        return 1
    fi
}

# Start a Node.js service
start_node_service() {
    local service_name=$1
    local script_name=$2
    local port=$3
    local work_dir=$4
    
    log_info "Starting $service_name..."
    
    if check_service_port "$port"; then
        log_success "$service_name already running on port $port"
        return 0
    fi
    
    cd "$work_dir" || {
        log_error "Cannot change to directory: $work_dir"
        return 1
    }
    
    mkdir -p "$PLATFORM_ROOT/pids"
    
    nohup node "$script_name" > "$PLATFORM_ROOT/logs/$service_name.log" 2>&1 &
    local pid=$!
    echo $pid > "$PLATFORM_ROOT/pids/$service_name.pid"
    
    if wait_for_service "$service_name" "$port" 15; then
        log_success "$service_name started successfully (PID: $pid)"
        return 0
    else
        log_error "Failed to start $service_name"
        return 1
    fi
}

# Start a .NET service  
start_dotnet_service() {
    local service_name=$1
    local port=$2
    local work_dir=$3
    local extra_args=${4:-""}
    
    log_info "Starting $service_name..."
    
    if check_service_port "$port"; then
        log_success "$service_name already running on port $port"
        return 0
    fi
    
    cd "$work_dir" || {
        log_error "Cannot change to directory: $work_dir"
        return 1
    }
    
    mkdir -p "$PLATFORM_ROOT/pids"
    
    nohup dotnet run --urls "http://0.0.0.0:$port" $extra_args > "$PLATFORM_ROOT/logs/$service_name.log" 2>&1 &
    local pid=$!
    echo $pid > "$PLATFORM_ROOT/pids/$service_name.pid"
    
    if wait_for_service "$service_name" "$port" 30; then
        log_success "$service_name started successfully (PID: $pid)"
        return 0
    else
        log_error "Failed to start $service_name"
        return 1
    fi
}

# Start vLLM service
start_vllm_service() {
    local service_name=$1
    local model=$2
    local port=$3
    local gpu_id=${4:-0}
    local extra_args=${5:-""}
    
    log_info "Starting vLLM $service_name with model $model..."
    
    if check_service_port "$port"; then
        log_success "vLLM $service_name already running on port $port"
        return 0
    fi
    
    cd "$PYTHON_AI_STACK" || {
        log_error "Cannot change to AI Stack directory"
        return 1
    }
    
    mkdir -p "$PLATFORM_ROOT/pids"
    
    # Start vLLM with specific GPU
    CUDA_VISIBLE_DEVICES=$gpu_id nohup vllm serve "$model" \
        --host 0.0.0.0 \
        --port "$port" \
        $extra_args > "$PLATFORM_ROOT/logs/vllm-$service_name.log" 2>&1 &
    local pid=$!
    echo $pid > "$PLATFORM_ROOT/pids/vllm-$service_name.pid"
    
    if wait_for_service "vLLM $service_name" "$port" 60; then
        log_success "vLLM $service_name started successfully (PID: $pid)"
        return 0
    else
        log_error "Failed to start vLLM $service_name"
        return 1
    fi
}

# Start Docker Compose service
start_docker_service() {
    local service_name=$1
    local compose_file=$2
    local service_key=$3
    
    log_info "Starting Docker service: $service_name"
    
    cd "$PLATFORM_ROOT" || {
        log_error "Cannot change to platform root"
        return 1
    }
    
    if docker-compose -f "$compose_file" ps "$service_key" | grep -q "Up"; then
        log_success "$service_name already running"
        return 0
    fi
    
    docker-compose -f "$compose_file" up -d "$service_key"
    if [ $? -eq 0 ]; then
        log_success "$service_name started successfully"
        return 0
    else
        log_error "Failed to start $service_name"
        return 1
    fi
}

# Check system dependencies
check_dependencies() {
    log_info "Checking system dependencies..."
    
    local deps=("python3" "node" "dotnet" "docker" "docker-compose" "vllm")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        log_success "All dependencies available"
        return 0
    else
        log_error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
}

# Main startup sequence
startup_services() {
    log_info "Starting AI Research Platform services..."
    
    # Phase 1: Infrastructure Services
    log_info "=== Phase 1: Infrastructure Services ==="
    
    start_node_service "webhook-server" "webhook-server.js" 11025 "$PLATFORM_ROOT/runtime-data"
    
    # Phase 2: Core Backend Services  
    log_info "=== Phase 2: Core Backend Services ==="
    
    start_dotnet_service "chat-copilot-backend" 11000 "$PLATFORM_ROOT/webapi"
    
    # Phase 3: AI Stack Services
    log_info "=== Phase 3: AI Stack Services ==="
    
    # Start AI Gateway first
    start_python_service "ai-gateway" "api_gateway.py" 9000 "$PYTHON_AI_STACK"
    
    # Start AI Monitor
    start_python_service "ai-monitor" "ai_monitor.py" 8090 "$PYTHON_AI_STACK" || log_warning "AI Monitor not available, continuing..."
    
    # Phase 4: vLLM Services (if GPUs available)
    log_info "=== Phase 4: vLLM Services ==="
    
    if nvidia-smi &>/dev/null; then
        log_info "NVIDIA GPUs detected, starting vLLM services..."
        start_vllm_service "reasoning" "distilgpt2" 8000 0 "--max-model-len 512 --gpu-memory-utilization 0.3"
        start_vllm_service "general" "distilgpt2" 8001 1 "--max-model-len 512 --gpu-memory-utilization 0.2"
        start_vllm_service "coding" "microsoft/DialoGPT-small" 8002 0 "--max-model-len 256 --gpu-memory-utilization 0.2"
    else
        log_warning "No NVIDIA GPUs detected, skipping vLLM services"
    fi
    
    # Phase 5: Agent Services
    log_info "=== Phase 5: Agent Services ==="
    
    start_python_service "autogen-studio" "autogen_studio_server.py" 11001 "$PLATFORM_ROOT/python/autogen" || log_warning "AutoGen Studio not available, continuing..."
    start_python_service "magentic-one" "magentic_one_server.py" 11003 "$PLATFORM_ROOT/python/magentic-one" || log_warning "Magentic-One not available, continuing..."
    
    # Phase 6: Utility Services
    log_info "=== Phase 6: Utility Services ==="
    
    start_python_service "port-scanner" "port-scanner.py" 11010 "$PLATFORM_ROOT/python/tools" "--host 0.0.0.0 --port 11010"
    
    # Phase 7: Docker Services
    log_info "=== Phase 7: Docker Services ==="
    
    if command -v docker-compose &> /dev/null; then
        start_docker_service "neo4j" "docker-compose.simple.yml" "neo4j" || log_warning "Neo4j not available, continuing..."
        start_docker_service "grafana" "docker-compose.simple.yml" "grafana" || log_warning "Grafana not available, continuing..."
        start_docker_service "prometheus" "docker-compose.simple.yml" "prometheus" || log_warning "Prometheus not available, continuing..."
        start_docker_service "perplexica" "Perplexica/docker-compose.yaml" "perplexica" || log_warning "Perplexica not available, continuing..."
    fi
    
    # Phase 8: Network Management Services
    log_info "=== Phase 8: Network Management Services ==="
    
    start_python_service "restaurant-voice" "restaurant-equipment-voice-interface.py" 11032 "$PLATFORM_ROOT/network-agents" || log_warning "Restaurant voice interface not available, continuing..."
    start_python_service "network-voice" "speech-web-interface.py" 11030 "$PLATFORM_ROOT/network-agents" || log_warning "Network voice interface not available, continuing..."
    start_python_service "network-hub" "network-management-hub.py" 11040 "$PLATFORM_ROOT/network-agents" || log_warning "Network hub not available, continuing..."
    
    log_success "Service startup sequence completed!"
}

# Service health check
check_all_services() {
    log_info "Checking health of all services..."
    
    # Get service health from the comprehensive registry
    cd "$PYTHON_AI_STACK"
    python3 -c "
from comprehensive_service_registry import comprehensive_registry
import json

health = comprehensive_registry.get_all_services_health()
print(json.dumps(health, indent=2))
" || log_error "Failed to get service health from registry"
}

# Stop all services
stop_services() {
    log_info "Stopping all platform services..."
    
    # Stop Python services
    for pidfile in "$PLATFORM_ROOT/pids"/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            service_name=$(basename "$pidfile" .pid)
            
            if kill -0 "$pid" 2>/dev/null; then
                log_info "Stopping $service_name (PID: $pid)"
                kill "$pid"
                sleep 2
                
                # Force kill if still running
                if kill -0 "$pid" 2>/dev/null; then
                    log_warning "Force killing $service_name"
                    kill -9 "$pid"
                fi
            fi
            
            rm -f "$pidfile"
        fi
    done
    
    # Stop Docker services
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$PLATFORM_ROOT/docker-compose.simple.yml" down 2>/dev/null || true
        docker-compose -f "$PLATFORM_ROOT/Perplexica/docker-compose.yaml" down 2>/dev/null || true
    fi
    
    log_success "All services stopped"
}

# Restart all services
restart_services() {
    log_info "Restarting all platform services..."
    stop_services
    sleep 5
    startup_services
}

# Get startup commands from registry
get_startup_commands() {
    log_info "Getting startup commands from service registry..."
    
    cd "$PYTHON_AI_STACK"
    python3 -c "
from comprehensive_service_registry import comprehensive_registry
import json

commands = comprehensive_registry.get_startup_commands()
for cmd in commands:
    print(f'Service: {cmd[\"service\"]}')
    if 'command' in cmd:
        print(f'  Command: {cmd[\"command\"]}')
        print(f'  Directory: {cmd.get(\"directory\", \"N/A\")}')
    if 'docker_service' in cmd:
        print(f'  Docker Service: {cmd[\"docker_service\"]}')
    if 'systemd_service' in cmd:
        print(f'  Systemd Service: {cmd[\"systemd_service\"]}')
    print(f'  Port: {cmd[\"port\"]}')
    print(f'  Description: {cmd[\"description\"]}')
    print()
"
}

# Main command handling
case "${1:-start}" in
    start)
        log "=== Starting AI Research Platform Services ==="
        check_dependencies
        startup_services
        check_all_services
        ;;
    stop)
        log "=== Stopping AI Research Platform Services ==="
        stop_services
        ;;
    restart)
        log "=== Restarting AI Research Platform Services ==="
        restart_services
        check_all_services
        ;;
    status|health)
        log "=== AI Research Platform Service Health ==="
        check_all_services
        ;;
    commands)
        log "=== AI Research Platform Startup Commands ==="
        get_startup_commands
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health|commands}"
        echo ""
        echo "Commands:"
        echo "  start     - Start all platform services"
        echo "  stop      - Stop all platform services"  
        echo "  restart   - Restart all platform services"
        echo "  status    - Check health of all services"
        echo "  health    - Alias for status"
        echo "  commands  - Show startup commands from registry"
        exit 1
        ;;
esac

exit 0