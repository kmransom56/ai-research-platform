#!/bin/bash

# AI Research Platform - Auto-Restore Setup
# Sets up automatic configuration restoration on boot

echo "🔧 Setting up automatic restore service..."

# Copy service file
sudo cp /tmp/ai-platform-restore.service /etc/systemd/system/

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ai-platform-restore.service

echo "✅ Auto-restore service enabled!"
echo ""
echo "📋 Service Management Commands:"
echo "   sudo systemctl status ai-platform-restore    # Check status"
echo "   sudo systemctl start ai-platform-restore     # Manual restore"
echo "   sudo systemctl disable ai-platform-restore   # Disable auto-restore"
echo "   journalctl -u ai-platform-restore             # View logs"
echo ""
echo "🚀 The service will automatically run on next boot to restore your configuration!"