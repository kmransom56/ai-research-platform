#!/bin/bash
# Test script for AI Stack integration

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing AI Stack Integration${NC}"
echo "=================================="

# Test 1: Check if services are running
echo -e "\n${YELLOW}1. Checking service availability...${NC}"

services=(
    "Gateway:9000"
    "vLLM Reasoning:8000"
    "vLLM General:8001"
    "vLLM Coding:8002"
    "Oobabooga:7860"
    "KoboldCpp:5001"
)

for service in "${services[@]}"; do
    name="${service%:*}"
    port="${service#*:}"
    
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1 || \
       curl -s "http://localhost:$port" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name (port $port)"
    else
        echo -e "${RED}✗${NC} $name (port $port)"
    fi
done

# Test 2: Gateway health check
echo -e "\n${YELLOW}2. Testing gateway health...${NC}"
if gateway_health=$(curl -s "http://localhost:9000/health" 2>/dev/null); then
    echo -e "${GREEN}✓${NC} Gateway health check successful"
    echo "$gateway_health" | python3 -m json.tool 2>/dev/null || echo "$gateway_health"
else
    echo -e "${RED}✗${NC} Gateway health check failed"
fi

# Test 3: Test completion endpoints
echo -e "\n${YELLOW}3. Testing completion endpoints...${NC}"

test_requests=(
    "reasoning:Solve this equation: 2x + 5 = 17"
    "general:Say hello in a friendly way"
    "coding:Write a Python function to add two numbers"
    "creative:Write a short poem about AI"
)

for test in "${test_requests[@]}"; do
    task_type="${test%:*}"
    prompt="${test#*:}"
    
    echo -e "\nTesting ${BLUE}$task_type${NC} task..."
    
    response=$(curl -s -X POST "http://localhost:9000/v1/completions" \
        -H "Content-Type: application/json" \
        -d "{\"task_type\": \"$task_type\", \"prompt\": \"$prompt\", \"max_tokens\": 50}" \
        2>/dev/null || echo '{"error": "Request failed"}')
    
    if echo "$response" | grep -q '"error"'; then
        echo -e "${RED}✗${NC} $task_type task failed"
        echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "$response"
    else
        echo -e "${GREEN}✓${NC} $task_type task successful"
    fi
done

# Test 4: Docker container status
echo -e "\n${YELLOW}4. Checking Docker containers...${NC}"

containers=(
    "ai-platform-ai-gateway"
    "ai-platform-vllm-reasoning"
    "ai-platform-vllm-general"
    "ai-platform-vllm-coding"
    "ai-platform-oobabooga"
    "ai-platform-koboldcpp"
)

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✓${NC} $container ($status)"
        else
            echo -e "${YELLOW}⚠${NC} $container ($status)"
        fi
    else
        echo -e "${RED}✗${NC} $container (not found)"
    fi
done

echo -e "\n${BLUE}Test completed!${NC}"
echo "=================================="
echo ""
echo "If tests failed, check logs with:"
echo "  docker-compose -f docker-compose.ai-stack.yml logs [service-name]"
echo ""
echo "For detailed status:"
echo "  ./scripts/platform-management/manage-ai-stack.sh health"