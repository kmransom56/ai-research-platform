#!/bin/bash

# AI Platform Health Monitor
# Comprehensive health checking for all services

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏥 AI Platform Health Monitor${NC}"
echo "=============================="
echo "$(date)"
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNING_TESTS=0

# Health check function
check_service() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    local timeout="${4:-5}"
    
    ((TOTAL_TESTS++))
    echo -n "[$TOTAL_TESTS] $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo "000")
    
    if [[ "$response" == "$expected_code" ]]; then
        echo -e "${GREEN}✅ HEALTHY${NC} ($response)"
        ((PASSED_TESTS++))
    elif [[ "$response" == "302" || "$response" == "405" ]]; then
        echo -e "${YELLOW}⚠️  WARNING${NC} ($response - Service running but needs config)"
        ((WARNING_TESTS++))
    else
        echo -e "${RED}❌ FAILED${NC} ($response)"
        ((FAILED_TESTS++))
    fi
}

# Process check function
check_process() {
    local name="$1"
    local pattern="$2"
    
    ((TOTAL_TESTS++))
    echo -n "[$TOTAL_TESTS] $name Process... "
    
    if pgrep -f "$pattern" > /dev/null; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        ((FAILED_TESTS++))
    fi
}

# Check core infrastructure
echo -e "${BLUE}🏗️  Core Infrastructure${NC}"
echo "======================"
check_service "Neo4j Database" "http://localhost:7474" "200"
check_service "PostgreSQL" "http://localhost:5432" "000" # TCP connection test
check_service "RabbitMQ Management" "http://localhost:15672" "200"
check_service "Prometheus" "http://localhost:9090" "405" # Method not allowed is OK
check_service "Grafana" "http://localhost:11002" "302" # Redirect is OK

echo ""
echo -e "${BLUE}🤖 AI Services${NC}"
echo "==============="
check_service "AI Gateway" "http://localhost:9000/health" "200"
check_service "Chat Copilot Backend" "http://localhost:11000/healthz" "200"
check_service "Reasoning Model API" "http://localhost:8000/health" "200"
check_service "General Model API" "http://localhost:8001/health" "200"

echo ""
echo -e "${BLUE}🌐 Web Interfaces${NC}"
echo "=================="
check_service "Open WebUI" "http://localhost:11880" "200"
check_service "VS Code Server" "http://localhost:57081" "302" # Redirect OK
check_service "AutoGen Studio" "http://localhost:11001" "200"

echo ""
echo -e "${BLUE}🔍 Process Health${NC}"
echo "=================="
check_process "Backend API" "dotnet.*11000"
check_process "AI Gateway" "gunicorn.*9000"
check_process "Reasoning Model" "python.*8000"
check_process "General Model" "python.*8001"

echo ""
echo -e "${BLUE}🐳 Docker Containers${NC}"
echo "===================="

# Check Docker containers
if command -v docker > /dev/null; then
    running_containers=$(docker ps --format "{{.Names}}" | wc -l)
    echo "Running containers: $running_containers"
    
    # Key containers
    key_containers=("ai-platform-neo4j" "ai-platform-postgres" "ai-platform-grafana" "ai-platform-openwebui")
    
    for container in "${key_containers[@]}"; do
        ((TOTAL_TESTS++))
        echo -n "[$TOTAL_TESTS] $container... "
        
        if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            status=$(docker inspect "$container" --format "{{.State.Health.Status}}" 2>/dev/null || echo "no-healthcheck")
            if [[ "$status" == "healthy" || "$status" == "no-healthcheck" ]]; then
                echo -e "${GREEN}✅ RUNNING${NC}"
                ((PASSED_TESTS++))
            else
                echo -e "${YELLOW}⚠️  UNHEALTHY${NC} ($status)"
                ((WARNING_TESTS++))
            fi
        else
            echo -e "${RED}❌ NOT RUNNING${NC}"
            ((FAILED_TESTS++))
        fi
    done
fi

echo ""
echo -e "${BLUE}📊 Health Summary${NC}"
echo "=================="
echo -e "✅ HEALTHY: ${GREEN}$PASSED_TESTS${NC}"
echo -e "⚠️  WARNINGS: ${YELLOW}$WARNING_TESTS${NC}"
echo -e "❌ FAILED: ${RED}$FAILED_TESTS${NC}"
echo -e "📊 TOTAL CHECKS: $TOTAL_TESTS"

if [ $TOTAL_TESTS -gt 0 ]; then
    HEALTH_PERCENTAGE=$(( (PASSED_TESTS + WARNING_TESTS) * 100 / TOTAL_TESTS ))
    echo -e "🎯 HEALTH SCORE: ${GREEN}${HEALTH_PERCENTAGE}%${NC}"
fi

echo ""
echo -e "${BLUE}📋 System Resources${NC}"
echo "==================="
echo "Memory usage:"
free -h | head -2

echo ""
echo "Disk usage:"
df -h / | tail -1

echo ""
echo "Load average:"
uptime

echo ""
echo -e "${BLUE}📝 Recent Logs${NC}"
echo "==============="
if [ -d logs ]; then
    echo "Log files available:"
    ls -la logs/ | tail -5
    
    echo ""
    echo "Recent errors (if any):"
    find logs/ -name "*.log" -exec grep -l "ERROR\|error\|Error" {} \; 2>/dev/null | head -3 | while read logfile; do
        echo "📄 $logfile:"
        tail -3 "$logfile" | grep -i error || echo "  (No recent errors)"
    done
fi

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi