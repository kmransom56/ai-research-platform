# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AI Research Platform** - a comprehensive multi-agent AI development environment built on Microsoft's Chat Copilot. It combines multiple AI services, local LLMs, and development tools into a unified platform with secure Tailscale networking.

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

## Architecture Overview

### Core Components
- **webapi/**: .NET 8.0 backend API with Semantic Kernel integration
- **webapp/**: React 18 frontend with Redux Toolkit state management
- **memorypipeline/**: Semantic memory processing service
- **plugins/**: Semantic Kernel plugins for extended functionality
- **python/**: AI services including AutoGen Studio and Magentic-One
- **scripts/**: Platform management, deployment, and utility scripts

### Service Architecture (Ports 11000-12000)
- **Backend API**: 11000
- **AutoGen Studio**: 11001  
- **Webhook Server**: 11002
- **Magentic-One**: 11003
- **Port Scanner**: 11010
- **Perplexica AI**: 11020
- **SearXNG**: 11021
- **Ollama LLM**: 11434
- **Caddy HTTPS**: 10443

### Key Technologies
- **.NET 8.0** with ASP.NET Core and SignalR
- **Microsoft Semantic Kernel** for AI orchestration
- **React 18** with TypeScript and Material-UI
- **Docker & Docker Compose** for containerization
- **Caddy** web server with automatic HTTPS
- **Tailscale** for secure mesh networking
- **AutoGen Studio** for multi-agent AI
- **Ollama** for local LLM serving

### Network Access
- **Tailscale Domain**: ubuntuaicodeserver-1.tail5137b4.ts.net
- **Main Services**: /copilot, /autogen, /openwebui, /hub, /vscode
- **Local Development**: Various localhost ports

## Configuration Files

### Key Configuration
- **webapi/appsettings.json**: Backend API configuration (AI keys, endpoints)
- **webapp/.env**: Frontend environment variables
- **docker-compose.yml**: Container orchestration
- **docker-configs/Caddyfile**: Reverse proxy configuration
- **pyproject.toml**: Python dependencies

### Configuration Protection
- Automated validation every 15 minutes
- Configuration backups every 6 hours
- File monitoring for unauthorized changes
- Configuration drift prevention system

## Development Workflow

1. **Check platform status**: `./scripts/platform-management/manage-platform.sh status`
2. **Start development**: Use either `./scripts/start.sh` for basic Chat Copilot or full platform startup
3. **Backend changes**: Work in webapi/ directory, standard .NET development
4. **Frontend changes**: Work in webapp/ directory, React with hot reload
5. **Platform services**: Managed via Docker Compose and management scripts

## Testing & Quality

### Test Commands
```bash
# .NET integration tests
cd integration-tests && dotnet test

# Frontend tests (Jest/React Testing Library)
cd webapp && yarn test

# Playwright E2E tests
cd webapp && npx playwright test
```

### Code Quality
- **ESLint**: Frontend linting with TypeScript support
- **Prettier**: Code formatting
- **GitIgnore**: Comprehensive exclusions for all tech stacks

## Important Notes

- **Port standardization**: All services use 11000-12000 range
- **Tailscale integration**: Secure network access across devices
- **Multi-agent AI**: AutoGen Studio enables collaborative AI workflows
- **Local LLMs**: Ollama supports 7+ models including llama3.2, deepseek-coder
- **Configuration monitoring**: Automated protection against drift
- **Health monitoring**: Comprehensive service health checking
- **GPU optimization**: Supports high-memory GPU systems (72GB+ VRAM)

## Quick References

### Health Checks
- Backend: http://localhost:11000/healthz
- Platform status: `./scripts/platform-management/check-platform-status.sh`

### Log Locations
- Platform logs: logs/management.log
- Service logs: Check individual Docker containers

### Emergency Recovery
- Emergency reset: `./scripts/backup-recovery/emergency-reset.sh`
- Config restore: `./scripts/backup-recovery/restore-config.sh`

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
cp .env.template .env
# Edit .env with your Azure OpenAI keys and passwords

# Start complete platform
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
- **All services** available through reverse proxy

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

### File Sync Issues
If HTML pages show old content:
```bash
# Copy updated files from webapp/public/ to webapi/wwwroot/
cp webapp/public/control-panel.html webapi/wwwroot/
cp webapp/public/applications.html webapi/wwwroot/
```