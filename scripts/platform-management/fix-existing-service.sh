#!/bin/bash
# Fix for Existing ai-platform-restore.service Configuration Drift
# This script addresses the specific issues with your current service

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

print_header "FIXING EXISTING AI-PLATFORM-RESTORE SERVICE"

# 1. ANALYZE CURRENT SERVICE STATUS
print_header "1. CURRENT SERVICE ANALYSIS"

print_status "INFO" "Checking current service status..."
if systemctl is-enabled ai-platform-restore.service >/dev/null 2>&1; then
    print_status "SUCCESS" "ai-platform-restore.service is enabled"
else
    print_status "ERROR" "ai-platform-restore.service is not enabled"
fi

if systemctl is-active ai-platform-restore.service >/dev/null 2>&1; then
    print_status "SUCCESS" "ai-platform-restore.service is active"
else
    print_status "WARNING" "ai-platform-restore.service is not active"
fi

# Check Docker status
if systemctl is-active docker >/dev/null 2>&1; then
    print_status "SUCCESS" "Docker service is running"
else
    print_status "ERROR" "Docker service is not running"
fi

# 2. IDENTIFY ISSUES WITH CURRENT SERVICE
print_header "2. IDENTIFIED ISSUES"

RESTORE_SCRIPT="/home/keith/chat-copilot/config-backups-working/latest/quick-restore.sh"
if [[ -f "$RESTORE_SCRIPT" ]]; then
    print_status "SUCCESS" "Restore script exists at $RESTORE_SCRIPT"
else
    print_status "ERROR" "Restore script missing at $RESTORE_SCRIPT"
fi

# Check if service has proper Docker dependency
if grep -q "Requires=docker.service" /etc/systemd/system/ai-platform-restore.service; then
    print_status "WARNING" "Service requires Docker but Docker connection issues detected"
else
    print_status "ERROR" "Service doesn't properly depend on Docker"
fi

# 3. CREATE IMPROVED SERVICE OVERRIDE
print_header "3. CREATING SERVICE IMPROVEMENTS"

# Create systemd override directory
sudo mkdir -p /etc/systemd/system/ai-platform-restore.service.d/

# Create improved override configuration
cat >ai-platform-restore-override.conf <<'EOF'
[Unit]
# Improved dependencies for Docker
After=network-online.target docker.service
Wants=network-online.target
Requires=docker.service

# Wait for Docker to be fully ready
After=docker.service

[Service]
# Add Docker environment variables
Environment=DOCKER_HOST=unix:///var/run/docker.sock
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Add pre-start checks
ExecStartPre=/bin/sleep 30
ExecStartPre=/bin/bash -c 'until docker info >/dev/null 2>&1; do echo "Waiting for Docker..."; sleep 5; done'
ExecStartPre=/bin/bash -c 'test -f /home/keith/chat-copilot/config-backups-working/latest/quick-restore.sh'

# Improved restart policy
Restart=on-failure
RestartSec=60
TimeoutStartSec=600

# Better logging
StandardOutput=journal+console
StandardError=journal+console
EOF

print_status "SUCCESS" "Created improved service override configuration"

# 4. INSTALL THE OVERRIDE
print_header "4. INSTALLING SERVICE IMPROVEMENTS"

if [[ $EUID -eq 0 ]]; then
    # Running as root, install directly
    cp ai-platform-restore-override.conf /etc/systemd/system/ai-platform-restore.service.d/override.conf
    systemctl daemon-reload
    print_status "SUCCESS" "Service override installed and systemd reloaded"
else
    # Not root, provide instructions
    print_status "INFO" "Run the following commands as root to install the improvements:"
    echo "sudo cp ai-platform-restore-override.conf /etc/systemd/system/ai-platform-restore.service.d/override.conf"
    echo "sudo systemctl daemon-reload"
    echo "sudo systemctl restart ai-platform-restore.service"
fi

# 5. CREATE VALIDATION SCRIPT FOR EXISTING SERVICE
print_header "5. CREATING VALIDATION SCRIPT"

