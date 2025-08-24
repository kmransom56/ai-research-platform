#!/bin/bash

# Setup HA Cluster for AI Research Platform
# Primary: 192.168.0.5 (2x 12GB GPUs + 125GB RAM) 
# Secondary: 192.168.0.1 (2x RTX 3060 Ti)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔧 Setting up AI Research Platform HA Cluster${NC}"
echo "=================================================="
echo "Primary Node: 192.168.0.5 (3x Tesla K80 = 72GB VRAM + i7 + 125GB RAM)"
echo "Secondary Node: 192.168.0.1 (2x RTX 3060 Ti = 16GB VRAM + i7 + 125GB RAM)"
echo "Cluster VIP: 192.168.0.100"
echo "Load Balancing: 80% Primary (Tesla K80) / 20% Secondary (RTX 3060 Ti)"
echo ""

# Function to install keepalived
install_keepalived() {
    echo -e "${BLUE}Installing keepalived...${NC}"
    
    if command -v keepalived &> /dev/null; then
        echo "keepalived already installed"
    else
        sudo apt update
        sudo apt install -y keepalived ipvsadm
        
        # Enable IP forwarding
        echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.conf
        echo 'net.ipv4.conf.all.send_redirects = 0' | sudo tee -a /etc/sysctl.conf
        echo 'net.ipv4.conf.default.send_redirects = 0' | sudo tee -a /etc/sysctl.conf
        sudo sysctl -p
    fi
}

# Function to configure keepalived
configure_keepalived() {
    echo -e "${BLUE}Configuring keepalived on primary node...${NC}"
    
    # Backup existing config
    sudo cp /etc/keepalived/keepalived.conf /etc/keepalived/keepalived.conf.backup 2>/dev/null || true
    
    # Install our configuration
    sudo cp /home/keith-ransom/chat-copilot/configs/keepalived-primary.conf /etc/keepalived/keepalived.conf
    
    # Create health check script
    sudo mkdir -p /etc/keepalived/scripts
    
    cat | sudo tee /etc/keepalived/scripts/check-ai-services.sh > /dev/null << 'EOF'
#!/bin/bash

# Health check for AI Research Platform services
# Exit 0 = healthy, Exit 1 = unhealthy

# Check core AI services
services=(
    "http://localhost:11000/healthz"  # Chat Copilot
    "http://localhost:9000/health"    # AI Gateway
    "http://localhost:11001/health"   # AutoGen Studio
)

failed=0

for service in "${services[@]}"; do
    if ! curl -f -s --max-time 5 "$service" > /dev/null 2>&1; then
        ((failed++))
    fi
done

# Allow 1 service failure
if [ $failed -gt 1 ]; then
    exit 1
fi

exit 0
EOF

    sudo chmod +x /etc/keepalived/scripts/check-ai-services.sh
}

