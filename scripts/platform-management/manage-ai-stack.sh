#!/bin/bash
# Advanced AI Stack Management Script
# Manages vLLM, Oobabooga, KoboldCpp, and API Gateway

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." &> /dev/null && pwd)"
AI_STACK_DIR="${PROJECT_ROOT}/python/ai-stack"
LOGS_DIR="${PROJECT_ROOT}/logs"

# Service configurations
GATEWAY_PORT=9000
VLLM_REASONING_PORT=8000
VLLM_GENERAL_PORT=8001
VLLM_CODING_PORT=8002
OOBABOOGA_API_PORT=5000
OOBABOOGA_UI_PORT=7860
KOBOLDCPP_PORT=5001

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if service is running on port
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        success "$service_name is running on port $port"
        return 0
    else
        warning "$service_name is not running on port $port"
        return 1
    fi
}

# Kill process on port
kill_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        log "Stopping $service_name on port $port..."
        echo $pids | xargs kill -TERM 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        local remaining=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining" ]; then
            echo $remaining | xargs kill -KILL 2>/dev/null || true
            warning "Force killed $service_name"
        else
            success "Stopped $service_name"
        fi
    else
        log "$service_name was not running on port $port"
    fi
}

# Start API Gateway
start_gateway() {
    log "Starting AI Stack Gateway..."
    
    if check_port $GATEWAY_PORT "AI Gateway"; then
        log "AI Gateway already running"
        return 0
    fi
    
    cd "$AI_STACK_DIR"
    
    # Install requirements if needed
    if [ ! -f requirements.txt ]; then
        cat > requirements.txt << EOF
flask>=2.0.0
requests>=2.25.0
gunicorn>=20.1.0
EOF
    fi
    
    if ! python3 -c "import flask, requests" 2>/dev/null; then
        log "Installing Python dependencies..."
        pip3 install -r requirements.txt
    fi
    
    # Start gateway with gunicorn for production
    log "Starting gateway with gunicorn..."
    nohup gunicorn -w 4 -b 0.0.0.0:$GATEWAY_PORT \
        --access-logfile "${LOGS_DIR}/ai-gateway-access.log" \
        --error-logfile "${LOGS_DIR}/ai-gateway-error.log" \
        --daemon \
        --pid "${LOGS_DIR}/ai-gateway.pid" \
        api_gateway:app 2>&1 | tee -a "${LOGS_DIR}/ai-gateway.log" &
    
    sleep 3
    
    if check_port $GATEWAY_PORT "AI Gateway"; then
        success "AI Stack Gateway started successfully"
    else
        error "Failed to start AI Gateway"
        return 1
    fi
}

# Stop API Gateway
stop_gateway() {
    log "Stopping AI Stack Gateway..."
    
    # Try to stop gracefully using PID file
    local pid_file="${LOGS_DIR}/ai-gateway.pid"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill -TERM "$pid"
            sleep 2
            
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL "$pid"
            fi
            rm -f "$pid_file"
        fi
    fi
    
    # Fallback to port-based killing
    kill_port $GATEWAY_PORT "AI Gateway"
}