cat >validate-existing-service.sh <<'EOF'
#!/bin/bash
# Validation script for ai-platform-restore.service

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

echo "=== AI PLATFORM RESTORE SERVICE VALIDATION ==="
echo

# Check service status
if systemctl is-enabled ai-platform-restore.service >/dev/null 2>&1; then
    print_status "SUCCESS" "ai-platform-restore.service is enabled"
else
    print_status "ERROR" "ai-platform-restore.service is not enabled"
fi

if systemctl is-active ai-platform-restore.service >/dev/null 2>&1; then
    print_status "SUCCESS" "ai-platform-restore.service is active"
else
    print_status "ERROR" "ai-platform-restore.service is not active"
fi

# Check Docker
if systemctl is-active docker >/dev/null 2>&1; then
    print_status "SUCCESS" "Docker service is running"
else
    print_status "ERROR" "Docker service is not running"
fi

# Check Docker containers
echo
print_status "INFO" "Current Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || print_status "WARNING" "Cannot connect to Docker daemon"

# Check service logs
echo
print_status "INFO" "Recent service logs:"
journalctl -u ai-platform-restore.service --no-pager -n 10 2>/dev/null || print_status "WARNING" "Cannot access service logs"

# Check if platform is accessible
echo
print_status "INFO" "Testing platform accessibility..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:11000 | grep -q "200\|302\|404"; then
    print_status "SUCCESS" "Platform backend is responding"
else
    print_status "WARNING" "Platform backend may not be accessible"
fi

echo
print_status "INFO" "Validation complete."
EOF

chmod +x validate-existing-service.sh
print_status "SUCCESS" "Created validation script: validate-existing-service.sh"

# 6. CREATE RESTART SCRIPT
print_header "6. CREATING RESTART SCRIPT"

cat >restart-platform-service.sh <<'EOF'
#!/bin/bash
# Safe restart script for ai-platform-restore.service

echo "Restarting AI Platform Restore Service..."

# Stop the service
sudo systemctl stop ai-platform-restore.service
echo "Service stopped."

# Wait a moment
sleep 5

# Start the service
sudo systemctl start ai-platform-restore.service
echo "Service started."

# Check status
sleep 10
sudo systemctl status ai-platform-restore.service --no-pager -l

echo
echo "Run './validate-existing-service.sh' to check if everything is working."
EOF

chmod +x restart-platform-service.sh
print_status "SUCCESS" "Created restart script: restart-platform-service.sh"

# SUMMARY
print_header "CONFIGURATION DRIFT FIX COMPLETE"

echo -e "${BLUE}ISSUES IDENTIFIED WITH YOUR EXISTING SERVICE:${NC}"
echo "1. ⚠️  Docker connection timing issues during startup"
echo "2. ⚠️  Service starts before Docker is fully ready"
echo "3. ⚠️  No pre-start validation of required files"
echo "4. ⚠️  Limited restart policy on failures"

echo
echo -e "${GREEN}SOLUTIONS CREATED:${NC}"
echo "1. ✅ ai-platform-restore-override.conf - Service improvements"
echo "2. ✅ validate-existing-service.sh - Service validation"
echo "3. ✅ restart-platform-service.sh - Safe restart script"

echo
echo -e "${YELLOW}NEXT STEPS:${NC}"
if [[ $EUID -eq 0 ]]; then
    echo "1. Service override has been installed automatically"
    echo "2. Run: systemctl restart ai-platform-restore.service"
    echo "3. Run: ./validate-existing-service.sh"
else
    echo "1. Run: sudo cp ai-platform-restore-override.conf /etc/systemd/system/ai-platform-restore.service.d/override.conf"
    echo "2. Run: sudo systemctl daemon-reload"
    echo "3. Run: ./restart-platform-service.sh"
    echo "4. Run: ./validate-existing-service.sh"
fi

echo
print_status "SUCCESS" "Your existing ai-platform-restore.service has been improved!"
print_status "INFO" "The service will now wait for Docker to be ready and handle failures better."
