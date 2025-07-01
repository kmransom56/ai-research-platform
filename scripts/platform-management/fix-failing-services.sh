#!/bin/bash
# Fix for Failing Services: Webhook Server and VS Code Web
# This script addresses the specific services that are not responding

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

print_header "FIXING FAILING SERVICES"

# 1. ANALYZE FAILING SERVICES
print_header "1. ANALYZING FAILING SERVICES"

print_status "INFO" "Checking Docker containers for failing services..."

# Check webhook server
if docker ps | grep -q webhook; then
    WEBHOOK_CONTAINER=$(docker ps --filter "name=webhook" --format "{{.Names}}" | head -1)
    print_status "INFO" "Found webhook container: $WEBHOOK_CONTAINER"

    # Check if it's actually responding
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:11002/health 2>/dev/null | grep -q "200"; then
        print_status "SUCCESS" "Webhook server is actually responding"
    else
        print_status "ERROR" "Webhook server container exists but not responding"
        echo "Container logs:"
        docker logs "$WEBHOOK_CONTAINER" --tail 10
    fi
else
    print_status "ERROR" "No webhook container found"
fi

# Check VS Code Web
if docker ps | grep -q vscode\|code-server; then
    VSCODE_CONTAINER=$(docker ps --filter "name=vscode" --format "{{.Names}}" | head -1)
    if [[ -z "$VSCODE_CONTAINER" ]]; then
        VSCODE_CONTAINER=$(docker ps --filter "name=code-server" --format "{{.Names}}" | head -1)
    fi

    if [[ -n "$VSCODE_CONTAINER" ]]; then
        print_status "INFO" "Found VS Code container: $VSCODE_CONTAINER"

        # Check if it's responding
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:57081 2>/dev/null | grep -q "200\|302"; then
            print_status "SUCCESS" "VS Code Web is actually responding"
        else
            print_status "ERROR" "VS Code Web container exists but not responding"
            echo "Container logs:"
            docker logs "$VSCODE_CONTAINER" --tail 10
        fi
    fi
else
    print_status "ERROR" "No VS Code Web container found"
fi

# 2. RESTART FAILING SERVICES
print_header "2. RESTARTING FAILING SERVICES"

# Function to restart a service by container name pattern
restart_service() {
    local service_pattern=$1
    local service_name=$2
    local port=$3

    print_status "INFO" "Restarting $service_name..."

    # Find and restart containers matching the pattern
    CONTAINERS=$(docker ps -a --filter "name=$service_pattern" --format "{{.Names}}")

    if [[ -n "$CONTAINERS" ]]; then
        for container in $CONTAINERS; do
            print_status "INFO" "Restarting container: $container"
            docker restart "$container"
            sleep 5

            # Check if it's now responding
            if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" 2>/dev/null | grep -q "200\|302\|404"; then
                print_status "SUCCESS" "$service_name is now responding"
                return 0
            fi
        done
        print_status "WARNING" "$service_name containers restarted but may still not be responding"
    else
        print_status "ERROR" "No containers found matching pattern: $service_pattern"
    fi

    return 1
}

# Restart webhook server
restart_service "webhook" "Webhook Server" "11002"

# Restart VS Code Web
restart_service "vscode\|code-server" "VS Code Web" "57081"

# 3. CHECK DOCKER COMPOSE SERVICES
print_header "3. CHECKING DOCKER COMPOSE SERVICES"

print_status "INFO" "Checking Docker Compose services status..."

cd /home/keith/chat-copilot 2>/dev/null || {
    print_status "ERROR" "Cannot change to chat-copilot directory"
    exit 1
}

if [[ -f "configs/docker-compose/docker-compose-full-stack.yml" ]]; then
    print_status "INFO" "Checking Docker Compose services..."

    # Check if webhook service is defined
    if grep -q "webhook" configs/docker-compose/docker-compose-full-stack.yml; then
        print_status "INFO" "Webhook service found in compose file"

        # Try to restart the webhook service specifically
        print_status "INFO" "Restarting webhook service via Docker Compose..."
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml restart webhook-server 2>/dev/null || {
            print_status "WARNING" "Could not restart webhook-server via compose"
        }
    fi

    # Check if vscode service is defined
    if grep -q "vscode\|code-server" configs/docker-compose/docker-compose-full-stack.yml; then
        print_status "INFO" "VS Code service found in compose file"

        # Try to restart the vscode service specifically
        print_status "INFO" "Restarting VS Code service via Docker Compose..."
        docker-compose -f configs/docker-compose/docker-compose-full-stack.yml restart vscode-server 2>/dev/null || {
            print_status "WARNING" "Could not restart vscode-server via compose"
        }
    fi
