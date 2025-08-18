# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AI Research Platform** - a comprehensive multi-agent AI development environment built on Microsoft's Chat Copilot. It combines multiple AI services, local LLMs, and development tools into a unified platform with secure Tailscale networking.

## 🚀 **NEW: Advanced AI Stack Integration**

### **High-Performance AI Services**
The platform now includes a **fully integrated advanced AI stack** with vLLM, Oobabooga, and KoboldCpp:

#### **🎯 AI Stack Services (Ports 8000-9000)**
- **vLLM DeepSeek R1**: http://localhost:8000 (Reasoning and complex analysis)
- **vLLM Mistral Small**: http://localhost:8001 (General purpose, fast responses)  
- **vLLM DeepSeek Coder**: http://localhost:8002 (Code generation and debugging)
- **Oobabooga WebUI**: http://localhost:7860 (Advanced features, multimodal)
- **Oobabooga API**: http://localhost:5000 (API endpoint for integrations)
- **KoboldCpp**: http://localhost:5001 (Creative writing and roleplay)
- **AI Stack Gateway**: http://localhost:9000 (Unified API with smart routing)
- **AI Stack Monitor**: http://localhost:8090 (System and service monitoring)

#### **📊 Integrated Management**
- **Management Scripts**: `./scripts/platform-management/manage-ai-stack.sh`
- **Docker Integration**: `docker-compose.ai-stack.yml` with full containerization
- **Python SDK**: Advanced AI client library in `python/ai-stack/`
- **Configuration**: Integrated into `appsettings.json` and `.env` files

## 🍽️ **Restaurant Network Management System**

### **Complete Multi-Vendor Network Management**
The platform includes a **comprehensive AI-powered restaurant network management system** with FortiManager integration and advanced monitoring:

#### **🎤 Main AI Network Management Hub**
- **Central Interface**: http://localhost:11040
- **Restaurant Operations Voice**: http://localhost:11032 (Store managers, equipment monitoring)
- **IT & Network Management Voice**: http://localhost:11030 (Network engineers, technical staff)

#### **📊 Advanced Monitoring & Visualization**
- **Grafana Dashboards**: http://localhost:11002 (admin/admin) - Real-time restaurant network monitoring
- **Prometheus Metrics**: http://localhost:9090 - Network health, FortiManager connectivity, alerting
- **Neo4j Network Topology**: http://localhost:7474 (neo4j/password) - Multi-vendor visualization

#### **🏢 Restaurant Network Scale**
- **25,000+ Total Devices**: Multi-vendor restaurant network infrastructure
- **Existing Meraki**: 7,816 devices across restaurant chains
- **FortiManager Integration**: 15,000-25,000 Fortinet devices
  - **Arby's**: ~2,000-3,000 devices (FortiManager: 10.128.144.132)
  - **Buffalo Wild Wings**: ~2,500-3,500 devices (FortiManager: 10.128.145.4)
  - **Sonic**: ~7,000-10,000 devices (FortiManager: 10.128.156.36)

#### **🎤 Voice Command Examples**
```bash
# Restaurant Operations Interface (11032)
"How are our POS systems?"
"Check kitchen equipment at Buffalo Wild Wings"
"Any drive-thru issues?"
"Are the kiosks working at store 4472?"

# IT & Network Management Interface (11030)
"How many devices do we have?"
"Show Fortinet devices"
"How is Arby's network?"
"Check FortiManager connectivity"
"What's the health of Sonic's infrastructure?"
```

#### **🛡️ FortiManager Integration Features**
- **Proven API Integration**: Based on user's GitHub repository implementation
- **Restaurant-Specific Enhancements**: Organization detection, device role classification
- **Corporate Network Ready**: SSL handling for Zscaler, corporate proxy support
- **Multi-Vendor Discovery**: Unified Meraki + Fortinet device management
- **Voice-Enabled Queries**: Natural language commands for all restaurant brands

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

