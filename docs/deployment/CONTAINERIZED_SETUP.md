# AI Research Platform - Fully Containerized Setup

This document describes how to run the entire AI Research Platform as a containerized application stack using Docker Compose.

## 🎯 Overview

The containerized setup provides:
- **Complete isolation** of all services
- **Consistent deployment** across environments
- **Easy scaling** and resource management
- **Simplified maintenance** and updates
- **Built-in health monitoring** and auto-recovery

## 📋 Prerequisites

### Required Software
- **Docker** 20.10+ with Docker Compose
- **Git** for repository management
- **Minimum 8GB RAM** (16GB recommended)
- **20GB available disk space**

### Network Requirements
- **Internet access** for image downloads and AI services
- **Port availability**: 80, 8443, 3000, 5432, 6333, 11000-11999, 15672, 57081
- **Optional**: Tailscale for secure external access

## 🚀 Quick Start

### 1. Clone and Configure
```bash
git clone https://github.com/kmransom56/ai-research-platform.git
cd ai-research-platform

# Copy environment template
cp .env.template .env

# Edit configuration (required!)
nano .env
```

### 2. Configure Environment Variables
Edit `.env` file with your settings:

```bash
# Required: Azure OpenAI Configuration
AZURE_OPENAI_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/

# Required: Database Passwords
POSTGRES_PASSWORD=secure-postgres-password
RABBITMQ_PASSWORD=secure-rabbitmq-password

# Required: Service Security
OPENWEBUI_SECRET_KEY=your-openwebui-secret-key
VSCODE_PASSWORD=your-vscode-password
```

### 3. Start the Platform
```bash
# Start with automatic image building
./start-containerized-platform.sh start-build

# Or just start (if images already built)
./start-containerized-platform.sh start
```

### 4. Access Your Platform
After startup (2-3 minutes), access via:
- **Main Hub**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443
- **Applications**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/applications.html
- **Control Panel**: https://ubuntuaicodeserver-1.tail5137b4.ts.net:8443/hub

## 🏗️ Architecture

### Service Stack
The containerized platform includes:

#### **Core AI Services**
- **Chat Copilot Backend** (.NET WebAPI) - Port 11000
- **Chat Copilot Frontend** (React) - Port 3000
- **AutoGen Studio** (Python Multi-Agent) - Port 11001
- **Magentic-One** (Microsoft Multi-Agent) - Port 11003
- **Webhook Server** (GitHub Integration) - Port 11002

#### **External AI Services**
- **OpenWebUI** (Primary LLM Interface) - Port 11880
- **Perplexica** (AI Search) - Port 11020
- **SearXNG** (Privacy Search) - Port 11021
- **VS Code Server** (Web IDE) - Port 57081

#### **Infrastructure Services**
- **Caddy** (Reverse Proxy + SSL) - Ports 80, 8443, 2019
- **Qdrant** (Vector Database) - Port 6333
- **PostgreSQL** (Relational Database) - Port 5432
- **RabbitMQ** (Message Queue) - Ports 5672, 15672

#### **Monitoring & Management**
- **Health Monitor** (Automated monitoring)
- **Port Scanner** (Network Discovery) - Port 11010

### Network Configuration
- **Internal Network**: 172.20.0.0/16 subnet
- **Service Discovery**: DNS-based within containers
- **External Access**: Caddy reverse proxy with SSL termination
- **Security**: Container isolation with minimal privileges

## 🛠️ Management Commands

### Platform Control
```bash
# Start platform
./start-containerized-platform.sh start

# Start with rebuild
./start-containerized-platform.sh start-build

# Stop platform
./start-containerized-platform.sh stop

# Restart platform
./start-containerized-platform.sh restart

# Check status
./start-containerized-platform.sh status

# View logs
./start-containerized-platform.sh logs

# Health check
./start-containerized-platform.sh health

# Complete cleanup
./start-containerized-platform.sh clean
```

### Docker Compose Commands
```bash
# View running services
docker-compose -f docker-compose-full-stack.yml ps

# View logs for specific service
docker-compose -f docker-compose-full-stack.yml logs -f chat-copilot-backend

# Scale a service
docker-compose -f docker-compose-full-stack.yml up -d --scale autogen-studio=2

# Update specific service
docker-compose -f docker-compose-full-stack.yml up -d --no-deps chat-copilot-backend
```

### Container Management
```bash
# Enter container shell
docker exec -it ai-platform-chat-backend bash

# View container resources
docker stats

# Inspect container configuration
docker inspect ai-platform-chat-backend
```

## 📊 Monitoring & Health Checks

### Built-in Health Monitoring
- **Automatic health checks** for all services
- **Container restart** on failure
- **Resource monitoring** and alerting
- **Log aggregation** in `/app/logs` volumes

### Health Check Endpoints
Each service provides health monitoring:
- **Chat Copilot**: http://172.20.0.20/healthz
- **AutoGen Studio**: http://172.20.0.22/health
- **Webhook Server**: http://172.20.0.23/health
- **Magentic-One**: http://172.20.0.24/health

### Accessing Logs
```bash
# Platform-wide logs
docker-compose -f docker-compose-full-stack.yml logs

# Specific service logs
docker logs ai-platform-chat-backend

# Follow logs in real-time
docker logs -f ai-platform-autogen

# Health monitor logs
docker logs ai-platform-monitor
```

## 🔧 Configuration & Customization

### Environment Variables
All configuration is handled through `.env` file:

