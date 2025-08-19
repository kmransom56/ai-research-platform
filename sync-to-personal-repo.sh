#!/bin/bash
# Sync Latest Changes to Personal Repository
# Applies only the latest changes without git history issues

set -e

echo "🔄 Syncing latest changes to personal repository..."

# Create temporary directory for clean checkout
TEMP_DIR="/tmp/personal-repo-sync"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Clone your personal repository
echo "📥 Cloning personal repository..."
git clone https://github.com/kmransom56/ai-research-platform.git "$TEMP_DIR"
cd "$TEMP_DIR"

# Copy the important files from our current implementation
echo "📋 Copying updated files..."

# Create directory structure
mkdir -p scripts/platform-management
mkdir -p python/ai-stack  
mkdir -p webapp/public/css

# Copy the key files with our improvements
cp /home/keith/chat-copilot/scripts/platform-management/chat-copilot-sync.service scripts/platform-management/
cp /home/keith/chat-copilot/scripts/platform-management/sync-service-wrapper.sh scripts/platform-management/
cp /home/keith/chat-copilot/scripts/platform-management/manage-sync-service.sh scripts/platform-management/
cp /home/keith/chat-copilot/sync-with-backup-server.sh .
cp /home/keith/chat-copilot/python/ai-stack/api_gateway.py python/ai-stack/ 2>/dev/null || echo "Skipping api_gateway.py"
cp /home/keith/chat-copilot/python/ai-stack/collaboration_orchestrator.py python/ai-stack/ 2>/dev/null || echo "Skipping collaboration_orchestrator.py" 
cp /home/keith/chat-copilot/python/ai-stack/workflow_templates.py python/ai-stack/ 2>/dev/null || echo "Skipping workflow_templates.py"
cp /home/keith/chat-copilot/webapp/public/control-panel.html webapp/public/ 2>/dev/null || echo "Skipping control-panel.html"
cp /home/keith/chat-copilot/webapp/public/applications.html webapp/public/ 2>/dev/null || echo "Skipping applications.html"
cp /home/keith/chat-copilot/webapp/public/css/restaurant-noc-theme.css webapp/public/css/ 2>/dev/null || echo "Skipping restaurant-noc-theme.css"
cp /home/keith/chat-copilot/test-mcp-integration.sh . 2>/dev/null || echo "Skipping test-mcp-integration.sh"

# Make scripts executable
chmod +x scripts/platform-management/*.sh 2>/dev/null || true
chmod +x sync-with-backup-server.sh 2>/dev/null || true
chmod +x test-mcp-integration.sh 2>/dev/null || true

# Create comprehensive README for the changes
cat > SYNC_UPDATES.md << 'EOF'
# Latest Sync Updates - August 18, 2025

## 🔄 Real-time HA Backup Synchronization

### New Components Added:
- **systemd Service**: `scripts/platform-management/chat-copilot-sync.service`
- **Service Wrapper**: `scripts/platform-management/sync-service-wrapper.sh`
- **Management Script**: `scripts/platform-management/manage-sync-service.sh`
- **Enhanced Sync Script**: `sync-with-backup-server.sh` with real-time monitoring

### Features:
- ✅ Real-time file monitoring with inotifywait
- ✅ Automatic service restart and error recovery
- ✅ SSH-based connectivity validation for systemd
- ✅ Smart exclude patterns for efficient syncing
- ✅ Backup server synchronization at 192.168.0.5

## 🎨 Restaurant NOC UI Redesign

### New UI Components:
- **CSS Framework**: `webapp/public/css/restaurant-noc-theme.css`
- **Control Panel**: Enhanced `webapp/public/control-panel.html`
- **Applications Directory**: Redesigned `webapp/public/applications.html`

### Design Features:
- 🎨 Modern card-based interface with restaurant branding
- 🎨 Responsive grid system optimized for NOC operations
- 🎨 Dark theme with custom color palette
- 🎨 Material Icons integration for better UX

## 🔧 MCP Server Enhancements

### Improved Files:
- **API Gateway**: `python/ai-stack/api_gateway.py` - Better async handling
- **Collaboration Orchestrator**: `python/ai-stack/collaboration_orchestrator.py` - Fixed imports
- **Workflow Templates**: `python/ai-stack/workflow_templates.py` - Resolved circular dependencies
- **Test Integration**: `test-mcp-integration.sh` - MCP server testing

### Technical Improvements:
- 🔧 Fixed circular import issues in workflow management
- 🔧 Enhanced FortiManager MCP server reliability
- 🔧 Better error handling in collaboration orchestration
- 🔧 Improved async/await patterns for MCP requests

## Installation Instructions

### 1. Install Real-time Sync Service:
```bash
# Copy service file
sudo cp scripts/platform-management/chat-copilot-sync.service /etc/systemd/system/

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable chat-copilot-sync.service
sudo systemctl start chat-copilot-sync.service

# Check status
sudo systemctl status chat-copilot-sync.service
```

### 2. Apply UI Updates:
```bash
# The CSS and HTML files are ready to use
# Ensure web server serves from webapp/public/
```

### 3. Test MCP Integration:
```bash
# Run MCP integration tests
./test-mcp-integration.sh
```

## Service Management Commands:
```bash
# Start real-time sync
sudo systemctl start chat-copilot-sync.service

# Stop real-time sync  
sudo systemctl stop chat-copilot-sync.service

# View sync logs
journalctl -u chat-copilot-sync.service -f

# Check sync status
./sync-with-backup-server.sh realtime-status
```

## Network Requirements:
- SSH key authentication to backup server at 192.168.0.5
- Network connectivity for real-time file synchronization
- inotify-tools package for optimal file monitoring

## Success Metrics:
- ✅ Real-time file sync operational
- ✅ systemd service auto-starting on boot
- ✅ Modern UI deployed with restaurant NOC theme
- ✅ MCP server integration stable and functional
EOF

# Add and commit changes
git add .
git status

echo "📝 Files staged for commit. Ready to commit and push."
echo "🎯 Next steps:"
echo "   cd $TEMP_DIR"
echo "   git commit -m 'Deploy Real-time HA Backup Sync + Restaurant NOC UI Redesign'"
echo "   git push origin main"
echo ""
echo "📋 Or run this complete command:"
echo "   cd $TEMP_DIR && git commit -m '🔄 Deploy Real-time HA Sync + Restaurant NOC UI' && git push origin main"
EOF