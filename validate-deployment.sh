#!/bin/bash
# AI Research Platform - Deployment Validation Script

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

check_prerequisites() {
    print_header "CHECKING PREREQUISITES"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_status "SUCCESS" "Docker is installed: $(docker --version)"
    else
        print_status "ERROR" "Docker is not installed"
        return 1
    fi
    
    # Check Docker daemon
    if docker info &> /dev/null; then
        print_status "SUCCESS" "Docker daemon is running"
    else
        print_status "ERROR" "Docker daemon is not running"
        return 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_status "SUCCESS" "Docker Compose is available: $(docker-compose --version)"
    elif docker compose version &> /dev/null; then
        print_status "SUCCESS" "Docker Compose (plugin) is available: $(docker compose version)"
    else
        print_status "ERROR" "Docker Compose is not available"
        return 1
    fi
    
    # Check permissions
    if docker ps &> /dev/null; then
        print_status "SUCCESS" "Docker permissions are correct"
    else
        print_status "WARNING" "Docker permissions may need adjustment"
        print_status "INFO" "Try: sudo usermod -aG docker \$USER && logout/login"
    fi
}

validate_environment() {
    print_header "VALIDATING ENVIRONMENT"
    
    # Check .env file
    if [[ -f ".env" ]]; then
        print_status "SUCCESS" "Environment file (.env) exists"
        
        # Check for required variables
        local required_vars=(
            "AZURE_OPENAI_API_KEY"
            "OPENAI_API_KEY" 
            "POSTGRES_PASSWORD"
            "JWT_SECRET"
        )
        
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env && ! grep -q "^${var}=your_" .env; then
                print_status "SUCCESS" "$var is configured"
            else
                print_status "WARNING" "$var needs to be set in .env"
            fi
        done
    else
        print_status "WARNING" "No .env file found"
        print_status "INFO" "Copy and customize .env.template to .env"
    fi
    
    # Check SSL certificates (for production deployment)
    local cert_path="/etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt"
    local key_path="/etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key"
    
    if [[ -f "$cert_path" ]] && [[ -f "$key_path" ]]; then
        print_status "SUCCESS" "SSL certificates found for production deployment"
    else
        print_status "WARNING" "SSL certificates not found (production deployment will fail)"
        print_status "INFO" "Certificates expected at: $cert_path and $key_path"
    fi
}

validate_configurations() {
    print_header "VALIDATING CONFIGURATIONS"
    
    # Test development configuration
    if [[ -f "docker/docker-compose.yaml" ]]; then
        if docker-compose -f docker/docker-compose.yaml config --quiet &> /dev/null; then
            print_status "SUCCESS" "Development configuration is valid"
        else
            print_status "ERROR" "Development configuration has issues"
        fi
    fi
    
    # Test SSL configuration  
    if [[ -f "docker-compose-ssl.yml" ]]; then
        if docker-compose -f docker-compose-ssl.yml config --quiet &> /dev/null; then
            print_status "SUCCESS" "SSL configuration is valid"
        else
            print_status "WARNING" "SSL configuration has issues (may be missing SSL certs)"
        fi
    fi
    
    # Test nginx configuration
    if [[ -f "docker-compose-nginx.yml" ]]; then
        if docker-compose -f docker-compose-nginx.yml config --quiet &> /dev/null; then
            print_status "SUCCESS" "Nginx configuration is valid"
        else
            print_status "ERROR" "Nginx configuration has issues"
        fi
    fi
    
    # Test full stack (may have environment variable warnings)
    if [[ -f "docker-compose-full-stack.yml" ]]; then
        print_status "INFO" "Checking full stack configuration (warnings expected)..."
        if docker-compose -f docker-compose-full-stack.yml config --quiet; then
            print_status "SUCCESS" "Full stack configuration is valid"
        else
            print_status "WARNING" "Full stack configuration has warnings (expected)"
        fi
    fi
}

