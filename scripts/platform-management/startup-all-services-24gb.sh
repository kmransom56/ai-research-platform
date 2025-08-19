#!/bin/bash
#
# 24GB VRAM Optimized Service Startup Script
# Intelligently manages services for systems with 24GB VRAM
# Prioritizes memory efficiency and prevents GPU OOM errors
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
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="$PLATFORM_ROOT/logs/startup-24gb-services.log"
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

log_memory() {
    echo -e "${MAGENTA}[MEMORY]${NC} $1" | tee -a "$LOG_FILE"
}

# Check GPU memory availability
check_gpu_memory() {
    if command -v nvidia-smi &> /dev/null; then
        local available_memory=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
        local total_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        local used_memory=$((total_memory - available_memory))
        local usage_percent=$((used_memory * 100 / total_memory))
        
        log_memory "GPU Memory: ${used_memory}MB used / ${total_memory}MB total (${usage_percent}%)"
        
        # Return 0 if we have enough memory (less than 80% used)
        if [ $usage_percent -lt 80 ]; then
            return 0
        else
            return 1
        fi
    else
        log_warning "nvidia-smi not available, assuming no GPU"
        return 1
    fi
}

# Check system memory
check_system_memory() {
    local total_mem=$(free -m | awk 'NR==2{printf "%d", $2}')
    local used_mem=$(free -m | awk 'NR==2{printf "%d", $3}')
    local usage_percent=$((used_mem * 100 / total_mem))
    
    log_memory "System Memory: ${used_mem}MB used / ${total_mem}MB total (${usage_percent}%)"
    
    # Return 0 if we have enough memory (less than 70% used)
    if [ $usage_percent -lt 70 ]; then
        return 0
    else
        return 1
    fi
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

# Wait for service with memory monitoring
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=${3:-20}
    local attempt=1
    
    log_info "Waiting for $service_name on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_service_port "$port" 2; then
            log_success "$service_name is ready (attempt $attempt/$max_attempts)"
            check_gpu_memory  # Monitor memory after service start
            return 0
        fi
        
        # Check for memory issues every 5 attempts
        if [ $((attempt % 5)) -eq 0 ]; then
            if ! check_gpu_memory; then
                log_warning "High GPU memory usage detected while starting $service_name"
            fi
            if ! check_system_memory; then
                log_warning "High system memory usage detected"
            fi
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for $service_name..."
        sleep 3
        ((attempt++))
    done
    
    log_warning "$service_name not ready after $max_attempts attempts"
    return 1
}

# Start vLLM service with memory optimization
start_vllm_service_optimized() {
    local service_name=$1
    local model=$2
    local port=$3
    local gpu_util=$4
    local max_len=$5
    local memory_desc=$6
    
    log_info "Starting vLLM $service_name ($memory_desc expected)"
    
    if check_service_port "$port"; then
        log_success "vLLM $service_name already running on port $port"
        return 0
    fi
    
    # Check if we have enough GPU memory before starting
    if ! check_gpu_memory; then
        log_warning "High GPU memory usage - may cause OOM for $service_name"
        log_info "Consider stopping other GPU services first"
    fi
    
    cd "$PYTHON_AI_STACK" || {
        log_error "Cannot change to AI Stack directory"
        return 1
    }
    
    mkdir -p "$PLATFORM_ROOT/pids"
    
    # Start vLLM with optimized parameters for 24GB system
    CUDA_VISIBLE_DEVICES=0 nohup vllm serve "$model" \
        --host 0.0.0.0 \
        --port "$port" \
        --gpu-memory-utilization "$gpu_util" \
        --max-model-len "$max_len" \
        --swap-space 4 \
        --disable-log-requests > "$PLATFORM_ROOT/logs/vllm-$service_name.log" 2>&1 &
    local pid=$!
    echo $pid > "$PLATFORM_ROOT/pids/vllm-$service_name.pid"
    
    if wait_for_service "vLLM $service_name" "$port" 45; then
        log_success "vLLM $service_name started successfully (PID: $pid)"
        check_gpu_memory  # Show memory usage after startup
        return 0
    else
        log_error "Failed to start vLLM $service_name"
        return 1
    fi
}

