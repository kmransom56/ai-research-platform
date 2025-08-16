# Chat Copilot Portable Deployment Guide

This guide explains how to deploy Chat Copilot on any system using the new portable configuration.

## 🎯 Overview

The Chat Copilot platform has been made portable by:
- Replacing hard-coded paths with environment variables
- Creating configurable installation scripts
- Using Docker environment variables for all services
- Providing templates for easy customization

## 📋 Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM and 20GB disk space
- Linux, macOS, or Windows with WSL2
- Internet connection for downloading images

## 🚀 Quick Start (New Installation)

### 1. Download and Extract

```bash
# Download the portable Chat Copilot package
git clone https://github.com/your-repo/chat-copilot.git
cd chat-copilot
```

### 2. Run Portable Installation

```bash
# Run the portable installation script
./scripts/setup/install-portable.sh
```

This script will:
- Detect your system configuration
- Create a customized `.env` file
- Set up directory structure
- Configure all paths for your system

### 3. Configure AI Provider

Edit the `.env` file to add your AI provider credentials:

```bash
# Edit environment configuration
nano .env

# Add your OpenAI API key
OPENAI_API_KEY=your-actual-api-key-here

# Or configure Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
```

### 4. Start the Platform

```bash
# Start using the portable startup script
./start-platform-portable.sh

# Or use Docker Compose directly
docker-compose -f docker-compose.portable.yml up -d
```

### 5. Access the Platform

- **OpenWebUI**: http://your-ip:11880
- **Chat Copilot**: http://your-ip:11000
- **VS Code**: http://your-ip:57081
- **Grafana**: http://your-ip:11004

## 🔧 Manual Installation

If you prefer manual setup or need to customize the installation:

### 1. Create Environment File

```bash
# Copy the template
cp .env.template .env

# Edit for your system
nano .env
```

### 2. Set Key Variables

```bash
# Installation paths
CHAT_COPILOT_ROOT=/path/to/your/installation
PLATFORM_USER=your-username
PLATFORM_GROUP=your-group

# Network configuration
PLATFORM_IP=your-server-ip
PLATFORM_DOMAIN=your-domain.com

# Service ports (customize as needed)
CHAT_COPILOT_BACKEND_PORT=11000
OPENWEBUI_PORT=11880
# ... other ports
```

### 3. Create Directory Structure

```bash
# Create required directories
mkdir -p {logs,pids,data,backups,config-backups,temp}
chmod 755 {logs,pids,data,backups,config-backups,temp}
```

### 4. Start Services

```bash
# Load environment and start
source scripts/setup/load-env.sh
docker-compose -f docker-compose.portable.yml up -d
```

## 🔄 Migrating Existing Installation

If you have an existing Chat Copilot installation with hard-coded paths:

### 1. Backup Current Installation

```bash
# Create backup
cp -r /path/to/current/chat-copilot /path/to/backup/chat-copilot-backup
```

### 2. Fix Hard-coded Paths

```bash
# Run the path fix script
cd /path/to/current/chat-copilot
./scripts/setup/fix-hardcoded-paths.sh
```

### 3. Configure Environment

```bash
# Run portable installation
./scripts/setup/install-portable.sh
```

### 4. Test and Verify

```bash
# Stop old services
docker-compose down

# Start with new portable configuration
./start-platform-portable.sh

# Verify all services are working
docker ps
```

## 📁 Directory Structure

After installation, your directory structure will be:

```
chat-copilot/
├── .env                          # Environment configuration
├── .env.template                 # Template for new installations
├── docker-compose.portable.yml   # Portable Docker Compose
├── start-platform-portable.sh    # Portable startup script
├── scripts/
│   └── setup/
│       ├── install-portable.sh   # Portable installer
│       ├── load-env.sh           # Environment loader
│       └── fix-hardcoded-paths.sh # Path fixer
├── configs/                      # Configuration files
├── data/                         # Application data
├── logs/                         # Log files
├── backups/                      # Backup files
└── docs/                         # Documentation
```

## ⚙️ Configuration Options

