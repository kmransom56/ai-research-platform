# AI Research Platform - Backup & Restore Guide

## 🚀 Quick Commands

### After Reboot - One Command Fix:
```bash
cd /home/keith/chat-copilot
./scripts/quick-restore.sh
```

### Create New Backup:
```bash
./scripts/backup-working-config.sh
```

### Check Platform Health:
```bash
./scripts/check-platform-health.sh
```

## 📁 Backup System

### Automatic Backup
- **Location**: `/home/keith/chat-copilot/config-backups-working/`
- **Latest**: Symlink at `config-backups-working/latest/`
- **Auto-restore**: Enabled on boot via systemd service

### What's Backed Up:
- ✅ Nginx configurations (`/etc/nginx/sites-available/ai-hub.conf`)
- ✅ SSL certificates with proper permissions
- ✅ Docker container states and configurations
- ✅ Application configs (`appsettings.json`, `.env`)
- ✅ Service startup commands
- ✅ Ollama model list
- ✅ Port mappings and process states

## 🔧 Restoration Options

### 1. Automatic (Enabled)
The system will automatically restore on boot via `ai-platform-restore.service`.

### 2. Manual Restore
```bash
# Quick restore
./scripts/quick-restore.sh

# Or run specific backup
cd config-backups-working/20250622-193657
./quick-restore.sh
```

### 3. Step-by-Step Manual Restore
```bash
# 1. Start backend
cd webapi && dotnet run --urls http://0.0.0.0:11000 &

# 2. Start frontend  
cd webapp && REACT_APP_BACKEND_URI=http://100.123.10.72:11000/ yarn start &

# 3. Start Docker containers
docker start $(docker ps -aq --filter "status=exited")

# 4. Fix SSL certificates
sudo cp config-backups-working/latest/ssl/tailscale/* /etc/ssl/tailscale/
sudo chmod 644 /etc/ssl/tailscale/*.crt
sudo chmod 640 /etc/ssl/tailscale/*.key
sudo chgrp www-data /etc/ssl/tailscale/*.key

# 5. Restore nginx config
sudo cp config-backups-working/latest/nginx/sites-available/ai-hub.conf /etc/nginx/sites-available/
sudo systemctl reload nginx
```

## 📊 Service Management

### Systemd Auto-Restore Service
```bash
# Check status
sudo systemctl status ai-platform-restore

# Manual restore
sudo systemctl start ai-platform-restore

# Disable auto-restore
sudo systemctl disable ai-platform-restore

# View logs
journalctl -u ai-platform-restore -f
```

### Health Monitoring
```bash
# Quick health check
./scripts/check-platform-health.sh

# Check specific services
curl -k https://100.123.10.72:10443/hub
curl -k https://100.123.10.72:10443/openwebui/
curl -k https://100.123.10.72:10443/neo4j/
```

## 🌐 Working Service URLs

After restore, these URLs should work:
- **Main Hub**: https://100.123.10.72:10443/hub
- **OpenWebUI**: https://100.123.10.72:10443/openwebui/
- **Neo4j Browser**: https://100.123.10.72:10443/neo4j/
- **Chat Copilot**: https://100.123.10.72:10443/copilot/
- **Fortinet Manager**: https://100.123.10.72:10443/fortinet/
- **Perplexica AI**: https://100.123.10.72:10443/perplexica/
- **Ollama API**: https://100.123.10.72:10443/ollama-api/

## 🔍 Troubleshooting

### If Services Don't Start:
1. Check logs: `journalctl -u ai-platform-restore -n 50`
2. Run health check: `./scripts/check-platform-health.sh`
3. Manual restore: `./scripts/quick-restore.sh`

### If Nginx Fails:
1. Test config: `sudo nginx -t`
2. Check certificates: `ls -la /etc/ssl/tailscale/`
3. Restore from backup: `sudo cp config-backups-working/latest/nginx/sites-available/ai-hub.conf /etc/nginx/sites-available/`

### If SSL Issues:
```bash
sudo cp config-backups-working/latest/ssl/tailscale/* /etc/ssl/tailscale/
sudo chmod 644 /etc/ssl/tailscale/*.crt
sudo chmod 640 /etc/ssl/tailscale/*.key
sudo chgrp www-data /etc/ssl/tailscale/*.key
sudo systemctl reload nginx
```

## 💡 Tips

- **Always create a backup** before making changes: `./scripts/backup-working-config.sh`
- **Check health regularly**: `./scripts/check-platform-health.sh`
- **Monitor auto-restore**: `journalctl -u ai-platform-restore -f`
- **Backup location**: All backups saved to `config-backups-working/`
- **Latest backup**: Always accessible via `config-backups-working/latest/`

## 🎯 Post-Reboot Checklist

1. ✅ Auto-restore should run automatically
2. ✅ Check health: `./scripts/check-platform-health.sh`
3. ✅ Verify URLs work (all should return 200 or 301)
4. ✅ Check Ollama models: `ollama list`
5. ✅ Verify Docker containers: `docker ps`

**If anything fails, simply run: `./scripts/quick-restore.sh`**