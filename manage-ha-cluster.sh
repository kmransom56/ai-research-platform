#!/bin/bash

# =============================================================================
# HA Cluster Management Script
# =============================================================================
# Comprehensive management tools for HA cluster operations
# =============================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

# Load environment if available
load_environment() {
    if [[ -f "$PLATFORM_ROOT/.env" ]]; then
        set -a
        source "$PLATFORM_ROOT/.env"
        set +a
    fi
}

# Check cluster health
check_cluster_health() {
    print_status "INFO" "Checking HA cluster health..."
    
    local node1_ip="${PLATFORM_IP:-10.0.1.10}"
    local node2_ip="${HA_PEER_IP:-10.0.1.11}"
    
    echo "🏥 Cluster Health Report"
    echo "========================"
    
    # Check Node 1
    echo -n "Node 1 ($node1_ip): "
    if curl -s -f "http://$node1_ip:11000/healthz" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
    fi
    
    # Check Node 2
    echo -n "Node 2 ($node2_ip): "
    if curl -s -f "http://$node2_ip:11000/healthz" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
    fi
    
    echo
    
    # Check database replication
    echo "📊 Database Status:"
    docker exec -it "postgres-ha-${NODE_ID:-primary}" psql -U postgres -d chatcopilot -c "SELECT pg_is_in_recovery();" 2>/dev/null || echo "Cannot check database status"
    
    # Check RabbitMQ cluster
    echo
    echo "🐰 RabbitMQ Cluster:"
    docker exec -it "rabbitmq-ha-${NODE_ID:-primary}" rabbitmqctl cluster_status 2>/dev/null || echo "Cannot check RabbitMQ status"
}

# Sync data between nodes
sync_ha_data() {
    print_status "INFO" "Syncing HA data between nodes..."
    
    if [[ -z "${HA_PEER_IP:-}" ]]; then
        print_status "ERROR" "HA_PEER_IP not configured"
        return 1
    fi
    
    # Sync shared application data
    rsync -avz --delete \
        "$PLATFORM_ROOT/data/ha/shared/" \
        "root@$HA_PEER_IP:$PLATFORM_ROOT/data/ha/shared/" \
        2>/dev/null || print_status "WARNING" "Data sync failed (peer may not be accessible)"
    
    print_status "SUCCESS" "Data sync completed"
}

# Backup HA configuration
backup_ha_config() {
    local backup_date=$(date +"%Y%m%d_%H%M%S")
    local backup_dir="$PLATFORM_ROOT/backups/ha/config_$backup_date"
    
    print_status "INFO" "Creating HA configuration backup..."
    
    mkdir -p "$backup_dir"
    
    # Backup configuration files
    cp -r "$PLATFORM_ROOT/configs/ha" "$backup_dir/"
    cp "$PLATFORM_ROOT/.env" "$backup_dir/env_${NODE_ID:-unknown}"
    cp "$PLATFORM_ROOT/docker-compose.ha.yml" "$backup_dir/"
    
    # Create backup manifest
    cat > "$backup_dir/backup_manifest.txt" << EOF
HA Configuration Backup
Created: $(date)
Node ID: ${NODE_ID:-unknown}
Platform IP: ${PLATFORM_IP:-unknown}
Peer IP: ${HA_PEER_IP:-unknown}
Backup Contents:
- HA configurations
- Environment settings
- Docker Compose files
EOF
    
    print_status "SUCCESS" "Backup created: $backup_dir"
}

# Monitor cluster performance
monitor_cluster() {
    print_status "INFO" "Starting cluster monitoring..."
    
    while true; do
        clear
        echo "🖥️  HA Cluster Monitor - $(date)"
        echo "====================================="
        
        # Service status
        echo "📊 Service Status:"
        docker-compose -f "$PLATFORM_ROOT/docker-compose.ha.yml" ps
        
        echo
        echo "🏥 Health Status:"
        check_cluster_health
        
        echo
        echo "💾 Resource Usage:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10
        
        echo
        echo "Press Ctrl+C to exit monitoring..."
        sleep 10
    done
}

# Initialize new HA cluster
init_cluster() {
    print_status "INFO" "Initializing new HA cluster..."
    
    # Create cluster configuration
    create_ha_directories
    generate_ha_nginx_config
    
    # Generate cluster token
    local cluster_token=$(openssl rand -hex 32)
    
    print_status "SUCCESS" "Cluster initialized"
    print_status "INFO" "Cluster Token: $cluster_token"
    print_status "WARNING" "Save this token and add it to both node configurations"
}

# Show cluster information
show_cluster_info() {
    echo "🏢 HA Cluster Information"
    echo "========================"
    echo "Node ID: ${NODE_ID:-Not configured}"
    echo "Platform IP: ${PLATFORM_IP:-Not configured}"
    echo "Peer IP: ${HA_PEER_IP:-Not configured}"
    echo "HA Enabled: ${HA_ENABLED:-false}"
    echo
    echo "📂 Configuration Files:"
    echo "   Primary Node:   .env.ha.node1"
    echo "   Secondary Node: .env.ha.node2"
    echo "   HA Compose:     docker-compose.ha.yml"
    echo "   HA Scripts:     start-ha-platform.sh, manage-ha-cluster.sh"
    echo
    echo "🚀 Quick Commands:"
    echo "   Start HA:       ./start-ha-platform.sh"
    echo "   Cluster Status: ./manage-ha-cluster.sh status"
    echo "   Health Check:   ./manage-ha-cluster.sh health"
    echo "   Monitor:        ./manage-ha-cluster.sh monitor"
}

# Main function
main() {
    local command="${1:-info}"
    
    load_environment
    
    case $command in
        "health")
            check_cluster_health
            ;;
        "sync")
            sync_ha_data
            ;;
        "backup")
            backup_ha_config
            ;;
        "monitor")
            monitor_cluster
            ;;
        "init")
            init_cluster
            ;;
        "status")
            show_cluster_info
            check_cluster_health
            ;;
        "info")
            show_cluster_info
            ;;
        "--help"|"-h")
            echo "HA Cluster Management Script"
            echo
            echo "Usage: $0 [COMMAND]"
            echo
            echo "Commands:"
            echo "  health    Check cluster health status"
            echo "  sync      Sync data between HA nodes"
            echo "  backup    Backup HA configuration"
            echo "  monitor   Real-time cluster monitoring"
            echo "  init      Initialize new HA cluster"
            echo "  status    Show cluster status and health"
            echo "  info      Show cluster information (default)"
            echo
            echo "Prerequisites:"
            echo "  1. Configure .env with HA settings"
            echo "  2. Ensure both nodes can communicate"
            echo "  3. Start primary node first"
            echo
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