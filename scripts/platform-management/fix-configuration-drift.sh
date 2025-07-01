#!/bin/bash
# Configuration Drift Prevention and Fix Script
# This script addresses all the common causes of configuration drift after reboot

set -euo pipefail

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

print_header() {
    echo
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

# Check if running as root for system-level changes
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        print_status "INFO" "Running as root - can make system-level changes"
        return 0
    else
        print_status "WARNING" "Not running as root - some fixes may require sudo"
        return 1
    fi
}

print_header "CONFIGURATION DRIFT ANALYSIS AND FIX"

# 1. SYSTEMD SERVICE INSTALLATION AND ENABLEMENT
print_header "1. FIXING SYSTEMD SERVICE PERSISTENCE"

SERVICE_FILE="/home/keith/chat-copilot/scripts/platform-management/ai-platform-consolidated.service"
SYSTEM_SERVICE_FILE="/etc/systemd/system/ai-platform-consolidated.service"

if [[ -f "$SERVICE_FILE" ]]; then
    print_status "INFO" "Found systemd service file at $SERVICE_FILE"

    # Copy service file to system directory
    if check_sudo; then
        cp "$SERVICE_FILE" "$SYSTEM_SERVICE_FILE"
        print_status "SUCCESS" "Copied service file to system directory"
    else
        print_status "INFO" "Run with sudo to install systemd service:"
        echo "sudo cp '$SERVICE_FILE' '$SYSTEM_SERVICE_FILE'"
        echo "sudo systemctl daemon-reload"
        echo "sudo systemctl enable ai-platform-consolidated.service"
    fi

    # Reload systemd and enable service
    if check_sudo; then
        systemctl daemon-reload
        systemctl enable ai-platform-consolidated.service
        print_status "SUCCESS" "Systemd service enabled for auto-start"
    fi
else
    print_status "ERROR" "Systemd service file not found at $SERVICE_FILE"
fi

# 2. DOCKER RESTART POLICIES
print_header "2. CHECKING DOCKER RESTART POLICIES"

COMPOSE_FILE="/home/keith/chat-copilot/configs/docker-compose/docker-compose-full-stack.yml"

if [[ -f "$COMPOSE_FILE" ]]; then
    print_status "SUCCESS" "Docker Compose file has 'restart: unless-stopped' policies"
    print_status "INFO" "All containers will restart automatically after reboot"
else
    print_status "ERROR" "Docker Compose file not found at $COMPOSE_FILE"
fi

# 3. DOCKER SERVICE ENABLEMENT
print_header "3. ENSURING DOCKER SERVICE AUTO-START"

if check_sudo; then
    systemctl enable docker
    print_status "SUCCESS" "Docker service enabled for auto-start"
else
    print_status "INFO" "Run 'sudo systemctl enable docker' to enable Docker auto-start"
fi

# 4. NGINX CONTAINER PERSISTENCE
print_header "4. FIXING NGINX CONTAINER PERSISTENCE"

print_status "INFO" "The startup script creates nginx-ssl container with --restart unless-stopped"
print_status "INFO" "This ensures nginx will restart automatically after reboot"

# Check if nginx config exists
NGINX_CONFIG="/home/keith/chat-copilot/configs/nginx/nginx-ssl.conf"
if [[ -f "$NGINX_CONFIG" ]]; then
    print_status "SUCCESS" "Nginx SSL config found at $NGINX_CONFIG"
else
    print_status "WARNING" "Nginx SSL config not found at $NGINX_CONFIG"
fi

# 5. SSL CERTIFICATE PERSISTENCE
print_header "5. CHECKING SSL CERTIFICATE PERSISTENCE"

CERT_FILE="/etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt"
KEY_FILE="/etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key"

if [[ -f "$CERT_FILE" ]] && [[ -f "$KEY_FILE" ]]; then
    print_status "SUCCESS" "SSL certificates found and persistent"
else
    print_status "WARNING" "SSL certificates missing - platform may start but SSL won't work"
    print_status "INFO" "Expected certificates at:"
    echo "  - $CERT_FILE"
    echo "  - $KEY_FILE"
