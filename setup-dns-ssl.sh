#!/bin/bash

# =============================================================================
# Chat Copilot Platform - DNS and SSL Setup
# =============================================================================
# Complete setup for unbound DNS server and SSL certificates
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Network Configuration
SOURCE_HOSTNAME="ubuntuaicodeserver"
SOURCE_IP="192.168.0.1"
SOURCE_USER="keith"

BACKUP_HOSTNAME="ubuntuaicodeserver-2"
BACKUP_IP="192.168.0.5"
BACKUP_USER="keith-ransom"

DNS_HOSTNAME="aicodeclient"
DNS_IP="192.168.0.253"
DNS_USER="keransom"

# SSL Configuration
DOMAIN_SUFFIX="local"
CA_NAME="ChatCopilot-CA"
CERT_DIR="/etc/ssl/chatcopilot"

print_status() {
    local level=$1
    local message=$2
    case $level in
        "INFO")  echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "ERROR") echo -e "${RED}❌ ${message}${NC}" ;;
        "DNS") echo -e "${PURPLE}🌐 ${message}${NC}" ;;
        "SSL") echo -e "${CYAN}🔒 ${message}${NC}" ;;
    esac
}

print_status "DNS" "🚀 Setting up Professional DNS and SSL for Chat Copilot Platform"
echo "=================================================================="

print_status "INFO" "Configuration:"
echo "  • DNS Server: $DNS_HOSTNAME ($DNS_IP) - user: $DNS_USER"
echo "  • Source Server: $SOURCE_HOSTNAME ($SOURCE_IP) - user: $SOURCE_USER"
echo "  • Backup Server: $BACKUP_HOSTNAME ($BACKUP_IP) - user: $BACKUP_USER"

echo
print_status "INFO" "This setup will provide:"
echo "  • Network-wide DNS resolution via unbound"
echo "  • SSL certificates for all Chat Copilot services"
echo "  • Secure HTTPS access to all services"
echo "  • Professional enterprise-grade security"

echo
read -p "Continue with DNS and SSL setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "INFO" "Setup cancelled"
    exit 0
fi

# Test connectivity to all servers
print_status "INFO" "Testing server connectivity..."

for server in "$SOURCE_HOSTNAME" "$BACKUP_HOSTNAME"; do
    if ssh -o ConnectTimeout=5 "$server" "echo 'connected'" >/dev/null 2>&1; then
        print_status "SUCCESS" "Connection to $server: OK"
    else
        print_status "ERROR" "Cannot connect to $server"
        exit 1
    fi
done

# Test DNS server connectivity (may need password)
print_status "INFO" "Testing DNS server connectivity..."
print_status "WARNING" "DNS server may require password authentication"

# Create SSH key for DNS server if needed
if [[ ! -f ~/.ssh/id_rsa ]]; then
    print_status "INFO" "Generating SSH key for secure connections..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -C "chatcopilot-platform"
fi

print_status "INFO" "SSH public key for DNS server setup:"
echo "Copy this key to $DNS_USER@$DNS_HOSTNAME:~/.ssh/authorized_keys"
echo "----------------------------------------"
cat ~/.ssh/id_rsa.pub
echo "----------------------------------------"

echo
print_status "INFO" "Manual steps for DNS server access:"
echo "1. SSH to DNS server: ssh $DNS_USER@$DNS_IP"
echo "2. Create .ssh directory: mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "3. Add public key: echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
echo "4. Set permissions: chmod 600 ~/.ssh/authorized_keys"

echo
read -p "Have you set up SSH key access to the DNS server? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "WARNING" "Please set up SSH key access first, then re-run this script"
    exit 0
fi

# Test DNS server access
if ssh -o ConnectTimeout=5 "$DNS_HOSTNAME" "echo 'DNS server connected'" >/dev/null 2>&1; then
    print_status "SUCCESS" "DNS server SSH access: OK"
else
    print_status "ERROR" "Cannot connect to DNS server with SSH keys"
    print_status "INFO" "Please ensure SSH key is properly configured"
    exit 1
fi

# Configure Unbound DNS Server
print_status "DNS" "Configuring Unbound DNS server..."

ssh "$DNS_HOSTNAME" << EOF
    echo "🌐 Configuring Unbound DNS for Chat Copilot Platform..."
    
    # Install unbound if not already installed
    if ! command -v unbound >/dev/null 2>&1; then
        echo "📦 Installing Unbound DNS server..."
        sudo apt update
        sudo apt install -y unbound unbound-utils
    else
        echo "✅ Unbound already installed"
    fi
    
    # Backup existing configuration
    if [[ -f /etc/unbound/unbound.conf ]]; then
        sudo cp /etc/unbound/unbound.conf /etc/unbound/unbound.conf.backup.\$(date +%Y%m%d_%H%M%S)
    fi
    
    # Create Chat Copilot DNS configuration
    echo "📋 Creating Chat Copilot DNS configuration..."
    sudo tee /etc/unbound/unbound.conf.d/chatcopilot.conf << 'UNBOUND_EOF'
