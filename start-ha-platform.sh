#!/bin/bash

# =============================================================================
# AI Research Platform - HA Deployment Script
# =============================================================================
# Starts the platform in High Availability mode with automatic failover
# =============================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Script directory (auto-detect platform root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$SCRIPT_DIR"

print_status() {
    local level=$1
    local message=$2
    case $level in
        "INFO")  echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "ERROR") echo -e "${RED}❌ ${message}${NC}" ;;
        "ENHANCE") echo -e "${PURPLE}🔧 ${message}${NC}" ;;
    esac
}

print_banner() {
    echo "=============================================================================="
    echo "🚀 AI RESEARCH PLATFORM - HIGH AVAILABILITY DEPLOYMENT"
    echo "🌐 Multi-node cluster with automatic failover and load balancing"
    echo "=============================================================================="
    echo
}

# Detect node configuration
detect_node_configuration() {
    print_status "INFO" "Detecting HA node configuration..."
    
    # Check for existing node configuration
    if [[ -f "$PLATFORM_ROOT/.env" ]]; then
        if grep -q "NODE_ID=" "$PLATFORM_ROOT/.env"; then
            local node_id=$(grep "NODE_ID=" "$PLATFORM_ROOT/.env" | cut -d'=' -f2)
            print_status "INFO" "Found existing node configuration: $node_id"
            return 0
        fi
    fi
    
    # Prompt for node selection if not configured
    echo "🔧 HA Node Configuration Required"
    echo "Please select the node type for this deployment:"
    echo "  1) Primary Node (node1)   - Main processing node"
    echo "  2) Secondary Node (node2) - Backup/failover node"
    echo
    read -p "Enter choice [1-2]: " choice
    
    case $choice in
        1)
            SELECTED_NODE="node1"
            SELECTED_ROLE="primary"
            ;;
        2)
            SELECTED_NODE="node2"
            SELECTED_ROLE="secondary"
            ;;
        *)
            print_status "ERROR" "Invalid choice. Please select 1 or 2."
            exit 1
            ;;
    esac
    
    print_status "SUCCESS" "Selected: $SELECTED_NODE ($SELECTED_ROLE)"
    
    # Copy appropriate environment file
    if [[ -f "$PLATFORM_ROOT/.env.ha.$SELECTED_NODE" ]]; then
        cp "$PLATFORM_ROOT/.env.ha.$SELECTED_NODE" "$PLATFORM_ROOT/.env"
        print_status "SUCCESS" "Configured environment for HA $SELECTED_NODE"
    else
        print_status "ERROR" "HA configuration file not found: .env.ha.$SELECTED_NODE"
        exit 1
    fi
}

# Validate HA prerequisites
check_ha_prerequisites() {
    print_status "INFO" "Checking HA prerequisites..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_status "ERROR" "Docker is required for HA deployment"
        return 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_status "ERROR" "Docker Compose is required for HA deployment"
        return 1
    fi
    
    # Check environment file
    if [[ ! -f "$PLATFORM_ROOT/.env" ]]; then
        print_status "ERROR" "Environment file (.env) not found"
        return 1
    fi
    
    # Load environment
    set -a
    source "$PLATFORM_ROOT/.env"
    set +a
    
    # Validate HA-specific variables
    local required_vars=("NODE_ID" "HA_ENABLED" "HA_PEER_IP" "PLATFORM_IP")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            print_status "ERROR" "Required HA variable missing: $var"
            return 1
        fi
    done
    
    print_status "SUCCESS" "HA prerequisites check passed"
    print_status "INFO" "Node ID: $NODE_ID"
    print_status "INFO" "Platform IP: $PLATFORM_IP"
    print_status "INFO" "Peer IP: $HA_PEER_IP"
}

# Test peer connectivity
test_peer_connectivity() {
    print_status "INFO" "Testing connectivity to HA peer..."
    
    if ping -c 3 "$HA_PEER_IP" >/dev/null 2>&1; then
        print_status "SUCCESS" "Peer connectivity OK: $HA_PEER_IP"
    else
        print_status "WARNING" "Cannot reach HA peer: $HA_PEER_IP"
        print_status "INFO" "This is expected if peer is not yet started"
    fi
}

