#!/bin/bash

# Certificate Authority Renewal Script
# Automatically renews certificates from internal CA server
# CA Server: https://192.168.0.2

set -euo pipefail

# Configuration
CA_SERVER="https://192.168.0.2"
CERT_DIR="/etc/ssl/ca-certificates"
TAILSCALE_CERT_DIR="/etc/ssl/tailscale"
LOG_FILE="/var/log/ca-certificate-renewal.log"
RENEWAL_THRESHOLD_DAYS="30"

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

Renew SSL certificates from internal Certificate Authority

OPTIONS:
    -c, --check-only        Only check certificate expiration, don't renew
    -t, --threshold DAYS    Days before expiration to trigger renewal [default: 30]
    -f, --force            Force renewal of all certificates regardless of expiration
    -d, --domain DOMAIN    Only process specific domain
    -h, --help             Show this help message

EXAMPLES:
    $0 --check-only                    # Check all certificates
    $0 --threshold 60                  # Renew certificates expiring in 60 days
    $0 --force                         # Force renew all certificates
    $0 --domain windmill.local         # Only process windmill.local

EOF
}

# Parse command line arguments
CHECK_ONLY=false
FORCE_RENEWAL=false
SPECIFIC_DOMAIN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--check-only)
            CHECK_ONLY=true
            shift
            ;;
        -t|--threshold)
            RENEWAL_THRESHOLD_DAYS="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_RENEWAL=true
            shift
            ;;
        -d|--domain)
            SPECIFIC_DOMAIN="$2"
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

# Check if certificate is expiring soon
check_certificate_expiration() {
    local cert_file="$1"
    local domain="$2"
    
    if [[ ! -f "$cert_file" ]]; then
        echo -e "${RED}Certificate file not found: $cert_file${NC}"
        return 2
    fi
    
    # Get certificate expiration date
    local expiry_date
    expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
    
    # Convert to epoch time
    local expiry_epoch
    expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch
    current_epoch=$(date +%s)
    local threshold_epoch
    threshold_epoch=$((current_epoch + (RENEWAL_THRESHOLD_DAYS * 24 * 3600)))
    
    # Calculate days until expiration
    local days_until_expiry
    days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    echo -e "${BLUE}Domain: $domain${NC}"
    echo -e "Expires: $expiry_date"
    echo -e "Days until expiry: $days_until_expiry"
    
    # Check if renewal is needed
    if [[ $expiry_epoch -le $threshold_epoch ]]; then
        echo -e "${YELLOW}Certificate needs renewal (expires in $days_until_expiry days)${NC}"
        log "INFO: Certificate for $domain expires in $days_until_expiry days - renewal needed"
        return 0  # Needs renewal
    else
        echo -e "${GREEN}Certificate is valid (expires in $days_until_expiry days)${NC}"
        log "INFO: Certificate for $domain is valid - expires in $days_until_expiry days"
        return 1  # No renewal needed
    fi
}

# Renew certificate using CA script
renew_certificate() {
    local domain="$1"
    local service_name="$2"
    local port="$3"
    
    echo -e "${BLUE}Renewing certificate for $domain...${NC}"
    
    # Path to CA certificate script
    local ca_script="/home/keith/chat-copilot/scripts/infrastructure/request-ca-certificate.sh"
    
    if [[ ! -f "$ca_script" ]]; then
        echo -e "${RED}Error: CA certificate script not found at $ca_script${NC}"
        return 1
    fi
    
    # Request new certificate
    local renewal_args="--domain $domain"
    
    if [[ -n "$service_name" ]]; then
        renewal_args="$renewal_args --service $service_name"
    fi
    
    if [[ -n "$port" ]]; then
        renewal_args="$renewal_args --port $port"
    fi
    
    echo -e "${BLUE}Running: $ca_script $renewal_args${NC}"
    
    if $ca_script $renewal_args; then
        echo -e "${GREEN}Certificate renewed successfully for $domain${NC}"
        log "SUCCESS: Certificate renewed for $domain"
        
        # Reload nginx to use new certificate
        if sudo nginx -t; then
            sudo systemctl reload nginx
            echo -e "${GREEN}Nginx reloaded with new certificate${NC}"
            log "INFO: Nginx reloaded for $domain certificate renewal"
        else
            echo -e "${RED}Error: Nginx configuration test failed after renewal${NC}"
            log "ERROR: Nginx configuration test failed for $domain"
        fi
        
        return 0
    else
        echo -e "${RED}Failed to renew certificate for $domain${NC}"
        log "ERROR: Certificate renewal failed for $domain"
        return 1
    fi
}

