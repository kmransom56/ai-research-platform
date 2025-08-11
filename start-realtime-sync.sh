#!/bin/bash

# =============================================================================
# Chat Copilot Platform - Start Real-Time Sync
# =============================================================================
# Quick start script for real-time synchronization
# =============================================================================

set -euo pipefail

# Colors (use $'...' for escape handling)
GREEN=$'\033[0;32m'
BLUE=$'\033[0;34m'
YELLOW=$'\033[1;33m'
RED=$'\033[0;31m'
NC=$'\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/scripts/sync/realtime-sync-simple.sh"

printf "%b\n" "${BLUE}🔄 Chat Copilot Platform - Real-Time Sync Starter${NC}"
printf "%b\n" "${GREEN}💾 Source: 192.168.0.1 (ubuntuaicodeserver)${NC}"
printf "%b\n" "${GREEN}🎮 Backup: 192.168.0.5 (ubuntuaicodeserver-2) - High GPU RAM${NC}"
echo "================================================================================"
echo

# Check if sync is already running
if "$SYNC_SCRIPT" status | grep -q "Sync is running"; then
    printf "%b\n" "${YELLOW}⚠️  Real-time sync is already running${NC}"
    echo "Use the following commands:"
    echo "  $SYNC_SCRIPT status   - Check sync status"
    echo "  $SYNC_SCRIPT monitor  - Monitor sync activity"
    echo "  $SYNC_SCRIPT stop     - Stop sync"
    exit 0
fi

printf "%b\n" "${BLUE}🚀 Starting real-time synchronization...${NC}"
echo "This will sync all changes from this server to the backup server in real-time."
echo

# Test connection first
printf "%b\n" "${BLUE}🔗 Testing connection to backup server...${NC}"
if ssh -o ConnectTimeout=5 keith-ransom@192.168.0.5 "echo 'connected'" >/dev/null 2>&1; then
    printf "%b\n" "${GREEN}✅ Connection successful${NC}"
else
    printf "%b\n" "${RED}❌ Cannot connect to backup server${NC}"
    echo "Please check SSH configuration and try again."
    exit 1
fi

echo
printf "%b\n" "${BLUE}📁 Directories that will be watched for changes:${NC}"
echo "  • webapi/ - Backend API code"
echo "  • webapp/ - Frontend web application"
echo "  • scripts/ - Platform scripts"
echo "  • configs/ - Configuration files"
echo "  • docker/ - Docker configurations"
echo "  • docs/ - Documentation"
echo "  • agents/ - AI agents"
echo "  • plugins/ - Platform plugins"
echo "  • tools/ - Development tools"
echo "  • python/ - Python modules"
echo "  • shared/ - Shared resources"
echo "  • systemd services - System service files"
echo

printf "%b\n" "${YELLOW}💡 Benefits of real-time sync:${NC}"
echo "  • Instant backup of all changes"
echo "  • Switch to high-GPU server anytime"
echo "  • Automatic systemd services sync"
echo "  • No manual sync needed"
echo

# Auto-confirm in non-interactive mode or when explicitly requested
AUTO_YES_FLAG="${AUTO_YES:-}"
if [[ "${1:-}" == "--yes" || "$AUTO_YES_FLAG" =~ ^(1|y|Y|yes|true)$ || ! -t 0 ]]; then
    REPLY="y"
else
    read -p "Start real-time sync? (y/N): " -n 1 -r
    echo
fi

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Real-time sync cancelled."
    exit 0
fi

echo
printf "%b\n" "${GREEN}🎯 Starting real-time sync in background...${NC}"

# Start sync in background
"$SYNC_SCRIPT" start &

# Wait a moment for it to start
sleep 3

# Show status
echo
"$SYNC_SCRIPT" status

echo
printf "%b\n" "${GREEN}✅ Real-time sync is now running!${NC}"
echo
printf "%b\n" "${BLUE}📋 Useful commands:${NC}"
echo "  $SYNC_SCRIPT status   - Check sync status"
echo "  $SYNC_SCRIPT monitor  - Monitor sync activity (live)"
echo "  $SYNC_SCRIPT stop     - Stop sync"
echo "  $SYNC_SCRIPT test     - Test sync functionality"
echo
printf "%b\n" "${BLUE}🎮 To switch to backup server (high GPU):${NC}"
echo "  ssh keith-ransom@192.168.0.5"
echo "  cd ~/chat-copilot"
echo
printf "%b\n" "${YELLOW}💡 Your changes are now being synced in real-time!${NC}"
echo "   Edit files on this server and they'll appear on the backup server instantly."