### Advanced AI Stack Management
```bash
# Manage AI Stack Gateway
./scripts/platform-management/manage-ai-stack.sh start-gateway
./scripts/platform-management/manage-ai-stack.sh stop-gateway
./scripts/platform-management/manage-ai-stack.sh health

# Monitor AI Stack
./scripts/platform-management/manage-ai-stack.sh monitor

# Test AI Stack functionality
./scripts/platform-management/manage-ai-stack.sh test

# Start with Docker (full stack)
docker-compose -f docker-compose.ai-stack.yml up -d

# Start individual AI services (following setup guide)
# See: Advanced AI Stack Setup Guide.md
```

### Restaurant Network Management
```bash
# Start complete multi-vendor network system
./start-multi-vendor-network-system.sh

# Launch restaurant network voice interfaces
cd network-agents
python3 speech-web-interface.py  # Main voice interface (11030)
python3 restaurant-equipment-voice-interface.py  # Restaurant operations (11032)

# Test FortiManager connectivity (corporate network required)
cd network-agents
python3 test_corporate_network.py
python3 fortimanager_api.py

# Launch monitoring dashboards
python3 launch-grafana-dashboards.py

# Multi-vendor network discovery
python3 multi-vendor-discovery.py
```

### Corporate Network Installation
```bash
# Automated corporate network setup
./scripts/corporate-network-setup.sh

# Quick corporate deployment
git clone https://github.com/kmransom56/chat-copilot.git
cd chat-copilot
./scripts/corporate-network-setup.sh
```

### Speech-Enabled Network Management
```bash
# Speech interface for network management
cd network-agents
python3 speech-web-interface.py  # Access: http://localhost:11030

# Command-line speech interface
python3 speech-enabled-network-manager.py

# Test speech commands
python3 test-speech-cli.py

# Full-scale network discovery
python3 full-scale-meraki-discovery.py

# Launch with browser integration
python3 launch-speech-interface.py
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
- **network-agents/**: Restaurant Network Management System with FortiManager integration

### Service Architecture (Ports 11000-12000)
- **Backend API**: 11000
- **AutoGen Studio**: 11001  
- **Grafana Dashboards**: 11002
- **Magentic-One**: 11003
- **Windmill (SSL)**: 11005
- **Windmill (Container)**: 11006
- **Port Scanner**: 11010
- **Perplexica AI**: 11020
- **SearXNG**: 11021
- **Ollama LLM**: 11434
- **Caddy HTTPS**: 10443

### Restaurant Network Management (Ports 11030-11040)
- **IT & Network Voice Interface**: 11030
- **Restaurant Operations Voice**: 11032
- **Main AI Network Management Hub**: 11040

### Monitoring & Database Services
- **Prometheus Metrics**: 9090
- **Neo4j Database**: 7474 (HTTP), 7687 (Bolt)

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
- **vLLM** for high-performance LLM inference
- **Oobabooga** for advanced text generation features
- **KoboldCpp** for creative writing and roleplay
- **Docker & Docker Compose** for containerization
- **Caddy** web server with automatic HTTPS
- **Tailscale** for secure mesh networking
- **AutoGen Studio** for multi-agent AI
- **Ollama** for local LLM serving
- **Neo4j** for graph database and knowledge graphs
- **LangChain** for GenAI Stack RAG implementation
- **Grafana** for monitoring dashboards and visualization
- **Prometheus** for metrics collection and alerting
- **FortiManager JSON-RPC API** for Fortinet device management
- **Meraki Dashboard API** for Cisco device management
- **Web Speech API** for voice interface capabilities

### Network Access
- **Tailscale Domain**: ubuntuaicodeserver-1.tail5137b4.ts.net
- **Main Services**: /copilot, /autogen, /openwebui, /hub, /vscode, /genai-stack, /neo4j
- **Local Development**: Various localhost ports

### Restaurant Network Management Access
- **Main AI Network Hub**: http://localhost:11040
- **Restaurant Operations Voice**: http://localhost:11032  
- **IT & Network Management Voice**: http://localhost:11030
- **Grafana Monitoring**: http://localhost:11002 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Neo4j Network Topology**: http://localhost:7474 (neo4j/password)

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

- **Port standardization**: Core services 11000-12000, AI Stack 8000-9000, Gateway 9000
- **Advanced AI Integration**: vLLM + Oobabooga + KoboldCpp for specialized tasks
- **Task-based routing**: Reasoning, coding, creative, general purpose AI endpoints
- **Hardware optimization**: Optimized for high-memory GPU systems (96GB+ VRAM)
- **Unified API**: Single gateway endpoint for intelligent request routing
- **Certificate automation**: CA server integration at https://192.168.0.2 with fallback systems
- **Application deployment**: Standardized addition process with validation and rollback
- **Windmill integration**: Workflow automation with SSL access on port 11005
- **Tailscale integration**: Secure network access across devices
- **Multi-agent AI**: AutoGen Studio enables collaborative AI workflows
- **Local LLMs**: Ollama supports 7+ models including llama3.2, deepseek-coder
- **Knowledge Graphs**: Neo4j GenAI Stack provides graph-based AI capabilities
- **Configuration monitoring**: Automated protection against drift
- **Health monitoring**: Comprehensive service health checking

## Quick References

### Health Checks
- Backend: http://localhost:11000/healthz
- **AI Stack Gateway**: http://localhost:9000/health
- **AI Stack Monitor**: http://localhost:8090
- **Individual AI services**: Check ports 8000-8002, 5000-5001, 7860
- **AI Stack Management**: `./scripts/platform-management/manage-ai-stack.sh health`
- Platform status: `./check-platform-status.sh`
- Neo4j: http://localhost:7474
- GenAI Stack: http://localhost:8505
- Windmill: https://localhost:11005
- CA Server: `./scripts/infrastructure/check-ca-server-status.sh`
- **Restaurant Network Management**: http://localhost:11040
- **Grafana Dashboards**: http://localhost:11002
- **Prometheus Metrics**: http://localhost:9090
- **FortiManager Connectivity**: `cd network-agents && python3 test_corporate_network.py`

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

## Advanced AI Stack Usage Examples

### Using the Python SDK
```python
from python.ai_stack.advanced_ai_client import AdvancedAIStack

