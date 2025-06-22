# AI Research Platform - Nginx SSL Setup

## ✅ **Current Status: WORKING**

Your AI Research Platform is now running with **nginx SSL termination** using your Tailscale certificates.

### 🌐 **Access URLs:**

- **Primary HTTPS Access**: https://100.123.10.72:8443/applications.html
- **Tailscale Access**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html
- **Control Panel**: https://100.123.10.72:8443/hub
- **HTTP Redirect**: http://100.123.10.72/ → redirects to HTTPS

### 🔧 **Working Services:**

✅ **OpenWebUI**: https://100.123.10.72:8443/openwebui/
✅ **SearXNG**: https://100.123.10.72:8443/searxng/
✅ **Perplexica**: https://100.123.10.72:8443/perplexica/
🔄 **Chat Copilot**: https://100.123.10.72:8443/copilot/ (needs backend/frontend running)
🔄 **AutoGen Studio**: https://100.123.10.72:8443/autogen/ (needs service running)
🔄 **VS Code**: https://100.123.10.72:8443/vscode/ (needs service running)

### 🚀 **Management Commands:**

```bash
# Start the platform
./start-ssl-platform.sh

# Check status
docker ps
curl -k https://100.123.10.72:8443/health

# Stop platform
docker stop nginx-ssl openwebui searxng perplexica

# View logs
docker logs nginx-ssl
```

### 🔒 **SSL Configuration:**

- **Certificates**: Tailscale certificates mounted from `/etc/ssl/`
- **Protocols**: TLSv1.2, TLSv1.3
- **Port**: 8443 (port 443 was already in use by system)
- **Security Headers**: HSTS, X-Frame-Options, etc.

### ⚙️ **File Locations:**

- **Nginx Config**: `/home/keith/chat-copilot/nginx-ssl.conf`
- **HTML Files**: `/home/keith/chat-copilot/webapp/public/`
- **Startup Script**: `/home/keith/chat-copilot/start-ssl-platform.sh`
- **Docker Compose**: `/home/keith/chat-copilot/docker-compose-ssl.yml`

### 🔧 **For Auto-Start on Reboot:**

```bash
# Install systemd service
sudo cp /home/keith/chat-copilot/ai-platform-ssl.service /etc/systemd/system/
sudo systemctl enable ai-platform-ssl.service
sudo systemctl start ai-platform-ssl.service

# Check service status
sudo systemctl status ai-platform-ssl.service
```

### 🎯 **Next Steps:**

1. Start remaining services (Chat Copilot backend/frontend, AutoGen, etc.)
2. Test all service links from the applications page
3. Set up auto-start systemd service if desired

**The platform is now stable and should survive reboots with the nginx setup!**