#!/bin/bash

# Generate Self-Signed Certificate for Development/Testing
# This script creates self-signed certificates for applications when CA server is not available

set -euo pipefail

# Configuration
CERT_DIR="/etc/ssl/ca-certificates"
TAILSCALE_CERT_DIR="/etc/ssl/tailscale"
LOG_FILE="/var/log/self-signed-certificates.log"

# Default values
DOMAIN=""
PORT=""
SERVICE_NAME=""
KEY_SIZE="2048"
VALIDITY_DAYS="365"

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

# Print usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Generate self-signed SSL certificate for development/testing

OPTIONS:
    -d, --domain DOMAIN      Domain name for certificate (required)
    -p, --port PORT         Service port number
    -s, --service SERVICE   Service name
    -k, --key-size SIZE     RSA key size [default: 2048]
    -v, --validity DAYS     Certificate validity in days [default: 365]
    -h, --help              Show this help message

EXAMPLES:
    $0 -d windmill.local -p 11005 -s windmill
    $0 -d api.local -p 8080 -s myapi

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -s|--service)
                SERVICE_NAME="$2"
                shift 2
                ;;
            -k|--key-size)
                KEY_SIZE="$2"
                shift 2
                ;;
            -v|--validity)
                VALIDITY_DAYS="$2"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done

    # Validate required parameters
    if [[ -z "$DOMAIN" ]]; then
        echo -e "${RED}Error: Domain is required${NC}"
        usage
        exit 1
    fi
}

# Generate self-signed certificate
generate_certificate() {
    local key_file="$1"
    local cert_file="$2"
    local domain="$3"
    
    echo -e "${BLUE}Generating self-signed certificate for $domain...${NC}"
    
    # Create certificate configuration
    local cert_config="/tmp/cert_config_$$.conf"
    cat > "$cert_config" << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=US
ST=Development
L=Local
O=AI Research Platform
OU=Development
CN=$domain

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $domain
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

    if [[ -n "$PORT" ]]; then
        echo "DNS.3 = $domain:$PORT" >> "$cert_config"
    fi
    
    # Generate private key and certificate
    openssl req -x509 -newkey rsa:$KEY_SIZE -keyout "$key_file" -out "$cert_file" \
        -days "$VALIDITY_DAYS" -nodes -config "$cert_config" -extensions v3_req
    
    # Cleanup
    rm -f "$cert_config"
    
    echo -e "${GREEN}Self-signed certificate generated successfully${NC}"
    log "INFO: Generated self-signed certificate for $domain"
}

# Install certificate
install_certificate() {
    local cert_file="$1"
    local key_file="$2"
    local domain="$3"
    
    echo -e "${BLUE}Installing certificate...${NC}"
    
    # Create certificate directories
    sudo mkdir -p "$CERT_DIR"
    sudo mkdir -p "$TAILSCALE_CERT_DIR"
    
    # Install certificate
    local final_cert_file="$CERT_DIR/${domain}.crt"
    local final_key_file="$CERT_DIR/${domain}.key"
    
    sudo cp "$cert_file" "$final_cert_file"
    sudo cp "$key_file" "$final_key_file"
    
    # Also install in Tailscale directory for compatibility
    local tailscale_cert_file="$TAILSCALE_CERT_DIR/${domain}.crt"
    local tailscale_key_file="$TAILSCALE_CERT_DIR/${domain}.key"
    
    sudo cp "$cert_file" "$tailscale_cert_file"
    sudo cp "$key_file" "$tailscale_key_file"
    
    # Set proper permissions
    sudo chmod 644 "$final_cert_file" "$tailscale_cert_file"
    sudo chmod 600 "$final_key_file" "$tailscale_key_file"
    sudo chown root:root "$final_cert_file" "$final_key_file" "$tailscale_cert_file" "$tailscale_key_file"
    
    echo -e "${GREEN}Certificate installed successfully${NC}"
    echo -e "${BLUE}Certificate paths:${NC}"
    echo "  Certificate: $final_cert_file"
    echo "  Private Key: $final_key_file"
    echo "  Tailscale Certificate: $tailscale_cert_file"
    echo "  Tailscale Private Key: $tailscale_key_file"
    
    log "INFO: Self-signed certificate installed for $domain at $final_cert_file"
}