# Check all AI services health
check_health() {
    log "Checking AI Stack health..."
    
    local services=(
        "AI Gateway:$GATEWAY_PORT"
        "vLLM Reasoning:$VLLM_REASONING_PORT"
        "vLLM General:$VLLM_GENERAL_PORT"
        "vLLM Coding:$VLLM_CODING_PORT"
        "Oobabooga API:$OOBABOOGA_API_PORT"
        "Oobabooga UI:$OOBABOOGA_UI_PORT"
        "KoboldCpp:$KOBOLDCPP_PORT"
    )
    
    local healthy=0
    local total=${#services[@]}
    
    echo -e "\n${BLUE}AI Stack Status:${NC}"
    echo "===================="
    
    for service in "${services[@]}"; do
        local name="${service%:*}"
        local port="${service#*:}"
        
        if check_port "$port" "$name"; then
            ((healthy++))
        fi
    done
    
    echo "===================="
    echo -e "Services: ${GREEN}$healthy${NC}/$total healthy"
    
    # Try to get detailed health from gateway
    if check_port $GATEWAY_PORT "AI Gateway" >/dev/null 2>&1; then
        log "Getting detailed health from gateway..."
        curl -s "http://localhost:$GATEWAY_PORT/health" 2>/dev/null | python3 -m json.tool 2>/dev/null || true
    fi
}

# Monitor AI Stack
monitor() {
    log "Starting AI Stack monitoring..."
    
    if [ ! -f "$AI_STACK_DIR/monitor.py" ]; then
        error "Monitor script not found at $AI_STACK_DIR/monitor.py"
        return 1
    fi
    
    cd "$AI_STACK_DIR"
    
    # Install monitoring dependencies
    if ! python3 -c "import psutil" 2>/dev/null; then
        log "Installing monitoring dependencies..."
        pip3 install psutil nvidia-ml-py3 2>/dev/null || pip3 install psutil
    fi
    
    # Run monitoring
    python3 monitor.py --interval 30
}

# Show AI Stack information
show_info() {
    echo -e "\n${BLUE}Advanced AI Stack Information${NC}"
    echo "======================================"
    echo "Gateway: http://localhost:$GATEWAY_PORT"
    echo ""
    echo "Backend Services:"
    echo "  - vLLM Reasoning (DeepSeek R1): http://localhost:$VLLM_REASONING_PORT"
    echo "  - vLLM General (Mistral): http://localhost:$VLLM_GENERAL_PORT"
    echo "  - vLLM Coding (DeepSeek Coder): http://localhost:$VLLM_CODING_PORT"
    echo "  - Oobabooga WebUI: http://localhost:$OOBABOOGA_UI_PORT"
    echo "  - Oobabooga API: http://localhost:$OOBABOOGA_API_PORT"
    echo "  - KoboldCpp: http://localhost:$KOBOLDCPP_PORT"
    echo ""
    echo "Management Commands:"
    echo "  $0 start-gateway    - Start API Gateway only"
    echo "  $0 stop-gateway     - Stop API Gateway only"
    echo "  $0 health          - Check health of all services"
    echo "  $0 monitor         - Start monitoring dashboard"
    echo "  $0 logs           - Show logs"
    echo ""
    echo "Installation:"
    echo "  See: $PROJECT_ROOT/Advanced AI Stack Setup Guide.md"
    echo "======================================"
}

# Show logs
show_logs() {
    local service=${1:-"gateway"}
    
    case $service in
        "gateway")
            log "AI Gateway logs:"
            if [ -f "${LOGS_DIR}/ai-gateway.log" ]; then
                tail -f "${LOGS_DIR}/ai-gateway.log"
            else
                error "Gateway log file not found"
            fi
            ;;
        "error")
            log "AI Gateway error logs:"
            if [ -f "${LOGS_DIR}/ai-gateway-error.log" ]; then
                tail -f "${LOGS_DIR}/ai-gateway-error.log"
            else
                error "Gateway error log file not found"
            fi
            ;;
        "access")
            log "AI Gateway access logs:"
            if [ -f "${LOGS_DIR}/ai-gateway-access.log" ]; then
                tail -f "${LOGS_DIR}/ai-gateway-access.log"
            else
                error "Gateway access log file not found"
            fi
            ;;
        *)
            echo "Available logs: gateway, error, access"
            ;;
    esac
}

# Test AI Stack
test_stack() {
    log "Testing AI Stack..."
    
    if ! check_port $GATEWAY_PORT "AI Gateway" >/dev/null 2>&1; then
        error "AI Gateway is not running. Start it first with: $0 start-gateway"
        return 1
    fi
    
    # Test basic connectivity
    log "Testing gateway connectivity..."
    local gateway_info=$(curl -s "http://localhost:$GATEWAY_PORT/info" 2>/dev/null || echo "{}")
    
    if echo "$gateway_info" | grep -q "Advanced AI Stack Gateway"; then
        success "Gateway is responding"
    else
        warning "Gateway may not be responding correctly"
    fi
    
    # Test completion endpoint
    log "Testing completion endpoint..."
    local test_response=$(curl -s -X POST "http://localhost:$GATEWAY_PORT/v1/completions" \
        -H "Content-Type: application/json" \
        -d '{"task_type": "general", "prompt": "Say hello", "max_tokens": 10}' 2>/dev/null || echo "{}")
    
    if echo "$test_response" | grep -q "error"; then
        warning "Test completion request returned error: $test_response"
    elif [ -n "$test_response" ] && [ "$test_response" != "{}" ]; then
        success "Completion endpoint is working"
    else
        warning "Completion endpoint test inconclusive"
    fi
}

# Main function
main() {
    # Create logs directory if it doesn't exist
    mkdir -p "$LOGS_DIR"
    
    case "${1:-help}" in
        "start-gateway")
            start_gateway
            ;;
        "stop-gateway")
            stop_gateway
            ;;
        "restart-gateway")
            stop_gateway
            sleep 2
            start_gateway
            ;;
        "health"|"status")
            check_health
            ;;
        "monitor")
            monitor
            ;;
        "info")
            show_info
            ;;
        "logs")
            show_logs "${2:-gateway}"
            ;;
        "test")
            test_stack
            ;;
        "help"|"-h"|"--help")
            echo "Advanced AI Stack Management"
            echo ""
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  start-gateway     Start the API Gateway"
            echo "  stop-gateway      Stop the API Gateway"
            echo "  restart-gateway   Restart the API Gateway"
            echo "  health, status    Check health of all AI services"
            echo "  monitor          Start monitoring dashboard"
            echo "  info             Show AI stack information"
            echo "  logs [type]      Show logs (gateway, error, access)"
            echo "  test             Test AI stack functionality"
            echo "  help             Show this help message"
            echo ""
            echo "Note: This script manages the API Gateway. Individual AI services"
            echo "      (vLLM, Oobabooga, KoboldCpp) need to be started separately"
            echo "      following the Advanced AI Stack Setup Guide."
            ;;
        *)
            error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"