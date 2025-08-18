#!/bin/bash
# Comprehensive validation script for Multi-Agent Collaboration System

set -euo pipefail

# Colors and formatting
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

GATEWAY_URL="http://localhost:9000"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test results array
declare -a TEST_RESULTS=()

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
    TEST_RESULTS+=("✓ $1")
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_TESTS++))
    TEST_RESULTS+=("✗ $1")
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Increment total test counter
count_test() {
    ((TOTAL_TESTS++))
}

# Test if service is responding
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    count_test
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_URL$endpoint" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            log_success "$description (HTTP $response)"
            return 0
        else
            log_error "$description (HTTP $response, expected $expected_status)"
            return 1
        fi
    else
        log_error "$description (connection failed)"
        return 1
    fi
}

# Test JSON endpoint
test_json_endpoint() {
    local endpoint="$1"
    local description="$2"
    local method="${3:-GET}"
    local payload="${4:-}"
    
    count_test
    
    local curl_cmd="curl -s"
    if [ "$method" = "POST" ]; then
        curl_cmd="$curl_cmd -X POST -H 'Content-Type: application/json'"
        if [ -n "$payload" ]; then
            curl_cmd="$curl_cmd -d '$payload'"
        fi
    fi
    
    if response=$(eval "$curl_cmd '$GATEWAY_URL$endpoint'" 2>/dev/null); then
        if echo "$response" | python3 -m json.tool >/dev/null 2>&1; then
            if echo "$response" | grep -q '"error"'; then
                local error_msg=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null)
                log_error "$description (API error: $error_msg)"
                return 1
            else
                log_success "$description"
                return 0
            fi
        else
            log_error "$description (invalid JSON response)"
            return 1
        fi
    else
        log_error "$description (request failed)"
        return 1
    fi
}

