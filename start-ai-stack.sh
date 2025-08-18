#!/bin/bash
# Advanced AI Stack Startup Script
# Starts the complete vLLM + Oobabooga + KoboldCpp + Gateway stack

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        return 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        return 1
    fi
    
    # Check .env file
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        error ".env file not found. Please create it with required environment variables."
        return 1
    fi
    
    # Check HuggingFace token
    if ! grep -q "HUGGINGFACE_TOKEN" "$PROJECT_ROOT/.env"; then
        warning "HUGGINGFACE_TOKEN not found in .env file. Some gated models may not be accessible."
    fi
    
    # Check NVIDIA drivers
    if command -v nvidia-smi &> /dev/null; then
        log "NVIDIA GPU detected:"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    else
        warning "NVIDIA drivers not found. GPU acceleration will not be available."
    fi
    
    success "Prerequisites check completed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/models"
    mkdir -p "$PROJECT_ROOT/python/ai-stack/oobabooga-config"
    
    # Create Tesla K80 config if it doesn't exist
    if [ ! -f "$PROJECT_ROOT/python/ai-stack/tesla_k80_config.py" ]; then
        cat > "$PROJECT_ROOT/python/ai-stack/tesla_k80_config.py" << 'EOF'
"""
Tesla K80 Optimization Configuration
Optimized settings for Tesla K80 GPUs (12GB VRAM, Kepler architecture)
"""

# Memory settings for Tesla K80 (12GB VRAM)
MAX_GPU_MEMORY = "10GB"  # Leave 2GB for system
TENSOR_PARALLEL_SIZE = 1  # Tesla K80 doesn't support multi-GPU well
GPU_MEMORY_UTILIZATION = 0.8

# Model size recommendations for Tesla K80
RECOMMENDED_MODELS = {
    "small": ["microsoft/DialoGPT-small", "gpt2"],
    "medium": ["microsoft/DialoGPT-medium", "gpt2-medium"],
    "large": ["microsoft/DialoGPT-large"]  # May require quantization
}

# Quantization settings
USE_QUANTIZATION = True
QUANTIZATION_BITS = 8  # 8-bit quantization for memory efficiency

# Performance settings
BATCH_SIZE = 1
MAX_CONTEXT_LENGTH = 2048  # Conservative for memory
EOF
    fi
    
    success "Directories and configuration files created"
}

# Start the AI stack
start_stack() {
    log "Starting Advanced AI Stack..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f docker-compose.ai-stack.yml pull
    
    # Build custom images
    log "Building custom Docker images..."
    docker-compose -f docker-compose.ai-stack.yml build
    
    # Start the stack
    log "Starting AI Stack services..."
    docker-compose -f docker-compose.ai-stack.yml up -d
    
    # Wait for services to start
    log "Waiting for services to initialize..."
    sleep 30
    
    # Check service health
    check_health
}

# Check service health
check_health() {
    log "Checking service health..."
    
    local services=(
        "ai-platform-postgres:5432"
        "ai-platform-neo4j:7474"
        "ai-platform-vllm-reasoning:8000"
        "ai-platform-vllm-general:8001"
        "ai-platform-vllm-coding:8002"
        "ai-platform-oobabooga:7860"
        "ai-platform-koboldcpp:5001"
        "ai-platform-ai-gateway:9000"
    )
    
    local healthy=0
    local total=${#services[@]}
    
    echo -e "\n${BLUE}AI Stack Health Status:${NC}"
    echo "================================"
    
    for service in "${services[@]}"; do
        local container="${service%:*}"
        local port="${service#*:}"
        
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            if docker exec "$container" sh -c "curl -f http://localhost:$port/health >/dev/null 2>&1 || curl -f http://localhost:$port >/dev/null 2>&1"; then
                echo -e "${GREEN}✓${NC} $container"
                ((healthy++))
            else
                echo -e "${YELLOW}⚠${NC} $container (starting...)"
            fi
        else
            echo -e "${RED}✗${NC} $container (not running)"
        fi
    done
    
    echo "================================"
    echo -e "Services: ${GREEN}$healthy${NC}/$total healthy"
    echo ""
    
    if [ $healthy -gt $((total / 2)) ]; then
        success "AI Stack is operational!"
        show_access_info
    else
        warning "Some services are not healthy. Check logs with: docker-compose -f docker-compose.ai-stack.yml logs"
    fi
}

# Show access information
show_access_info() {
    echo -e "\n${BLUE}AI Stack Access Information:${NC}"
    echo "=========================================="
    echo ""
    echo "🚀 Main Gateway:"
    echo "   http://localhost:9000"
    echo "   Health: http://localhost:9000/health"
    echo ""
    echo "🧠 AI Services:"
    echo "   vLLM Reasoning (DeepSeek R1):  http://localhost:8000"
    echo "   vLLM General (Mistral):        http://localhost:8001"
    echo "   vLLM Coding (DeepSeek Coder):  http://localhost:8002"
    echo "   Oobabooga WebUI:               http://localhost:7860"
    echo "   KoboldCpp Creative:            http://localhost:5001"
    echo ""
    echo "💾 Infrastructure:"
    echo "   Neo4j Browser:                 http://localhost:7474 (neo4j/password)"
    echo "   PostgreSQL:                    localhost:5432"
    echo ""
    echo "📊 Monitoring:"
    echo "   Grafana:                       http://localhost:11002 (admin/admin)"
    echo "   Prometheus:                    http://localhost:9090"
    echo ""
    echo "🛠️ Management:"
    echo "   Stop: docker-compose -f docker-compose.ai-stack.yml down"
    echo "   Logs: docker-compose -f docker-compose.ai-stack.yml logs [service]"
    echo "   Status: ./scripts/platform-management/manage-ai-stack.sh health"
    echo ""
    echo "🔗 Example API Usage:"
    echo "   curl -X POST http://localhost:9000/v1/completions \\"
    echo "        -H 'Content-Type: application/json' \\"
    echo "        -d '{\"task_type\": \"reasoning\", \"prompt\": \"Solve: 2x + 5 = 17\", \"max_tokens\": 100}'"
    echo "=========================================="
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 Advanced AI Stack Startup                   ║"
    echo "║              vLLM + Oobabooga + KoboldCpp                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    case "${1:-start}" in
        "start")
            check_prerequisites
            create_directories
            start_stack
            ;;
        "stop")
            log "Stopping AI Stack..."
            docker-compose -f docker-compose.ai-stack.yml down
            success "AI Stack stopped"
            ;;
        "restart")
            log "Restarting AI Stack..."
            docker-compose -f docker-compose.ai-stack.yml down
            sleep 5
            check_prerequisites
            create_directories
            start_stack
            ;;
        "status"|"health")
            check_health
            ;;
        "logs")
            docker-compose -f docker-compose.ai-stack.yml logs -f "${2:-}"
            ;;
        "help"|"-h"|"--help")
            echo "Advanced AI Stack Management"
            echo ""
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  start     Start the complete AI stack (default)"
            echo "  stop      Stop all AI stack services"
            echo "  restart   Restart the AI stack"
            echo "  status    Check health of all services"
            echo "  logs      Show logs (optionally for specific service)"
            echo "  help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 start              # Start the complete stack"
            echo "  $0 logs ai-gateway    # Show gateway logs"
            echo "  $0 logs               # Show all logs"
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