#!/bin/bash

# Quick Restore Script - One-command restoration
# Usage: ./quick-restore.sh

cd /home/keith/chat-copilot

echo "🔄 Quick Restore - AI Research Platform"
echo "======================================"

if [ -f "config-backups-working/latest/quick-restore.sh" ]; then
    echo "📦 Found latest backup, running restore..."
    ./config-backups-working/latest/quick-restore.sh
else
    echo "❌ No backup found! Please run backup first:"
    echo "   ./scripts/backup-working-config.sh"
    exit 1
fi