# Update nginx configuration
update_nginx_config() {
    local domain="$1"
    local port="$2"
    local service="$3"
    
    if [[ -z "$port" || -z "$service" ]]; then
        echo -e "${YELLOW}Port or service name not provided, skipping nginx configuration${NC}"
        return
    fi
    
    echo -e "${BLUE}Updating nginx configuration for $service...${NC}"
    
    local nginx_config="/etc/nginx/sites-available/${service}.conf"
    local cert_file="$CERT_DIR/${domain}.crt"
    local key_file="$CERT_DIR/${domain}.key"
    
    # Create nginx configuration
    sudo tee "$nginx_config" > /dev/null << EOF
# $service - Self-Signed Certificate (Development)
# Port: $port
# Service: $service
# Certificate: Self-Signed (Development Only)

server {
    listen $port ssl http2;
    server_name $domain localhost;

    # SSL Configuration using self-signed certificates
    ssl_certificate $cert_file;
    ssl_certificate_key $key_file;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Development warning
    add_header X-Certificate-Type "Self-Signed-Development" always;

    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:$((port + 1));
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }

    # Logging
    access_log /var/log/nginx/${service}.access.log combined;
    error_log /var/log/nginx/${service}.error.log;
}
EOF

    # Enable the site
    sudo ln -sf "$nginx_config" "/etc/nginx/sites-enabled/${service}.conf"
    
    # Test nginx configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        echo -e "${GREEN}Nginx configuration updated and reloaded${NC}"
        log "INFO: Nginx configuration created for $service on port $port with self-signed certificate"
    else
        echo -e "${RED}Error: Nginx configuration test failed${NC}"
        sudo rm -f "/etc/nginx/sites-enabled/${service}.conf"
        exit 1
    fi
}

# Main function
main() {
    parse_args "$@"
    
    echo -e "${BLUE}=== Self-Signed Certificate Generator ===${NC}"
    echo -e "${BLUE}Domain: $DOMAIN${NC}"
    echo -e "${BLUE}Service: ${SERVICE_NAME:-'Not specified'}${NC}"
    echo -e "${BLUE}Port: ${PORT:-'Not specified'}${NC}"
    echo -e "${YELLOW}WARNING: Self-signed certificates are for development only${NC}"
    echo ""
    
    # Create temporary files
    local temp_dir
    temp_dir=$(mktemp -d)
    local key_file="$temp_dir/${DOMAIN}.key"
    local cert_file="$temp_dir/${DOMAIN}.crt"
    
    # Ensure cleanup on exit
    trap "rm -rf $temp_dir" EXIT
    
    # Execute certificate generation process
    generate_certificate "$key_file" "$cert_file" "$DOMAIN"
    install_certificate "$cert_file" "$key_file" "$DOMAIN"
    
    if [[ -n "$PORT" && -n "$SERVICE_NAME" ]]; then
        update_nginx_config "$DOMAIN" "$PORT" "$SERVICE_NAME"
    fi
    
    echo -e "${GREEN}=== Self-Signed Certificate Generated Successfully ===${NC}"
    echo -e "${GREEN}Certificate for $DOMAIN has been generated and installed${NC}"
    echo -e "${YELLOW}Remember: This is a self-signed certificate for development only${NC}"
    
    if [[ -n "$PORT" ]]; then
        echo -e "${GREEN}Access your service at: https://$DOMAIN:$PORT${NC}"
        echo -e "${YELLOW}You will need to accept the security warning in your browser${NC}"
    fi
    
    log "SUCCESS: Self-signed certificate generated for $DOMAIN"
}

# Initialize log file
sudo touch "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"

# Run main function
main "$@"