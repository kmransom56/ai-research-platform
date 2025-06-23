# AI Research Platform - Recovery Guide

## Quick Recovery After Reboot

### 1. One-Command Restore
```bash
cd /home/keith/chat-copilot
./config-backups-working/latest/quick-restore.sh
```

### 2. Check Status
```bash
./check-platform-status.sh
```

### 3. If Issues Persist
```bash
# Check logs
tail -f /tmp/backend.log /tmp/frontend.log

# Restart individual services
cd webapi && dotnet run --urls http://0.0.0.0:11000 &
cd webapp && yarn start &
```

## Manual Recovery Steps

### Backend (Chat Copilot API)
```bash
cd /home/keith/chat-copilot/webapi
dotnet run --urls http://0.0.0.0:11000 > /tmp/backend.log 2>&1 &
```

### Frontend (React App)
```bash
cd /home/keith/chat-copilot/webapp
REACT_APP_BACKEND_URI=http://100.123.10.72:11000/ yarn start > /tmp/frontend.log 2>&1 &
```

### SSL Certificates
```bash
sudo mkdir -p /etc/ssl/tailscale
sudo cp config-backups-working/latest/ssl/tailscale/* /etc/ssl/tailscale/
sudo chmod 644 /etc/ssl/tailscale/*.crt
sudo chmod 640 /etc/ssl/tailscale/*.key
sudo chgrp www-data /etc/ssl/tailscale/*.key
```

### Nginx Configuration
```bash
sudo cp config-backups-working/latest/nginx/sites-available/ai-hub.conf /etc/nginx/sites-available/
sudo nginx -t && sudo systemctl reload nginx
```

## Critical Files Backed Up

### Application Configuration
- `webapi/appsettings.json` - Backend API configuration with OpenAI settings
- `webapp/.env` - Frontend environment with backend URI

### Network Configuration  
- `/etc/nginx/sites-available/ai-hub.conf` - Reverse proxy with ntopng support
- `/etc/ssl/tailscale/*` - SSL certificates for HTTPS

### Service States
- Running Docker containers
- Ollama model list
- Service startup commands

## Key Service URLs

- **Platform Status**: `./check-platform-status.sh`
- **Main Access**: https://100.123.10.72:10443/
- **Chat Copilot**: https://100.123.10.72:10443/copilot/
- **ntopng Monitor**: https://100.123.10.72:10443/ntopng
- **Backend Health**: http://100.123.10.72:11000/healthz

## Backup Locations

- **Latest Backup**: `/home/keith/chat-copilot/config-backups-working/latest/`
- **All Backups**: `/home/keith/chat-copilot/config-backups-working/`
- **Manual Backup**: `./scripts/backup-working-config.sh`

## Troubleshooting

### Backend 500 Errors
- Check OpenAI API key in `webapi/appsettings.json`
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check logs: `tail -f /tmp/backend.log`

### Frontend Connection Issues
- Check `webapp/.env` has correct backend URI
- Verify backend is responding: `curl http://100.123.10.72:11000/healthz`
- Check logs: `tail -f /tmp/frontend.log`

### HTTPS Issues
- Verify SSL certificates exist and have correct permissions
- Check nginx config: `sudo nginx -t`
- Reload nginx: `sudo systemctl reload nginx`

## Emergency Contacts
- Recovery script: `./config-backups-working/latest/quick-restore.sh`
- Status checker: `./check-platform-status.sh`
- Full backup: `./scripts/backup-working-config.sh`