```bash
# Service URLs and ports
CHAT_BACKEND_URL=http://172.20.0.20:80
AUTOGEN_PORT=11001

# Resource limits
POSTGRES_MAX_CONNECTIONS=100
RABBITMQ_MEMORY_HIGH_WATERMARK=0.8

# Monitoring settings
HEALTH_CHECK_INTERVAL=300
FAILURE_THRESHOLD=3
LOG_RETENTION_DAYS=7
```

### Volume Mounts
Persistent data is stored in Docker volumes:
- **qdrant_data**: Vector database storage
- **postgres_data**: Relational database storage
- **platform_logs**: Application logs
- **caddy_data**: SSL certificates and cache

### Custom SSL Certificates
To use custom SSL certificates:
1. Place certificates in `/etc/ssl/certs/` and `/etc/ssl/private/`
2. Update volume mounts in `docker-compose-full-stack.yml`
3. Restart Caddy service

## 🔒 Security Considerations

### Container Security
- **Non-root users** in all containers
- **Minimal base images** (Alpine Linux where possible)
- **Resource limits** on all containers
- **Network isolation** between services
- **Secret management** via environment variables

### Network Security
- **Internal network** for service communication
- **SSL termination** at reverse proxy
- **Port exposure** only for required services
- **Firewall-friendly** design

### Data Security
- **Volume encryption** (configure Docker volume driver)
- **Secret rotation** via environment variable updates
- **Database security** with authentication
- **Log sanitization** to prevent data leaks

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check container status
docker-compose -f docker-compose-full-stack.yml ps

# View container logs
docker-compose -f docker-compose-full-stack.yml logs [service-name]

# Check resource usage
docker stats
```

#### Network Connectivity Issues
```bash
# Test internal DNS resolution
docker exec ai-platform-chat-backend nslookup qdrant

# Check network configuration
docker network inspect ai-research-platform_ai-platform

# Verify port mappings
docker port ai-platform-caddy
```

#### Database Connection Issues
```bash
# Check database status
docker exec ai-platform-postgres pg_isready

# Test connection from application
docker exec ai-platform-chat-backend curl postgres:5432

# View database logs
docker logs ai-platform-postgres
```

#### SSL Certificate Issues
```bash
# Verify certificate files
docker exec ai-platform-caddy ls -la /etc/ssl/certs/

# Test SSL configuration
curl -k https://localhost:8443

# Check Caddy configuration
docker exec ai-platform-caddy caddy validate --config /etc/caddy/Caddyfile
```

### Recovery Procedures

#### Complete Platform Reset
```bash
# Stop all services
./start-containerized-platform.sh stop

# Clean everything
./start-containerized-platform.sh clean

# Rebuild and restart
./start-containerized-platform.sh start-build
```

#### Individual Service Recovery
```bash
# Restart specific service
docker-compose -f docker-compose-full-stack.yml restart chat-copilot-backend

# Rebuild specific service
docker-compose -f docker-compose-full-stack.yml up -d --build chat-copilot-backend

# View service health
docker exec ai-platform-chat-backend curl localhost/healthz
```

## 📈 Performance Optimization

### Resource Allocation
Recommended resource limits per service:
- **Chat Copilot Backend**: 2GB RAM, 1 CPU
- **AutoGen Studio**: 4GB RAM, 2 CPU
- **OpenWebUI**: 4GB RAM, 2 CPU
- **Databases**: 2GB RAM, 1 CPU each

### Scaling Strategies
```bash
# Horizontal scaling for stateless services
docker-compose -f docker-compose-full-stack.yml up -d --scale autogen-studio=3

# Load balancer configuration for scaled services
# (Update Caddy configuration for load balancing)
```

### Storage Optimization
- **Volume cleanup**: Regular cleanup of old logs
- **Database optimization**: Regular VACUUM and ANALYZE
- **Container optimization**: Multi-stage builds for smaller images

## 🔄 Migration from Process-Based Setup

### Migration Steps
1. **Backup current data**: Run backup scripts
2. **Stop current services**: Use existing stop scripts
3. **Configure environment**: Set up `.env` file
4. **Import data**: Mount existing data volumes
5. **Start containerized platform**: Run startup script
6. **Verify functionality**: Test all services

### Data Migration
```bash
# Export existing data
./scripts/platform-management/backup-platform.sh

# Mount data in containers (update docker-compose-full-stack.yml)
volumes:
  - /path/to/existing/data:/app/data

# Import data in containers
docker exec ai-platform-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -f /backup/data.sql
```

## 📞 Support & Contributing

### Getting Help
- **Documentation**: Check this README and inline comments
- **Logs**: Always include relevant logs when reporting issues
- **Configuration**: Verify `.env` file configuration
- **Health Status**: Run health checks before reporting

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/containerization-improvement`
3. Make changes and test thoroughly
4. Submit pull request with detailed description

### Reporting Issues
Include in issue reports:
- Platform version and commit hash
- Docker and Docker Compose versions
- Environment configuration (sanitized)
- Container logs and error messages
- Steps to reproduce

---

## 🎉 Benefits of Containerized Setup

- ✅ **Consistent Deployments** across environments
- ✅ **Simplified Management** with single command startup
- ✅ **Better Resource Utilization** with container limits
- ✅ **Enhanced Security** with container isolation
- ✅ **Easy Scaling** of individual services
- ✅ **Simplified Backup/Recovery** with volume management
- ✅ **Development Efficiency** with reproducible environments
- ✅ **Production Ready** with health monitoring and auto-recovery

The containerized setup transforms the AI Research Platform into a modern, scalable, and maintainable application stack suitable for both development and production environments! 🚀