# Create HA directories
create_ha_directories() {
    print_status "INFO" "Creating HA-specific directories..."
    
    local dirs=(
        "$PLATFORM_ROOT/data/ha"
        "$PLATFORM_ROOT/data/ha/postgres-$NODE_ID"
        "$PLATFORM_ROOT/data/ha/rabbitmq-$NODE_ID"
        "$PLATFORM_ROOT/data/ha/shared"
        "$PLATFORM_ROOT/data/ha/autogen-$NODE_ID"
        "$PLATFORM_ROOT/data/ha/models"
        "$PLATFORM_ROOT/logs/ha-$NODE_ID"
        "$PLATFORM_ROOT/logs/nginx-ha-$NODE_ID"
        "$PLATFORM_ROOT/backups/ha/$NODE_ID"
        "$PLATFORM_ROOT/configs/ha"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_status "SUCCESS" "Created HA directory: $dir"
        fi
    done
}

# Generate HA nginx configuration
generate_ha_nginx_config() {
    print_status "INFO" "Generating HA nginx configuration..."
    
    local nginx_config="$PLATFORM_ROOT/configs/ha/nginx-ha.conf"
    
    cat > "$nginx_config" << EOF
# nginx HA Configuration for AI Research Platform
# Auto-generated by start-ha-platform.sh

upstream chat_copilot_backend {
    server $PLATFORM_IP:11000 max_fails=3 fail_timeout=30s;
    server $HA_PEER_IP:11000 backup max_fails=3 fail_timeout=30s;
}

upstream ai_gateway {
    server $PLATFORM_IP:9000 max_fails=3 fail_timeout=30s;
    server $HA_PEER_IP:9000 backup max_fails=3 fail_timeout=30s;
}

server {
    listen 8443 ssl http2;
    server_name $PLATFORM_DOMAIN;
    
    ssl_certificate /etc/ssl/certs/$PLATFORM_DOMAIN.crt;
    ssl_private_key /etc/ssl/private/$PLATFORM_DOMAIN.key;
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK - Node: $NODE_ID\\n";
        add_header Content-Type text/plain;
    }
    
    # Chat Copilot backend
    location /copilot/api/ {
        proxy_pass http://chat_copilot_backend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-HA-Node $NODE_ID;
    }
    
    # AI Gateway
    location /ai-gateway/ {
        proxy_pass http://ai_gateway/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-HA-Node $NODE_ID;
    }
}
EOF
    
    print_status "SUCCESS" "Generated HA nginx configuration"
}

# Start HA services
start_ha_services() {
    print_status "INFO" "Starting HA services..."
    
    # Export all environment variables for Docker Compose
    export PLATFORM_ROOT PLATFORM_IP NODE_ID HA_PEER_IP
    
    # Start HA services based on node role
    if [[ "$NODE_ID" == "node1" ]]; then
        print_status "INFO" "Starting primary node services..."
        docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" --profile monitoring up -d
    else
        print_status "INFO" "Starting secondary node services..."
        # Wait a bit for primary node to initialize
        sleep 10
        docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" up -d
    fi
    
    print_status "SUCCESS" "HA services started"
}

# Monitor cluster health
monitor_cluster_health() {
    print_status "INFO" "Monitoring cluster health..."
    
    local retries=30
    local success=false
    
    for ((i=1; i<=retries; i++)); do
        if curl -s -f "http://$PLATFORM_IP:11000/healthz" >/dev/null 2>&1; then
            print_status "SUCCESS" "Local node health check passed"
            success=true
            break
        fi
        
        print_status "INFO" "Waiting for services to start... (attempt $i/$retries)"
        sleep 5
    done
    
    if [[ "$success" == "false" ]]; then
        print_status "WARNING" "Local health check failed after $retries attempts"
    fi
    
    # Test peer connectivity
    if curl -s -f "http://$HA_PEER_IP:11000/healthz" >/dev/null 2>&1; then
        print_status "SUCCESS" "Peer node health check passed"
    else
        print_status "WARNING" "Peer node health check failed (may not be started yet)"
    fi
}