# Main validation function
validate_collaboration_system() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          Multi-Agent Collaboration System Validation        ║"
    echo "║                     Comprehensive Test Suite                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Phase 1: Basic Gateway Health
    log_info "Phase 1: Gateway Health & Basic Endpoints"
    echo "────────────────────────────────────────────────────"
    
    test_endpoint "/" "Gateway root endpoint"
    test_endpoint "/info" "Gateway information endpoint"
    test_endpoint "/health" "Health check endpoint"
    test_endpoint "/services" "Service discovery endpoint"
    
    # Phase 2: Workflow Templates
    log_info ""
    log_info "Phase 2: Workflow Template System"
    echo "────────────────────────────────────────────────────"
    
    test_json_endpoint "/workflows" "List workflow templates"
    test_json_endpoint "/workflows/research_analysis" "Get research_analysis template"
    test_json_endpoint "/workflows/code_development" "Get code_development template"
    test_json_endpoint "/workflows/creative_project" "Get creative_project template"
    
    test_json_endpoint "/workflows/suggest" "Template suggestion" "POST" '{"prompt": "Build a web application"}'
    
    # Phase 3: Service Status Validation
    log_info ""
    log_info "Phase 3: Service Status & Capabilities"
    echo "────────────────────────────────────────────────────"
    
    count_test
    if services_response=$(curl -s "$GATEWAY_URL/services" 2>/dev/null); then
        if online_services=$(echo "$services_response" | python3 -c "import json,sys; print(json.load(sys.stdin)['online_services'])" 2>/dev/null); then
            total_services=$(echo "$services_response" | python3 -c "import json,sys; print(json.load(sys.stdin)['total_services'])" 2>/dev/null)
            if [ "$online_services" -gt 0 ]; then
                log_success "Service discovery ($online_services/$total_services services online)"
            else
                log_error "Service discovery (no services online)"
            fi
        else
            log_error "Service discovery (invalid response format)"
        fi
    else
        log_error "Service discovery (request failed)"
    fi
    
    # Phase 4: Basic Collaboration
    log_info ""
    log_info "Phase 4: Basic Collaboration Tests"
    echo "────────────────────────────────────────────────────"
    
    # Simple collaboration test
    test_json_endpoint "/v1/collaborate" "Simple collaboration" "POST" '{
        "prompt": "Write a Python function to calculate the factorial of a number",
        "context": {"max_tokens": 150}
    }'
    
    # Test different task types
    local task_types=("reasoning" "general" "coding" "creative")
    for task_type in "${task_types[@]}"; do
        test_json_endpoint "/v1/completions" "$task_type task routing" "POST" "{
            \"task_type\": \"$task_type\",
            \"prompt\": \"Test prompt for $task_type\",
            \"max_tokens\": 50
        }"
    done
    
    # Phase 5: Template-Based Collaboration
    log_info ""
    log_info "Phase 5: Template-Based Collaboration"
    echo "────────────────────────────────────────────────────"
    
    # Test each template
    local templates=("research_analysis" "code_development" "creative_project" "technical_docs")
    local prompts=(
        "Analyze renewable energy trends"
        "Create a REST API for task management"
        "Write a story about time travel"
        "Document API authentication methods"
    )
    
    for i in "${!templates[@]}"; do
        template="${templates[$i]}"
        prompt="${prompts[$i]}"
        
        test_json_endpoint "/v1/collaborate/template" "Template collaboration: $template" "POST" "{
            \"prompt\": \"$prompt\",
            \"template\": \"$template\",
            \"context\": {\"test_mode\": true}
        }"
    done
    
    # Phase 6: Plan Creation and Execution
    log_info ""
    log_info "Phase 6: Plan Creation & Execution Workflow"
    echo "────────────────────────────────────────────────────"
    
    # Create a plan
    count_test
    plan_payload='{
        "prompt": "Research machine learning frameworks and create a comparison guide",
        "template": "research_analysis"
    }'
    
    if plan_response=$(curl -s -X POST "$GATEWAY_URL/v1/plan" \
        -H "Content-Type: application/json" \
        -d "$plan_payload" 2>/dev/null); then
        
        if plan_id=$(echo "$plan_response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null); then
            if [ -n "$plan_id" ] && [ "$plan_id" != "null" ]; then
                log_success "Plan creation (ID: ${plan_id:0:8}...)"
                
                # Test plan execution
                count_test
                if execution_response=$(curl -s -X POST "$GATEWAY_URL/v1/execute/$plan_id" 2>/dev/null); then
                    if echo "$execution_response" | python3 -m json.tool >/dev/null 2>&1; then
                        if echo "$execution_response" | grep -q '"error"'; then
                            log_error "Plan execution (API error)"
                        else
                            log_success "Plan execution"
                        fi
                    else
                        log_error "Plan execution (invalid JSON response)"
                    fi
                else
                    log_error "Plan execution (request failed)"
                fi
            else
                log_error "Plan creation (no plan ID returned)"
            fi
        else
            log_error "Plan creation (cannot parse plan ID)"
        fi
    else
        log_error "Plan creation (request failed)"
    fi
    
    # Phase 7: Error Handling & Edge Cases
    log_info ""
    log_info "Phase 7: Error Handling & Edge Cases"
    echo "────────────────────────────────────────────────────"
    
    # Test invalid template
    count_test
    if error_response=$(curl -s -X POST "$GATEWAY_URL/v1/collaborate/template" \
        -H "Content-Type: application/json" \
        -d '{"prompt": "test", "template": "invalid_template"}' 2>/dev/null); then
        
        if echo "$error_response" | grep -q '"error"'; then
            log_success "Invalid template handling"
        else
            log_error "Invalid template handling (should return error)"
        fi
    else
        log_error "Invalid template handling (request failed)"
    fi
    
    # Test empty prompt
    count_test
    if error_response=$(curl -s -X POST "$GATEWAY_URL/v1/collaborate" \
        -H "Content-Type: application/json" \
        -d '{"prompt": ""}' 2>/dev/null); then
        
        if echo "$error_response" | grep -q '"error"'; then
            log_success "Empty prompt handling"
        else
            log_error "Empty prompt handling (should return error)"
        fi
    else
        log_error "Empty prompt handling (request failed)"
    fi
    
    # Test invalid plan execution
    count_test
    if error_response=$(curl -s -X POST "$GATEWAY_URL/v1/execute/invalid-plan-id" 2>/dev/null); then
        if echo "$error_response" | grep -q '"error"'; then
            log_success "Invalid plan ID handling"
        else
            log_error "Invalid plan ID handling (should return error)"
        fi
    else
        log_error "Invalid plan ID handling (request failed)"
    fi
    
    # Phase 8: Performance & Load Testing
    log_info ""
    log_info "Phase 8: Performance & Concurrent Requests"
    echo "────────────────────────────────────────────────────"
    
    # Test concurrent requests
    count_test
    log_info "Testing 5 concurrent collaboration requests..."
    
    start_time=$(date +%s)
    for i in {1..5}; do
        curl -s -X POST "$GATEWAY_URL/v1/collaborate" \
            -H "Content-Type: application/json" \
            -d "{\"prompt\": \"Simple test request $i\", \"context\": {\"test\": true}}" \
            >/dev/null 2>&1 &
    done
    wait
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ $duration -lt 60 ]; then
        log_success "Concurrent request handling (${duration}s)"
    else
        log_warning "Concurrent request handling (${duration}s - may be slow)"
    fi
    
    # Generate comprehensive report
    echo ""
    echo -e "${BOLD}${BLUE}Validation Results Summary${NC}"
    echo "════════════════════════════════════════════════════"
    echo ""
    echo -e "Total Tests: ${BOLD}$TOTAL_TESTS${NC}"
    echo -e "Passed: ${GREEN}${BOLD}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}${BOLD}$FAILED_TESTS${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "Status: ${GREEN}${BOLD}ALL TESTS PASSED ✓${NC}"
    else
        echo -e "Status: ${RED}${BOLD}$FAILED_TESTS TESTS FAILED ✗${NC}"
    fi
    
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Success Rate: ${BOLD}${success_rate}%${NC}"
    
    # Detailed results
    echo ""
    echo -e "${BOLD}Detailed Test Results:${NC}"
    echo "────────────────────────────────────────────────────"
    for result in "${TEST_RESULTS[@]}"; do
        if [[ $result == ✓* ]]; then
            echo -e "${GREEN}$result${NC}"
        else
            echo -e "${RED}$result${NC}"
        fi
    done
    
    # System information
    echo ""
    echo -e "${BOLD}System Information:${NC}"
    echo "────────────────────────────────────────────────────"
    echo "Gateway URL: $GATEWAY_URL"
    echo "Test Date: $(date)"
    echo "User: $(whoami)"
    
    # Service status summary
    if services_info=$(curl -s "$GATEWAY_URL/services" 2>/dev/null); then
        echo ""
        echo -e "${BOLD}Active Services:${NC}"
        echo "$services_info" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    services = data.get('services', {})
    for name, info in services.items():
        status = info.get('status', 'unknown')
        if status == 'online':
            print(f'  ✓ {name} ({info.get(\"url\", \"N/A\")})')
        else:
            print(f'  ✗ {name} ({status})')