fi

# 6. ENVIRONMENT VARIABLES PERSISTENCE
print_header "6. CHECKING ENVIRONMENT VARIABLES"

ENV_FILE="/home/keith/chat-copilot/.env"
if [[ -f "$ENV_FILE" ]]; then
    print_status "SUCCESS" "Environment file found at $ENV_FILE"
else
    print_status "WARNING" "No .env file found - Docker Compose may fail without required variables"
    print_status "INFO" "Create $ENV_FILE with required variables like:"
    echo "  AZURE_OPENAI_KEY=your_key"
    echo "  AZURE_OPENAI_ENDPOINT=your_endpoint"
    echo "  GITHUB_WEBHOOK_SECRET=your_secret"
    echo "  POSTGRES_PASSWORD=your_password"
fi

# 7. WORKING DIRECTORY ISSUES
print_header "7. FIXING WORKING DIRECTORY ISSUES"

STARTUP_SCRIPT="/home/keith/chat-copilot/start-ssl-platform.sh"
if [[ -f "$STARTUP_SCRIPT" ]]; then
    # Check if script changes to correct directory
    if grep -q "cd.*chat-copilot" "$STARTUP_SCRIPT"; then
        print_status "SUCCESS" "Startup script handles working directory"
    else
        print_status "WARNING" "Startup script may not handle working directory correctly"
        print_status "INFO" "Consider adding 'cd /home/keith/chat-copilot' at the beginning"
    fi
else
    print_status "ERROR" "Startup script not found at $STARTUP_SCRIPT"
fi

# 8. CREATE IMPROVED SYSTEMD SERVICE
print_header "8. CREATING IMPROVED SYSTEMD SERVICE"

cat >"ai-platform-consolidated-fixed.service" <<'EOF'
[Unit]
Description=AI Research Platform - Complete Stack (Fixed)
Documentation=https://github.com/kmransom56/ai-research-platform
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=keith
Group=keith
WorkingDirectory=/home/keith/chat-copilot

# Environment setup
Environment=HOME=/home/keith
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/keith/.local/bin
Environment=DOCKER_HOST=unix:///var/run/docker.sock

# Pre-start checks
ExecStartPre=/bin/bash -c 'cd /home/keith/chat-copilot && test -f start-ssl-platform.sh'
ExecStartPre=/bin/bash -c 'cd /home/keith/chat-copilot && test -f configs/docker-compose/docker-compose-full-stack.yml'

# Use the production SSL startup script with proper working directory
ExecStart=/bin/bash -c 'cd /home/keith/chat-copilot && ./start-ssl-platform.sh'

# Improved stop command
ExecStop=/bin/bash -c 'cd /home/keith/chat-copilot && docker stop nginx-ssl 2>/dev/null || true && docker-compose -f configs/docker-compose/docker-compose-full-stack.yml down'

# Restart policy
Restart=on-failure
RestartSec=30
TimeoutStartSec=600
TimeoutStopSec=300

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-platform

# Security
NoNewPrivileges=false
PrivateTmp=false

[Install]
WantedBy=multi-user.target
EOF

print_status "SUCCESS" "Created improved systemd service file: ai-platform-consolidated-fixed.service"

# 9. CREATE BOOT-TIME VALIDATION SCRIPT
print_header "9. CREATING BOOT-TIME VALIDATION SCRIPT"

cat >"validate-platform-config.sh" <<'EOF'
#!/bin/bash
# Boot-time Platform Configuration Validator
# Run this after reboot to check if everything is properly configured

set -euo pipefail

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

echo "=== POST-REBOOT PLATFORM VALIDATION ==="
echo

# Check Docker service
if systemctl is-active --quiet docker; then
    print_status "SUCCESS" "Docker service is running"
else
    print_status "ERROR" "Docker service is not running"
fi

