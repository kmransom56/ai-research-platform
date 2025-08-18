#!/bin/bash
# Test script for Multi-Agent Collaboration System

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GATEWAY_URL="http://localhost:9000"

echo -e "${BLUE}Testing Multi-Agent Collaboration System${NC}"
echo "================================================"

# Test 1: Gateway Information
echo -e "\n${YELLOW}1. Testing Gateway Information...${NC}"
if gateway_info=$(curl -s "$GATEWAY_URL/info" 2>/dev/null); then
    echo -e "${GREEN}✓${NC} Gateway info retrieved"
    echo "$gateway_info" | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "${RED}✗${NC} Gateway info failed"
    exit 1
fi

# Test 2: Service Status
echo -e "\n${YELLOW}2. Testing Service Discovery...${NC}"
if services_status=$(curl -s "$GATEWAY_URL/services" 2>/dev/null); then
    echo -e "${GREEN}✓${NC} Service status retrieved"
    
    # Count online services
    online_count=$(echo "$services_status" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('online_services', 0))
" 2>/dev/null || echo "0")
    
    total_count=$(echo "$services_status" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('total_services', 0))
" 2>/dev/null || echo "0")
    
    echo "Services online: $online_count/$total_count"
else
    echo -e "${RED}✗${NC} Service status failed"
fi

# Test 3: Simple Collaboration
echo -e "\n${YELLOW}3. Testing Simple Collaboration...${NC}"
simple_test_request='{
    "prompt": "Create a Python function to calculate fibonacci numbers and explain how it works",
    "context": {"max_tokens": 200}
}'

echo "Request: Create fibonacci function with explanation"
if collaboration_result=$(curl -s -X POST "$GATEWAY_URL/v1/collaborate" \
    -H "Content-Type: application/json" \
    -d "$simple_test_request" 2>/dev/null); then
    
    # Check if response contains error
    if echo "$collaboration_result" | grep -q '"error"'; then
        echo -e "${RED}✗${NC} Simple collaboration failed"
        echo "$collaboration_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Error:', data.get('error', 'Unknown error'))
except:
    print('Failed to parse error response')
" 2>/dev/null
    else
        echo -e "${GREEN}✓${NC} Simple collaboration successful"
        
        # Show summary
        echo "$collaboration_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Plan ID:', data.get('plan_id', 'N/A'))
    print('Status:', data.get('status', 'N/A'))
    print('Summary:', data.get('summary', 'N/A'))
    print('Tasks completed:', len(data.get('results', {})))
except:
    print('Response received but could not parse details')
" 2>/dev/null
    fi
else
    echo -e "${RED}✗${NC} Simple collaboration request failed"
fi

# Test 4: Multi-Step Collaboration Plan
echo -e "\n${YELLOW}4. Testing Multi-Step Collaboration Plan...${NC}"
complex_test_request='{
    "prompt": "Research quantum computing, write a Python simulation of a quantum circuit, and create a creative story about quantum entanglement",
    "context": {"complexity": "high"}
}'

echo "Request: Complex multi-step task (research + coding + creative)"
if plan_result=$(curl -s -X POST "$GATEWAY_URL/v1/plan" \
    -H "Content-Type: application/json" \
    -d "$complex_test_request" 2>/dev/null); then
    
    if echo "$plan_result" | grep -q '"error"'; then
        echo -e "${RED}✗${NC} Plan creation failed"
    else
        echo -e "${GREEN}✓${NC} Multi-step plan created"
        
        # Extract plan ID and show details
        plan_id=$(echo "$plan_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('id', ''))
except:
    pass
" 2>/dev/null)
        
        task_count=$(echo "$plan_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(len(data.get('task_sequence', [])))
except:
    print('0')
" 2>/dev/null)
        
        echo "Plan ID: $plan_id"
        echo "Tasks in plan: $task_count"
        
        # Show task breakdown
        echo "$plan_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for i, task in enumerate(data.get('task_sequence', []), 1):
        print(f'  {i}. {task.get(\"type\", \"unknown\")}: {task.get(\"id\", \"N/A\")}')
        if task.get('assigned_services'):
            print(f'     → {task[\"assigned_services\"][0]}')
except:
    pass
" 2>/dev/null
        
        # Test 5: Execute the plan (if we have a valid plan ID)
        if [ -n "$plan_id" ] && [ "$plan_id" != "" ]; then
            echo -e "\n${YELLOW}5. Testing Plan Execution...${NC}"
            
            echo "Executing plan: $plan_id"
            if execution_result=$(curl -s -X POST "$GATEWAY_URL/v1/execute/$plan_id" 2>/dev/null); then
                if echo "$execution_result" | grep -q '"error"'; then
                    echo -e "${RED}✗${NC} Plan execution failed"
                    echo "$execution_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Error:', data.get('error', 'Unknown error'))
except:
    pass
" 2>/dev/null
                else
                    echo -e "${GREEN}✓${NC} Plan execution completed"
                    
                    # Show execution summary
                    echo "$execution_result" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    results = data.get('results', {})
    successful = len([r for r in results.values() if 'error' not in str(r)])
    total = len(results)
    print(f'Tasks completed: {successful}/{total}')
    print('Summary:', data.get('summary', 'N/A'))
except Exception as e:
    print('Could not parse execution results')
" 2>/dev/null
                fi
            else
                echo -e "${RED}✗${NC} Plan execution request failed"
            fi
        fi
    fi
else
    echo -e "${RED}✗${NC} Plan creation request failed"
fi

# Test 6: Individual Service Types
echo -e "\n${YELLOW}6. Testing Individual Task Types...${NC}"

task_types=(
    "reasoning:Solve this equation: x^2 + 5x - 14 = 0"
    "coding:Write a Python function to reverse a string"
    "creative:Write a haiku about artificial intelligence"
    "research:What are the latest developments in machine learning?"
)

for task in "${task_types[@]}"; do
    task_type="${task%:*}"
    prompt="${task#*:}"
    
    echo -e "\nTesting ${BLUE}$task_type${NC} task..."
    
    task_request=$(cat <<EOF
{
    "task_type": "$task_type",
    "prompt": "$prompt",
    "max_tokens": 100
}
EOF
)
    
    if task_result=$(curl -s -X POST "$GATEWAY_URL/v1/completions" \
        -H "Content-Type: application/json" \
        -d "$task_request" 2>/dev/null); then
        
        if echo "$task_result" | grep -q '"error"'; then
            echo -e "${RED}✗${NC} $task_type task failed"
        else
            echo -e "${GREEN}✓${NC} $task_type task successful"
        fi
    else
        echo -e "${RED}✗${NC} $task_type task request failed"
    fi
done

# Summary
echo -e "\n${BLUE}Test Summary${NC}"
echo "=============="
echo ""
echo "Collaboration endpoints tested:"
echo "  • Gateway info and service discovery"
echo "  • Simple collaboration (/v1/collaborate)"
echo "  • Multi-step planning (/v1/plan)"
echo "  • Plan execution (/v1/execute)"
echo "  • Individual task routing (/v1/completions)"
echo ""
echo -e "${GREEN}Testing completed!${NC}"
echo ""
echo "📋 Next steps:"
echo "  1. Check service logs if any tests failed:"
echo "     docker-compose -f docker-compose.ai-stack.yml logs ai-gateway"
echo "  2. Verify all services are running:"
echo "     ./start-ai-stack.sh status"
echo "  3. Try collaboration via curl:"
echo "     curl -X POST http://localhost:9000/v1/collaborate \\"
echo "          -H 'Content-Type: application/json' \\"
echo "          -d '{\"prompt\": \"Your complex task here\"}'"