#!/bin/bash
# Start AI Research Platform with SSL (Production)

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

print_header() {
    echo
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

print_header "AI RESEARCH PLATFORM - SSL PRODUCTION STARTUP"

# Comprehensive cleanup function
cleanup_platform() {
    print_status "INFO" "Starting comprehensive platform cleanup..."
    
    # Stop all competing systemd services
    print_status "INFO" "Stopping competing systemd services..."
    sudo systemctl stop ai-platform-consolidated.service ai-platform-restore.service ollama-ai-platform.service ai-platform-validator.service ai-platform.service ai-platform-open-webui.service multifamily-valuation-app.service 2>/dev/null || true
    
    # Stop all AI platform containers
    print_status "INFO" "Stopping all existing containers..."
    docker stop $(docker ps -aq) 2>/dev/null || true
    
    # Remove stopped containers
    print_status "INFO" "Removing stopped containers..."
    docker container prune -f 2>/dev/null || true
    
    # Kill processes on critical ports
    print_status "INFO" "Freeing up critical ports..."
    local critical_ports=(11001 11007 11020 8502 8505 3000 7474 7687 57081 8080 8443 11080 5432 6333 6379)
    for port in "${critical_ports[@]}"; do
        local pids=$(sudo lsof -ti:$port 2>/dev/null || true)
        if [[ -n "$pids" ]]; then
            print_status "INFO" "Killing processes on port $port: $pids"
            sudo kill -9 $pids 2>/dev/null || true
        fi
    done
    
    # Clean up any dangling networks and IP conflicts
    print_status "INFO" "Cleaning up Docker networks..."
    docker network prune -f 2>/dev/null || true
    
    # Remove any existing ai-platform network to avoid IP conflicts
    docker network rm chat-copilot_ai-platform 2>/dev/null || true
    docker network rm ai-platform 2>/dev/null || true
    
    # Wait a moment for cleanup to complete
    sleep 2
    
    print_status "SUCCESS" "Platform cleanup completed"
}

# Run cleanup before starting
cleanup_platform

# Ensure HTML symlinks are up-to-date
bash /home/keith/chat-copilot/scripts/platform-management/create-html-symlinks.sh

# Pre-flight checks
preflight_checks() {
    print_status "INFO" "Running pre-flight checks..."
    
    # Check prerequisites
    if ! command -v docker &> /dev/null; then
        print_status "ERROR" "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_status "ERROR" "Docker Compose is not available"
        exit 1
    fi
    
    # Verify critical ports are free
    local critical_ports=(11001 11007 11020 8502 8505)
    local conflicts_found=false
    
    for port in "${critical_ports[@]}"; do
        if sudo netstat -tulpn 2>/dev/null | grep -q ":$port "; then
            print_status "WARNING" "Port $port is still occupied - cleanup may be needed"
            conflicts_found=true
        fi
    done
    
    if $conflicts_found; then
        print_status "WARNING" "Port conflicts detected - running additional cleanup..."
        cleanup_platform
    fi
    
    # Verify Docker is running
    if ! docker info &> /dev/null; then
        print_status "ERROR" "Docker daemon is not running"
        exit 1
    fi
    
    print_status "SUCCESS" "Pre-flight checks passed"
}

# Run pre-flight checks
preflight_checks

# Check SSL certificates
CERT_FILE="/etc/ssl/certs/ubuntuaicodeserver-1.tail5137b4.ts.net.crt"
KEY_FILE="/etc/ssl/private/ubuntuaicodeserver-1.tail5137b4.ts.net.key"

if [[ ! -f "$CERT_FILE" ]] || [[ ! -f "$KEY_FILE" ]]; then
    print_status "WARNING" "SSL certificates not found. Platform will start but SSL may not work."
    print_status "INFO" "Expected certificates at: $CERT_FILE and $KEY_FILE"
fi

# Ensure generic symlinks for Nginx
if [[ -f "$CERT_FILE" ]] && [[ ! -f /etc/ssl/certs/server.crt ]]; then
    sudo ln -sf "$CERT_FILE" /etc/ssl/certs/server.crt
fi
if [[ -f "$KEY_FILE" ]] && [[ ! -f /etc/ssl/private/server.key ]]; then
    sudo ln -sf "$KEY_FILE" /etc/ssl/private/server.key
fi

# Stop any existing nginx-ssl container
print_status "INFO" "Stopping any existing nginx-ssl container..."
docker stop nginx-ssl 2>/dev/null || true
docker rm nginx-ssl 2>/dev/null || true

# Start nginx with SSL configuration
print_status "INFO" "Starting nginx SSL reverse proxy on port 8443..."

docker run -d \
  --name nginx-ssl \
  --restart unless-stopped \
  -p 8443:443 \
  -p 8080:80 \
  -v /etc/ssl/certs/ubuntuaicodeserver-1.tail5137b4.ts.net.crt:/etc/ssl/certs/ubuntuaicodeserver-1.tail5137b4.ts.net.crt:ro \
  -v /etc/ssl/private/ubuntuaicodeserver-1.tail5137b4.ts.net.key:/etc/ssl/private/ubuntuaicodeserver-1.tail5137b4.ts.net.key:ro \
  -v /home/keith/chat-copilot/configs/nginx/nginx-ssl.conf:/etc/nginx/nginx.conf:ro \
  -v /home/keith/chat-copilot/nginx-configs/ssl-main.conf:/etc/nginx/conf.d/ssl-main.conf:ro \
  -v /home/keith/chat-copilot/webapi/wwwroot:/var/www/html:ro \
  --network host \
  nginx:alpine

if [[ $? -eq 0 ]]; then
    print_status "SUCCESS" "nginx SSL reverse proxy started"
else
    print_status "ERROR" "Failed to start nginx SSL reverse proxy"
    exit 1
fi

# Create the AI platform network first
print_status "INFO" "Creating AI platform network..."
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --gateway=172.20.0.1 \
  --attachable \
  chat-copilot_ai-platform 2>/dev/null || print_status "INFO" "Network already exists"

# Start Docker Compose services
print_status "INFO" "Starting Docker Compose services..."

if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
    docker-compose -f configs/docker-compose/docker-compose-full-stack.yml up -d
    print_status "SUCCESS" "Docker Compose services started"
else
    print_status "WARNING" "docker-compose-full-stack.yml not found, starting basic services"
    if [[ -f "docker/docker-compose.yaml" ]]; then
        cd docker && docker-compose up -d && cd ..
        print_status "SUCCESS" "Basic Docker services started"
    else
        print_status "ERROR" "No docker-compose configuration found"
        exit 1
    fi
fi

print_status "INFO" "Starting additional nginx management UIs..."

# Start Nginx Proxy Manager
if [[ -f "docker-configs/docker-compose.nginx-proxy-manager.yml" ]]; then
    docker-compose -f docker-configs/docker-compose.nginx-proxy-manager.yml up -d
    print_status "SUCCESS" "Nginx Proxy Manager stack started"
else
    print_status "WARNING" "docker-compose.nginx-proxy-manager.yml not found"
fi

# Start Nginx Config UI
if [[ -f "docker-configs/docker-compose.nginx-config-ui.yml" ]]; then
    docker-compose -f docker-configs/docker-compose.nginx-config-ui.yml up -d
    print_status "SUCCESS" "Nginx Config UI stack started (port 11084)"
else
    print_status "WARNING" "docker-compose.nginx-config-ui.yml not found"
fi

print_header "STARTUP COMPLETE"

print_status "SUCCESS" "AI Research Platform is starting up with SSL!"
echo
print_status "INFO" "Access the platform at:"
echo "   🌐 Main Hub: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/"
echo "   🎛️ Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/control-panel.html"
echo "   📚 Applications: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html"
echo "   💬 Chat Copilot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/copilot/"
echo
print_status "INFO" "Services are starting up. Please wait 30-60 seconds for full availability."
print_status "INFO" "Check service status with: docker ps"
print_status "INFO" "View logs with: docker logs nginx-ssl"
