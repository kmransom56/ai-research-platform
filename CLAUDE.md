# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AI Research Platform** - a comprehensive multi-agent AI development environment built on Microsoft's Chat Copilot. It combines multiple AI services, local LLMs, and development tools into a unified platform with secure Tailscale networking.

## External AI Application Resources

- Docker GenAI Stack: https://github.com/docker/genai-stack 
- Neo4j GenAI Ecosystem Stack: https://neo4j.com/labs/genai-ecosystem/genai-stack/

## Build & Development Commands

### Backend (.NET)
```bash
# Build solution
dotnet build CopilotChat.sln

# Run backend API (development)
cd webapi && dotnet run --urls http://0.0.0.0:11000

# Run tests
cd integration-tests && dotnet test
```

### Frontend (React)
```bash
# Install dependencies
cd webapp && yarn install

# Development server
yarn start

# Build for production  
yarn build

# Run linting
yarn lint
yarn lint:fix

# Format code
yarn format
yarn format:fix

# Run tests
yarn test
```

### Python Services
```bash
# Install Python dependencies
pip install -e .

# Run specific Python services (various ports 11001-11020)
# Services managed via platform scripts
```

### Platform Management
```bash
# User-friendly platform management
./scripts/platform-management/manage-platform.sh

# Start entire platform
./scripts/platform-management/startup-platform.sh

# Check platform status
./scripts/platform-management/check-platform-status.sh

# Stop platform
./scripts/platform-management/stop-platform.sh

# Quick start (original Chat Copilot)
./scripts/start.sh
```

### SSL Certificate Management
```bash
# Setup Tailscale SSL certificates
./scripts/infrastructure/setup-tailscale-ssl.sh

# Verify SSL certificate setup
./scripts/infrastructure/verify-ssl-setup.sh

# Renew SSL certificates
./scripts/infrastructure/renew-certificates.sh

# Monitor certificate expiration
python3 python/utilities/check-certificates.py

# CA Certificate Automation (NEW)
./scripts/infrastructure/check-ca-server-status.sh
./scripts/infrastructure/request-ca-certificate.sh -d domain.local -p 11005 -s servicename
./scripts/platform-management/add-application.sh --name windmill --port 11005
```

## Architecture Overview

