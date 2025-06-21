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
