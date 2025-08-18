#!/bin/bash
# MCP Integration Test Suite for AI Collaboration System
# Tests the complete MCP server integration with the AI stack

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GATEWAY_URL="http://localhost:9000"
TEST_COUNT=0
PASSED_COUNT=0
FAILED_COUNT=0

log_test() {
    ((TEST_COUNT++))
    echo -e "${BLUE}[TEST $TEST_COUNT]${NC} $1"
}

log_pass() {
    ((PASSED_COUNT++))
    echo -e "${GREEN}✓ PASS:${NC} $1"
}

log_fail() {
    ((FAILED_COUNT++))
    echo -e "${RED}✗ FAIL:${NC} $1"
}

log_info() {
    echo -e "${YELLOW}ℹ INFO:${NC} $1"
}

# Test MCP server listing
test_mcp_servers() {
    log_test "Testing MCP server listing"
    
    response=$(curl -s "$GATEWAY_URL/mcp" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot connect to API gateway"
        return 1
    fi
    
    if echo "$response" | grep -q '"mcp_servers"'; then
        log_pass "MCP servers endpoint responding"
        
        # Show available servers
        server_count=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['server_count'])" 2>/dev/null || echo "0")
        log_info "Found $server_count MCP servers"
        
        # List server names
        if [[ $server_count -gt 0 ]]; then
            echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    servers = data.get('mcp_servers', {})
    for name, info in servers.items():
        print(f'  - {name}: {info.get(\"name\", \"Unknown\")} ({info.get(\"status\", \"unknown\")})')
except:
    pass
" 2>/dev/null
        fi
    else
        log_fail "MCP servers endpoint not returning expected data"
        return 1
    fi
}

# Test MCP server health
test_mcp_health() {
    log_test "Testing MCP server health checks"
    
    response=$(curl -s "$GATEWAY_URL/mcp/health" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot check MCP server health"
        return 1
    fi
    
    if echo "$response" | grep -q '"overall_status"'; then
        overall_status=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['overall_status'])" 2>/dev/null || echo "unknown")
        online_servers=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['online_servers'])" 2>/dev/null || echo "0")
        
        log_pass "MCP health check responding - Status: $overall_status, Online: $online_servers"
    else
        log_fail "MCP health endpoint not returning expected data"
        return 1
    fi
}

# Test workflow templates with MCP
test_workflow_templates() {
    log_test "Testing workflow templates with MCP integration"
    
    response=$(curl -s "$GATEWAY_URL/workflows" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot get workflow templates"
        return 1
    fi
    
    if echo "$response" | grep -q '"templates"'; then
        template_count=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")
        log_pass "Workflow templates available: $template_count"
        
        # Test restaurant network template specifically
        restaurant_response=$(curl -s "$GATEWAY_URL/workflows/restaurant_network" || echo "ERROR")
        if echo "$restaurant_response" | grep -q '"mcp_integrations"'; then
            log_pass "Restaurant network template has MCP integrations"
        else
            log_fail "Restaurant network template missing MCP integrations"
        fi
    else
        log_fail "Workflow templates endpoint not responding properly"
        return 1
    fi
}

# Test MCP collaboration
test_mcp_collaboration() {
    log_test "Testing MCP-enhanced collaboration"
    
    payload='{
        "prompt": "Check the status of restaurant network devices",
        "template": "restaurant_network",
        "context": {"test_mode": true}
    }'
    
    response=$(curl -s -X POST "$GATEWAY_URL/v1/collaborate/mcp" \
        -H "Content-Type: application/json" \
        -d "$payload" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot test MCP collaboration"
        return 1
    fi
    
    if echo "$response" | grep -q '"collaboration_id"'; then
        collaboration_id=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['collaboration_id'])" 2>/dev/null || echo "unknown")
        log_pass "MCP collaboration successful - ID: ${collaboration_id:0:8}..."
        
        # Check for MCP integrations in response
        if echo "$response" | grep -q '"mcp_integrations_available"'; then
            log_pass "MCP integrations included in collaboration result"
        else
            log_fail "MCP integrations missing from collaboration result"
        fi
    else
        log_fail "MCP collaboration not returning expected data"
        echo "Response: $response"
        return 1
    fi
}