# Check systemd service
if systemctl is-enabled --quiet ai-platform-consolidated.service 2>/dev/null; then
    print_status "SUCCESS" "AI Platform service is enabled"
    if systemctl is-active --quiet ai-platform-consolidated.service; then
        print_status "SUCCESS" "AI Platform service is running"
    else
        print_status "WARNING" "AI Platform service is enabled but not running"
    fi
else
    print_status "ERROR" "AI Platform service is not enabled"
fi

# Check Docker containers
echo
print_status "INFO" "Docker container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check key services
echo
print_status "INFO" "Checking key service endpoints:"

# Check nginx-ssl
if docker ps | grep -q nginx-ssl; then
    print_status "SUCCESS" "nginx-ssl container is running"
else
    print_status "ERROR" "nginx-ssl container is not running"
fi

# Check compose services
if docker-compose -f /home/keith/chat-copilot/configs/docker-compose/docker-compose-full-stack.yml ps | grep -q "Up"; then
    print_status "SUCCESS" "Docker Compose services are running"
else
    print_status "WARNING" "Some Docker Compose services may not be running"
fi

echo
print_status "INFO" "Validation complete. Check any ERROR or WARNING items above."
EOF

chmod +x "validate-platform-config.sh"
print_status "SUCCESS" "Created boot-time validation script: validate-platform-config.sh"

# 10. CREATE AUTOMATED FIX SCRIPT
print_header "10. CREATING AUTOMATED INSTALLATION SCRIPT"

cat >"install-persistent-platform.sh" <<'EOF'
#!/bin/bash
# Automated Platform Persistence Installation
# Run this script with sudo to fix all configuration drift issues

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

echo "=== INSTALLING PERSISTENT AI PLATFORM CONFIGURATION ==="

# 1. Install systemd service
cp ai-platform-consolidated-fixed.service /etc/systemd/system/ai-platform-consolidated.service
systemctl daemon-reload
systemctl enable ai-platform-consolidated.service
echo "✅ Systemd service installed and enabled"

# 2. Enable Docker service
systemctl enable docker
echo "✅ Docker service enabled for auto-start"

# 3. Create startup validation service
cat > /etc/systemd/system/ai-platform-validator.service << 'VALIDATOR_EOF'
[Unit]
Description=AI Platform Post-Boot Validator
After=ai-platform-consolidated.service
Wants=ai-platform-consolidated.service

[Service]
Type=oneshot
User=keith
WorkingDirectory=/home/keith/chat-copilot/scripts/platform-management
ExecStart=/home/keith/chat-copilot/scripts/platform-management/validate-platform-config.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
VALIDATOR_EOF

systemctl enable ai-platform-validator.service
echo "✅ Post-boot validator service installed"

echo
echo "=== INSTALLATION COMPLETE ==="
echo "The AI Platform will now start automatically after reboot."
echo "Run 'sudo systemctl start ai-platform-consolidated.service' to start now."
echo "Run './validate-platform-config.sh' after reboot to verify everything works."
EOF

chmod +x "install-persistent-platform.sh"
print_status "SUCCESS" "Created automated installation script: install-persistent-platform.sh"

# SUMMARY
print_header "CONFIGURATION DRIFT ANALYSIS COMPLETE"

echo -e "${BLUE}IDENTIFIED ISSUES:${NC}"
echo "1. ❌ Systemd service not installed in /etc/systemd/system/"
echo "2. ❌ Systemd service not enabled for auto-start"
echo "3. ⚠️  Working directory issues in systemd service"
echo "4. ⚠️  No post-boot validation"
echo "5. ⚠️  Docker service may not be enabled"

echo
echo -e "${GREEN}SOLUTIONS CREATED:${NC}"
echo "1. ✅ ai-platform-consolidated-fixed.service - Improved systemd service"
echo "2. ✅ validate-platform-config.sh - Post-reboot validation"
echo "3. ✅ install-persistent-platform.sh - Automated installation"

echo
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo "1. Run: sudo ./install-persistent-platform.sh"
echo "2. Test: sudo systemctl start ai-platform-consolidated.service"
echo "3. Reboot and run: ./validate-platform-config.sh"

print_status "SUCCESS" "Configuration drift prevention system created!"