# Show HA access information
show_ha_access_info() {
    print_status "SUCCESS" "HA AI Research Platform is now running!"
    echo
    echo "🌐 HA Access Points:"
    echo "   Node 1 (Primary):       https://$PLATFORM_IP:8443/"
    echo "   Node 2 (Secondary):     https://$HA_PEER_IP:8443/"
    echo "   Load Balancer:          https://$PLATFORM_IP:8443/"
    echo
    echo "🚀 HA Services:"
    echo "   Chat Copilot:           https://$PLATFORM_IP:8443/copilot/"
    echo "   AI Gateway:             https://$PLATFORM_IP:8443/ai-gateway/"
    echo "   Control Panel:          https://$PLATFORM_IP:8443/hub"
    echo
    echo "📊 HA Management:"
    echo "   Cluster Status:         docker ps --format \"table {{.Names}}\\t{{.Status}}\""
    echo "   Health Check:           curl -k https://$PLATFORM_IP:8443/health"
    echo "   Peer Health:            curl -k https://$HA_PEER_IP:8443/health"
    echo "   View Logs:              docker-compose -f docker-compose.ha.yml logs -f"
    echo "   Stop Cluster:           docker-compose -f docker-compose.ha.yml down"
    echo
    echo "🔧 HA Configuration:"
    echo "   Current Node:           $NODE_ID"
    echo "   Platform Root:          $PLATFORM_ROOT"
    echo "   Platform IP:            $PLATFORM_IP"
    echo "   Peer IP:                $HA_PEER_IP"
    echo
}

# Main function
main() {
    local command="${1:-start}"
    
    print_banner
    
    case $command in
        "start")
            print_status "INFO" "Starting HA deployment..."
            
            detect_node_configuration
            check_ha_prerequisites
            test_peer_connectivity
            create_ha_directories
            generate_ha_nginx_config
            start_ha_services
            
            # Wait for services to stabilize
            sleep 10
            
            monitor_cluster_health
            show_ha_access_info
            ;;
            
        "stop")
            print_status "INFO" "Stopping HA services..."
            docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" down
            print_status "SUCCESS" "HA services stopped"
            ;;
            
        "status")
            print_status "INFO" "HA Cluster Status:"
            docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" ps
            echo
            print_status "INFO" "Health Status:"
            curl -s "http://localhost:11000/healthz" || print_status "WARNING" "Local health check failed"
            ;;
            
        "logs")
            docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" logs -f
            ;;
            
        "restart")
            print_status "INFO" "Restarting HA services..."
            docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" restart
            print_status "SUCCESS" "HA services restarted"
            ;;
            
        "failover")
            print_status "INFO" "Initiating manual failover..."
            # Stop services on current node
            docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" stop
            print_status "SUCCESS" "Manual failover initiated - peer node should take over"
            ;;
            
        "--help"|"-h")
            echo "Usage: $0 [COMMAND]"
            echo
            echo "Commands:"
            echo "  start     Start HA cluster (default)"
            echo "  stop      Stop HA services"
            echo "  status    Show cluster status"
            echo "  logs      View service logs"
            echo "  restart   Restart HA services"
            echo "  failover  Initiate manual failover"
            echo
            echo "Environment Files:"
            echo "  .env.ha.node1    Primary node configuration"
            echo "  .env.ha.node2    Secondary node configuration"
            echo
            echo "Examples:"
            echo "  $0 start         # Start HA cluster"
            echo "  $0 status        # Check cluster health"
            echo "  $0 failover      # Manual failover test"
            exit 0
            ;;
            
        *)
            print_status "ERROR" "Unknown command: $command"
            print_status "INFO" "Use '$0 --help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"