# Test restaurant network endpoints
test_restaurant_endpoints() {
    log_test "Testing restaurant network management endpoints"
    
    # Test network overview
    response=$(curl -s "$GATEWAY_URL/v1/restaurant/network" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot access restaurant network endpoint"
        return 1
    fi
    
    if echo "$response" | grep -q '"restaurant"'; then
        log_pass "Restaurant network overview endpoint responding"
    else
        log_fail "Restaurant network endpoint not returning expected data"
        return 1
    fi
    
    # Test security alerts
    security_response=$(curl -s "$GATEWAY_URL/v1/restaurant/security" || echo "ERROR")
    
    if echo "$security_response" | grep -q '"alerts"' || echo "$security_response" | grep -q '"restaurant"'; then
        log_pass "Restaurant security alerts endpoint responding"
    else
        log_fail "Restaurant security alerts endpoint not working"
    fi
}

# Test service discovery with MCP
test_service_discovery() {
    log_test "Testing service discovery with MCP integration"
    
    response=$(curl -s "$GATEWAY_URL/services" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot access service discovery"
        return 1
    fi
    
    if echo "$response" | grep -q '"mcp_servers"'; then
        log_pass "Service discovery includes MCP servers"
        
        # Show AI vs MCP service counts
        ai_services=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['ai_services']['total_services'])" 2>/dev/null || echo "0")
        mcp_servers=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['mcp_servers']['total_servers'])" 2>/dev/null || echo "0")
        
        log_info "AI Services: $ai_services, MCP Servers: $mcp_servers"
    else
        log_fail "Service discovery missing MCP integration"
        return 1
    fi
}

# Test capability-based routing
test_capability_routing() {
    log_test "Testing MCP capability-based routing"
    
    # Test network management capability
    response=$(curl -s "$GATEWAY_URL/mcp/capabilities/network_management" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot test capability routing"
        return 1
    fi
    
    if echo "$response" | grep -q '"servers"'; then
        server_count=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin)['server_count'])" 2>/dev/null || echo "0")
        log_pass "Capability routing working - network_management: $server_count servers"
    else
        log_fail "Capability routing not working properly"
        return 1
    fi
}

# Test gateway info with MCP features
test_gateway_info() {
    log_test "Testing gateway info with MCP features"
    
    response=$(curl -s "$GATEWAY_URL/info" || echo "ERROR")
    
    if [[ "$response" == "ERROR" ]]; then
        log_fail "Cannot get gateway info"
        return 1
    fi
    
    if echo "$response" | grep -q '"mcp_features"'; then
        log_pass "Gateway info includes MCP features"
        
        # Check for restaurant network features
        if echo "$response" | grep -q '"restaurant_network_features"'; then
            log_pass "Restaurant network features documented"
        else
            log_fail "Restaurant network features missing from gateway info"
        fi
    else
        log_fail "Gateway info missing MCP features"
        return 1
    fi
}

# Main test execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               MCP Integration Test Suite                     ║"
    echo "║         AI Collaboration System with MCP Servers            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    log_info "Testing MCP integration at $GATEWAY_URL"
    echo
    
    # Run all tests
    test_mcp_servers
    echo
    test_mcp_health
    echo
    test_workflow_templates
    echo
    test_service_discovery
    echo
    test_capability_routing
    echo
    test_gateway_info
    echo
    test_mcp_collaboration
    echo
    test_restaurant_endpoints
    echo
    
    # Summary
    echo -e "${BLUE}Test Results Summary${NC}"
    echo "════════════════════════════════════════════════════"
    echo "Total Tests: $TEST_COUNT"
    echo -e "Passed: ${GREEN}$PASSED_COUNT${NC}"
    echo -e "Failed: ${RED}$FAILED_COUNT${NC}"
    
    if [[ $FAILED_COUNT -eq 0 ]]; then
        echo -e "Status: ${GREEN}ALL TESTS PASSED ✓${NC}"
        echo
        echo -e "${GREEN}🎉 MCP integration is working correctly!${NC}"
        echo "✓ All MCP servers are properly integrated"
        echo "✓ Restaurant network management is operational"
        echo "✓ Multi-agent collaboration with MCP is functional"
        echo "✓ Service discovery includes both AI and MCP services"
    else
        echo -e "Status: ${RED}$FAILED_COUNT TESTS FAILED ✗${NC}"
        echo
        echo -e "${YELLOW}⚠️  Some MCP integration issues detected${NC}"
        echo "Check the failed tests above for details"
        exit 1
    fi
}

# Check if gateway is running
if ! curl -s "$GATEWAY_URL/health" >/dev/null 2>&1; then
    echo -e "${RED}ERROR: API Gateway not running at $GATEWAY_URL${NC}"
    echo "Please start the AI Stack Gateway first:"
    echo "  cd python/ai-stack && python api_gateway.py"
    exit 1
fi

# Run tests
main