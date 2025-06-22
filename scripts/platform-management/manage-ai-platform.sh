#!/bin/bash
# AI Research Platform Complete Service Management Script

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

show_usage() {
    echo "Usage: $0 {start|stop|restart|status|logs|install|uninstall|test}"
    echo
    echo "Commands:"
    echo "  start     - Start all AI Platform services"
    echo "  stop      - Stop all AI Platform services"
    echo "  restart   - Restart all AI Platform services"
    echo "  status    - Show comprehensive service status"
    echo "  logs      - Show service logs"
    echo "  install   - Install auto-startup services"
    echo "  uninstall - Remove auto-startup services"
    echo "  test      - Test all service URLs"
    echo
}

show_status() {
    print_status "INFO" "AI Research Platform Complete Status:"
    echo
    
    # Check systemd services
    echo "🔧 Systemd Services:"
    services=(
        "ai-platform-services.service"
        "ai-platform-python.service"
        "ai-platform-external.service"
        "ai-platform-gateways.service"
        "neo4j-genai.service"
        "genai-stack-services.service"
    )
    
    for service in "${services[@]}"; do
        if sudo systemctl is-active "$service" &>/dev/null; then
            echo "  ✅ $service: ACTIVE"
        else
            echo "  ❌ $service: INACTIVE"
        fi
    done
    
    echo
    echo "🐳 Docker Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -20
    
    echo
    echo "🌐 Service URLs (All accessible through nginx):"
    echo "  • Control Panel: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/hub"
    echo "  • Chat Copilot: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/copilot/"
    echo "  • AutoGen Studio: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/autogen/"
    echo "  • Magentic-One: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/magentic/"
    echo "  • Perplexica: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/perplexica/"
    echo "  • SearXNG: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/searxng/"
    echo "  • Port Scanner: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/portscanner/"
    echo "  • Neo4j: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/neo4j/"
    echo "  • GenAI Stack: https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/"
}

start_services() {
    print_status "INFO" "Starting AI Research Platform services..."
    
    if sudo systemctl start ai-platform.target; then
        print_status "SUCCESS" "AI Platform services started"
        sleep 10
        show_status
    else
        print_status "ERROR" "Failed to start AI Platform services"
        return 1
    fi
}

stop_services() {
    print_status "INFO" "Stopping AI Research Platform services..."
    
    if sudo systemctl stop ai-platform.target; then
        print_status "SUCCESS" "AI Platform services stopped"
    else
        print_status "ERROR" "Failed to stop AI Platform services"
        return 1
    fi
}

restart_services() {
    print_status "INFO" "Restarting AI Research Platform services..."
    stop_services
    sleep 5
    start_services
}

show_logs() {
    print_status "INFO" "Showing AI Platform logs (Ctrl+C to exit)..."
    echo
    sudo journalctl -u ai-platform.target -u ai-platform-services.service -u ai-platform-python.service -u ai-platform-external.service -u ai-platform-gateways.service -u neo4j-genai.service -f
}

test_services() {
    print_status "INFO" "Testing AI Platform service URLs..."
    echo
    
    services=(
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/hub:Control Panel"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/copilot/:Chat Copilot"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/copilot/api/:API Health Check"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/autogen/:AutoGen Studio"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/magentic/:Magentic-One"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/webhook/:Webhook Server"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/perplexica/:Perplexica"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/searxng/:SearXNG"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/portscanner/:Port Scanner"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/nginx/:Nginx Gateway"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/fortinet/:Fortinet Manager"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/bacula/:Bacula Backup"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/neo4j/:Neo4j Database"
        "https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/genai-stack/:GenAI Stack"
    )
    
    accessible_count=0
    total_count=${#services[@]}
    
    for service in "${services[@]}"; do
        url="${service%%:*}"
        name="${service##*:}"
        
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
        print_status "WARNING" "Many services are not responding (may need startup time)"
    fi
}

install_services() {
    print_status "INFO" "Installing AI Platform auto-startup services..."
    if [[ -f "install-ai-platform-startup.sh" ]]; then
        ./install-ai-platform-startup.sh
    else
        print_status "ERROR" "install-ai-platform-startup.sh not found"
        return 1
    fi
}

uninstall_services() {
    print_status "INFO" "Uninstalling AI Platform auto-startup services..."
    
    # Stop and disable services
    services=(
        "ai-platform.target"
        "ai-platform-services.service"
        "ai-platform-python.service"
        "ai-platform-external.service"
        "ai-platform-gateways.service"
        "neo4j-genai.service"
        "genai-stack-services.service"
    )
    
    for service in "${services[@]}"; do
        sudo systemctl stop "$service" || true
        sudo systemctl disable "$service" || true
        sudo rm -f "/etc/systemd/system/$service"
    done
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    print_status "SUCCESS" "AI Platform auto-startup services removed"
}

# Main script logic
case "${1:-}" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        test_services
        ;;
    "install")
        install_services
        ;;
    "uninstall")
        uninstall_services
        ;;
    *)
        show_usage
        exit 1
        ;;
esac