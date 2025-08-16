#!/bin/bash

# =============================================================================
# Chat Copilot Platform - Portable Startup Script
# =============================================================================
# This script starts the platform using environment-based configuration
# for maximum portability across systems and HA deployments
# =============================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Script directory (auto-detect platform root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$SCRIPT_DIR"

print_status() {
    local level=$1
    local message=$2
    case $level in
        "INFO")  echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "ERROR") echo -e "${RED}❌ ${message}${NC}" ;;
        "ENHANCE") echo -e "${PURPLE}🔧 ${message}${NC}" ;;
    esac
}

print_banner() {
    echo "=============================================================================="
    echo "🚀 CHAT COPILOT PLATFORM - PORTABLE STARTUP"
    echo "🌐 Environment-based configuration for maximum portability"
    echo "=============================================================================="
    echo
}

# Auto-detect system configuration
detect_system() {
    print_status "INFO" "Auto-detecting system configuration..."
    
    # Detect IP address
    if command -v ip >/dev/null 2>&1; then
        DETECTED_IP=$(ip route get 1.1.1.1 | grep -oP 'src \K\S+' 2>/dev/null || echo "127.0.0.1")
    elif command -v ifconfig >/dev/null 2>&1; then
        DETECTED_IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1 || echo "127.0.0.1")
    else
        DETECTED_IP="127.0.0.1"
    fi
    
    # Detect user
    DETECTED_USER=$(whoami)
    DETECTED_GROUP=$(id -gn)
    
    print_status "SUCCESS" "System detected: $DETECTED_USER@$DETECTED_IP"
}

# Load environment configuration
load_environment() {
    if [[ -f "$PLATFORM_ROOT/.env" ]]; then
        print_status "INFO" "Loading environment from .env file..."
        set -a
        source "$PLATFORM_ROOT/.env"
        set +a
    elif [[ -f "$PLATFORM_ROOT/.env.template" ]]; then
        print_status "WARNING" "No .env file found. Creating from template..."
        
        # Create .env from template with auto-detected values
        sed -e "s|\$USER|$DETECTED_USER|g" \
            -e "s|127\.0\.0\.1|$DETECTED_IP|g" \
            -e "s|/home/\$USER|$PLATFORM_ROOT|g" \
            "$PLATFORM_ROOT/.env.template" > "$PLATFORM_ROOT/.env"
            
        print_status "SUCCESS" "Created .env with auto-detected values"
        print_status "INFO" "Please review and edit .env file, then run again"
        print_status "INFO" "nano $PLATFORM_ROOT/.env"
        return 1
    else
        print_status "ERROR" "No environment configuration found"
        print_status "INFO" "Create .env.template or run: ./scripts/setup/enhance-portability.sh"
        return 1
    fi
    
    # Set defaults for missing variables
    export PLATFORM_ROOT="${PLATFORM_ROOT:-$SCRIPT_DIR}"
    export PLATFORM_IP="${PLATFORM_IP:-$DETECTED_IP}"
    export PLATFORM_USER="${PLATFORM_USER:-$DETECTED_USER}"
    export PLATFORM_GROUP="${PLATFORM_GROUP:-$DETECTED_GROUP}"
    
    print_status "SUCCESS" "Environment loaded successfully"
    print_status "INFO" "Platform Root: $PLATFORM_ROOT"
    print_status "INFO" "Platform IP: $PLATFORM_IP"
    print_status "INFO" "Platform User: $PLATFORM_USER:$PLATFORM_GROUP"
}

# Check prerequisites
check_prerequisites() {
    print_status "INFO" "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        missing_deps+=("docker")
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        missing_deps+=("docker-compose")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_status "ERROR" "Missing dependencies: ${missing_deps[*]}"
        print_status "INFO" "Install Docker and Docker Compose first"
        return 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_status "ERROR" "Docker is not running"
        print_status "INFO" "Start Docker service first"
        return 1
    fi
    
    print_status "SUCCESS" "Prerequisites check passed"
}

