#!/bin/bash
# AI Research Platform - Containerized Startup Script

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️ $message${NC}" ;;
    esac
}

check_prerequisites() {
    print_status "INFO" "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_status "ERROR" "Docker is not installed"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_status "ERROR" "Docker daemon is not running"
        return 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_status "ERROR" "Docker Compose is not installed"
        return 1
    fi
    
    print_status "SUCCESS" "Prerequisites check passed"
}

check_environment_config() {
    print_status "INFO" "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_status "WARNING" ".env file not found"
        if [ -f ".env.template" ]; then
            print_status "INFO" "Creating .env from template..."
            cp .env.template .env
            print_status "WARNING" "Please edit .env file with your configuration before continuing"
            return 1
        else
            print_status "ERROR" "No environment template found"
            return 1
        fi
    fi
    
    # Check for required variables
    local required_vars=("AZURE_OPENAI_KEY" "AZURE_OPENAI_ENDPOINT" "POSTGRES_PASSWORD")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env || grep -q "^${var}=your-" .env; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_status "ERROR" "Missing or incomplete environment variables:"
        printf '   %s\n' "${missing_vars[@]}"
        print_status "INFO" "Please edit .env file with your configuration"
        return 1
    fi
    
    print_status "SUCCESS" "Environment configuration is complete"
}

build_images() {
    print_status "INFO" "Building custom Docker images..."
    
    # Build all custom images
    docker-compose -f docker-compose-full-stack.yml build
    
    print_status "SUCCESS" "Docker images built successfully"
}

start_platform() {
    local mode=${1:-"up"}
    
    print_status "INFO" "Starting AI Research Platform in containerized mode..."
    
    case $mode in
        "up")
            docker-compose -f docker-compose-full-stack.yml up -d
            ;;
        "up-build")
            docker-compose -f docker-compose-full-stack.yml up -d --build
            ;;
        "logs")
            docker-compose -f docker-compose-full-stack.yml logs -f
            ;;
        *)
            print_status "ERROR" "Unknown mode: $mode"
            return 1
            ;;
    esac
    
    print_status "SUCCESS" "Platform startup initiated"
}

check_service_health() {
    print_status "INFO" "Checking service health..."
    
    local services=(
        "ai-platform-caddy:172.20.0.10"
        "ai-platform-chat-backend:172.20.0.20"
        "ai-platform-chat-frontend:172.20.0.21"
        "ai-platform-autogen:172.20.0.22"
        "ai-platform-webhook:172.20.0.23"
        "ai-platform-magentic:172.20.0.24"
        "ai-platform-portscanner:172.20.0.25"
    )
    
    sleep 30  # Allow services to start
    
    local healthy_count=0
    local total_count=${#services[@]}
    
    for service_info in "${services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_ip=$(echo "$service_info" | cut -d: -f2)
        
        if docker ps --filter "name=$service_name" --filter "status=running" | grep -q "$service_name"; then
            print_status "SUCCESS" "$service_name is running"
            ((healthy_count++))
        else
            print_status "ERROR" "$service_name is not running"
        fi
    done
    
    local health_percentage=$((healthy_count * 100 / total_count))
    print_status "INFO" "Platform health: $healthy_count/$total_count services ($health_percentage%)"
    
    if [ $health_percentage -ge 90 ]; then
        print_status "SUCCESS" "Platform is healthy and ready!"
    else
        print_status "WARNING" "Some services may need attention"
    fi
}

show_access_information() {
    echo
    print_status "INFO" "AI Research Platform Access Information"
    echo
    echo -e "${BLUE}🌐 Primary Access (HTTPS):${NC}"
    echo -e "   Main Hub: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443"
    echo -e "   Applications: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html"
    echo -e "   Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub"
    echo
    echo -e "${BLUE}🤖 AI Services:${NC}"
    echo -e "   Chat Copilot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/copilot"
    echo -e "   AutoGen Studio: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/autogen"
    echo -e "   Magentic-One: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/magentic"
    echo -e "   OpenWebUI: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/openwebui"
    echo -e "   Perplexica: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/perplexica"
    echo
    echo -e "${BLUE}💻 Development Tools:${NC}"
    echo -e "   VS Code: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/vscode/login"
    echo -e "   Port Scanner: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/portscanner"
    echo
    echo -e "${BLUE}🔧 Management:${NC}"
    echo -e "   Docker containers: docker ps"
    echo -e "   View logs: docker-compose -f docker-compose-full-stack.yml logs -f [service]"
    echo -e "   Stop platform: docker-compose -f docker-compose-full-stack.yml down"
    echo
}

show_usage() {
    echo "AI Research Platform - Containerized Startup"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start         - Start the platform (default)"
    echo "  start-build   - Start with image rebuild"
    echo "  stop          - Stop the platform"
    echo "  restart       - Restart the platform"
    echo "  logs          - Show platform logs"
    echo "  status        - Show platform status"
    echo "  health        - Check service health"
    echo "  clean         - Stop and remove all containers/volumes"
    echo "  help          - Show this help"
}

main() {
    local command=${1:-"start"}
    
    echo -e "${BLUE}🚀 AI Research Platform - Containerized Mode${NC}"
    echo -e "${BLUE}=============================================${NC}"
    echo
    
    case $command in
        "start")
            check_prerequisites
            check_environment_config
            start_platform "up"
            check_service_health
            show_access_information
            ;;
        "start-build")
            check_prerequisites
            check_environment_config
            build_images
            start_platform "up-build"
            check_service_health
            show_access_information
            ;;
        "stop")
            print_status "INFO" "Stopping AI Research Platform..."
            docker-compose -f docker-compose-full-stack.yml down
            print_status "SUCCESS" "Platform stopped"
            ;;
        "restart")
            print_status "INFO" "Restarting AI Research Platform..."
            docker-compose -f docker-compose-full-stack.yml restart
            check_service_health
            ;;
        "logs")
            start_platform "logs"
            ;;
        "status")
            check_service_health
            ;;
        "health")
            check_service_health
            ;;
        "clean")
            print_status "WARNING" "This will remove all containers, networks, and volumes"
            read -p "Are you sure? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                docker-compose -f docker-compose-full-stack.yml down -v --remove-orphans
                docker system prune -f
                print_status "SUCCESS" "Platform cleaned"
            else
                print_status "INFO" "Clean cancelled"
            fi
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_status "ERROR" "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"