# AI Research Platform - Deployment Strategy Guide

## 🎯 **Overview**

The AI Research Platform now supports **4 distinct deployment strategies** to accommodate different environments and requirements:

1. **🏢 Production SSL Deployment** - Full nginx SSL termination with Tailscale certificates
2. **🔄 Containerized Full Stack** - Complete containerization with Caddy reverse proxy  
3. **⚡ Development Quick Start** - Core Chat Copilot services for development
4. **🖥️ Hybrid Deployment** - Mix of containerized and host-based services

## 📋 **Deployment Options Comparison**

| Deployment Type | Use Case | SSL | Complexity | Startup Time |
|----------------|----------|-----|------------|--------------|
| **Production SSL** | Production, secure access | ✅ Nginx + Tailscale | Medium | ~2 minutes |
| **Containerized Full** | Complete isolation | ✅ Caddy auto-HTTPS | High | ~5 minutes |
| **Development** | Quick testing | ❌ HTTP only | Low | ~30 seconds |
| **Hybrid** | Custom setup | ⚠️ Optional | Medium | ~3 minutes |

## 🚀 **Quick Start Commands**

### Production SSL Deployment (Recommended)
```bash
# Start complete SSL platform
./start-ssl-platform.sh

# Access at: https://100.123.10.72:8443/
```

### Containerized Full Stack  
```bash
# Start complete containerized platform
./start-containerized-platform.sh start-build

# Access at: https://localhost:8443/
```

### Development Quick Start
```bash
# Start core Chat Copilot only
cd docker && docker-compose up --build

# Access at: http://localhost:3000/
```

### Hybrid Deployment
```bash
# Start nginx proxy only
./start-nginx-platform.sh

# Then start services manually as needed
```

## 📁 **File Structure Overview**

### Deployment Configuration Files
```
chat-copilot/
├── docker-compose-ssl.yml          # Production SSL deployment
├── docker-compose-full-stack.yml   # Complete containerization  
├── docker-compose-nginx.yml        # Nginx proxy only
├── docker/docker-compose.yaml      # Core Chat Copilot
├── start-ssl-platform.sh          # SSL deployment script
├── start-containerized-platform.sh # Full containerization script
├── start-nginx-platform.sh        # Nginx proxy script
└── nginx-ssl.conf                  # Nginx SSL configuration
```

### Service Discovery Files
```
webapp/public/                      # Source HTML files
├── applications.html               # Service directory
├── control-panel.html             # Management dashboard
└── index.html                     # Main landing page

webapi/wwwroot/                     # Served HTML files (synced)
├── applications.html               # Enhanced with URL rewriting
├── control-panel.html             # Enhanced with dynamic patching
└── index.html                     # Production-ready version
```

## 🏗️ **Architecture Diagrams**

### Production SSL Architecture
```
Internet/Tailscale
       ↓
  nginx:8443 (SSL)
       ↓
┌─────────────────────────────────────┐
│ OpenWebUI:11880  SearXNG:11021     │
│ Perplexica:11020  Chat:3000/3080   │
│ AutoGen:11001  VS Code:57081       │
│ Port Scanner:11010  Ollama:11434   │
└─────────────────────────────────────┘
```

### Containerized Full Stack Architecture
```
Internet
    ↓
Caddy:8443 (Auto-HTTPS)
    ↓
┌─────────────────────────────────────┐
│         Docker Network              │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │ Backend │ │Frontend │ │AutoGen  │ │
│ │ :3080   │ │ :3000   │ │ :11001  │ │
│ └─────────┘ └─────────┘ └─────────┘ │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │Webhook  │ │Scanner  │ │Magentic │ │
│ │ :11002  │ │ :11010  │ │ :11003  │ │
│ └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────┘
```

## 🔧 **Configuration Details**

### Environment Variables Required
```bash
# Core API Keys
AZURE_OPENAI_API_KEY=your_azure_key
OPENAI_API_KEY=your_openai_key

# Database Configuration  
POSTGRES_PASSWORD=secure_password
QDRANT_API_KEY=chat-copilot

# Security
CODE_SERVER_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret
```

### Port Allocation Strategy
```
Core Services:
- Frontend: 3000
- Backend API: 3080, 11000
- Memory Pipeline: 3280

External Services:
- OpenWebUI: 11880
- AutoGen Studio: 11001
- Webhook Server: 11002
- Magentic-One: 11003
- Port Scanner: 11010
- Perplexica: 11020
- SearXNG: 11021
- Ollama: 11434
- VS Code Web: 57081

Proxy Ports:
- HTTP: 80
- HTTPS/SSL: 443, 8443, 10443
```

### Network Configuration
```yaml
networks:
  ai-platform:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

# Service IPs:
# Caddy: 172.20.0.10
# Backend: 172.20.0.20  
# Frontend: 172.20.0.30
# AutoGen: 172.20.0.40
```

## 🗺️ **Complete Service Directory**