except:
    print('  Could not parse service information')
" 2>/dev/null
    fi
    
    # Recommendations
    echo ""
    echo -e "${BOLD}Recommendations:${NC}"
    echo "────────────────────────────────────────────────────"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo "🎉 Collaboration system is fully operational!"
        echo "✓ All endpoints are responding correctly"
        echo "✓ All workflow templates are functional"
        echo "✓ Service discovery and health monitoring working"
        echo "✓ Multi-agent collaboration ready for production use"
    else
        echo "⚠️  Issues detected in collaboration system:"
        if [ $success_rate -lt 50 ]; then
            echo "❌ Major issues - check service status and gateway logs"
            echo "   Run: docker-compose -f docker-compose.ai-stack.yml logs ai-gateway"
        elif [ $success_rate -lt 80 ]; then
            echo "⚠️  Some services may be unavailable"
            echo "   Run: ./start-ai-stack.sh status"
        else
            echo "✓ Most functionality working - minor issues detected"
        fi
        
        echo ""
        echo "🔧 Troubleshooting steps:"
        echo "1. Check service health: curl $GATEWAY_URL/services"
        echo "2. Restart AI stack: ./start-ai-stack.sh restart"
        echo "3. Check gateway logs: docker logs ai-platform-ai-gateway"
        echo "4. Verify all services: ./start-ai-stack.sh status"
    fi
    
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo "────────────────────────────────────────────────────"
    echo "📚 Read the collaboration guide: COLLABORATION_GUIDE.md"
    echo "🧪 Try example collaborations: ./test-collaboration.sh"
    echo "🔧 Monitor system health: watch curl -s $GATEWAY_URL/health"
    echo "📊 View service dashboard: curl $GATEWAY_URL/services | jq"
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run validation if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    validate_collaboration_system
fi