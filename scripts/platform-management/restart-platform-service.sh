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
