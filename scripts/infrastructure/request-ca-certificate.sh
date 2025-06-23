#!/bin/bash

# Certificate Authority Integration Script
# Automatically requests SSL certificates from internal CA server
# CA Server: https://192.168.0.2

set -euo pipefail

# Configuration
CA_SERVER="https://192.168.0.2"
CERT_DIR="/etc/ssl/ca-certificates"
TAILSCALE_CERT_DIR="/etc/ssl/tailscale"
LOG_FILE="/var/log/ca-certificate-requests.log"

# Default values
DOMAIN=""
PORT=""
SERVICE_NAME=""
CERT_TYPE="server"
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

Request SSL certificate from internal Certificate Authority

OPTIONS:
    -d, --domain DOMAIN      Domain name for certificate (required)
    -p, --port PORT         Service port number
    -s, --service SERVICE   Service name
    -t, --type TYPE         Certificate type (server|client) [default: server]
    -k, --key-size SIZE     RSA key size [default: 2048]
    -v, --validity DAYS     Certificate validity in days [default: 365]
    -h, --help              Show this help message

EXAMPLES:
    $0 -d windmill.example.com -p 11005 -s windmill
    $0 -d api.example.com -p 8080 -s myapi -t server -k 4096

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
            -t|--type)
                CERT_TYPE="$2"
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

# Check if CA server is accessible
check_ca_server() {
    echo -e "${BLUE}Checking CA server accessibility...${NC}"
    
    if ! curl -k -s --connect-timeout 10 "$CA_SERVER" > /dev/null; then
        echo -e "${RED}Error: Cannot reach CA server at $CA_SERVER${NC}"
        log "ERROR: CA server $CA_SERVER is not accessible"
        exit 1
    fi
    
    echo -e "${GREEN}CA server is accessible${NC}"
    log "INFO: CA server $CA_SERVER is accessible"
}

# Generate private key and CSR
generate_csr() {
    local key_file="$1"
    local csr_file="$2"
    local domain="$3"
    
    echo -e "${BLUE}Generating private key and CSR for $domain...${NC}"
    
    # Generate private key
    openssl genrsa -out "$key_file" "$KEY_SIZE" 2>/dev/null
    
    # Create CSR configuration
    local csr_config="/tmp/csr_config_$$.conf"
    cat > "$csr_config" << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=US
ST=State
L=City
O=AI Research Platform
OU=Infrastructure
CN=$domain

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $domain
EOF

    if [[ -n "$PORT" ]]; then
        echo "DNS.2 = $domain:$PORT" >> "$csr_config"
    fi
    
    # Generate CSR
    openssl req -new -key "$key_file" -out "$csr_file" -config "$csr_config"
    
    # Cleanup
    rm -f "$csr_config"
    
    echo -e "${GREEN}CSR generated successfully${NC}"
    log "INFO: Generated CSR for $domain"
}

