# AI Research Platform - Comprehensive Deployment Guide

## 🎯 **Current Status: NGINX SSL Platform ACTIVE**

Your AI Research Platform is successfully running with **nginx SSL termination** using Tailscale certificates.

### 🌐 **Primary Access URLs**

- **Main Platform**: https://100.123.10.72:8443/applications.html
- **Control Panel**: https://100.123.10.72:8443/hub
- **Tailscale Access**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/

## 🚀 **Quick Start Commands**

### Start Platform
```bash
./start-ssl-platform.sh
```

### Check Status  
```bash
docker ps
curl -k https://100.123.10.72:8443/health
```

### Stop Platform
```bash
docker stop nginx-ssl openwebui searxng perplexica
```

## 📋 **Complete Service Directory**

### ✅ **Active Services (Working)**
| Service | URL | Status | Description |
|---------|-----|--------|-------------|
| **Applications Directory** | https://100.123.10.72:8443/applications.html | ✅ Active | Main platform dashboard |
| **Control Panel** | https://100.123.10.72:8443/hub | ✅ Active | Management interface |
| **OpenWebUI** | https://100.123.10.72:8443/openwebui/ | ✅ Active | Primary LLM interface |
| **SearXNG** | https://100.123.10.72:8443/searxng/ | ✅ Active | Privacy search engine |
| **Perplexica** | https://100.123.10.72:8443/perplexica/ | ✅ Active | AI-powered web search |

### 🔄 **Configurable Services (Need Manual Start)**
| Service | URL | Status | Start Command |
|---------|-----|--------|---------------|
| **Chat Copilot** | https://100.123.10.72:8443/copilot/ | 🔄 Manual | `cd webapi && dotnet run` + `cd webapp && yarn start` |
| **AutoGen Studio** | https://100.123.10.72:8443/autogen/ | 🔄 Manual | See AutoGen setup guide |
| **VS Code Web** | https://100.123.10.72:8443/vscode/ | 🔄 Manual | See VS Code setup guide |
| **Magentic-One** | https://100.123.10.72:8443/magentic/ | 🔄 Manual | See Magentic-One setup guide |

### 🔧 **Backend Services**
| Service | URL | Description |
|---------|-----|-------------|
| **Health Check** | https://100.123.10.72:8443/copilot/healthz | Backend API health |
| **Port Scanner** | https://100.123.10.72:8443/portscanner/ | Network monitoring |
| **Fortinet Manager** | https://100.123.10.72:8443/fortinet/ | Network management |

## 🔧 **Architecture Overview**

### Current Setup: **NGINX SSL Termination**
- **SSL Certificates**: Tailscale certificates from `/etc/ssl/`
- **Reverse Proxy**: nginx container handling SSL and routing
- **Port**: 8443 (port 443 was in use)
- **Security**: HSTS headers, TLS 1.2/1.3

### Network Layout
```
Internet/Tailscale → nginx:8443 (SSL termination) → Internal Services
                          ↓
    ┌─────────────────────────────────────────────────────────┐
    │ OpenWebUI:11880  SearXNG:11021  Perplexica:11020      │
    │ Chat Copilot:11000/3000  AutoGen:11001  VS Code:57081  │
    │ Port Scanner:11010  Fortinet:3001  Ollama:11434        │
    └─────────────────────────────────────────────────────────┘
```

## 📁 **Key File Locations**

### Configuration Files
- **Nginx Config**: `/home/keith/chat-copilot/nginx-ssl.conf`
- **Startup Script**: `/home/keith/chat-copilot/start-ssl-platform.sh`
- **Docker Compose**: `/home/keith/chat-copilot/docker-compose-ssl.yml`
- **HTML Files**: `/home/keith/chat-copilot/webapp/public/`

### SSL Certificates
- **Certificate**: `/etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt`
- **Private Key**: `/etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key`

### Platform Documentation
- **This Guide**: `/home/keith/chat-copilot/COMPREHENSIVE_DEPLOYMENT_GUIDE.md`
- **Claude Instructions**: `/home/keith/chat-copilot/CLAUDE.md`
- **Project Overview**: `/home/keith/chat-copilot/docs/project-meta/README.md`

## 🔄 **Auto-Start Configuration**

### Systemd Service Setup
```bash
# Install auto-start service
sudo cp /home/keith/chat-copilot/ai-platform-ssl.service /etc/systemd/system/
sudo systemctl enable ai-platform-ssl.service
sudo systemctl start ai-platform-ssl.service

# Check service status
sudo systemctl status ai-platform-ssl.service
```

### Manual Service Management
```bash
# Start platform
./start-ssl-platform.sh

# Stop all containers
docker stop $(docker ps -q)

# View logs
docker logs nginx-ssl
docker logs openwebui
```

## 🛠️ **Starting Additional Services**

### Chat Copilot Backend + Frontend
```bash
# Terminal 1: Backend API
cd /home/keith/chat-copilot/webapi
dotnet run --urls http://0.0.0.0:11000

# Terminal 2: Frontend  
cd /home/keith/chat-copilot/webapp
yarn install
yarn start
```

### AutoGen Studio
```bash
# Activate environment and start
cd /home/keith/chat-copilot/python
pip install -e .
autogenstudio ui --port 11001 --host 0.0.0.0
```