# Start CPU-based service
start_cpu_service() {
    local service_name=$1
    local script_name=$2
    local port=$3
    local work_dir=$4
    local extra_args=${5:-""}
    
    log_info "Starting CPU service $service_name..."
    
    if check_service_port "$port"; then
        log_success "$service_name already running on port $port"
        return 0
    fi
    
    cd "$work_dir" || {
        log_error "Cannot change to directory: $work_dir"
        return 1
    }
    
    mkdir -p "$PLATFORM_ROOT/pids"
    
    # Start with CPU affinity to avoid interfering with GPU services
    nohup taskset -c 0-7 python3 "$script_name" $extra_args > "$PLATFORM_ROOT/logs/$service_name.log" 2>&1 &
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

# Start Python service
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
    
    mkdir -p "$PLATFORM_ROOT/pids"
    
    nohup python3 "$script_name" $extra_args > "$PLATFORM_ROOT/logs/$service_name.log" 2>&1 &
    local pid=$!
    echo $pid > "$PLATFORM_ROOT/pids/$service_name.pid"
    
    if wait_for_service "$service_name" "$port" 20; then
        log_success "$service_name started successfully (PID: $pid)"
        return 0
    else
        log_error "Failed to start $service_name"
        return 1
    fi
}

# Start .NET service
start_dotnet_service() {
    local service_name=$1
    local port=$2
    local work_dir=$3
    
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
    
    nohup dotnet run --urls "http://0.0.0.0:$port" > "$PLATFORM_ROOT/logs/$service_name.log" 2>&1 &
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

# Memory-aware service startup for 24GB system
startup_services_24gb() {
    log "=== AI Research Platform Startup (24GB VRAM Optimized) ==="
    
    # Show initial memory status
    check_gpu_memory
    check_system_memory
    
    # Phase 1: Essential Infrastructure (minimal memory)
    log_info "=== Phase 1: Essential Infrastructure ==="
    start_python_service "webhook-server" "webhook-server.js" 11025 "$PLATFORM_ROOT/runtime-data"
    start_python_service "ai-gateway" "api_gateway.py" 9000 "$PYTHON_AI_STACK"
    
    # Phase 2: Core Platform Services
    log_info "=== Phase 2: Core Platform Services ==="
    start_dotnet_service "chat-copilot-backend" 11000 "$PLATFORM_ROOT/webapi"
    start_python_service "port-scanner" "port-scanner.py" 11010 "$PLATFORM_ROOT/python/tools" "--host 0.0.0.0 --port 11010"
    
    # Phase 3: Primary GPU Service (highest priority, most memory)
    log_info "=== Phase 3: Primary GPU Service ==="
    if nvidia-smi &>/dev/null; then
        log_info "NVIDIA GPU detected, starting optimized vLLM services..."
        start_vllm_service_optimized "reasoning" "microsoft/DialoGPT-small" 8000 "0.4" "1024" "9.6GB VRAM"
    else
        log_warning "No NVIDIA GPU detected, skipping GPU services"
    fi
    
    # Phase 4: Secondary GPU Service (if memory allows)
    log_info "=== Phase 4: Secondary GPU Service ==="
    if nvidia-smi &>/dev/null && check_gpu_memory; then
        start_vllm_service_optimized "general" "distilgpt2" 8001 "0.3" "512" "7.2GB VRAM"
    else
        log_warning "Insufficient GPU memory for general service, using CPU fallback"
    fi
    
    # Phase 5: Additional GPU Service (if memory allows)
    log_info "=== Phase 5: Additional GPU Service ==="
    if nvidia-smi &>/dev/null && check_gpu_memory; then
        start_vllm_service_optimized "coding" "microsoft/DialoGPT-small" 8002 "0.3" "1024" "7.2GB VRAM"
    else
        log_warning "Insufficient GPU memory for coding service, skipping"
    fi
    
    # Phase 6: Local LLM Services (CPU/small GPU)
    log_info "=== Phase 6: Local LLM Services ==="
    if command -v ollama &> /dev/null; then
        start_python_service "ollama-server" "ollama" 11434 "/usr/local/bin" "serve"
    else
        log_warning "Ollama not installed, skipping"
    fi
    
    # Phase 7: CPU-based Services (memory permitting)
    log_info "=== Phase 7: CPU-based Services ==="
    if check_system_memory; then
        start_cpu_service "creative" "koboldcpp.py" 5001 "$PYTHON_AI_STACK" "--model models/ggml-gpt4all-j-v1.3-groovy.bin --port 5001 --threads 8"
    else
        log_warning "Insufficient system memory for creative service"
    fi
    
    # Phase 8: Optional Services (resource permitting)
    log_info "=== Phase 8: Optional Services ==="
    if check_system_memory && check_gpu_memory; then
        start_python_service "autogen-studio" "autogen_studio_server.py" 11001 "$PLATFORM_ROOT/python/autogen" || log_warning "AutoGen Studio not available"
    else
        log_warning "Skipping resource-intensive optional services"
    fi
    
    # Phase 9: Docker Services (if resources allow)
    log_info "=== Phase 9: Docker Services ==="
    if command -v docker-compose &> /dev/null && check_system_memory; then
        if docker-compose -f "$PLATFORM_ROOT/docker-compose.simple.yml" ps neo4j | grep -q "Up" 2>/dev/null; then
            log_success "Neo4j already running"
        else
            docker-compose -f "$PLATFORM_ROOT/docker-compose.simple.yml" up -d neo4j 2>/dev/null || log_warning "Neo4j failed to start"
        fi
    else
        log_warning "Skipping Docker services due to resource constraints"
    fi
    
    # Final memory status
    log_memory "=== Final Memory Status ==="
    check_gpu_memory
    check_system_memory
    
    log_success "24GB VRAM optimized service startup completed!"
}

# Get memory analysis
get_memory_analysis() {
    log_info "=== 24GB System Memory Analysis ==="
    
    cd "$PYTHON_AI_STACK"
    python3 -c "
from comprehensive_service_registry_24gb import optimized_registry_24gb
import json

analysis = optimized_registry_24gb.get_memory_usage_analysis()
health = optimized_registry_24gb.get_all_services_health()

print('Memory Usage Analysis:')
for key, value in analysis.items():
    print(f'  {key}: {value}')

print('\nHardware Optimization:')
hw_opt = health.get('hardware_optimization', {})
for key, value in hw_opt.items():
    print(f'  {key}: {value}')
" || log_error "Failed to get memory analysis"
}

# Stop services with priority order
stop_services_24gb() {
    log_info "Stopping 24GB optimized services..."
    
    # Stop in reverse priority order to free memory gracefully
    for pidfile in "$PLATFORM_ROOT/pids"/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            service_name=$(basename "$pidfile" .pid)
            
            if kill -0 "$pid" 2>/dev/null; then
                log_info "Stopping $service_name (PID: $pid)"
                kill "$pid"
                sleep 2
                
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
    fi
    
    log_success "All services stopped"
}

# Show service status optimized for 24GB system
check_24gb_services() {
    log_info "Checking 24GB optimized services..."
    
    cd "$PYTHON_AI_STACK"
    python3 -c "
from comprehensive_service_registry_24gb import optimized_registry_24gb
import json

health = optimized_registry_24gb.get_all_services_health()
print(json.dumps(health, indent=2))
" || log_error "Failed to get service health from 24GB registry"
}

# Main command handling
case "${1:-start}" in
    start)
        log "=== Starting 24GB VRAM Optimized AI Platform ==="
        startup_services_24gb
        get_memory_analysis
        ;;
    stop)
        log "=== Stopping 24GB Optimized Services ==="
        stop_services_24gb
        ;;
    restart)
        log "=== Restarting 24GB Optimized Services ==="
        stop_services_24gb
        sleep 5
        startup_services_24gb
        get_memory_analysis
        ;;
    status|health)
        log "=== 24GB System Service Health ==="
        check_24gb_services
        get_memory_analysis
        ;;
    memory)
        log "=== 24GB System Memory Analysis ==="
        get_memory_analysis
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health|memory}"
        echo ""
        echo "Commands:"
        echo "  start     - Start all 24GB optimized services"
        echo "  stop      - Stop all services"  
        echo "  restart   - Restart all services"
        echo "  status    - Check health of all services"
        echo "  health    - Alias for status"
        echo "  memory    - Show memory usage analysis"
        echo ""
        echo "Optimizations for 24GB VRAM systems:"
        echo "  - Sequential GPU service startup to prevent OOM"
        echo "  - Memory monitoring and fallback strategies"
        echo "  - Optimized model sizes and memory utilization"
        echo "  - CPU fallbacks for memory-intensive services"
        echo "  - Resource-aware service prioritization"
        exit 1
        ;;
esac

exit 0