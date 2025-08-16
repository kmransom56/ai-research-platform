# AI Research Platform

A comprehensive multi-agent AI development environment built on Microsoft's Chat Copilot, featuring restaurant network management capabilities and enterprise-grade monitoring.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/kmransom56/ai-research-platform.git
cd ai-research-platform

# Quick installation
./easy-installer.sh

# Or manual installation
cp .env.template .env
# Edit .env with your API keys
docker-compose up -d
```

## Features

### Core AI Platform
- **Chat Copilot**: Microsoft's AI assistant framework
- **AutoGen Studio**: Multi-agent AI collaboration
- **Local LLMs**: Ollama integration with 7+ models
- **Advanced AI Stack**: vLLM + Oobabooga + KoboldCpp (see `ADVANCED_AI_STACK_GUIDE.md`)
- **GenAI Stack**: Neo4j-powered knowledge graphs

### Restaurant Network Management
- **Multi-Vendor Support**: Cisco Meraki + Fortinet FortiManager
- **25,000+ Devices**: Enterprise-scale network monitoring
- **Voice Interface**: Natural language network queries
- **Real-time Monitoring**: Grafana + Prometheus integration

### Enterprise Features
- **SSL/TLS**: Automatic certificate management
- **Monitoring**: Comprehensive health checks
- **Backup System**: Automated configuration backup
- **Scalability**: Container-based architecture

## Network Access

- **Main Platform**: http://localhost:11000
- **AutoGen Studio**: http://localhost:11001
- **Network Management**: http://localhost:11040
- **Grafana Dashboards**: http://localhost:11002
- **Neo4j Browser**: http://localhost:7474

## Documentation

- `EASY_INSTALL.md` - Quick setup guide
- `ADVANCED_AI_STACK_GUIDE.md` - **NEW!** vLLM + Oobabooga + KoboldCpp setup
- `PRODUCTION_READY_GUIDE.md` - Enterprise deployment
- `PORTABLE_DEPLOYMENT_GUIDE.md` - Cross-platform setup
- `CLAUDE.md` - Development instructions

## Architecture

```
├── webapi/          # .NET 8 backend API
├── webapp/          # React frontend
├── python/          # Python AI services
├── network-agents/  # Restaurant network management
├── genai-stack/     # Neo4j GenAI integration
├── scripts/         # Platform management
└── configs/         # Configuration files
```

## Support

- GitHub Issues: https://github.com/kmransom56/ai-research-platform/issues
- Documentation: Check CLAUDE.md for comprehensive setup instructions

## License

Built on Microsoft's Chat Copilot framework with enterprise extensions.