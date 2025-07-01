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

# Check prerequisites
if ! command -v docker &> /dev/null; then
    print_status "ERROR" "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_status "ERROR" "Docker Compose is not available"
    exit 1
fi

# Check SSL certificates
CERT_FILE="/etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt"
KEY_FILE="/etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key"

if [[ ! -f "$CERT_FILE" ]] || [[ ! -f "$KEY_FILE" ]]; then
    print_status "WARNING" "SSL certificates not found. Platform will start but SSL may not work."
    print_status "INFO" "Expected certificates at: $CERT_FILE and $KEY_FILE"
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
  -v /etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt:/etc/ssl/certs/server.crt:ro \
  -v /etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key:/etc/ssl/private/server.key:ro \
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