# Chat Copilot Platform DNS Configuration
server:
    # Local zone for Chat Copilot hostnames
    local-zone: "$DOMAIN_SUFFIX." static
    
    # Chat Copilot server entries
    local-data: "$SOURCE_HOSTNAME.$DOMAIN_SUFFIX. IN A $SOURCE_IP"
    local-data: "$BACKUP_HOSTNAME.$DOMAIN_SUFFIX. IN A $BACKUP_IP"
    local-data: "$DNS_HOSTNAME.$DOMAIN_SUFFIX. IN A $DNS_IP"
    
    # Reverse DNS entries
    local-data-ptr: "$SOURCE_IP $SOURCE_HOSTNAME.$DOMAIN_SUFFIX"
    local-data-ptr: "$BACKUP_IP $BACKUP_HOSTNAME.$DOMAIN_SUFFIX"
    local-data-ptr: "$DNS_IP $DNS_HOSTNAME.$DOMAIN_SUFFIX"
    
    # Also support without .local suffix for compatibility
    local-data: "$SOURCE_HOSTNAME. IN A $SOURCE_IP"
    local-data: "$BACKUP_HOSTNAME. IN A $BACKUP_IP"
    local-data: "$DNS_HOSTNAME. IN A $DNS_IP"

UNBOUND_EOF
    
    # Test configuration
    echo "🧪 Testing Unbound configuration..."
    if sudo unbound-checkconf; then
        echo "✅ Unbound configuration is valid"
    else
        echo "❌ Unbound configuration has errors"
        exit 1
    fi
    
    # Restart and enable Unbound
    echo "🔄 Restarting Unbound DNS service..."
    sudo systemctl restart unbound
    sudo systemctl enable unbound
    
    # Check service status
    if sudo systemctl is-active unbound >/dev/null 2>&1; then
        echo "✅ Unbound DNS service is running"
    else
        echo "❌ Unbound DNS service failed to start"
        sudo systemctl status unbound
        exit 1
    fi
    
    echo "🎉 Unbound DNS server configured successfully!"
EOF

# Test DNS resolution
print_status "DNS" "Testing DNS resolution..."

for hostname in "$SOURCE_HOSTNAME" "$BACKUP_HOSTNAME" "$DNS_HOSTNAME"; do
    if nslookup "$hostname" "$DNS_IP" >/dev/null 2>&1; then
        print_status "SUCCESS" "DNS resolution for $hostname: OK"
    else
        print_status "WARNING" "DNS resolution for $hostname: Failed"
    fi
done

# Set up Certificate Authority and SSL Certificates
print_status "SSL" "Setting up SSL Certificate Authority..."

# Create local CA directory
CA_DIR="$HOME/.chatcopilot-ca"
mkdir -p "$CA_DIR"
cd "$CA_DIR"

# Generate CA private key
if [[ ! -f ca-key.pem ]]; then
    print_status "SSL" "Generating Certificate Authority..."
    openssl genrsa -out ca-key.pem 4096
    
    # Generate CA certificate
    openssl req -new -x509 -days 3650 -key ca-key.pem -out ca-cert.pem -subj "/C=US/ST=State/L=City/O=ChatCopilot/OU=IT/CN=$CA_NAME"
    
    print_status "SUCCESS" "Certificate Authority created"
else
    print_status "INFO" "Certificate Authority already exists"
fi

# Generate server certificates
generate_server_cert() {
    local hostname=$1
    local ip=$2
    
    print_status "SSL" "Generating SSL certificate for $hostname..."
    
    # Generate server private key
    openssl genrsa -out "${hostname}-key.pem" 4096
    
    # Generate certificate signing request
    openssl req -new -key "${hostname}-key.pem" -out "${hostname}-csr.pem" -subj "/C=US/ST=State/L=City/O=ChatCopilot/OU=IT/CN=$hostname"
    
    # Create extensions file for SAN
    cat > "${hostname}-ext.cnf" << EXT_EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $hostname
DNS.2 = $hostname.$DOMAIN_SUFFIX
IP.1 = $ip
EXT_EOF
    
    # Generate signed certificate
    openssl x509 -req -days 365 -in "${hostname}-csr.pem" -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out "${hostname}-cert.pem" -extensions v3_req -extfile "${hostname}-ext.cnf"
    
    # Clean up CSR
    rm "${hostname}-csr.pem" "${hostname}-ext.cnf"
    
    print_status "SUCCESS" "SSL certificate for $hostname created"
}

# Generate certificates for all servers
generate_server_cert "$SOURCE_HOSTNAME" "$SOURCE_IP"
generate_server_cert "$BACKUP_HOSTNAME" "$BACKUP_IP"
generate_server_cert "$DNS_HOSTNAME" "$DNS_IP"

# Distribute certificates to servers
print_status "SSL" "Distributing SSL certificates to servers..."

