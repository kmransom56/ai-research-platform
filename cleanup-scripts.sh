#!/bin/bash
# Script Cleanup and Consolidation
# Removes redundant scripts and keeps only the essential ones

echo "🧹 AI Research Platform Script Cleanup"
echo "====================================="

# Script analysis:
echo "📋 SCRIPT ANALYSIS:"
echo ""

# Create archive directory
mkdir -p scripts-archive
echo "📁 Created scripts-archive/ for redundant scripts"

echo ""
echo "🔍 IDENTIFIED REDUNDANT SCRIPTS:"
echo ""

# ==============================================================================
# REDUNDANT STARTUP SCRIPTS (Keep only startup-platform.sh)
# ==============================================================================

echo "🚀 STARTUP SCRIPTS:"
echo "   KEEP: startup-platform.sh (comprehensive startup with UV)"
echo "   REMOVE: startup-platform-uv.sh (redundant - UV now in main script)"
echo "   REMOVE: start-all-services.sh (redundant - functionality in startup-platform.sh)"
echo "   REMOVE: start-all-services-uv.sh (redundant - UV now in main script)"
echo "   REMOVE: start-platform.sh (minimal script - superseded by startup-platform.sh)"

mv startup-platform-uv.sh scripts-archive/ 2>/dev/null
mv start-all-services.sh scripts-archive/ 2>/dev/null  
mv start-all-services-uv.sh scripts-archive/ 2>/dev/null
mv start-platform.sh scripts-archive/ 2>/dev/null

echo "   ✅ Moved 4 redundant startup scripts to archive"

# ==============================================================================
# REDUNDANT STOP SCRIPTS (Update stop-platform.sh)
# ==============================================================================

echo ""
echo "🛑 STOP SCRIPTS:"
echo "   KEEP: stop-platform.sh (updated with comprehensive service coverage)"
echo "   REMOVE: stop-all-services.sh (basic - superseded by stop-platform.sh)"

mv stop-all-services.sh scripts-archive/ 2>/dev/null

echo "   ✅ Moved 1 redundant stop script to archive"

# ==============================================================================
# REDUNDANT SERVICE-SPECIFIC SCRIPTS
# ==============================================================================

echo ""
echo "🔧 SERVICE-SPECIFIC SCRIPTS:"
echo "   KEEP: manage-platform.sh (comprehensive service management)"
echo "   REMOVE: restart-port-scanner.sh (functionality in manage-platform.sh)"
echo "   REMOVE: enable-user-services.sh (systemd services now disabled by design)"

mv restart-port-scanner.sh scripts-archive/ 2>/dev/null
mv enable-user-services.sh scripts-archive/ 2>/dev/null

echo "   ✅ Moved 2 redundant service scripts to archive"

# ==============================================================================
# ESSENTIAL SCRIPTS TO KEEP
# ==============================================================================

echo ""
echo "✅ ESSENTIAL SCRIPTS (KEEPING):"
echo ""

echo "🏠 CORE PLATFORM:"
echo "   • startup-platform.sh - Comprehensive startup (all services, UV, phases)"  
echo "   • stop-platform.sh - Complete shutdown (graceful, cleanup)"
echo "   • check-platform-status.sh - Full status checking (all services)"
echo "   • manage-platform.sh - User-friendly management interface"

echo ""
echo "🔧 CONFIGURATION:"
echo "   • validate-config.sh - Configuration validation (every 15 min)"
echo "   • protect-config.sh - Configuration protection"
echo "   • switch-ai-provider.sh - AI provider switching"
echo "   • fix-configuration-drift.sh - Configuration drift fix"

echo ""
echo "🔄 BACKUP & RECOVERY:"
echo "   • backup-configs.sh - Manual configuration backup"
echo "   • backup-configs-auto.sh - Automated backup (cron)"
echo "   • restore-config.sh - Configuration restore"
echo "   • emergency-reset.sh - Emergency reset to defaults"

echo ""
echo "📊 MONITORING:"
echo "   • health-monitor.sh - Continuous health monitoring"
echo "   • file-monitor.sh - Configuration file monitoring"

echo ""
echo "🚀 DEPLOYMENT:"
echo "   • deploy.sh - Deployment automation"

# ==============================================================================
# CREATE SCRIPT REFERENCE
# ==============================================================================

echo ""
echo "📚 Creating script reference documentation..."

cat > SCRIPT_REFERENCE.md << 'EOF'
# AI Research Platform Scripts Reference

## Core Platform Management

### `startup-platform.sh` 🚀
**Primary startup script** - Comprehensive service startup with all phases
- ✅ UV environment support
- ✅ All services (Backend:11000, AutoGen:11001, Webhook:11002, Magentic-One:11003, Port Scanner:11010)
- ✅ Health verification
- ✅ Docker services
- ✅ Infrastructure dependencies
- **Usage:** `./startup-platform.sh`

