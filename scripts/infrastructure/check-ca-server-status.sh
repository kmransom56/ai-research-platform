#!/bin/bash

# CA Server Status Check Script
# Monitors CA server health and API endpoint availability
# Helps determine when CA server fixes are complete

set -euo pipefail

# Configuration
CA_SERVER="https://192.168.0.2"
LOG_FILE="/var/log/ca-server-status.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sudo tee -a "$LOG_FILE"
}

# Check basic server connectivity
check_server_connectivity() {
    echo -e "${BLUE}Checking CA server connectivity...${NC}"
    
    if curl -k -s --connect-timeout 10 "$CA_SERVER" > /dev/null; then
        echo -e "${GREEN}✅ CA server is accessible${NC}"
        log "INFO: CA server $CA_SERVER is accessible"
        return 0
    else
        echo -e "${RED}❌ CA server is not accessible${NC}"
        log "ERROR: CA server $CA_SERVER is not accessible"
        return 1
    fi
}

# Check web interface
check_web_interface() {
    echo -e "${BLUE}Checking web interface...${NC}"
    
    local response
    if response=$(curl -k -s -w "%{http_code}" "$CA_SERVER" 2>/dev/null); then
        local http_code="${response: -3}"
        local body="${response%???}"
        
        case $http_code in
            200)
                echo -e "${GREEN}✅ Web interface responding (HTTP 200)${NC}"
                
                # Check if it looks like a Next.js app
                if echo "$body" | grep -qi "next\|react\|certificate"; then
                    echo -e "${GREEN}  └─ Appears to be Next.js Certificate Management App${NC}"
                fi
                
                log "INFO: Web interface responding correctly"
                return 0
                ;;
            404|500|502|503)
                echo -e "${YELLOW}⚠️  Web interface issues (HTTP $http_code)${NC}"
                log "WARNING: Web interface HTTP $http_code"
                return 1
                ;;
            *)
                echo -e "${YELLOW}⚠️  Unexpected response (HTTP $http_code)${NC}"
                log "WARNING: Unexpected HTTP code $http_code"
                return 1
                ;;
        esac
    else
        echo -e "${RED}❌ Web interface not responding${NC}"
        log "ERROR: Web interface not responding"
        return 1
    fi
}

# Test potential API endpoints
test_api_endpoints() {
    echo -e "${BLUE}Testing API endpoints...${NC}"
    
    local endpoints=(
        "/api/certificates/generate"
        "/api/csr/submit"
        "/api/certificates/csr"
        "/api/ca/generate"
        "/api/ca/csr"
        "/generate"
        "/certificates"
        "/csr"
        "/api/health"
        "/api/status"
    )
    
    local working_endpoints=()
    local broken_endpoints=()
    
    for endpoint in "${endpoints[@]}"; do
        local response
        local http_code
        
        # Test GET request
        if response=$(curl -k -s -w "%{http_code}" "$CA_SERVER$endpoint" 2>/dev/null); then
            http_code="${response: -3}"
            
            case $http_code in
                200)
                    echo -e "${GREEN}✅ $endpoint (HTTP 200)${NC}"
                    working_endpoints+=("$endpoint")
                    ;;
                405)
                    echo -e "${YELLOW}🔶 $endpoint (Method Not Allowed - may work with POST)${NC}"
                    working_endpoints+=("$endpoint")
                    ;;
                404)
                    echo -e "${RED}❌ $endpoint (Not Found)${NC}"
                    broken_endpoints+=("$endpoint")
                    ;;
                500|502|503)
                    echo -e "${YELLOW}⚠️  $endpoint (Server Error $http_code)${NC}"
                    broken_endpoints+=("$endpoint")
                    ;;
                *)
                    echo -e "${YELLOW}🔶 $endpoint (HTTP $http_code)${NC}"
                    ;;
            esac
        else
            echo -e "${RED}❌ $endpoint (Connection failed)${NC}"
            broken_endpoints+=("$endpoint")
        fi
    done
    
    echo ""
    echo -e "${BLUE}API Endpoint Summary:${NC}"
    echo -e "Working/Accessible: ${GREEN}${#working_endpoints[@]}${NC}"
    echo -e "Not Found/Broken: ${RED}${#broken_endpoints[@]}${NC}"
    
    if [[ ${#working_endpoints[@]} -gt 0 ]]; then
        log "INFO: Working endpoints found: ${working_endpoints[*]}"
    fi
    
    if [[ ${#broken_endpoints[@]} -gt 0 ]]; then
        log "WARNING: Broken endpoints: ${broken_endpoints[*]}"
    fi
}

# Test certificate generation capability
test_certificate_generation() {
    echo -e "${BLUE}Testing certificate generation capability...${NC}"
    
    # Create a test CSR
    local temp_dir
    temp_dir=$(mktemp -d)
    local test_key="$temp_dir/test.key"
    local test_csr="$temp_dir/test.csr"
    
    # Generate test key and CSR
    openssl genrsa -out "$test_key" 2048 2>/dev/null
    openssl req -new -key "$test_key" -out "$test_csr" -subj "/C=US/ST=Test/L=Test/O=Test/CN=test.local" 2>/dev/null
    
    local csr_content
    csr_content=$(cat "$test_csr")
    
    # Test JSON payload
    local json_payload
    json_payload=$(jq -n \
        --arg csr "$csr_content" \
        --arg domain "test.local" \
        '{
            csr: $csr,
            domain: $domain,
            validityDays: 365,
            certificateType: "server"
        }')
    
    # Try the most likely endpoints
    local test_endpoints=("/api/certificates/generate" "/api/csr/submit" "/generate")
    local cert_generation_working=false
    
    for endpoint in "${test_endpoints[@]}"; do
        echo -e "${YELLOW}Testing certificate generation at $endpoint...${NC}"
        
        local response
        if response=$(curl -k -s -X POST \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d "$json_payload" \
            --connect-timeout 10 \
            --max-time 30 \
            "$CA_SERVER$endpoint" 2>/dev/null); then
            
            # Check if we got a certificate back
            if echo "$response" | jq -e '.certificate' > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Certificate generation working at $endpoint${NC}"
                cert_generation_working=true
                log "SUCCESS: Certificate generation working at $endpoint"
                break
            elif echo "$response" | grep -qi "certificate\|error\|invalid"; then
                echo -e "${YELLOW}🔶 $endpoint responding but may have issues${NC}"
                echo -e "   Response preview: $(echo "$response" | head -c 100)..."
                log "INFO: $endpoint responding with: $response"
            fi
        fi
    done
    
    if [[ "$cert_generation_working" == "false" ]]; then
        echo -e "${RED}❌ Certificate generation not working on tested endpoints${NC}"
        log "ERROR: Certificate generation not working"
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    return $([ "$cert_generation_working" == "true" ] && echo 0 || echo 1)
}

# Check for known CA server issues
check_known_issues() {
    echo -e "${BLUE}Checking for known CA server issues...${NC}"
    
    # Test for Router compatibility issues
    local response
    if response=$(curl -k -s "$CA_SERVER/api/certificates/generate" 2>/dev/null); then
        if echo "$response" | grep -qi "cannot.*get\|method.*not.*allowed\|404"; then
            echo -e "${YELLOW}⚠️  Possible Router incompatibility (Pages vs App Router)${NC}"
            log "WARNING: Possible Router incompatibility detected"
        fi
    fi
    
    # Test for permission issues
    if response=$(curl -k -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' \
        "$CA_SERVER/api/certificates/generate" 2>/dev/null); then
        
        if echo "$response" | grep -qi "permission\|eacces\|enoent\|forbidden"; then
            echo -e "${YELLOW}⚠️  Possible file permission issues${NC}"
            log "WARNING: Possible file permission issues detected"
        fi
    fi
    
    echo -e "${BLUE}✅ Known issues check completed${NC}"
}

# Main status check
main() {
    echo -e "${BLUE}=== CA Server Status Check ===${NC}"
    echo -e "${BLUE}Server: $CA_SERVER${NC}"
    echo -e "${BLUE}Time: $(date)${NC}"
    echo ""
    
    local overall_status="healthy"
    
    # Run all checks
    if ! check_server_connectivity; then
        overall_status="down"
    fi
    
    if ! check_web_interface; then
        overall_status="issues"
    fi
    
    test_api_endpoints
    
    if ! test_certificate_generation; then
        overall_status="not-ready"
    fi
    
    check_known_issues
    
    echo ""
    echo -e "${BLUE}=== Overall Status ===${NC}"
    case $overall_status in
        "healthy")
            echo -e "${GREEN}🎉 CA Server appears to be working correctly!${NC}"
            echo -e "${GREEN}   Certificate automation should work.${NC}"
            log "SUCCESS: CA server is healthy and ready"
            ;;
        "not-ready")
            echo -e "${YELLOW}⚠️  CA Server is accessible but certificate generation not working${NC}"
            echo -e "${YELLOW}   Still needs fixes for automation.${NC}"
            log "WARNING: CA server accessible but not ready for automation"
            ;;
        "issues")
            echo -e "${YELLOW}⚠️  CA Server has some issues but may be partially working${NC}"
            log "WARNING: CA server has issues"
            ;;
        "down")
            echo -e "${RED}❌ CA Server is not accessible${NC}"
            log "ERROR: CA server is down"
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}💡 To recheck status: $0${NC}"
    echo -e "${BLUE}📋 Log file: $LOG_FILE${NC}"
    
    log "STATUS_CHECK: Overall status is $overall_status"
}

# Initialize log file
sudo touch "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"

# Run status check
main "$@"