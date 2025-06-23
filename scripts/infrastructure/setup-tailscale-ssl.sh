#!/bin/bash
# Tailscale SSL Certificate Setup Script
# Creates SSL certificate directories and copies certificates for nginx configurations

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Configuration
readonly TAILSCALE_DOMAIN="ubuntuaicodeserver-1.tail5137b4.ts.net"
readonly TAILSCALE_CERT_DIR="/var/lib/tailscale/certs"
readonly NGINX_SSL_DIR="/etc/ssl/tailscale"
readonly DOCKER_SSL_DIR="/opt/tailscale-certs"

# Applications that need SSL certificates
declare -a APPLICATIONS=(
    "autogen"
    "copilot"
    "fortinet"
    "http-gateway"
    "https-gateway"
    "magentic"
    "nginx-manager"
    "openwebui"
    "perplexica"
    "portscanner"
    "searxng"
    "vscode"
    "webhook"
)

log() {
    local level="$1"
    shift
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
    "ERROR") echo -e "${RED}❌ [$timestamp] ERROR: $*${NC}" ;;
    "SUCCESS") echo -e "${GREEN}✅ [$timestamp] SUCCESS: $*${NC}" ;;
    "INFO") echo -e "${BLUE}ℹ️  [$timestamp] INFO: $*${NC}" ;;
    "WARN") echo -e "${YELLOW}⚠️  [$timestamp] WARN: $*${NC}" ;;
    esac
}

check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if Tailscale is installed
    if ! command -v tailscale &> /dev/null; then
        log ERROR "Tailscale is not installed. Please install Tailscale first."
        exit 1
    fi
    
    # Check if Tailscale is authenticated
    if ! tailscale status &> /dev/null; then
        log ERROR "Tailscale is not authenticated. Please run 'tailscale up' first."
        exit 1
    fi
    
    log SUCCESS "Prerequisites check passed"
}

setup_directories() {
    log INFO "Setting up SSL certificate directories..."
    
    # Create nginx SSL directory
    if [[ ! -d "$NGINX_SSL_DIR" ]]; then
        sudo mkdir -p "$NGINX_SSL_DIR"
        sudo chmod 755 "$NGINX_SSL_DIR"
        log SUCCESS "Created nginx SSL directory: $NGINX_SSL_DIR"
    else
        log INFO "Nginx SSL directory already exists: $NGINX_SSL_DIR"
    fi
    
    # Create Docker SSL directory
    if [[ ! -d "$DOCKER_SSL_DIR" ]]; then
        sudo mkdir -p "$DOCKER_SSL_DIR"
        sudo chown "$USER:$USER" "$DOCKER_SSL_DIR"
        sudo chmod 755 "$DOCKER_SSL_DIR"
        log SUCCESS "Created Docker SSL directory: $DOCKER_SSL_DIR"
    else
        log INFO "Docker SSL directory already exists: $DOCKER_SSL_DIR"
    fi
}

generate_main_certificate() {
    log INFO "Generating main Tailscale certificate for $TAILSCALE_DOMAIN..."
    
    # Change to Docker SSL directory for certificate generation
    cd "$DOCKER_SSL_DIR"
    
    if tailscale cert "$TAILSCALE_DOMAIN"; then
        log SUCCESS "Generated main certificate for $TAILSCALE_DOMAIN"
        
        # Copy to nginx SSL directory
        sudo cp "${TAILSCALE_DOMAIN}.crt" "$NGINX_SSL_DIR/"
        sudo cp "${TAILSCALE_DOMAIN}.key" "$NGINX_SSL_DIR/"
        sudo chmod 644 "$NGINX_SSL_DIR/${TAILSCALE_DOMAIN}.crt"
        sudo chmod 600 "$NGINX_SSL_DIR/${TAILSCALE_DOMAIN}.key"
        
        log SUCCESS "Copied main certificate to nginx SSL directory"
    else
        log ERROR "Failed to generate main certificate for $TAILSCALE_DOMAIN"
        return 1
    fi
}

generate_subdomain_certificates() {
    log INFO "Generating subdomain certificates..."
    
    cd "$DOCKER_SSL_DIR"
    
    for app in "${APPLICATIONS[@]}"; do
        local subdomain="${app}.${TAILSCALE_DOMAIN}"
        log INFO "Generating certificate for $subdomain..."
        
        if tailscale cert "$subdomain"; then
            log SUCCESS "Generated certificate for $subdomain"
            
            # Copy to nginx SSL directory
            sudo cp "${subdomain}.crt" "$NGINX_SSL_DIR/"
            sudo cp "${subdomain}.key" "$NGINX_SSL_DIR/"
            sudo chmod 644 "$NGINX_SSL_DIR/${subdomain}.crt"
            sudo chmod 600 "$NGINX_SSL_DIR/${subdomain}.key"
            
            log SUCCESS "Copied certificate for $subdomain to nginx SSL directory"
        else
            log WARN "Failed to generate certificate for $subdomain (this may be expected if not configured in Tailscale)"
        fi
    done
}

