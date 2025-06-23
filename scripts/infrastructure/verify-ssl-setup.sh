#!/bin/bash
# Tailscale SSL Certificate Verification Script
# Checks if SSL certificates are properly configured and accessible

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Configuration
readonly TAILSCALE_DOMAIN="ubuntuaicodeserver-1.tail5137b4.ts.net"
readonly NGINX_SSL_DIR="/etc/ssl/tailscale"
readonly DOCKER_SSL_DIR="/opt/tailscale-certs"
readonly TAILSCALE_CERT_DIR="/var/lib/tailscale/certs"

# Applications to check
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
    "TITLE") echo -e "${GREEN}🔍 [$timestamp] $*${NC}" ;;
    esac
}

check_directories() {
    log TITLE "Checking SSL certificate directories..."
    
    local issues=0
    
    # Check nginx SSL directory
    if [[ -d "$NGINX_SSL_DIR" ]]; then
        log SUCCESS "Nginx SSL directory exists: $NGINX_SSL_DIR"
        ls -la "$NGINX_SSL_DIR" | head -5
    else
        log ERROR "Nginx SSL directory missing: $NGINX_SSL_DIR"
        issues=$((issues + 1))
    fi
    
    # Check Docker SSL directory
    if [[ -d "$DOCKER_SSL_DIR" ]]; then
        log SUCCESS "Docker SSL directory exists: $DOCKER_SSL_DIR"
        ls -la "$DOCKER_SSL_DIR" | head -5
    else
        log ERROR "Docker SSL directory missing: $DOCKER_SSL_DIR"
        issues=$((issues + 1))
    fi
    
    # Check Tailscale cert directory (optional)
    if [[ -d "$TAILSCALE_CERT_DIR" ]]; then
        log SUCCESS "Tailscale cert directory exists: $TAILSCALE_CERT_DIR"
    else
        log WARN "Tailscale cert directory missing: $TAILSCALE_CERT_DIR (this may be normal)"
    fi
    
    return $issues
}

check_main_certificate() {
    log TITLE "Checking main certificate..."
    
    local issues=0
    local cert_file="$NGINX_SSL_DIR/${TAILSCALE_DOMAIN}.crt"
    local key_file="$NGINX_SSL_DIR/${TAILSCALE_DOMAIN}.key"
    
    # Check certificate file
    if [[ -f "$cert_file" ]]; then
        log SUCCESS "Main certificate exists: $cert_file"
        
        # Check certificate validity
        if openssl x509 -in "$cert_file" -noout -text >/dev/null 2>&1; then
            log SUCCESS "Main certificate is valid"
            
            # Check expiration
            local expiry=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
            log INFO "Main certificate expires: $expiry"
        else
            log ERROR "Main certificate is invalid or corrupted"
            issues=$((issues + 1))
        fi
    else
        log ERROR "Main certificate missing: $cert_file"
        issues=$((issues + 1))
    fi
    
    # Check key file
    if [[ -f "$key_file" ]]; then
        log SUCCESS "Main private key exists: $key_file"
        
        # Check key permissions
        local perms=$(stat -c "%a" "$key_file")
        if [[ "$perms" == "600" ]]; then
            log SUCCESS "Main private key has correct permissions: $perms"
        else
            log WARN "Main private key permissions should be 600, found: $perms"
        fi
    else
        log ERROR "Main private key missing: $key_file"
        issues=$((issues + 1))
    fi
    
    return $issues
}

check_subdomain_certificates() {
    log TITLE "Checking subdomain certificates..."
    
    local issues=0
    local found_certs=0
    
    for app in "${APPLICATIONS[@]}"; do
        local subdomain="${app}.${TAILSCALE_DOMAIN}"
        local cert_file="$NGINX_SSL_DIR/${subdomain}.crt"
        local key_file="$NGINX_SSL_DIR/${subdomain}.key"
        
        if [[ -f "$cert_file" && -f "$key_file" ]]; then
            log SUCCESS "Certificate found for $app: $subdomain"
            found_certs=$((found_certs + 1))
            
            # Check certificate validity
            if ! openssl x509 -in "$cert_file" -noout -text >/dev/null 2>&1; then
                log ERROR "Certificate for $app is invalid or corrupted"
                issues=$((issues + 1))
            fi
        else
            log WARN "Certificate missing for $app: $subdomain"
        fi
    done
    
    log INFO "Found $found_certs subdomain certificates out of ${#APPLICATIONS[@]} applications"
    
    return $issues
}

check_nginx_configurations() {
    log TITLE "Checking nginx configuration references..."
    
    local issues=0
    local config_dir="/home/keith/chat-copilot/nginx-configs"
    
    if [[ ! -d "$config_dir" ]]; then
        log ERROR "Nginx configs directory not found: $config_dir"
        return 1
    fi
    
    # Check main SSL config
    local ssl_main_config="$config_dir/ssl-main.conf"
    if [[ -f "$ssl_main_config" ]]; then
        log SUCCESS "Main SSL config found: ssl-main.conf"
        
        # Check certificate path references
        if grep -q "/var/lib/tailscale/certs/" "$ssl_main_config"; then
            log SUCCESS "ssl-main.conf references correct certificate path"
        else
            log WARN "ssl-main.conf may have incorrect certificate paths"
        fi
    else
        log WARN "Main SSL config not found: ssl-main.conf"
    fi
    
    # Check individual app configs
    local config_count=0
    for app in "${APPLICATIONS[@]}"; do
        local config_file="$config_dir/${app}.conf"
        if [[ -f "$config_file" ]]; then
            config_count=$((config_count + 1))
            
            if grep -q "/etc/ssl/tailscale/" "$config_file"; then
                log SUCCESS "$app.conf has correct certificate path"
            else
                log WARN "$app.conf may have incorrect certificate paths"
            fi
        fi
    done
    
    log INFO "Found $config_count nginx configuration files"
    
    return $issues
}

check_docker_integration() {
    log TITLE "Checking Docker certificate integration..."
    
    local issues=0
    local override_file="/home/keith/chat-copilot/docker-configs/docker-compose.override.yml"
    
    if [[ -f "$override_file" ]]; then
        log SUCCESS "Docker override file found"
        
        if grep -q "/opt/tailscale-certs:/etc/ssl/tailscale" "$override_file"; then
            log SUCCESS "Docker override mounts certificate directory correctly"
        else
            log WARN "Docker override may not mount certificates correctly"
        fi
    else
        log WARN "Docker override file not found: $override_file"
    fi
    
    return $issues
}

check_tailscale_status() {
    log TITLE "Checking Tailscale status..."
    
    if command -v tailscale >/dev/null 2>&1; then
        log SUCCESS "Tailscale command available"
        
        if tailscale status >/dev/null 2>&1; then
            log SUCCESS "Tailscale is authenticated and running"
            echo "Tailscale Status:"
            tailscale status | head -5
        else
            log ERROR "Tailscale is not authenticated or not running"
            return 1
        fi
    else
        log ERROR "Tailscale is not installed"
        return 1
    fi
    
    return 0
}

generate_summary() {
    local total_issues=$1
    
    echo
    log TITLE "=== SSL Certificate Setup Verification Summary ==="
    echo
    
    if [[ $total_issues -eq 0 ]]; then
        log SUCCESS "✅ SSL certificate setup appears to be working correctly!"
        echo
        echo "🌐 Your services should be accessible via HTTPS at:"
        echo "   • Main Platform: https://$TAILSCALE_DOMAIN:10443/"
        echo "   • Control Panel: https://$TAILSCALE_DOMAIN:10443/hub"
        for app in "${APPLICATIONS[@]}"; do
            if [[ -f "$NGINX_SSL_DIR/${app}.${TAILSCALE_DOMAIN}.crt" ]]; then
                echo "   • ${app^}: https://${app}.${TAILSCALE_DOMAIN}/"
            fi
        done
    else
        log ERROR "❌ Found $total_issues issues with SSL certificate setup"
        echo
        echo "🔧 Recommended actions:"
        echo "   1. Run the SSL setup script: ./scripts/infrastructure/setup-tailscale-ssl.sh"
        echo "   2. Check Tailscale admin console for MagicDNS and HTTPS settings"
        echo "   3. Verify certificate file permissions and paths"
        echo "   4. Restart nginx services after fixing issues"
    fi
    
    echo
    echo "📋 Useful commands:"
    echo "   • Setup SSL: ./scripts/infrastructure/setup-tailscale-ssl.sh"
    echo "   • Renew certificates: ./scripts/infrastructure/renew-certificates.sh"
    echo "   • Monitor certificates: python3 python/utilities/check-certificates.py"
    echo
}

main() {
    log INFO "Starting SSL certificate setup verification..."
    echo
    
    local total_issues=0
    
    # Run all checks
    check_tailscale_status || total_issues=$((total_issues + $?))
    echo
    
    check_directories || total_issues=$((total_issues + $?))
    echo
    
    check_main_certificate || total_issues=$((total_issues + $?))
    echo
    
    check_subdomain_certificates || total_issues=$((total_issues + $?))
    echo
    
    check_nginx_configurations || total_issues=$((total_issues + $?))
    echo
    
    check_docker_integration || total_issues=$((total_issues + $?))
    
    # Generate summary
    generate_summary $total_issues
    
    # Exit with appropriate code
    exit $total_issues
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Verify Tailscale SSL certificate setup for the AI Research Platform"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --summary      Show summary only (skip detailed checks)"
        echo
        exit 0
        ;;
    --summary)
        log INFO "SSL Certificate Setup Summary"
        if [[ -f "$NGINX_SSL_DIR/${TAILSCALE_DOMAIN}.crt" ]]; then
            log SUCCESS "Main certificate exists"
        else
            log ERROR "Main certificate missing"
        fi
        
        local cert_count=0
        for app in "${APPLICATIONS[@]}"; do
            if [[ -f "$NGINX_SSL_DIR/${app}.${TAILSCALE_DOMAIN}.crt" ]]; then
                cert_count=$((cert_count + 1))
            fi
        done
        log INFO "Subdomain certificates: $cert_count/${#APPLICATIONS[@]}"
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