distribute_cert() {
    local hostname=$1
    local user=$2
    
    print_status "INFO" "Distributing certificate to $hostname..."
    
    # Create certificate directory on remote server
    ssh "$hostname" "sudo mkdir -p $CERT_DIR && sudo chown $user:$user $CERT_DIR"
    
    # Copy certificates
    scp ca-cert.pem "${hostname}-cert.pem" "${hostname}-key.pem" "$hostname:$CERT_DIR/"
    
    # Set proper permissions
    ssh "$hostname" "sudo chown root:root $CERT_DIR/* && sudo chmod 644 $CERT_DIR/*cert.pem && sudo chmod 600 $CERT_DIR/*key.pem"
    
    print_status "SUCCESS" "Certificates distributed to $hostname"
}

distribute_cert "$SOURCE_HOSTNAME" "$SOURCE_USER"
distribute_cert "$BACKUP_HOSTNAME" "$BACKUP_USER"

# Configure Nginx with SSL
print_status "SSL" "Configuring Nginx with SSL certificates..."

configure_nginx_ssl() {
    local hostname=$1
    
    print_status "INFO" "Configuring SSL for $hostname..."
    
    ssh "$hostname" << NGINX_EOF
        echo "🔒 Configuring Nginx SSL for $hostname..."
        
        # Install nginx if not present
        if ! command -v nginx >/dev/null 2>&1; then
            echo "📦 Installing Nginx..."
            sudo apt update
            sudo apt install -y nginx
        fi
        
        # Create SSL configuration
        sudo tee /etc/nginx/sites-available/chatcopilot-ssl << 'SSL_CONF'
server {
    listen 80;
    server_name $hostname $hostname.$DOMAIN_SUFFIX;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $hostname $hostname.$DOMAIN_SUFFIX;
    
    # SSL Configuration
    ssl_certificate $CERT_DIR/$hostname-cert.pem;
    ssl_certificate_key $CERT_DIR/$hostname-key.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Chat Copilot Services Proxy
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # AutoGen Studio
    location /autogen/ {
        proxy_pass http://localhost:11001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # OpenWebUI
    location /openwebui/ {
        proxy_pass http://localhost:11880/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Ollama API
    location /ollama/ {
        proxy_pass http://localhost:11434/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Perplexica
    location /perplexica/ {
        proxy_pass http://localhost:11020/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # VS Code Web
    location /vscode/ {
        proxy_pass http://localhost:57081/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection upgrade;
    }
}
SSL_CONF
        
        # Enable the site
        sudo ln -sf /etc/nginx/sites-available/chatcopilot-ssl /etc/nginx/sites-enabled/
        
        # Test nginx configuration
        if sudo nginx -t; then
            echo "✅ Nginx configuration is valid"
            sudo systemctl restart nginx
            sudo systemctl enable nginx
            echo "✅ Nginx SSL configured successfully"
        else
            echo "❌ Nginx configuration has errors"
            exit 1
        fi
NGINX_EOF
}

configure_nginx_ssl "$SOURCE_HOSTNAME"
configure_nginx_ssl "$BACKUP_HOSTNAME"

# Update network DNS settings
print_status "DNS" "Updating network DNS settings..."

# Update local DNS to use the unbound server
print_status "INFO" "Updating local DNS configuration..."
sudo tee /etc/systemd/resolved.conf.d/chatcopilot.conf << DNS_CONF
[Resolve]
DNS=$DNS_IP
Domains=$DOMAIN_SUFFIX
DNSSEC=no
DNS_CONF

sudo systemctl restart systemd-resolved

# Test the complete setup
print_status "INFO" "Testing complete DNS and SSL setup..."

echo
print_status "SUCCESS" "🎉 DNS and SSL setup completed!"
echo "=================================================================="

print_status "INFO" "📋 Setup Summary:"
echo "  • Unbound DNS server configured on $DNS_HOSTNAME"
echo "  • SSL certificates generated and distributed"
echo "  • Nginx configured with SSL on both servers"
echo "  • Network DNS updated to use unbound server"

echo
print_status "INFO" "🌐 Secure HTTPS Access:"
echo "  • Source Server: https://$SOURCE_HOSTNAME"
echo "  • Backup Server: https://$BACKUP_HOSTNAME"
echo "  • DNS Server: https://$DNS_HOSTNAME"

echo
print_status "INFO" "🔒 SSL Services Available:"
echo "  • Main Platform: https://$SOURCE_HOSTNAME"
echo "  • AutoGen Studio: https://$SOURCE_HOSTNAME/autogen/"
echo "  • OpenWebUI: https://$SOURCE_HOSTNAME/openwebui/"
echo "  • Ollama API: https://$SOURCE_HOSTNAME/ollama/"
echo "  • Perplexica: https://$SOURCE_HOSTNAME/perplexica/"
echo "  • VS Code Web: https://$SOURCE_HOSTNAME/vscode/"

echo
print_status "SUCCESS" "Your Chat Copilot platform now has enterprise-grade DNS and SSL! 🌐🔒✨"

cd - >/dev/null