# Submit CSR to CA server
submit_csr() {
    local csr_file="$1"
    local cert_file="$2"
    
    echo -e "${BLUE}Submitting CSR to CA server...${NC}"
    
    # Read CSR content
    local csr_content
    csr_content=$(cat "$csr_file")
    
    # Prepare JSON payload for CA API (new format for generate-cert endpoint)
    local json_payload
    json_payload=$(jq -n \
        --arg csr "$csr_content" \
        --arg domain "$DOMAIN" \
        --arg service "$SERVICE_NAME" \
        --arg validity "$VALIDITY_DAYS" \
        --arg type "$CERT_TYPE" \
        '{
            csr: $csr,
            domain: $domain,
            service: $service,
            validityDays: ($validity | tonumber),
            certificateType: $type,
            requestedBy: "ai-platform-automation"
        }')
    
    # Alternative payload for generate-cert endpoint
    local generate_cert_payload
    generate_cert_payload=$(jq -n \
        --arg serverName "$DOMAIN" \
        --arg validity "$VALIDITY_DAYS" \
        '{
            serverName: $serverName,
            serverIp: "127.0.0.1",
            certificateType: "nginx",
            outputFormat: "pem",
            keySize: 2048,
            validityDays: ($validity | tonumber)
        }')
    
    # Submit to CA server (try multiple possible endpoints)
    local endpoints=(
        "/api/generate-cert"
        "/api/certificates/generate" 
        "/api/csr/submit" 
        "/api/certificates/csr" 
        "/api/ca/generate"
        "/api/ca/csr"
        "/generate" 
        "/certificates"
        "/csr"
    )
    local success=false
    
    # Try each endpoint with different HTTP methods and content types
    for endpoint in "${endpoints[@]}"; do
        echo -e "${YELLOW}Trying endpoint: $endpoint${NC}"
        
        local payload_to_use="$json_payload"
        if [[ "$endpoint" == "/api/generate-cert" ]]; then
            payload_to_use="$generate_cert_payload"
        fi
        
        # Try POST with JSON first (App Router style)
        local response
        if response=$(curl -k -s -X POST \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -H "X-Requested-With: XMLHttpRequest" \
            -d "$payload_to_use" \
            --connect-timeout 30 \
            --max-time 60 \
            "$CA_SERVER$endpoint" 2>/dev/null); then
            
            # Check if response contains certificate data
            if echo "$response" | jq -e '.certificate' > /dev/null 2>&1; then
                echo "$response" | jq -r '.certificate' > "$cert_file"
                echo -e "${GREEN}Certificate received from CA server${NC}"
                log "INFO: Certificate obtained from $CA_SERVER$endpoint for $DOMAIN"
                success=true
                break
            elif echo "$response" | jq -e '.cert' > /dev/null 2>&1; then
                echo "$response" | jq -r '.cert' > "$cert_file"
                echo -e "${GREEN}Certificate received from CA server${NC}"
                log "INFO: Certificate obtained from $CA_SERVER$endpoint for $DOMAIN"
                success=true
                break
            elif echo "$response" | jq -e '.data.certificate' > /dev/null 2>&1; then
                echo "$response" | jq -r '.data.certificate' > "$cert_file"
                echo -e "${GREEN}Certificate received from CA server${NC}"
                log "INFO: Certificate obtained from $CA_SERVER$endpoint for $DOMAIN"
                success=true
                break
            fi
        fi
        
        # Try form-encoded data (Pages Router style)
        local form_data="csr=$(echo "$csr_content" | base64 -w 0)&domain=$DOMAIN&service=$SERVICE_NAME&validityDays=$VALIDITY_DAYS"
        if response=$(curl -k -s -X POST \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -H "Accept: application/json" \
            -d "$form_data" \
            --connect-timeout 30 \
            --max-time 60 \
            "$CA_SERVER$endpoint" 2>/dev/null); then
            
            # Check for certificate in response
            if echo "$response" | jq -e '.certificate' > /dev/null 2>&1; then
                echo "$response" | jq -r '.certificate' > "$cert_file"
                echo -e "${GREEN}Certificate received from CA server (form data)${NC}"
                log "INFO: Certificate obtained from $CA_SERVER$endpoint for $DOMAIN"
                success=true
                break
            fi
        fi
        
        # Log the response for debugging when nothing works
        if [[ -n "$response" ]]; then
            log "DEBUG: Response from $endpoint: $response"
        fi
    done
    
    if [[ "$success" == "false" ]]; then
        echo -e "${YELLOW}CA server automation failed, falling back to manual process...${NC}"
        log "WARNING: Automated certificate request failed for $DOMAIN"
        
        # Provide manual instructions
        cat << EOF
${YELLOW}Manual Certificate Request Instructions:${NC}
1. Visit the CA server: $CA_SERVER
2. Navigate to the certificate generation page
3. Upload the CSR file: $csr_file
4. Download the generated certificate
5. Save it as: $cert_file

CSR Content:
$(cat "$csr_file")

Press Enter when you have manually downloaded the certificate...
EOF
        read -r
        
        # Verify certificate was placed manually
        if [[ ! -f "$cert_file" ]]; then
            echo -e "${RED}Error: Certificate file not found. Please place the certificate at $cert_file${NC}"
            exit 1
        fi
    fi
}

