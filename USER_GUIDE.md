# AI Research Platform - User Guide

## 🚀 Quick Start

**For new users - One command setup:**
```bash
./manage-platform.sh start
```

**Check if everything is working:**
```bash
./manage-platform.sh status
```

**If something breaks:**
```bash
./manage-platform.sh emergency-reset
```

## 🛡️ Configuration Drift Prevention

This platform now has **automatic protection** against configuration drift:

### ✅ What's Protected
- ✅ **Automatic validation** every 15 minutes
- ✅ **Health monitoring** with auto-restart
- ✅ **Configuration backups** every 6 hours
- ✅ **File monitoring** for unauthorized changes
- ✅ **Emergency reset** to known good state

### 🔧 Management Commands

| Command | Purpose |
|---------|---------|
| `./manage-platform.sh start` | Start all services |
| `./manage-platform.sh stop` | Stop all services |
| `./manage-platform.sh status` | Check service health |
| `./manage-platform.sh validate` | Check configuration |
| `./manage-platform.sh logs [service]` | View logs |
| `./manage-platform.sh backup` | Create backup |
| `./manage-platform.sh restore latest` | Restore latest backup |
| `./manage-platform.sh emergency-reset` | Reset everything |

## 🌐 Service Access Points

After starting the platform, access these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Control Panel** | http://100.123.10.72:11000/control-panel.html | Main dashboard |
| **Chat Copilot** | http://100.123.10.72:11000 | AI chat interface |
| **Port Scanner** | http://100.123.10.72:11010 | Network port scanning with nmap |
| **Nginx Proxy** | http://100.123.10.72:11080 | Proxy manager (admin@example.com/changeme) |
| **AutoGen Studio** | http://100.123.10.72:8085 | Multi-agent AI studio |
| **Webhook Server** | http://100.123.10.72:11002/health | Deployment automation |

## 🔍 Troubleshooting

### Problem: Services won't start
**Solution:**
```bash
./manage-platform.sh validate
./manage-platform.sh restart
```

### Problem: Port Scanner shows wrong data
**Solution:**
```bash
./validate-config.sh
./restart-port-scanner.sh
```

### Problem: Configuration keeps changing
**Solutions:**
1. **Enable monitoring:** `./manage-platform.sh monitor-enable`
2. **Check protection:** `./protect-config.sh`
3. **Emergency reset:** `./manage-platform.sh emergency-reset`

### Problem: Can't access services
**Check:**
1. `./manage-platform.sh status` - Are services running?
2. `netstat -tlnp | grep 11000` - Are ports listening?
3. `./manage-platform.sh logs backend` - Check backend logs

## 🚨 Emergency Procedures

### If Everything Breaks
```bash
# Nuclear option - resets everything
./manage-platform.sh emergency-reset
```

### If Configuration Drift Occurs
```bash
# Restore from backup
./manage-platform.sh restore latest

# Or validate and fix
./validate-config.sh
```

### If Services Keep Dying
```bash
# Enable automatic monitoring
./manage-platform.sh monitor-enable

# Check what's killing them
./manage-platform.sh logs health-monitor
```

## 📊 Monitoring and Maintenance

### Automatic Systems
- **Health Monitor:** Checks services every 60 seconds, auto-restarts if needed
- **Config Validation:** Runs every 15 minutes via cron
- **Auto Backups:** Creates backups every 6 hours
- **File Monitoring:** Watches for unauthorized config changes

### Manual Monitoring
```bash
# Check overall health
./manage-platform.sh status

# View service logs
./manage-platform.sh logs [backend|webhook|port-scanner|health-monitor]

# Check recent backups
ls -la config-backups-auto/

# View health report
cat health-report.json
```

## 🔧 Advanced Configuration

### Port Configuration
All services use the **11000-11200** port range to avoid conflicts:
- Backend: 11000
- Webhook: 11002  
- Port Scanner: 11010
- Nginx Proxy: 11080-11082
- AutoGen Studio: 8085 (external requirement)

### Configuration Files
| File | Purpose | Auto-Protected |
|------|---------|----------------|
| `webapp/.env` | Frontend API endpoint | ✅ |
| `webapi/appsettings.json` | Backend configuration | ✅ |
| `port-scanner-material-ui/src/index.html` | Port scanner frontend | ✅ |
| `startup-platform.sh` | Service startup | ✅ |

## 📁 File Structure
```
/home/keith/chat-copilot/
├── manage-platform.sh          # Main management interface
├── validate-config.sh          # Configuration validator
├── health-monitor.sh           # Continuous health monitoring
├── protect-config.sh           # Configuration protection setup
├── emergency-reset.sh          # Emergency reset
├── backup-configs-auto.sh      # Automatic backups
├── restore-config.sh           # Configuration restore
├── logs/                       # All system logs
├── config-backups-auto/        # Automatic configuration backups
├── config-snapshots/           # Validation snapshots
└── pids/                       # Process ID files
```

## 💡 Tips for Users

1. **Always use manage-platform.sh** - Don't start services manually
2. **Check status first** - Run `./manage-platform.sh status` before reporting issues
3. **Enable monitoring** - Run `./manage-platform.sh monitor-enable` for automatic recovery
4. **Regular backups** - Automatic backups run every 6 hours, but you can create manual ones
5. **Emergency reset** - When in doubt, use `./manage-platform.sh emergency-reset`

## 🆘 Getting Help

1. **Check logs:** `./manage-platform.sh logs [service]`
2. **Validate config:** `./manage-platform.sh validate`
3. **View status:** `./manage-platform.sh status`
4. **Emergency reset:** `./manage-platform.sh emergency-reset`

**Log locations:**
- System logs: `/home/keith/chat-copilot/logs/`
- Service status: `health-report.json`
- Configuration validation: `logs/config-validation.log`

---

## 🎯 For Developers

### Adding New Services
1. Add to `startup-platform.sh`
2. Add health check to `health-monitor.sh`
3. Add to `manage-platform.sh status` function
4. Use ports in 11000-11200 range

### Configuration Protection
- All critical configs are auto-backed up
- File monitoring detects unauthorized changes
- Validation runs every 15 minutes
- Emergency reset available for quick recovery

### Debugging
```bash
# Enable debug mode
export DEBUG=1
./manage-platform.sh start

# Monitor file changes
./file-monitor.sh

# Manual validation
./validate-config.sh
```