# Create required directories
create_directories() {
    print_status "INFO" "Creating required directories..."
    
    local dirs=(
        "$PLATFORM_ROOT/data"
        "$PLATFORM_ROOT/logs"
        "$PLATFORM_ROOT/backups"
        "$PLATFORM_ROOT/temp"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_status "SUCCESS" "Created directory: $dir"
        fi
    done
}

# Start services
start_services() {
    local profile="${1:-default}"
    
    print_status "INFO" "Starting Chat Copilot platform with profile: $profile"
    
    # Export environment variables for Docker Compose
    export PLATFORM_ROOT PLATFORM_IP PLATFORM_USER PLATFORM_GROUP
    
    # Determine which startup script to use
    if [[ -f "$PLATFORM_ROOT/start-ssl-platform.sh" ]] && [[ "$profile" == "production" ]]; then
        print_status "INFO" "Using SSL production startup..."
        "$PLATFORM_ROOT/start-ssl-platform.sh"
    elif [[ -f "$PLATFORM_ROOT/docker-compose.portable.yml" ]]; then
        print_status "INFO" "Using portable Docker Compose..."
        
        case $profile in
            "development")
                docker-compose -f "$PLATFORM_ROOT/docker-compose.portable.yml" --profile development up -d
                ;;
            "monitoring")
                docker-compose -f "$PLATFORM_ROOT/docker-compose.portable.yml" --profile monitoring up -d
                ;;
            "full")
                docker-compose -f "$PLATFORM_ROOT/docker-compose.portable.yml" --profile development --profile monitoring up -d
                ;;
            *)
                docker-compose -f "$PLATFORM_ROOT/docker-compose.portable.yml" up -d
                ;;
        esac
    elif [[ -f "$PLATFORM_ROOT/docker-compose.yml" ]]; then
        print_status "INFO" "Using standard Docker Compose..."
        docker-compose -f "$PLATFORM_ROOT/docker-compose.yml" up -d
    else
        print_status "ERROR" "No Docker Compose configuration found"
        return 1
    fi
    
    print_status "SUCCESS" "Services started successfully"
}

# Show access information
show_access_info() {
    print_status "SUCCESS" "Chat Copilot Platform is now running!"
    echo
    echo "🌐 Access Points:"
    echo "   Control Panel:          https://${PLATFORM_IP}:8443/hub"
    echo "   Applications Hub:       https://${PLATFORM_IP}:8443/applications.html"
    echo "   Chat Copilot:           https://${PLATFORM_IP}:8443/copilot/"
    echo "   AI Gateway:             https://${PLATFORM_IP}:8443/ai-gateway/"
    echo
    echo "🚀 Advanced AI Stack:"
    echo "   DeepSeek R1 (Reasoning): http://localhost:8000"
    echo "   Mistral (General):       http://localhost:8001"
    echo "   DeepSeek Coder:          http://localhost:8002"
    echo "   Oobabooga WebUI:         http://localhost:7860"
    echo "   KoboldCpp:               http://localhost:5001"
    echo "   AI Gateway:              http://localhost:9000"
    echo
    echo "📊 Management:"
    echo "   View logs:              docker-compose logs -f"
    echo "   Stop platform:          docker-compose down"
    echo "   Restart services:       docker-compose restart"
    echo "   Health check:           curl -k https://${PLATFORM_IP}:8443/copilot/healthz"
    echo
    echo "🔧 Platform Configuration:"
    echo "   Platform Root:          $PLATFORM_ROOT"
    echo "   Platform IP:            $PLATFORM_IP"
    echo "   Platform User:          $PLATFORM_USER:$PLATFORM_GROUP"
    echo
}

# Main function
main() {
    local profile="${1:-default}"
    
    print_banner
    
    print_status "INFO" "Starting portable Chat Copilot platform..."
    print_status "INFO" "Profile: $profile"
    print_status "INFO" "Platform Root: $PLATFORM_ROOT"
    
    # Auto-detect system
    detect_system
    
    # Load environment
    if ! load_environment; then
        exit 1
    fi
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Create directories
    create_directories
    
    # Start services
    if ! start_services "$profile"; then
        exit 1
    fi
    
    # Wait for services to start
    sleep 5
    
    # Show access information
    show_access_info
}

# Show help
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [PROFILE]"
    echo
    echo "Profiles:"
    echo "  default      Start core services only"
    echo "  development  Include development tools"
    echo "  production   Use SSL production configuration"
    echo "  monitoring   Include monitoring services"
    echo "  full         Include all services"
    echo
    echo "Environment Variables:"
    echo "  PLATFORM_ROOT    Platform installation directory"
    echo "  PLATFORM_IP      Server IP address"
    echo "  PLATFORM_USER    Service user account"
    echo
    echo "Examples:"
    echo "  $0                    # Start with default profile"
    echo "  $0 development        # Start with development tools"
    echo "  $0 production         # Start with SSL production setup"
    echo "  $0 full               # Start everything"
    echo
    echo "HA Deployment:"
    echo "  NODE_ID=node1 $0      # Start as HA node 1"
    echo "  NODE_ID=node2 $0      # Start as HA node 2"
    exit 0
fi

# Run main function
main "$@"