else
    print_status "ERROR" "Docker Compose file not found"
fi

# 4. CREATE SERVICE HEALTH CHECK SCRIPT
print_header "4. CREATING SERVICE HEALTH CHECK SCRIPT"

cat >check-service-health.sh <<'EOF'
#!/bin/bash
# Service Health Check Script

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

check_service() {
    local name=$1
    local url=$2
    local expected_codes=${3:-"200|302|404"}
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -qE "$expected_codes"; then
        print_status "SUCCESS" "$name is responding"
        return 0
    else
        print_status "ERROR" "$name is not responding"
        return 1
    fi
}

echo "=== SERVICE HEALTH CHECK ==="
echo

# Check all services
check_service "Webhook Server" "http://localhost:11002/health" "200|404"
check_service "VS Code Web" "http://localhost:57081" "200|302"
check_service "Magentic-One Server" "http://localhost:11003" "200|404"
check_service "Port Scanner" "http://localhost:11010" "200"
check_service "Nginx Proxy Manager" "http://localhost:81" "200|302"
check_service "Neo4j Database" "http://localhost:7474" "200"
check_service "GenAI Stack Frontend" "http://localhost:8505" "200"
check_service "GenAI Stack API" "http://localhost:8504" "200"
check_service "GenAI Stack Bot" "http://localhost:8501" "200"
check_service "Perplexica Search AI" "http://localhost:11020" "200"
check_service "SearXNG Search Engine" "http://localhost:11021" "200"
check_service "OpenWebUI" "http://localhost:11880" "200"
check_service "Ollama LLM Server" "http://localhost:11434" "200|404"

echo
print_status "INFO" "Health check complete."
EOF

chmod +x check-service-health.sh
print_status "SUCCESS" "Created service health check script: check-service-health.sh"

# 5. CREATE SERVICE RESTART SCRIPT
print_header "5. CREATING SERVICE RESTART SCRIPT"

cat >restart-failed-services.sh <<'EOF'
#!/bin/bash
# Restart Failed Services Script

restart_if_failed() {
    local name=$1
    local url=$2
    local container_pattern=$3
    local expected_codes=${4:-"200|302|404"}
    
    echo "Checking $name..."
    if ! curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -qE "$expected_codes"; then
        echo "❌ $name is not responding, attempting restart..."
        
        # Find and restart containers
        CONTAINERS=$(docker ps -a --filter "name=$container_pattern" --format "{{.Names}}")
        if [[ -n "$CONTAINERS" ]]; then
            for container in $CONTAINERS; do
                echo "Restarting $container..."
                docker restart "$container"
            done
            sleep 10
            
            # Check again
            if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -qE "$expected_codes"; then
                echo "✅ $name is now responding"
            else
                echo "⚠️ $name still not responding after restart"
            fi
        else
            echo "⚠️ No containers found for $name"
        fi
    else
        echo "✅ $name is responding"
    fi
}

echo "=== RESTARTING FAILED SERVICES ==="
echo

restart_if_failed "Webhook Server" "http://localhost:11002/health" "webhook" "200|404"
restart_if_failed "VS Code Web" "http://localhost:57081" "vscode|code-server" "200|302"

echo
echo "Restart attempt complete. Run './check-service-health.sh' to verify."
EOF

chmod +x restart-failed-services.sh
print_status "SUCCESS" "Created service restart script: restart-failed-services.sh"

# 6. FINAL STATUS CHECK
print_header "6. FINAL STATUS CHECK"

print_status "INFO" "Running final health check..."
sleep 5

# Quick health check
./check-service-health.sh

print_header "SERVICE REPAIR COMPLETE"

echo -e "${GREEN}SOLUTIONS CREATED:${NC}"
echo "1. ✅ check-service-health.sh - Check all service health"
echo "2. ✅ restart-failed-services.sh - Restart only failed services"
echo "3. ✅ Attempted restart of failing services"

echo
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo "1. Run: ./check-service-health.sh (to verify current status)"
echo "2. Run: ./restart-failed-services.sh (to restart any failed services)"
echo "3. If services still fail, check Docker logs: docker logs <container-name>"

echo
print_status "SUCCESS" "Service repair tools created and initial restart attempted!"