# Function to create notification scripts
create_notification_scripts() {
    echo -e "${BLUE}Creating HA notification scripts...${NC}"
    
    sudo mkdir -p /home/keith/chat-copilot/scripts/ha-management
    
    # Master notification script
    cat | sudo tee /home/keith/chat-copilot/scripts/ha-management/master_notify.sh > /dev/null << 'EOF'
#!/bin/bash
# Notification script when becoming master
echo "$(date): Becoming MASTER - Starting all AI services" | logger -t keepalived
# Ensure all services are running
systemctl --user start ai-research-platform.target 2>/dev/null || true
EOF

    # Backup notification script
    cat | sudo tee /home/keith/chat-copilot/scripts/ha-management/backup_notify.sh > /dev/null << 'EOF'
#!/bin/bash
# Notification script when becoming backup
echo "$(date): Becoming BACKUP - Stopping non-essential services" | logger -t keepalived
# Keep database services running but stop AI processing
EOF

    # Fault notification script
    cat | sudo tee /home/keith/chat-copilot/scripts/ha-management/fault_notify.sh > /dev/null << 'EOF'
#!/bin/bash
# Notification script when fault detected
echo "$(date): FAULT detected in HA cluster" | logger -t keepalived
# Send alerts to administrators
EOF

    sudo chmod +x /home/keith/chat-copilot/scripts/ha-management/*.sh
    sudo chown keith:keith /home/keith/chat-copilot/scripts/ha-management/*.sh
}

# Function to test connectivity
test_connectivity() {
    echo -e "${BLUE}Testing cluster connectivity...${NC}"
    
    echo -n "Testing secondary node (192.168.0.1)... "
    if ping -c 1 192.168.0.1 &> /dev/null; then
        echo -e "${GREEN}✅ Connected${NC}"
    else
        echo -e "${RED}❌ Cannot reach secondary node${NC}"
        echo "Please ensure the secondary server is online and accessible"
        return 1
    fi
    
    echo -n "Testing SSH access to secondary... "
    if ssh -o ConnectTimeout=5 -o BatchMode=yes keith@192.168.0.1 exit &> /dev/null; then
        echo -e "${GREEN}✅ SSH access working${NC}"
    else
        echo -e "${YELLOW}⚠️  SSH key authentication needed${NC}"
        echo "Run: ssh-copy-id keith@192.168.0.1"
    fi
}

# Function to start keepalived service
start_keepalived() {
    echo -e "${BLUE}Starting keepalived service...${NC}"
    
    sudo systemctl enable keepalived
    sudo systemctl restart keepalived
    
    sleep 3
    
    if sudo systemctl is-active keepalived &> /dev/null; then
        echo -e "${GREEN}✅ keepalived is running${NC}"
        
        # Show VRRP status
        echo ""
        echo "VRRP Status:"
        ip addr show | grep "192.168.0.100" && echo -e "${GREEN}✅ VIP is active on this node${NC}" || echo -e "${YELLOW}⚠️  VIP not active yet${NC}"
    else
        echo -e "${RED}❌ keepalived failed to start${NC}"
        sudo systemctl status keepalived
        return 1
    fi
}

# Function to check network interface
check_network_interface() {
    echo -e "${BLUE}Checking network interface...${NC}"
    
    interfaces=$(ip route | grep default | awk '{print $5}' | head -1)
    if [ -z "$interfaces" ]; then
        echo -e "${RED}❌ Cannot determine primary network interface${NC}"
        echo "Please update keepalived.conf with correct interface name"
        return 1
    fi
    
    echo "Primary interface detected: $interfaces"
    
    # Update keepalived config with correct interface
    sudo sed -i "s/interface eno1/interface $interfaces/" /etc/keepalived/keepalived.conf
    
    echo -e "${GREEN}✅ Network interface configured${NC}"
}

# Main setup function
main() {
    echo "Starting HA cluster setup..."
    echo ""
    
    # Pre-flight checks
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}❌ Do not run this script as root${NC}"
        exit 1
    fi
    
    # Test connectivity first
    if ! test_connectivity; then
        echo -e "${RED}❌ Connectivity test failed${NC}"
        exit 1
    fi
    
    # Install and configure components
    install_keepalived
    check_network_interface
    configure_keepalived
    create_notification_scripts
    
    # Start services
    start_keepalived
    
    echo ""
    echo -e "${GREEN}🎉 HA Cluster Setup Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Deploy services to secondary server: ./deploy-secondary-server.sh"
    echo "2. Test failover: ./test-ha-failover.sh"
    echo "3. Monitor cluster: ./monitor-ha-cluster.sh"
    echo ""
    echo "Cluster Access:"
    echo "• Primary Services: 192.168.0.5:11000-11040"
    echo "• Secondary Services: 192.168.0.1:11000-11040" 
    echo "• Load Balanced VIP: 192.168.0.100:11000-11040"
    
    # Show current status
    echo ""
    echo "Current Status:"
    sudo systemctl status keepalived --no-pager -l
}

# Run main function
main "$@"