### Core Components
- **webapi/**: .NET 8.0 backend API with Semantic Kernel integration
- **webapp/**: React 18 frontend with Redux Toolkit state management
- **memorypipeline/**: Semantic memory processing service
- **plugins/**: Semantic Kernel plugins for extended functionality
- **python/**: AI services including AutoGen Studio and Magentic-One
- **scripts/**: Platform management, deployment, and utility scripts
- **genai-stack/**: Neo4j GenAI Stack for knowledge graph AI applications

### Service Architecture (Ports 11000-12000)
- **Backend API**: 11000
- **AutoGen Studio**: 11001  
- **Webhook Server**: 11002
- **Magentic-One**: 11003
- **Windmill (SSL)**: 11005
- **Windmill (Container)**: 11006
- **Port Scanner**: 11010
- **Perplexica AI**: 11020
- **SearXNG**: 11021
- **Ollama LLM**: 11434
- **Caddy HTTPS**: 10443

### Neo4j GenAI Stack (Ports 7474, 7687, 8501-8505)
- **Neo4j Database**: 7474 (HTTP), 7687 (Bolt)
- **GenAI Stack Bot**: 8501
- **GenAI Stack Loader**: 8502
- **GenAI Stack PDF Reader**: 8503
- **GenAI Stack API**: 8504
- **GenAI Stack Frontend**: 8505

### Key Technologies
- **.NET 8.0** with ASP.NET Core and SignalR
- **Microsoft Semantic Kernel** for AI orchestration
- **React 18** with TypeScript and Material-UI
- **Docker & Docker Compose** for containerization
- **Caddy** web server with automatic HTTPS
- **Tailscale** for secure mesh networking
- **AutoGen Studio** for multi-agent AI
- **Ollama** for local LLM serving
- **Neo4j** for graph database and knowledge graphs
- **LangChain** for GenAI Stack RAG implementation

### Network Access
- **Tailscale Domain**: ubuntuaicodeserver-1.tail5137b4.ts.net
- **Main Services**: /copilot, /autogen, /openwebui, /hub, /vscode, /genai-stack, /neo4j
- **Local Development**: Various localhost ports

## Configuration Files

### Key Configuration
- **webapi/appsettings.json**: Backend API configuration (AI keys, endpoints)
- **webapp/.env**: Frontend environment variables
- **docker-compose.yml**: Container orchestration
- **docker-configs/Caddyfile**: Reverse proxy configuration
- **pyproject.toml**: Python dependencies
- **genai-stack/**: GenAI Stack configuration and Dockerfiles

### Configuration Protection
- Automated validation every 15 minutes
- Configuration backups every 6 hours
- File monitoring for unauthorized changes
- Configuration drift prevention system

## Certificate Automation (NEW)

### CA Server Integration
- **CA Server URL**: https://192.168.0.2
- **Supported APIs**: Certificate generation, CSR signing, certificate inventory, download
- **Managed Certificates**: 5 active certificates tracked and managed
- **Certificate Types**: Server, HTTPS, nginx, CSR-based certificates

### Certificate Management Scripts
```bash
# Check CA server status and API health
./scripts/infrastructure/check-ca-server-status.sh

# Request certificate from CA server
./scripts/infrastructure/request-ca-certificate.sh -d windmill.local -p 11005 -s windmill

# Generate self-signed certificates (fallback)
./scripts/infrastructure/generate-self-signed-cert.sh windmill.local 11005

# Certificate renewal automation
./scripts/infrastructure/renew-ca-certificates.sh

# Add new application with certificate automation
./scripts/platform-management/add-application.sh --name newapp --port 11007
```

### Certificate Features
- **Automatic Generation**: CA API integration with multi-endpoint fallback
- **Self-signed Fallback**: Development certificate support when CA unavailable
- **nginx Integration**: Automatic SSL configuration and deployment
- **Certificate Monitoring**: Expiration tracking and automated renewal
- **Download Support**: Full certificate and private key retrieval
- **Validation**: OpenSSL verification and certificate structure validation

### Certificate Inventory Management
- **Real-time Tracking**: Monitor certificate status and expiration
- **Multiple Types**: Support for various certificate types and use cases
- **Automated Renewal**: Proactive certificate lifecycle management
- **Health Monitoring**: Continuous validation of certificate infrastructure

## Development Workflow

1. **Check platform status**: `./scripts/platform-management/manage-platform.sh status`
2. **Start development**: Use either `./scripts/start.sh` for basic Chat Copilot or full platform startup
3. **Backend changes**: Work in webapi/ directory, standard .NET development
4. **Frontend changes**: Work in webapp/ directory, React with hot reload
5. **Platform services**: Managed via Docker Compose and management scripts
6. **GenAI Stack development**: Work in genai-stack/ directory for knowledge graph applications

## Adding New Applications

The platform includes a standardized process for adding new applications:

### Using the Add Application Script
```bash
# Basic usage
./scripts/platform-management/add-application.sh \
  --name "MyApp" \
  --port 11006 \
  --path "/myapp" \
  --description "My Application Description" \
  --category "ai|dev|network|api"

# With Docker integration
./scripts/platform-management/add-application.sh \
  --name "Grafana" \
  --port 11007 \
  --path "/grafana" \
  --description "Monitoring Dashboard" \
  --category "dev" \
  --docker-image "grafana/grafana:latest"

# Test mode (see what would be done)
./scripts/platform-management/add-application.sh --test-mode [options]

# Nginx configuration only
./scripts/platform-management/add-application.sh --nginx-only [options]
```

### Using the Control Panel
1. Access Control Panel: `https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/hub`
2. Click "Add Application" in the Application Management section
3. Fill in the prompted information
4. Copy the generated command and run it in terminal

### What the Script Does
- **Nginx Configuration**: Adds reverse proxy location to `/etc/nginx/sites-available/ai-hub.conf`
- **Docker Integration**: Adds service to `docker-compose.yml` (if Docker image provided)
- **Web Interface**: Updates `applications.html` with new application card and quick link
- **Documentation**: Updates port configuration documentation
- **Validation**: Tests nginx configuration and reloads automatically

### Manual Steps After Adding
1. Start Docker service: `docker-compose up -d`
2. Test application: `https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/[path]`
3. Update application status in applications.html if needed

## Testing & Quality

### Test Commands
```bash
# .NET integration tests
cd integration-tests && dotnet test

# Frontend tests (Jest/React Testing Library)
cd webapp && yarn test

# Playwright E2E tests
cd webapp && npx playwright test

# Platform validation
./validate-deployment.sh
```

### Code Quality
- **ESLint**: Frontend linting with TypeScript support
- **Prettier**: Code formatting
- **GitIgnore**: Comprehensive exclusions for all tech stacks

## Important Notes

- **Port standardization**: All services use 11000-12000 range, GenAI Stack uses 8501-8505
- **Certificate automation**: CA server integration at https://192.168.0.2 with fallback systems
- **Application deployment**: Standardized addition process with validation and rollback
- **Windmill integration**: Workflow automation with SSL access on port 11005
- **Tailscale integration**: Secure network access across devices
- **Multi-agent AI**: AutoGen Studio enables collaborative AI workflows
- **Local LLMs**: Ollama supports 7+ models including llama3.2, deepseek-coder
- **Knowledge Graphs**: Neo4j GenAI Stack provides graph-based AI capabilities
- **Configuration monitoring**: Automated protection against drift
- **Health monitoring**: Comprehensive service health checking
- **GPU optimization**: Supports high-memory GPU systems (72GB+ VRAM)

## Quick References

### Health Checks
- Backend: http://localhost:11000/healthz
- Platform status: `./check-platform-status.sh`
- Neo4j: http://localhost:7474
- GenAI Stack: http://localhost:8505
- Windmill: https://localhost:11005
- CA Server: `./scripts/infrastructure/check-ca-server-status.sh`

### Log Locations
- Service logs: Check individual Docker containers with `docker logs <container-name>`
- Neo4j logs: Via Docker volumes
- Health status: `./validate-deployment.sh`

### Emergency Recovery
- Service restart: Use Docker commands or platform management scripts
- Configuration issues: Check `.env` file and `appsettings.json`

## Containerized Installation

### Quick Start (New Computer)
```bash
# Option 1: Install in user directory
git clone https://github.com/kmransom56/ai-research-platform.git
cd ai-research-platform

# Option 2: Install in /opt (system-wide)
sudo git clone https://github.com/kmransom56/ai-research-platform.git /opt/ai-research-platform
sudo chown -R $USER:$USER /opt/ai-research-platform
cd /opt/ai-research-platform

# Configure environment
cp configs/.env.template .env
# Edit .env with your Azure OpenAI keys and passwords

# Start complete platform with GenAI Stack
./start-containerized-platform.sh start-build
```

### Container Commands
```bash
# Start platform
./start-containerized-platform.sh start

# Stop platform  
./start-containerized-platform.sh stop

# View logs
./start-containerized-platform.sh logs

# Check health
./start-containerized-platform.sh health

# Clean restart
./start-containerized-platform.sh clean
```

### Access After Installation
- **Main Hub**: https://localhost:8443
- **Control Panel**: https://localhost:8443/hub
- **Applications**: https://localhost:8443/applications.html
- **GenAI Stack**: https://localhost:8443/genai-stack
- **Neo4j Browser**: https://localhost:8443/neo4j
- **All services** available through reverse proxy

## GenAI Stack Features

### Knowledge Graph Capabilities
- **Neo4j Database**: Graph database with APOC plugins
- **Support Agent Bot**: AI assistant using knowledge graphs
- **Document Loader**: Import and process documents into knowledge graphs
- **PDF Reader**: AI-powered PDF analysis with graph storage
- **RAG API**: Retrieval-Augmented Generation with graph context
- **Frontend Dashboard**: Web interface for all GenAI Stack features

### GenAI Stack Applications
- **Data Import**: /genai-stack/loader (port 8502)
- **Import Interface**: /genai-stack/import (port 8081) 
- **Support Bot**: /genai-stack/bot (port 8501)
- **PDF Reader**: /genai-stack/pdf (port 8503)
- **API Endpoint**: /genai-stack/api (port 8504)
- **Main Interface**: /genai-stack (port 8505)

## Debugging & Development

### Getting Back to This Chat Session
1. **Copy CLAUDE.md**: This file contains all instructions for Claude Code
2. **Use Claude Code CLI**: Run `claude` in project directory
3. **Or use VS Code**: Access web IDE at https://localhost:8443/vscode

### Common Issues
- **Port conflicts**: Change ports in docker-compose-full-stack.yml
- **SSL issues**: Check Caddy logs with `docker logs ai-platform-caddy`
- **Service failures**: Check individual service logs with `docker logs <service-name>`
- **Environment issues**: Verify .env file has all required values
- **Permission issues in /opt**: Ensure user owns the directory with `sudo chown -R $USER:$USER /opt/ai-research-platform`
- **Docker permission denied**: Add user to docker group with `sudo usermod -aG docker $USER` (logout/login required)
- **Neo4j connection issues**: Check NEO4J_PASSWORD environment variable
- **GenAI Stack build failures**: Ensure genai-stack directory exists and contains Dockerfiles

### SSL Certificate Issues
- **Tailscale certificate generation fails**: Check Tailscale authentication with `tailscale status`
- **Nginx SSL errors**: Verify certificate paths in nginx configs match actual certificate locations
- **Certificate not found errors**: Run `./scripts/infrastructure/setup-tailscale-ssl.sh` to generate certificates
- **Permission denied on certificates**: Check certificate file permissions are 644 for .crt and 600 for .key files
- **Subdomain certificates missing**: Ensure subdomains are configured in Tailscale admin console
- **Certificate expiration**: Use `./scripts/infrastructure/verify-ssl-setup.sh` to check certificate status

### Package Dependency Issues
**Azure.AI.OpenAI Version Compatibility (As of June 2025):**
- Issue: KernelMemory 0.98.x expects Azure.AI.OpenAI version 2.2.0.0 but only 2.2.0-beta.4 is available
- Current Status: Updated to latest compatible package versions:
  - Microsoft.KernelMemory.Core: 0.98.250508.3
  - Microsoft.KernelMemory.Abstractions: 0.98.250508.3
  - Microsoft.SemanticKernel: 1.57.0
  - Microsoft.SemanticKernel.Abstractions: 1.57.0
- Workaround: Use Ollama or disable AI services in appsettings.json for basic API functionality
- Alternative: Consider Paket package manager for complex dependency resolution

**Package Management:**
```bash
# Standard NuGet commands
dotnet list package --include-transitive
dotnet add package [PackageName] --version [Version]

# Alternative: Paket (better dependency resolution)
paket add [PackageName] --version [Version]
paket install
```

### File Sync Issues
If HTML pages show old content:
```bash
# Copy updated files from webapp/public/ to webapi/wwwroot/
cp webapp/public/control-panel.html webapi/wwwroot/
cp webapp/public/applications.html webapi/wwwroot/
```

## Repository Management

### Latest Updates (June 23, 2025)
- **Certificate Automation**: Full CA server integration with https://192.168.0.2
- **Windmill Integration**: Workflow automation engine with SSL support
- **Application Addition**: Standardized scripts for adding new applications
- **Certificate Management**: Complete lifecycle automation with fallback systems
- **Repository Cleaned**: Removed runtime files, backups, and duplicates
- **Python Scripts**: All 19 scripts reviewed and updated with proper headers
- **Shell Scripts**: 67+ scripts reviewed, permissions fixed
- **Documentation**: Updated GenAI Stack README and backup guides
- **Backup System**: Comprehensive backup/restore system implemented

### Repository Cleanup Completed
- ✅ Removed runtime files (*.log, *.pid, certificates)
- ✅ Cleaned up excessive config snapshots (kept latest 3)
- ✅ Removed duplicate/empty files and directories  
- ✅ Updated .gitignore to prevent future runtime file commits
- ✅ Fixed Python script headers and documentation
- ✅ Verified shell script permissions and executable status

### Current Deployment Status (June 23, 2025)
- ✅ **Certificate Automation**: CA server integration fully functional
- ✅ **Windmill**: Workflow automation engine deployed at https://localhost:11005
- ✅ **Application Management**: Standardized addition process with dashboard integration
- ✅ **SSL Infrastructure**: Self-signed certificates working, CA certificates ready
- ✅ **GitHub Updated**: Complete documentation and backup/restore system
- ✅ **Configuration Backup**: Automated backup system with quick restore capability

### Backup & Restore System
- **Quick Restore**: `./config-backups-working/latest/quick-restore.sh` (one-command post-reboot fix)
- **Create Backup**: `./scripts/backup-working-config.sh`
- **Health Check**: `./check-platform-status.sh`
- **Recovery Guide**: Complete recovery documentation in `./RECOVERY_GUIDE.md`
- **Backup Location**: `/home/keith/chat-copilot/config-backups-working/latest/`

### New Applications Added
- **Windmill**: Workflow automation engine
  - **SSL Access**: https://localhost:11005 
  - **Features**: Workflow designer, script execution, scheduling
  - **Database**: PostgreSQL with persistent storage
  - **Status**: ✅ Fully operational with SSL certificate

Last backup: Mon Jun 23 06:42:52 AM EDT 2025
Last backup: Mon Jun 23 08:29:57 PM EDT 2025