# Verify certificate
verify_certificate() {
    local cert_file="$1"
    local key_file="$2"
    
    echo -e "${BLUE}Verifying certificate...${NC}"
    
    # Check certificate format
    if ! openssl x509 -in "$cert_file" -text -noout > /dev/null 2>&1; then
        echo -e "${RED}Error: Invalid certificate format${NC}"
        exit 1
    fi
    
    # Check key-certificate pair
    local cert_modulus key_modulus
    cert_modulus=$(openssl x509 -noout -modulus -in "$cert_file" | openssl md5)
    key_modulus=$(openssl rsa -noout -modulus -in "$key_file" | openssl md5)
    
    if [[ "$cert_modulus" != "$key_modulus" ]]; then
        echo -e "${RED}Error: Certificate and private key do not match${NC}"
        exit 1
    fi
    
    # Display certificate information
    echo -e "${GREEN}Certificate verification successful${NC}"
    echo -e "${BLUE}Certificate Details:${NC}"
    openssl x509 -in "$cert_file" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:|DNS:)"
    
    log "INFO: Certificate verified successfully for $DOMAIN"
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
    
    # Install CA certificate
    local ca_cert_file="$CERT_DIR/${domain}.crt"
    local ca_key_file="$CERT_DIR/${domain}.key"
    
    sudo cp "$cert_file" "$ca_cert_file"
    sudo cp "$key_file" "$ca_key_file"
    
    # Also install in Tailscale directory for compatibility
    local tailscale_cert_file="$TAILSCALE_CERT_DIR/${domain}.crt"
    local tailscale_key_file="$TAILSCALE_CERT_DIR/${domain}.key"
    
    sudo cp "$cert_file" "$tailscale_cert_file"
    sudo cp "$key_file" "$tailscale_key_file"
    
    # Set proper permissions
    sudo chmod 644 "$ca_cert_file" "$tailscale_cert_file"
    sudo chmod 600 "$ca_key_file" "$tailscale_key_file"
    sudo chown root:root "$ca_cert_file" "$ca_key_file" "$tailscale_cert_file" "$tailscale_key_file"
    
    echo -e "${GREEN}Certificate installed successfully${NC}"
    echo -e "${BLUE}Certificate paths:${NC}"
    echo "  Certificate: $ca_cert_file"
    echo "  Private Key: $ca_key_file"
    echo "  Tailscale Certificate: $tailscale_cert_file"
    echo "  Tailscale Private Key: $tailscale_key_file"
    
    log "INFO: Certificate installed for $DOMAIN at $ca_cert_file"
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
# $service - CA Generated Certificate
# Port: $port
# Service: $service
# Certificate: CA Generated

server {
    listen $port ssl http2;
    server_name $domain;

    # SSL Configuration using CA certificates
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
        log "INFO: Nginx configuration created for $service on port $port"
    else
        echo -e "${RED}Error: Nginx configuration test failed${NC}"
        sudo rm -f "/etc/nginx/sites-enabled/${service}.conf"
        exit 1
    fi
}

# Main function
main() {
    parse_args "$@"
    
    echo -e "${BLUE}=== Certificate Authority Integration Script ===${NC}"
    echo -e "${BLUE}Domain: $DOMAIN${NC}"
    echo -e "${BLUE}Service: ${SERVICE_NAME:-'Not specified'}${NC}"
    echo -e "${BLUE}Port: ${PORT:-'Not specified'}${NC}"
    echo -e "${BLUE}Certificate Type: $CERT_TYPE${NC}"
    echo ""
    
    # Create temporary files
    local temp_dir
    temp_dir=$(mktemp -d)
    local key_file="$temp_dir/${DOMAIN}.key"
    local csr_file="$temp_dir/${DOMAIN}.csr"
    local cert_file="$temp_dir/${DOMAIN}.crt"
    
    # Ensure cleanup on exit
    trap "rm -rf $temp_dir" EXIT
    
    # Execute certificate request process
    check_ca_server
    generate_csr "$key_file" "$csr_file" "$DOMAIN"
    submit_csr "$csr_file" "$cert_file"
    verify_certificate "$cert_file" "$key_file"
    install_certificate "$cert_file" "$key_file" "$DOMAIN"
    
    if [[ -n "$PORT" && -n "$SERVICE_NAME" ]]; then
        update_nginx_config "$DOMAIN" "$PORT" "$SERVICE_NAME"
    fi
    
    echo -e "${GREEN}=== Certificate Request Completed Successfully ===${NC}"
    echo -e "${GREEN}Certificate for $DOMAIN has been generated and installed${NC}"
    
    if [[ -n "$PORT" ]]; then
        echo -e "${GREEN}Access your service at: https://$DOMAIN:$PORT${NC}"
    fi
    
    log "SUCCESS: Certificate request completed for $DOMAIN"
}

# Initialize log file
sudo touch "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"

# Run main function
main "$@"