### Production Service URLs (SSL Nginx Proxy)
```
# Core Platform Services
https://100.123.10.72:8443/hub                → Control Panel Dashboard
https://100.123.10.72:8443/applications.html  → Applications Directory
https://100.123.10.72:8443/copilot/          → Chat Copilot Frontend (→3000)
https://100.123.10.72:8443/copilot/api/      → Chat Copilot Backend API (→3080)

# AI & Automation Services  
https://100.123.10.72:8443/autogen/          → AutoGen Studio (→11001)
https://100.123.10.72:8443/magentic/         → Magentic-One (→11003)
https://100.123.10.72:8443/webhook/          → Webhook Server (→11002)
https://100.123.10.72:8443/ollama-api/       → Ollama LLM API (→11434)

# Search & Discovery Services
https://100.123.10.72:8443/perplexica/       → Perplexica AI Search (→11020)
https://100.123.10.72:8443/searxng/          → SearXNG Search Engine (→11021)

# Network & Management Services
https://100.123.10.72:8443/portscanner/      → Port Scanner Dashboard (→11010)
https://100.123.10.72:8443/nginx/            → Nginx Manager (→11080)
https://100.123.10.72:8443/gateway-http/     → HTTP Gateway (→11081)
https://100.123.10.72:8443/gateway-https/    → HTTPS Gateway (→11082)
https://100.123.10.72:8443/fortinet/         → Fortinet Manager (→3001)
https://100.123.10.72:8443/bacula/           → Bacula Backup System (→8081)
https://100.123.10.72:8443/vscode/           → VS Code Web IDE (→57081)
```

### Service Categories
| Category | Services | Description |
|----------|----------|-------------|
| **🎯 Core Platform** | Control Panel, Applications Hub, Chat Copilot | Main platform interface and AI chat |
| **🤖 AI Services** | AutoGen Studio, Magentic-One, Ollama API | Multi-agent AI and local LLM services |
| **🔍 Search Services** | Perplexica, SearXNG | AI-powered and privacy-focused search |
| **🔧 Management** | Port Scanner, Nginx Manager, Fortinet, Bacula | Network and system management tools |
| **🌐 Gateways** | HTTP Gateway, HTTPS Gateway, Webhook Server | Traffic routing and automation |
| **💻 Development** | VS Code Web | Cloud-based development environment |

## 🛠️ **Service Management**

### Health Check Commands
```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test SSL endpoints
curl -k https://100.123.10.72:8443/health
curl -k https://100.123.10.72:8443/copilot/healthz

# Check service logs
docker logs nginx-ssl
docker logs ai-platform-caddy
docker logs chat-copilot-backend
```

### Restart Individual Services
```bash
# Restart proxy
docker restart nginx-ssl
docker restart ai-platform-caddy

# Restart backend services
docker restart chat-copilot-backend
docker restart chat-copilot-frontend

# Restart external services
docker restart openwebui
docker restart autogen-studio
```

## 🔍 **Troubleshooting Guide**

### Common Issues and Solutions

#### Platform Won't Start
```bash
# Check Docker status
systemctl status docker
docker version

# Check port conflicts
sudo lsof -i :8443
sudo lsof -i :443

# View startup logs
./start-ssl-platform.sh 2>&1 | tee startup.log
```

#### SSL Certificate Issues
```bash
# Verify certificate files exist
ls -la /etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt
ls -la /etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key

# Test nginx config
docker exec nginx-ssl nginx -t

# Reload nginx config
docker exec nginx-ssl nginx -s reload
```

#### Service Not Accessible
```bash
# Check service is running
docker ps | grep service-name

# Check network connectivity
docker network inspect ai-platform

# Test internal connectivity
docker exec nginx-ssl wget -qO- http://openwebui:8080/health
```

#### HTML Files Out of Sync
```bash
# Sync files from source to served
cp webapp/public/*.html webapi/wwwroot/

# Restart containers using the files
docker restart nginx-ssl
docker restart ai-platform-caddy
```

## 🎯 **Recommended Deployment Flow**

### For Production Use
1. **Start with SSL deployment**: `./start-ssl-platform.sh`
2. **Verify core services**: Check applications.html dashboard
3. **Add additional services**: Start Chat Copilot backend/frontend as needed
4. **Monitor and maintain**: Use control panel for management

### For Development
1. **Quick start**: `cd docker && docker-compose up --build`
2. **Access locally**: http://localhost:3000
3. **Add services incrementally**: Use individual docker-compose files
4. **Iterate rapidly**: Hot reload enabled for frontend

### For Custom Deployments  
1. **Choose base**: Start with appropriate docker-compose file
2. **Customize configuration**: Edit environment variables and ports
3. **Test incrementally**: Start services one by one
4. **Document changes**: Update this guide with customizations

## 📈 **Performance Optimization**

### Resource Allocation
```yaml
# High-performance settings for containers
services:
  chat-copilot-backend:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
    environment:
      - DOTNET_gcServer=1
      - DOTNET_gcConcurrent=1
```

### Monitoring and Scaling
```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Scale services (Docker Swarm mode)
docker service scale chat-copilot-backend=3

# Load balancing with nginx
# See nginx-ssl.conf for upstream configuration
```

## 🔐 **Security Hardening**

### Production Security Checklist
- ✅ SSL/TLS encryption enabled
- ✅ Security headers configured
- ✅ Network segmentation (Docker networks)
- ✅ Secret management (environment variables)
- ⚠️ Container security scanning needed
- ⚠️ Log aggregation setup needed
- ⚠️ Backup and disaster recovery needed

### Recommended Security Enhancements
```bash
# Enable Docker security scanning
docker scout cves chat-copilot-backend

# Set up log rotation
sudo logrotate -f /etc/logrotate.d/docker

# Configure firewall
sudo ufw allow 8443/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable
```

---

**🎉 Your AI Research Platform now supports flexible, production-ready deployment with minimal friction!**

Choose your deployment strategy based on your needs and follow the appropriate startup script.