copy_certificates_for_docker() {
    log INFO "Copying certificates for Docker containers..."
    
    # Also copy to the Tailscale cert directory if it exists
    if [[ -d "$TAILSCALE_CERT_DIR" ]]; then
        sudo cp "$DOCKER_SSL_DIR"/*.crt "$TAILSCALE_CERT_DIR/" 2>/dev/null || true
        sudo cp "$DOCKER_SSL_DIR"/*.key "$TAILSCALE_CERT_DIR/" 2>/dev/null || true
        log SUCCESS "Copied certificates to Tailscale cert directory"
    fi
}

verify_certificates() {
    log INFO "Verifying generated certificates..."
    
    local cert_count=0
    
    # Check main certificate
    if [[ -f "$NGINX_SSL_DIR/${TAILSCALE_DOMAIN}.crt" ]]; then
        cert_count=$((cert_count + 1))
        log SUCCESS "Main certificate exists: ${TAILSCALE_DOMAIN}.crt"
    else
        log ERROR "Main certificate missing: ${TAILSCALE_DOMAIN}.crt"
    fi
    
    # Check subdomain certificates
    for app in "${APPLICATIONS[@]}"; do
        local subdomain="${app}.${TAILSCALE_DOMAIN}"
        if [[ -f "$NGINX_SSL_DIR/${subdomain}.crt" ]]; then
            cert_count=$((cert_count + 1))
            log SUCCESS "Certificate exists: ${subdomain}.crt"
        else
            log WARN "Certificate missing: ${subdomain}.crt"
        fi
    done
    
    log INFO "Total certificates found: $cert_count"
}

setup_certificate_renewal() {
    log INFO "Setting up certificate renewal..."
    
    # Create renewal script if it doesn't exist
    local renewal_script="/home/keith/chat-copilot/scripts/infrastructure/renew-certificates.sh"
    
    if [[ -f "$renewal_script" ]]; then
        # Make sure it's executable
        chmod +x "$renewal_script"
        log SUCCESS "Certificate renewal script is ready: $renewal_script"
        
        # Add to crontab if not already present
        if ! crontab -l 2>/dev/null | grep -q "renew-certificates.sh"; then
            (crontab -l 2>/dev/null; echo "0 2 * * 0 $renewal_script") | crontab -
            log SUCCESS "Added certificate renewal to crontab (weekly at 2 AM Sunday)"
        else
            log INFO "Certificate renewal already in crontab"
        fi
    else
        log WARN "Certificate renewal script not found: $renewal_script"
    fi
}

print_summary() {
    log INFO "=== SSL Certificate Setup Summary ==="
    echo
    echo "📁 SSL Certificate Directories:"
    echo "   • Nginx SSL: $NGINX_SSL_DIR"
    echo "   • Docker SSL: $DOCKER_SSL_DIR"
    echo "   • Tailscale: $TAILSCALE_CERT_DIR (if exists)"
    echo
    echo "🔐 Main Certificate:"
    echo "   • Domain: $TAILSCALE_DOMAIN"
    echo "   • Files: ${TAILSCALE_DOMAIN}.crt, ${TAILSCALE_DOMAIN}.key"
    echo
    echo "🌐 Subdomain Certificates:"
    for app in "${APPLICATIONS[@]}"; do
        echo "   • ${app}.${TAILSCALE_DOMAIN}"
    done
    echo
    echo "🔄 Certificate Renewal:"
    echo "   • Script: /home/keith/chat-copilot/scripts/infrastructure/renew-certificates.sh"
    echo "   • Schedule: Weekly (Sunday 2 AM)"
    echo
    echo "📋 Next Steps:"
    echo "   1. Verify nginx configurations reference correct certificate paths"
    echo "   2. Restart nginx/Docker services to load certificates"
    echo "   3. Test HTTPS access to your applications"
    echo "   4. Monitor certificate expiration with the renewal script"
    echo
}

main() {
    log INFO "Starting Tailscale SSL Certificate Setup..."
    
    check_prerequisites
    setup_directories
    generate_main_certificate
    generate_subdomain_certificates
    copy_certificates_for_docker
    verify_certificates
    setup_certificate_renewal
    print_summary
    
    log SUCCESS "Tailscale SSL Certificate Setup completed!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Set up Tailscale SSL certificates for nginx configurations"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --verify       Verify existing certificates only"
        echo "  --renew        Force renewal of all certificates"
        echo
        exit 0
        ;;
    --verify)
        verify_certificates
        exit 0
        ;;
    --renew)
        log INFO "Force renewing all certificates..."
        setup_directories
        generate_main_certificate
        generate_subdomain_certificates
        copy_certificates_for_docker
        verify_certificates
        log SUCCESS "Certificate renewal completed!"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log ERROR "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac