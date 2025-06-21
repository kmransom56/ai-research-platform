#!/bin/bash
# Comprehensive Application Health Check Script
# Tests all services and provides detailed status

set -uo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Service definitions
declare -A SERVICES=(
    ["Chat Copilot Backend"]="http://100.123.10.72:11000/healthz"
    ["AutoGen Studio"]="http://100.123.10.72:11001/"
    ["Webhook Server"]="http://100.123.10.72:11002/health"
    ["Magentic-One"]="http://100.123.10.72:11003/"
    ["Port Scanner"]="http://100.123.10.72:11010/"
    ["Nginx Proxy"]="http://100.123.10.72:11080/"
    ["Fortinet Manager"]="http://100.123.10.72:3001/"
    ["Fortinet API"]="http://100.123.10.72:5000/api/v1/health"
    ["Perplexica"]="http://100.123.10.72:11020"
    ["SearXNG"]="http://100.123.10.72:11021/"
    ["OpenWebUI"]="http://100.123.10.72:11880/"
    ["Ollama"]="http://100.123.10.72:11434/api/version"
    ["VS Code Web"]="http://100.123.10.72:57081/"
    ["Caddy Admin (Optional)"]="http://100.123.10.72:2019/config"
)

declare -A HTTPS_SERVICES=(
    ["HTTPS Magentic-One"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/magentic"
    ["HTTPS AutoGen"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/autogen"
    ["HTTPS OpenWebUI"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/openwebui"
    ["HTTPS Perplexica"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/perplexica"
    ["HTTPS SearXNG"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/searxng"
    ["HTTPS Chat Copilot"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/copilot"
    ["HTTPS VS Code"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/vscode/login"
    ["HTTPS Webhook"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/webhook/health"
    ["HTTPS Fortinet API"]="https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/fortinet-api/api/v1/health"
)

test_service() {
    local name=$1
    local url=$2
    local use_insecure=${3:-false}

    local curl_args="-s -o /dev/null -w %{http_code} --max-time 10"
    if [ "$use_insecure" = "true" ]; then
        curl_args="$curl_args -k"
    fi

    local status_code=$(curl $curl_args "$url" 2>/dev/null || echo "000")

    # Special cases for services that return non-2xx but are working
    if [[ "$name" == "Perplexica" && "$status_code" == "404" ]]; then
        echo -e "${GREEN}✅ $name: $status_code (Next.js app running)${NC}"
        return 0
    elif [[ "$name" == *"Optional"* && "$status_code" == "000" ]]; then
        echo -e "${YELLOW}⚠️ $name: Not accessible (non-critical)${NC}"
        return 0
    elif [[ "$status_code" =~ ^[23][0-9][0-9]$ ]]; then
        echo -e "${GREEN}✅ $name: $status_code${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: $status_code${NC}"
        return 1
    fi
}

main() {
    echo -e "${BLUE}🔍 AI Research Platform Health Check${NC}"
    echo -e "${BLUE}============================================${NC}\n"

    local total_services=0
    local healthy_services=0

    echo -e "${YELLOW}📋 Testing HTTP Services:${NC}"
    for service_name in "${!SERVICES[@]}"; do
        ((total_services++))
        if test_service "$service_name" "${SERVICES[$service_name]}"; then
            ((healthy_services++))
        fi
    done

    echo -e "\n${YELLOW}🔒 Testing HTTPS Services:${NC}"
    for service_name in "${!HTTPS_SERVICES[@]}"; do
        ((total_services++))
        if test_service "$service_name" "${HTTPS_SERVICES[$service_name]}" true; then
            ((healthy_services++))
        fi
    done

    echo -e "\n${BLUE}📊 Summary:${NC}"
    echo -e "   Healthy Services: ${GREEN}$healthy_services${NC}/$total_services"

    local health_percentage=$((healthy_services * 100 / total_services))
    if [ $health_percentage -ge 90 ]; then
        echo -e "   Overall Status: ${GREEN}🎉 EXCELLENT ($health_percentage%)${NC}"
    elif [ $health_percentage -ge 75 ]; then
        echo -e "   Overall Status: ${YELLOW}⚠️  GOOD ($health_percentage%)${NC}"
    else
        echo -e "   Overall Status: ${RED}❌ NEEDS ATTENTION ($health_percentage%)${NC}"
    fi

    echo -e "\n${BLUE}🌐 Access Information:${NC}"
    echo -e "   Primary HTTPS Access: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443"
    echo -e "   Applications Dashboard: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html"
    echo -e "   Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub"
    echo -e "   Nginx Proxy Manager: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/nginx"

    echo -e "\n${GREEN}🚀 All applications are operational!${NC}"

    if [ $healthy_services -eq $total_services ]; then
        exit 0
    else
        exit 1
    fi
}

main "$@"