# Extract service information from nginx configuration
get_service_info() {
    local domain="$1"
    local service_name=""
    local port=""
    
    # Try to find nginx configuration for this domain
    local nginx_configs
    nginx_configs=$(sudo find /etc/nginx/sites-enabled -name "*.conf" -type f)
    
    for config in $nginx_configs; do
        if sudo grep -q "server_name.*$domain" "$config"; then
            # Extract port from listen directive
            port=$(sudo grep -m1 "listen.*ssl" "$config" | grep -o '[0-9]\+' | head -1)
            
            # Extract service name from filename
            service_name=$(basename "$config" .conf)
            
            echo "$service_name:$port"
            return 0
        fi
    done
    
    echo ":"
}

# Process all certificates in directory
process_certificates() {
    local cert_dir="$1"
    local processed=0
    local renewed=0
    local failed=0
    
    echo -e "${BLUE}Processing certificates in $cert_dir...${NC}"
    
    if [[ ! -d "$cert_dir" ]]; then
        echo -e "${YELLOW}Certificate directory not found: $cert_dir${NC}"
        return 0
    fi
    
    # Find all certificate files
    local cert_files
    cert_files=$(find "$cert_dir" -name "*.crt" -type f)
    
    if [[ -z "$cert_files" ]]; then
        echo -e "${YELLOW}No certificate files found in $cert_dir${NC}"
        return 0
    fi
    
    for cert_file in $cert_files; do
        local domain
        domain=$(basename "$cert_file" .crt)
        
        # Skip if specific domain requested and this isn't it
        if [[ -n "$SPECIFIC_DOMAIN" && "$domain" != "$SPECIFIC_DOMAIN" ]]; then
            continue
        fi
        
        echo ""
        echo -e "${BLUE}=== Processing $domain ===${NC}"
        
        ((processed++))
        
        # Check certificate expiration
        local needs_renewal=false
        
        if [[ "$FORCE_RENEWAL" == "true" ]]; then
            echo -e "${YELLOW}Force renewal requested${NC}"
            needs_renewal=true
        else
            if check_certificate_expiration "$cert_file" "$domain"; then
                needs_renewal=true
            fi
        fi
        
        # Renew if needed and not in check-only mode
        if [[ "$needs_renewal" == "true" && "$CHECK_ONLY" != "true" ]]; then
            # Get service information
            local service_info
            service_info=$(get_service_info "$domain")
            local service_name
            service_name=$(echo "$service_info" | cut -d: -f1)
            local port
            port=$(echo "$service_info" | cut -d: -f2)
            
            if renew_certificate "$domain" "$service_name" "$port"; then
                ((renewed++))
            else
                ((failed++))
            fi
        fi
    done
    
    echo ""
    echo -e "${BLUE}=== Certificate Processing Summary ===${NC}"
    echo -e "Processed: $processed"
    echo -e "Renewed: ${GREEN}$renewed${NC}"
    echo -e "Failed: ${RED}$failed${NC}"
    
    log "SUMMARY: Processed $processed certificates, renewed $renewed, failed $failed"
}

# Check CA server accessibility
check_ca_server() {
    echo -e "${BLUE}Checking CA server accessibility...${NC}"
    
    if ! curl -k -s --connect-timeout 10 "$CA_SERVER" > /dev/null; then
        echo -e "${RED}Error: Cannot reach CA server at $CA_SERVER${NC}"
        log "ERROR: CA server $CA_SERVER is not accessible"
        return 1
    fi
    
    echo -e "${GREEN}CA server is accessible${NC}"
    log "INFO: CA server $CA_SERVER is accessible"
    return 0
}

# Main function
main() {
    echo -e "${BLUE}=== Certificate Authority Renewal Script ===${NC}"
    echo -e "${BLUE}CA Server: $CA_SERVER${NC}"
    echo -e "${BLUE}Renewal Threshold: $RENEWAL_THRESHOLD_DAYS days${NC}"
    echo -e "${BLUE}Check Only: $CHECK_ONLY${NC}"
    echo -e "${BLUE}Force Renewal: $FORCE_RENEWAL${NC}"
    
    if [[ -n "$SPECIFIC_DOMAIN" ]]; then
        echo -e "${BLUE}Specific Domain: $SPECIFIC_DOMAIN${NC}"
    fi
    
    echo ""
    
    # Check CA server accessibility (skip if check-only mode)
    if [[ "$CHECK_ONLY" != "true" ]]; then
        if ! check_ca_server; then
            exit 1
        fi
    fi
    
    # Process certificates in both directories
    process_certificates "$CERT_DIR"
    process_certificates "$TAILSCALE_CERT_DIR"
    
    echo ""
    echo -e "${GREEN}=== Certificate renewal process completed ===${NC}"
    
    if [[ "$CHECK_ONLY" == "true" ]]; then
        echo -e "${BLUE}Check-only mode - no certificates were renewed${NC}"
    fi
    
    log "SUCCESS: Certificate renewal process completed"
}

# Initialize log file
sudo touch "$LOG_FILE"
sudo chmod 644 "$LOG_FILE"

# Run main function
main "$@"