### VS Code Web
```bash
# Start VS Code server
code-server --bind-addr 0.0.0.0:57081 --auth none /home/keith/chat-copilot
```

## 🔍 **Troubleshooting**

### Common Issues

#### Platform Won't Start
```bash
# Check Docker status
docker ps -a

# Check nginx logs
docker logs nginx-ssl

# Restart platform
./start-ssl-platform.sh
```

#### SSL Certificate Issues
```bash
# Check certificate files
ls -la /etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.*
ls -la /etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.*

# Test nginx config
docker exec nginx-ssl nginx -t
```

#### Service Links Broken
```bash
# Check HTML file sync
diff /home/keith/chat-copilot/webapp/public/applications.html /home/keith/chat-copilot/webapi/wwwroot/applications.html

# Re-sync files
cp /home/keith/chat-copilot/webapp/public/*.html /home/keith/chat-copilot/webapi/wwwroot/
```

#### Port Conflicts
```bash
# Check what's using ports
sudo lsof -i :443
sudo lsof -i :8443
sudo lsof -i :11000

# Kill conflicting processes if needed
sudo fuser -k 8443/tcp
```

### Service-Specific Troubleshooting

#### OpenWebUI Issues
- **URL**: https://100.123.10.72:8443/openwebui/
- **Container**: `openwebui`
- **Logs**: `docker logs openwebui`

#### SearXNG Issues  
- **URL**: https://100.123.10.72:8443/searxng/
- **Container**: `searxng`
- **Logs**: `docker logs searxng`

#### Perplexica Issues
- **URL**: https://100.123.10.72:8443/perplexica/
- **Container**: `perplexica`
- **Logs**: `docker logs perplexica`

## 📈 **Performance Optimization**

### High-Performance GPU Setup
For systems with 72GB+ VRAM, see: `/home/keith/chat-copilot/docs/setup-guides/GPU_OPTIMIZATION_72GB.md`

### Resource Monitoring
```bash
# System resources
htop
nvidia-smi

# Docker resources
docker stats

# Network connections
netstat -tulpn | grep :8443
```

## 🔐 **Security Considerations**

### Current Security Features
- ✅ SSL/TLS termination with Tailscale certificates
- ✅ HSTS security headers
- ✅ Tailscale network encryption
- ✅ X-Frame-Options and security headers
- ✅ Access restricted to Tailscale network

### Recommended Additional Security
- Set up firewall rules for non-Tailscale access
- Regular certificate renewal monitoring
- Container security scanning
- Log monitoring for suspicious activity

## 📚 **Additional Documentation**

### Component-Specific Guides
- **AutoGen Studio Setup**: `/home/keith/chat-copilot/docs/setup-guides/AUTOGEN_STUDIO_SETUP.md`
- **VS Code Web Setup**: `/home/keith/chat-copilot/docs/setup-guides/VSCODE_WEB_SETUP.md`
- **Magentic-One Setup**: `/home/keith/chat-copilot/docs/setup-guides/MAGENTIC_ONE_SETUP.md`
- **Webhook Setup**: `/home/keith/chat-copilot/docs/setup-guides/WEBHOOK_SETUP.md`

### Troubleshooting Guides
- **Configuration Issues**: `/home/keith/chat-copilot/docs/troubleshooting/CONFIGURATION_DRIFT_SOLUTION.md`
- **Port Configuration**: `/home/keith/chat-copilot/docs/troubleshooting/PORT_CONFIGURATION_SUMMARY.md`
- **Restart Verification**: `/home/keith/chat-copilot/docs/troubleshooting/RESTART_VERIFICATION_SUMMARY.md`

### Project Documentation
- **Complete Project Overview**: `/home/keith/chat-copilot/docs/project-meta/README.md`
- **Claude AI Instructions**: `/home/keith/chat-copilot/CLAUDE.md`
- **Business Partnership Guide**: `/home/keith/chat-copilot/docs/business-docs/BUSINESS_PARTNERSHIP_GUIDE.md`

## 🎉 **Success Indicators**

Your platform is working correctly when:

1. ✅ **Main page loads**: https://100.123.10.72:8443/applications.html
2. ✅ **Control panel accessible**: https://100.123.10.72:8443/hub
3. ✅ **OpenWebUI responsive**: Can create and manage conversations
4. ✅ **SearXNG searches**: Can perform web searches
5. ✅ **Perplexica AI search**: Can perform AI-powered searches
6. ✅ **SSL certificate valid**: No browser security warnings
7. ✅ **All links working**: No 404 errors on service links

## 🔄 **Migration Notes**

### From Caddy to Nginx
Your platform has been migrated from Caddy to nginx SSL termination for better stability. The Caddy configuration files remain in `/home/keith/chat-copilot/docker-configs/` but are no longer used.

### File Synchronization
HTML files are automatically synchronized across:
- `/home/keith/chat-copilot/webapp/public/` (source)
- `/home/keith/chat-copilot/webapp/build/` (build output)
- `/home/keith/chat-copilot/webapi/wwwroot/` (served files)

All locations contain identical, properly configured files with nginx reverse proxy paths.

---

**🎯 Your AI Research Platform is ready and stable! The nginx SSL setup should survive reboots and provide reliable access to all services.**