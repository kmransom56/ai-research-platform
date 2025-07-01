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