# Initialize client
ai = AdvancedAIStack()

# Check health
health = ai.health_check()
print(f"Overall status: {health.get('overall_status')}")

# Different task types
reasoning_result = ai.complete("Solve: 2x + 5 = 17", task_type="reasoning")
coding_result = ai.complete("Write a Python function to sort a list", task_type="coding")
creative_result = ai.complete("Write a haiku about AI", task_type="creative")

print(f"Reasoning: {reasoning_result.content}")
print(f"Coding: {coding_result.content}")
print(f"Creative: {creative_result.content}")
```

### Using via HTTP API
```bash
# Health check
curl http://localhost:9000/health

# Completion request
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reasoning",
    "prompt": "Explain quantum computing",
    "max_tokens": 200,
    "temperature": 0.7
  }'

# OpenAI-compatible endpoint
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, AI!"}],
    "task_type": "general",
    "max_tokens": 100
  }'
```

### Docker Deployment
```bash
# Start full AI stack with containerization
docker-compose -f docker-compose.ai-stack.yml up -d

# Check container status
docker-compose -f docker-compose.ai-stack.yml ps

# View logs
docker-compose -f docker-compose.ai-stack.yml logs ai-gateway
docker-compose -f docker-compose.ai-stack.yml logs ai-monitor

# Scale gateway instances
docker-compose -f docker-compose.ai-stack.yml up -d --scale ai-gateway=3
```

### Integration Points
1. **Backend (.NET)**: AI Stack endpoints configured in `appsettings.json`
2. **Frontend (React)**: Environment variables in `webapp/.env`
3. **Docker**: Full containerization with `docker-compose.ai-stack.yml`
4. **Monitoring**: Integrated with Grafana and Prometheus
5. **Management**: Platform scripts in `scripts/platform-management/`
Last backup: Sun Aug 17 07:16:19 PM EDT 2025
