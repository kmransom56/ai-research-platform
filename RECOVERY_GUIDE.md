# AI Research Platform Recovery Guide

This guide provides comprehensive recovery procedures for the AI Research Platform after system issues, reboots, or configuration problems.

## Quick Recovery (Most Common)

If services aren't working after a reboot or configuration issue:

```bash
# One-command recovery
./config-backups-working/latest/quick-restore.sh
```

This script:
- Restores known-good configurations
- Starts essential services (Chat Copilot backend on port 11000)
- Fixes common startup issues
- Runs automatically via `ai-platform-restore.service`

## Platform Status Check

```bash
# Check what's running
./check-platform-status.sh

# Or use the management interface
./scripts/platform-management/manage-platform.sh status
```

## Startup System v4.0

The platform now uses a simplified startup system:

### Automatic Startup
- **Service**: `ai-platform-restore.service` (enabled by default)
- **Script**: `config-backups-working/latest/quick-restore.sh`
- **Trigger**: Automatically runs on boot

### Manual Startup Options
```bash
# Preferred: Use management interface
./scripts/platform-management/manage-platform.sh start

# Alternative: Direct quick restore
./config-backups-working/latest/quick-restore.sh

# Legacy: Old startup script (deprecated)
./scripts/platform-management/startup-platform.sh
```

## Common Issues & Solutions

### 502 Bad Gateway (Hub Service)
**Cause**: Backend API not running on port 11000

**Solution**:
```bash
# Check if backend is running
curl -s http://100.123.10.72:11000/healthz

# If not running, start it
./config-backups-working/latest/quick-restore.sh
```

### Configuration Drift After Reboot
**Cause**: Multiple conflicting startup services (fixed in v4.0)

**Solution**: The new startup system eliminates this issue. If you still experience drift:
```bash
# Verify only one startup service is enabled
systemctl list-unit-files | grep ai-platform
# Should only show: ai-platform-restore.service enabled

# If other services are enabled, disable them
sudo systemctl disable ai-platform.service
sudo systemctl disable ai-platform-gateways.service
# etc.
```

### Service Port Conflicts
**Cause**: Services trying to bind to already-used ports

**Solution**:
```bash
# Kill conflicting processes
sudo pkill -f "dotnet.*webapi"
sudo pkill -f "autogenstudio"

# Restart with quick restore
./config-backups-working/latest/quick-restore.sh
```

### SSL Certificate Issues
**Cause**: Tailscale certificates missing or expired

**Solution**:
```bash
# Regenerate Tailscale certificates
./scripts/infrastructure/setup-tailscale-ssl.sh

# Verify certificate status
./scripts/infrastructure/verify-ssl-setup.sh
```

## Recovery Procedures by Scenario

### Complete System Reboot
1. **Automatic**: `ai-platform-restore.service` should start everything
2. **Manual verification**: Run `./check-platform-status.sh`
3. **If issues**: Run `./config-backups-working/latest/quick-restore.sh`

### After Configuration Changes
1. **Backup current state**: `./scripts/backup-working-config.sh`
2. **Test changes**: Verify services still work
3. **If broken**: `./config-backups-working/latest/quick-restore.sh`

### Docker Container Issues
```bash
# Stop all containers
docker stop $(docker ps -q)

# Remove problematic containers
docker container prune -f

# Restart platform
./config-backups-working/latest/quick-restore.sh
```

### Neo4j Database Issues
```bash
# Stop Neo4j
sudo pkill -f neo4j
docker stop $(docker ps -q --filter "ancestor=neo4j")

# Clear database locks (if needed)
sudo rm -f data/databases/*/database_lock
sudo rm -f genai-stack/data/databases/*/database_lock

# Restart platform
./config-backups-working/latest/quick-restore.sh
```

## Service Endpoints

Once recovered, verify these endpoints work:

### Core Services
- **Chat Copilot API**: http://100.123.10.72:11000/healthz
- **Control Panel**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub
- **Applications**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html

### AI Services
- **AutoGen Studio**: http://100.123.10.72:11001
- **Magentic-One**: http://100.123.10.72:11003
- **Ollama LLM**: http://100.123.10.72:11434/api/version

### Infrastructure
- **Port Scanner**: http://100.123.10.72:11010
- **Nginx Proxy Manager**: http://100.123.10.72:11080
- **VS Code Web**: http://100.123.10.72:57081

## Backup and Restore

### Create Backup
```bash
# Create a new backup of current working state
./scripts/backup-working-config.sh

# Backups are stored in: config-backups-working/YYYYMMDD-HHMMSS/
```

### Restore from Specific Backup
```bash
# List available backups
ls -la config-backups-working/

# Restore from specific backup
./config-backups-working/20250622-193657/quick-restore.sh
```

## Emergency Reset

If all else fails:

```bash
# Stop everything
sudo systemctl stop ai-platform-restore.service
docker stop $(docker ps -q)
sudo pkill -f "dotnet"
sudo pkill -f "autogenstudio"
sudo pkill -f "magentic"

# Wait a moment
sleep 5

# Start fresh
./config-backups-working/latest/quick-restore.sh
```

## Getting Help

1. **Check logs**: `./scripts/platform-management/manage-platform.sh logs`
2. **Platform status**: `./check-platform-status.sh`
3. **Validation**: `./scripts/config-management/validate-config.sh`

## File Locations

- **Quick Restore**: `config-backups-working/latest/quick-restore.sh`
- **Platform Logs**: `logs/`
- **Service PIDs**: `pids/`
- **Backups**: `config-backups-working/`
- **Health Check**: `check-platform-status.sh`

---

**Last Updated**: June 23, 2025 - Startup System v4.0