### `stop-platform.sh` 🛑
**Complete shutdown script** - Graceful service shutdown
- ✅ Phased shutdown (monitoring → core → network → docker → cleanup)
- ✅ PID management
- ✅ Port verification
- ✅ Log rotation
- **Usage:** `./stop-platform.sh`

### `check-platform-status.sh` 📊
**Comprehensive status checker** - Full platform health check
- ✅ All service endpoints
- ✅ PID verification
- ✅ Docker containers
- ✅ Systemd services
- ✅ Platform health summary
- **Usage:** `./check-platform-status.sh`

### `manage-platform.sh` 🎛️
**User-friendly management interface** - Simple platform control
- Commands: `status`, `start`, `stop`, `restart`, `logs`, `backup`, `restore`
- **Usage:** `./manage-platform.sh status`

## Configuration Management

### `validate-config.sh` ✅
**Configuration validation** - Runs every 15 minutes via cron
- Port configuration checking
- Service health verification
- Configuration snapshots
- **Usage:** Automatic via cron

### `protect-config.sh` 🔒
**Configuration protection** - Prevents unauthorized changes
- File protection mechanisms
- Backup validation
- **Usage:** `./protect-config.sh`

### `fix-configuration-drift.sh` 🔧
**Configuration drift fix** - Solves reboot configuration issues
- Fixes systemd conflicts
- Consolidates startup systems
- **Usage:** `./fix-configuration-drift.sh`

### `switch-ai-provider.sh` 🔄
**AI provider switching** - Switch between OpenAI/Azure
- Configuration backup
- Provider switching
- Health testing
- **Usage:** `./switch-ai-provider.sh openai`

## Backup & Recovery

### `backup-configs.sh` 💾
**Manual configuration backup**
- Creates timestamped backups
- **Usage:** `./backup-configs.sh`

### `backup-configs-auto.sh` ⏰
**Automated backup** - Runs every 6 hours via cron
- **Usage:** Automatic via cron

### `restore-config.sh` 🔄
**Configuration restoration**
- **Usage:** `./restore-config.sh [backup_name]`

### `emergency-reset.sh` 🚨
**Emergency platform reset**
- Resets to default configuration
- **Usage:** `./emergency-reset.sh`

## Monitoring

### `health-monitor.sh` 🏥
**Continuous health monitoring**
- Service health checks
- Auto-recovery
- **Usage:** Runs in background

### `file-monitor.sh` 👁️
**Configuration file monitoring**
- Watches for configuration changes
- **Usage:** Runs in background

## Deployment

### `deploy.sh` 🚀
**Deployment automation**
- Git pull and build
- Service restart
- **Usage:** `./deploy.sh`

## Port Assignments

- **Backend API:** 11000
- **AutoGen Studio:** 11001  
- **Webhook Server:** 11002
- **Magentic-One:** 11003
- **Port Scanner:** 11010
- **Nginx Proxy Manager:** 11080-11082
- **Ollama:** 11434

## Quick Commands

```bash
# Start platform
./startup-platform.sh

# Check status
./check-platform-status.sh

# Stop platform  
./stop-platform.sh

# User-friendly management
./manage-platform.sh status
./manage-platform.sh start
./manage-platform.sh logs autogen-studio

# Fix configuration issues
./fix-configuration-drift.sh

# Backup configuration
./backup-configs.sh
```
EOF

echo "   ✅ Created SCRIPT_REFERENCE.md"

# ==============================================================================
# SUMMARY
# ==============================================================================

echo ""
echo "🎉 CLEANUP COMPLETE!"
echo "==================="

echo ""
echo "📊 CLEANUP SUMMARY:"
echo "   🗑️ Archived: 7 redundant scripts"
echo "   ✅ Kept: 15 essential scripts"
echo "   📚 Created: SCRIPT_REFERENCE.md"

echo ""
echo "📁 ARCHIVED SCRIPTS:"
ls -la scripts-archive/ 2>/dev/null || echo "   (No scripts to archive)"

echo ""
echo "✅ CURRENT ESSENTIAL SCRIPTS:"
echo "   🏠 Platform: startup-platform.sh, stop-platform.sh, check-platform-status.sh, manage-platform.sh"
echo "   🔧 Config: validate-config.sh, protect-config.sh, fix-configuration-drift.sh, switch-ai-provider.sh"  
echo "   💾 Backup: backup-configs.sh, backup-configs-auto.sh, restore-config.sh, emergency-reset.sh"
echo "   📊 Monitor: health-monitor.sh, file-monitor.sh"
echo "   🚀 Deploy: deploy.sh"

echo ""
echo "📖 VIEW REFERENCE: cat SCRIPT_REFERENCE.md"
echo "🚀 START PLATFORM: ./startup-platform.sh"
echo "📊 CHECK STATUS: ./check-platform-status.sh"