### Environment Variables

Key environment variables you can customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `CHAT_COPILOT_ROOT` | Installation directory | Auto-detected |
| `PLATFORM_USER` | User for file ownership | Current user |
| `PLATFORM_IP` | Server IP address | Auto-detected |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `*_PORT` | Service ports | See .env.template |

### Service Configuration

Each service can be configured through environment variables:

```bash
# Database configuration
POSTGRES_DB=chatcopilot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password

# AI provider configuration
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4

# SSL configuration
SSL_CERT_PATH=/path/to/cert.crt
SSL_KEY_PATH=/path/to/cert.key
```

## 🔒 Security Considerations

### 1. Environment File Security

```bash
# Secure the .env file
chmod 600 .env
chown $USER:$USER .env
```

### 2. Database Passwords

```bash
# Generate secure passwords
POSTGRES_PASSWORD=$(openssl rand -hex 16)
RABBITMQ_DEFAULT_PASS=$(openssl rand -hex 16)
```

### 3. SSL/TLS Setup

```bash
# Generate SSL certificates (if using Tailscale)
tailscale cert your-domain.ts.net

# Or use Let's Encrypt
certbot certonly --standalone -d your-domain.com
```

## 🐳 Docker Configuration

### Custom Docker Compose

You can create your own Docker Compose file based on the portable template:

```bash
# Copy the portable template
cp docker-compose.portable.yml docker-compose.custom.yml

# Customize for your needs
nano docker-compose.custom.yml

# Start with custom configuration
docker-compose -f docker-compose.custom.yml up -d
```

### Volume Management

```bash
# List volumes
docker volume ls | grep chatcopilot

# Backup volumes
docker run --rm -v chatcopilot_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v chatcopilot_postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /data
```

## 🔍 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER /path/to/chat-copilot
   ```

2. **Port Conflicts**
   ```bash
   # Check what's using a port
   sudo lsof -i :11000
   
   # Change port in .env file
   CHAT_COPILOT_BACKEND_PORT=11001
   ```

3. **Environment Variables Not Loading**
   ```bash
   # Manually load environment
   source scripts/setup/load-env.sh
   
   # Check variables
   env | grep CHAT_COPILOT
   ```

### Logs and Debugging

```bash
# Check service logs
docker-compose logs chat-copilot-backend

# Check all logs
docker-compose logs

# Monitor logs in real-time
docker-compose logs -f
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check service health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test endpoints
curl http://localhost:11000/healthz
curl http://localhost:11880/health
```

### Backups

```bash
# Automated backup script
./scripts/backup/backup-platform.sh

# Manual backup
docker-compose exec postgres pg_dump -U postgres chatcopilot > backup.sql
```

### Updates

```bash
# Update images
docker-compose pull

# Restart services
docker-compose up -d
```

## 🌐 Multi-Environment Deployment

### Development Environment

```bash
# Copy environment template
cp .env.template .env.development

# Set development-specific values
ASPNETCORE_ENVIRONMENT=Development
LOG_LEVEL=Debug
```

### Production Environment

```bash
# Copy environment template
cp .env.template .env.production

# Set production-specific values
ASPNETCORE_ENVIRONMENT=Production
LOG_LEVEL=Warning
ENABLE_HEALTH_MONITORING=true
```

### Staging Environment

```bash
# Copy environment template
cp .env.template .env.staging

# Set staging-specific values
ASPNETCORE_ENVIRONMENT=Staging
LOG_LEVEL=Info
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Chat Copilot Documentation](./docs/)
- [Troubleshooting Guide](./docs/troubleshooting/)

## 🆘 Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Verify environment variables in `.env`
3. Review the troubleshooting section
4. Check Docker container status
5. Restore from backup if needed

## 📝 Contributing

To contribute to the portable deployment:

1. Test on different systems
2. Report issues with environment detection
3. Suggest improvements to the installation process
4. Update documentation

---

**Note**: This portable deployment system makes Chat Copilot easy to install on any system while maintaining all functionality and security features.