check_startup_scripts() {
    print_header "CHECKING STARTUP SCRIPTS"
    
    local scripts=(
        "start-ssl-platform.sh"
        "start-containerized-platform.sh"
        "start-nginx-platform.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                print_status "SUCCESS" "$script is executable"
            else
                print_status "WARNING" "$script exists but is not executable"
                chmod +x "$script"
                print_status "INFO" "Made $script executable"
            fi
        else
            print_status "WARNING" "$script not found"
        fi
    done
}

test_build_capability() {
    print_header "TESTING BUILD CAPABILITY"
    
    print_status "INFO" "Testing Docker build for webapi..."
    if docker build -f docker/webapi/Dockerfile -t chat-copilot-webapi-test . &> /tmp/webapi-build.log; then
        print_status "SUCCESS" "WebAPI Docker build successful"
        docker rmi chat-copilot-webapi-test &> /dev/null || true
    else
        print_status "ERROR" "WebAPI Docker build failed"
        print_status "INFO" "Check build log: tail -20 /tmp/webapi-build.log"
    fi
    
    print_status "INFO" "Testing Docker build for webapp..."
    if docker build -f docker/webapp/Dockerfile.nginx -t chat-copilot-webapp-test . &> /tmp/webapp-build.log; then
        print_status "SUCCESS" "WebApp Docker build successful"
        docker rmi chat-copilot-webapp-test &> /dev/null || true
    else
        print_status "ERROR" "WebApp Docker build failed"  
        print_status "INFO" "Check build log: tail -20 /tmp/webapp-build.log"
    fi
}

check_file_structure() {
    print_header "CHECKING FILE STRUCTURE"
    
    # Core directories
    local required_dirs=(
        "webapi"
        "webapp" 
        "docker"
        "docker-configs"
        "scripts"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            print_status "SUCCESS" "Directory $dir exists"
        else
            print_status "ERROR" "Required directory $dir missing"
        fi
    done
    
    # Key files
    local required_files=(
        "docker/webapi/Dockerfile"
        "docker/webapp/Dockerfile.nginx"
        "docker-configs/Caddyfile"
        "webapp/public/applications.html"
        "webapp/public/control-panel.html"
        "webapi/wwwroot/applications.html"
        "webapi/wwwroot/control-panel.html"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            print_status "SUCCESS" "File $file exists"
        else
            print_status "WARNING" "File $file missing"
        fi
    done
}

test_service_urls() {
    print_header "TESTING SERVICE URLS"
    
    local services=(
        "hub:Control Panel"
        "applications.html:Applications Directory"
        "copilot/:Chat Copilot UI"
        "copilot/api/:Chat Copilot API"
        "copilot/healthz:Health Check"
        "autogen/:AutoGen Studio"
        "magentic/:Magentic-One"
        "webhook/:Webhook Server"
        "perplexica/:Perplexica AI Search"
        "searxng/:SearXNG Search"
        "portscanner/:Port Scanner"
        "nginx/:Nginx Manager"
        "gateway-http/:HTTP Gateway"
        "gateway-https/:HTTPS Gateway"
        "fortinet/:Fortinet Manager"
        "bacula/:Bacula Backup"
        "ollama-api/:Ollama API"
        "vscode/:VS Code Web"
        "genai-stack/:GenAI Stack Frontend"
        "genai-stack/bot:GenAI Stack Bot"
        "genai-stack/pdf:GenAI Stack PDF Reader"
        "genai-stack/api:GenAI Stack API"
        "genai-stack/loader:GenAI Stack Data Loader"
        "neo4j/:Neo4j Database Browser"
    )
    
    print_status "INFO" "Testing service URL accessibility..."
    echo
    
    local base_url="https://100.123.10.72:8443"
    local accessible_count=0
    local total_count=${#services[@]}
    
    for service in "${services[@]}"; do
        local path="${service%%:*}"
        local name="${service##*:}"
        local url="$base_url/$path"
        
        # Test URL accessibility (allowing self-signed certificates)
        if curl -k -s --max-time 5 --head "$url" &> /dev/null; then
            print_status "SUCCESS" "$name: $url"
            ((accessible_count++))
        else
            print_status "WARNING" "$name: $url (not accessible)"
        fi
    done
    
    echo
    print_status "INFO" "Service Accessibility: $accessible_count/$total_count services responding"
    
    if [[ $accessible_count -gt $((total_count / 2)) ]]; then
        print_status "SUCCESS" "Majority of services are accessible"
    else
        print_status "WARNING" "Many services are not responding (may need manual startup)"
    fi
}

generate_recommendations() {
    print_header "DEPLOYMENT RECOMMENDATIONS"
    
    print_status "INFO" "Based on your system configuration:"
    echo
    
    if [[ -f "/etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt" ]]; then
        echo -e "${GREEN}🏢 PRODUCTION SSL DEPLOYMENT (Recommended)${NC}"
        echo "   Command: ./start-ssl-platform.sh"
        echo "   Access:  https://100.123.10.72:8443/"
        echo "   ✅ SSL certificates available"
        echo "   ✅ Production-ready with nginx"
        echo "   🌐 All 18 services available through reverse proxy"
        echo
    fi
    
    echo -e "${BLUE}⚡ DEVELOPMENT DEPLOYMENT${NC}"
    echo "   Command: cd docker && docker-compose up --build"
    echo "   Access:  http://localhost:3000/"
    echo "   ✅ Fast startup for development"
    echo "   ✅ Core Chat Copilot functionality"
    echo "   📋 Control Panel: http://localhost:3000/control-panel.html"
    echo
    
    if command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}🔄 CONTAINERIZED FULL STACK${NC}"
        echo "   Command: ./start-containerized-platform.sh start-build"
        echo "   Access:  https://localhost:8443/"
        echo "   ⚠️ Complex setup with all services including GenAI Stack"
        echo "   ⚠️ Longer startup time"
        echo
    fi
    
    echo -e "${BLUE}📚 COMPLETE SERVICE DIRECTORY (24 Services)${NC}"
    echo "   🎯 Core: Control Panel, Chat Copilot, API"
    echo "   🤖 AI: AutoGen Studio, Magentic-One, GenAI Stack, Ollama API"
    echo "   🔍 Search: Perplexica AI Search, SearXNG"
    echo "   🔧 Management: Port Scanner, Nginx, Fortinet, Bacula"
    echo "   🌐 Gateways: HTTP/HTTPS Gateways, Webhook Server"
    echo "   💻 Development: VS Code Web"
    echo "   📊 Knowledge Graphs: Neo4j Database, GenAI Stack Platform"
    echo
    
    echo -e "${BLUE}📚 DOCUMENTATION${NC}"
    echo "   • Complete guide: DEPLOYMENT_STRATEGY_GUIDE.md"
    echo "   • Service summary: DEPLOYMENT_SUMMARY.md"
    echo "   • Current status: COMPREHENSIVE_DEPLOYMENT_GUIDE.md"
    echo "   • Claude instructions: CLAUDE.md"
    echo
}

main() {
    print_header "AI RESEARCH PLATFORM - DEPLOYMENT VALIDATION"
    
    check_prerequisites
    validate_environment  
    validate_configurations
    check_startup_scripts
    check_file_structure
    
    # Only test builds if basic checks pass
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        test_build_capability
    fi
    
    generate_recommendations
    
    print_header "VALIDATION COMPLETE"
    print_status "SUCCESS" "Platform validation finished"
    print_status "INFO" "Choose a deployment strategy and run the appropriate script"
    echo
    print_status "INFO" "To test running services, use: ./validate-deployment.sh urls"
}

# Handle script arguments
case "${1:-validate}" in
    "validate")
        main
        ;;
    "quick")
        check_prerequisites
        validate_environment
        generate_recommendations
        ;;
    "build-test")
        check_prerequisites
        test_build_capability
        ;;
    "urls")
        print_header "AI RESEARCH PLATFORM - SERVICE URL TESTING"
        test_service_urls
        ;;
    *)
        echo "Usage: $0 [validate|quick|build-test|urls]"
        echo "  validate    - Full validation (default)"
        echo "  quick       - Quick environment check"
        echo "  build-test  - Test Docker builds only"
        echo "  urls        - Test all service URLs"
        exit 1
        ;;
esac