# 🤖 AI Research Platform

**A comprehensive multi-agent AI development environment built on Microsoft's Chat Copilot with secure Tailscale networking, containerized deployment, and production-ready SSL termination.**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![SSL](https://img.shields.io/badge/SSL-Enabled-green)](https://tailscale.com)
[![.NET](https://img.shields.io/badge/.NET-8.0-purple)](https://dotnet.microsoft.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)

## 🚀 **Quick Start**

### **Choose Your Deployment Strategy**

#### 🏢 **Production (Recommended)**
```bash
# 1. Clone and configure
git clone <repository-url>
cd ai-research-platform
cp .env.template .env
# Edit .env with your API keys

# 2. Start production platform with AI Stack
./start-ssl-platform.sh

# 3. Access platform: https://${PLATFORM_IP}:8443/applications.html
# 4. Access AI Gateway: https://${PLATFORM_IP}:8443/ai-gateway/
```

#### ⚡ **Development**
```bash
# Quick development setup
cd docker && docker-compose up --build

# Access at: http://localhost:3000/
```

#### 🔄 **Full Containerization**
```bash
# Complete isolated environment
./start-containerized-platform.sh start-build

# Access at: https://localhost:8443/
```

## 🏗️ **Architecture Overview**

### **Core Services**
- **🧠 Chat Copilot**: Microsoft Semantic Kernel AI chat platform
- **🌐 OpenWebUI**: Advanced LLM interface with multiple models
- **🚀 Advanced AI Stack**: High-performance vLLM + Oobabooga + KoboldCpp integration
- **🔍 Perplexica**: AI-powered web search with real-time internet access
- **🕵️ SearXNG**: Privacy-focused search engine
- **👥 AutoGen Studio**: Multi-agent conversation platform
- **🏭 Magentic-One**: Microsoft's flagship multi-agent system
- **💻 VS Code Web**: Cloud-based development environment

### **Network & Security**
- **🔒 SSL Termination**: nginx with Tailscale certificates
- **🌐 Reverse Proxy**: Intelligent routing and load balancing
- **🔐 Tailscale VPN**: Secure mesh networking
- **📊 Health Monitoring**: Automated service health checks

### **Technology Stack**
- **.NET 8.0** with ASP.NET Core and SignalR
- **React 18** with TypeScript and Material-UI
- **Microsoft Semantic Kernel** for AI orchestration
- **vLLM** for high-performance LLM inference
- **Oobabooga** for advanced text generation features
- **KoboldCpp** for creative writing and roleplay
- **Docker & Docker Compose** for containerization
- **nginx** for reverse proxy and SSL termination
- **PostgreSQL** & **Qdrant** for data storage

## 📋 **Complete Service Directory**

### **Core Platform Services**
| Service | Production URL | Development URL | Description |
|---------|----------------|-----------------|-------------|
| **🎛️ Control Panel** | `https://${PLATFORM_IP}:8443/hub` | `http://localhost:3000/control-panel.html` | Platform management dashboard |
| **🌐 Applications Hub** | `https://${PLATFORM_IP}:8443/applications.html` | `http://localhost:3000/applications.html` | Service directory and launcher |
| **💬 Chat Copilot UI** | `https://${PLATFORM_IP}:8443/copilot/` | `http://localhost:3000/` | AI chat interface |
| **🔌 Chat Copilot API** | `https://${PLATFORM_IP}:8443/copilot/api/` | `http://localhost:3080/` | REST API endpoints |
| **🏥 Health Check** | `https://${PLATFORM_IP}:8443/copilot/healthz` | `http://localhost:3080/healthz` | System health status |

### **🚀 Advanced AI Stack Services**
| Service | Production URL | Development URL | Description | Status |
|---------|----------------|-----------------|-------------|--------|
| **🧠 DeepSeek R1** | `https://${PLATFORM_IP}:8443/ai-stack/reasoning/` | `http://localhost:8000` | Ultra-high performance reasoning and analysis | ⚡ Auto Start |
| **⚡ Mistral Small** | `https://${PLATFORM_IP}:8443/ai-stack/general/` | `http://localhost:8001` | Fast general-purpose AI for everyday tasks | ⚡ Auto Start |
| **💻 DeepSeek Coder** | `https://${PLATFORM_IP}:8443/ai-stack/coding/` | `http://localhost:8002` | Specialized AI for code generation and debugging | ⚡ Auto Start |
| **🎛️ Oobabooga WebUI** | `https://${PLATFORM_IP}:8443/ai-stack/advanced/` | `http://localhost:7860` | Advanced text generation with multimodal support | ⚡ Auto Start |
| **🎛️ Oobabooga API** | `https://${PLATFORM_IP}:8443/ai-stack/api/` | `http://localhost:5000` | API endpoint for integrations | ⚡ Auto Start |
| **✍️ KoboldCpp** | `https://${PLATFORM_IP}:8443/ai-stack/creative/` | `http://localhost:5001` | Creative writing and roleplay AI interface | ⚡ Auto Start |
| **🌐 AI Stack Gateway** | `https://${PLATFORM_IP}:8443/ai-gateway/` | `http://localhost:9000` | Unified API with intelligent task routing | ⚡ Auto Start |

### **AI & Automation Services**
| Service | Production URL | Description | Status |
|---------|----------------|-------------|--------|
| **👥 AutoGen Studio** | `https://${PLATFORM_IP}:8443/autogen/` | Multi-agent conversation platform | 🔄 Manual Start |
| **🏭 Magentic-One** | `https://${PLATFORM_IP}:8443/magentic/` | Microsoft flagship multi-agent system | 🔄 Manual Start |
| **🔗 Webhook Server** | `https://${PLATFORM_IP}:8443/webhook/` | GitHub integration & automation | 🔄 Manual Start |
| **🧠 Ollama API** | `https://${PLATFORM_IP}:8443/ollama-api/` | Local LLM API access | 🔄 Manual Start |

### **Search & Discovery Services**  
| Service | Production URL | Description | Status |
|---------|----------------|-------------|--------|
| **🔍 Perplexica** | `https://${PLATFORM_IP}:8443/perplexica/` | AI-powered web search | 🔄 Manual Start |
| **🕵️ SearXNG** | `https://${PLATFORM_IP}:8443/searxng/` | Privacy-focused search engine | 🔄 Manual Start |

### **Network & Management Services**
| Service | Production URL | Description | Status |
|---------|----------------|-------------|--------|
| **📡 Port Scanner** | `https://${PLATFORM_IP}:8443/portscanner/` | Network discovery & monitoring | 🔄 Manual Start |
| **⚙️ Nginx Manager** | `https://${PLATFORM_IP}:8443/nginx/` | Web server management | 🔄 Manual Start |
| **🌐 HTTP Gateway** | `https://${PLATFORM_IP}:8443/gateway-http/` | HTTP traffic gateway | 🔄 Manual Start |
| **🔒 HTTPS Gateway** | `https://${PLATFORM_IP}:8443/gateway-https/` | HTTPS traffic gateway | 🔄 Manual Start |
| **🛡️ Fortinet Manager** | `https://${PLATFORM_IP}:8443/fortinet/` | Network security management | 🔄 Manual Start |
| **💾 Bacula Backup** | `https://${PLATFORM_IP}:8443/bacula/` | Backup management system | 🔄 Manual Start |

## 🚀 **Advanced AI Stack**

### **High-Performance AI Services**

The platform features a **unified AI Stack** with specialized models for different tasks, powered by **vLLM**, **Oobabooga**, and **KoboldCpp** for maximum performance and flexibility.

#### **🎯 Task-Specific AI Models**

| **Task Type** | **Recommended Service** | **Port** | **Use Cases** |
|---------------|-------------------------|----------|---------------|
| **🧠 Reasoning** | DeepSeek R1 | 8000 | Complex analysis, problem-solving, logical reasoning |
| **⚡ General** | Mistral Small | 8001 | Fast responses, general questions, everyday tasks |
| **💻 Coding** | DeepSeek Coder | 8002 | Code generation, debugging, technical documentation |
| **🎨 Creative** | KoboldCpp | 5001 | Creative writing, storytelling, roleplay |
| **🎛️ Advanced** | Oobabooga | 7860 | Multimodal, advanced features, custom workflows |

#### **🌐 Unified AI Gateway (Port 9000)**

**Smart Request Routing** - The AI Gateway automatically routes requests to the optimal model based on task type:

```bash
# Reasoning tasks → DeepSeek R1
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"task_type": "reasoning", "prompt": "Analyze this complex problem..."}'

# Coding tasks → DeepSeek Coder  
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"task_type": "coding", "prompt": "Write a Python function to..."}'

# Creative tasks → KoboldCpp
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"task_type": "creative", "prompt": "Write a short story about..."}'
```

#### **🔥 Performance Features**

- **⚡ vLLM Acceleration**: GPU-optimized inference for 3x faster responses
- **🧠 Model Specialization**: Each AI optimized for specific task types
- **🌐 Intelligent Routing**: Automatic model selection based on request content
- **💾 Memory Optimization**: Efficient VRAM usage across multiple models
- **📊 Load Balancing**: Distribute requests across available resources

#### **🎮 Advanced Features**

- **🖼️ Multimodal Support**: Image analysis with Oobabooga
- **🎭 Character Roleplay**: Advanced character creation with KoboldCpp
- **💬 Conversation Memory**: Persistent context across sessions
- **🔄 Model Swapping**: Hot-swap models without service restart
- **📈 Usage Analytics**: Real-time performance monitoring

#### **🛠️ AI Stack Management**

```bash
# Start AI Stack
~/ai-stack/manage_stack.sh start

# Check status
~/ai-stack/manage_stack.sh status

# Monitor resources
python3 ~/ai-stack/monitor.py

# Health check
curl http://localhost:9000/health
```

## 🔧 **Configuration**

### **🌐 Portable Environment Setup**

The platform is designed for **cross-system portability** with environment-based configuration:

```bash
# 1. Copy and customize environment template
cp .env.template .env

# 2. Auto-detect system configuration
./scripts/setup/detect-system.sh

# 3. Update environment with your settings
nano .env
```

#### **Key Environment Variables**
```bash
# System Configuration (auto-detected)
PLATFORM_ROOT=/path/to/your/installation
PLATFORM_IP=your.server.ip
PLATFORM_USER=your_user

# Service Ports (customizable)
CHAT_COPILOT_BACKEND_PORT=11000
CHAT_COPILOT_FRONTEND_PORT=3000
AI_GATEWAY_PORT=9000

# AI Services
DEEPSEEK_R1_PORT=8000
MISTRAL_PORT=8001
DEEPSEEK_CODER_PORT=8002
OOBABOOGA_WEBUI_PORT=7860
OOBABOOGA_API_PORT=5000
KOBOLDCPP_PORT=5001

# Required API Keys
AZURE_OPENAI_API_KEY=your_azure_key
OPENAI_API_KEY=your_openai_key
POSTGRES_PASSWORD=secure_password
JWT_SECRET=your_jwt_secret
```

### **🏢 HA (High Availability) Support**

For HA pairs and multi-node deployments:

```bash
# Node 1 (.env.node1)
PLATFORM_IP=10.0.1.10
NODE_ID=node1
HA_ENABLED=true
HA_PEER_IP=10.0.1.11

# Node 2 (.env.node2)  
PLATFORM_IP=10.0.1.11
NODE_ID=node2
HA_ENABLED=true
HA_PEER_IP=10.0.1.10
```

### **SSL Certificates (Production)**
```bash
# Tailscale certificates should be at:
/etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt
/etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key
```

## 🛠️ **Development**

### **Backend (.NET)**
```bash
# Build and run
cd webapi && dotnet run --urls http://0.0.0.0:11000

# Run tests
cd integration-tests && dotnet test

# Build solution
dotnet build CopilotChat.sln
```

### **Frontend (React)**
```bash
cd webapp

# Install dependencies
yarn install

# Development server
yarn start

# Build for production
yarn build

# Run tests
yarn test
```

### **Validation & Testing**
```bash
# Comprehensive validation
./validate-deployment.sh

# Quick environment check
./validate-deployment.sh quick

# Test Docker builds
./validate-deployment.sh build-test
```

## 📚 **Documentation**

### **Primary References**
- 📖 **[Complete Deployment Guide](docs/deployment/COMPREHENSIVE_DEPLOYMENT_GUIDE.md)** - All deployment strategies and production setup
- 🎯 **[Containerized Setup](docs/deployment/CONTAINERIZED_SETUP.md)** - Docker-based deployment
- 🤖 **[Claude Instructions](CLAUDE.md)** - AI assistant guidance and development commands
- 📋 **[Project Organization](PROJECT_ORGANIZATION.md)** - Directory structure and architecture

### **Specialized Guides**
- 🔧 **[Setup Guides](docs/setup-guides/)** - Service-specific configuration
- 🚨 **[Troubleshooting](docs/troubleshooting/)** - Problem resolution
- 🏢 **[Business Documentation](docs/business-docs/)** - Partnership and deployment guides

## 🏥 **Health & Monitoring**

### **Health Checks**
```bash
# Platform status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Core service health
curl -k https://${PLATFORM_IP}:8443/copilot/healthz

# AI Stack Gateway health
curl http://localhost:9000/health

# Individual AI services
curl http://localhost:8000/health  # DeepSeek R1
curl http://localhost:8001/health  # Mistral Small
curl http://localhost:8002/health  # DeepSeek Coder

# Validation script
./validate-deployment.sh
```

### **Logs & Debugging**
```bash
# Container logs
docker logs nginx-ssl
docker logs ai-platform-caddy

# Service restart
docker restart nginx-ssl

# Health check
./validate-deployment.sh
```

## 🚀 **Deployment Options**

### **1. Production SSL (Recommended)**
- ✅ nginx SSL termination with Tailscale certificates
- ✅ Production-ready configuration
- ✅ Automatic HTTPS redirect
- 🎯 **Command**: `./start-ssl-platform.sh`
- 🌐 **Access**: `https://100.123.10.72:8443/`

### **2. Development Quick Start**
- ✅ Fast startup (~30 seconds)
- ✅ Core Chat Copilot functionality
- ✅ Hot reload for development
- 🎯 **Command**: `cd docker && docker-compose up --build`
- 🌐 **Access**: `http://localhost:3000/`

### **3. Containerized Full Stack**
- ✅ Complete service isolation
- ✅ Caddy automatic HTTPS
- ✅ All services containerized
- 🎯 **Command**: `./start-containerized-platform.sh start-build`
- 🌐 **Access**: `https://localhost:8443/`

### **4. Hybrid/Custom**
- ✅ Flexible manual configuration
- ✅ Mix of containerized and host services
- ✅ Custom service combinations
- 🎯 **Command**: `./start-nginx-platform.sh` + manual services

## 🔐 **Security Features**

- 🔒 **SSL/TLS Encryption** with Tailscale certificates
- 🛡️ **Security Headers** (HSTS, X-Frame-Options, CSP)
- 🌐 **Tailscale VPN** integration for secure access
- 🔐 **JWT Authentication** for API security
- 🚪 **Network Segmentation** with Docker networks
- 📝 **Security Logging** and monitoring

## 🎯 **Getting Started Checklist**

1. **✅ Clone Repository**: `git clone <repository-url>`
2. **✅ Configure Environment**: `cp .env.template .env` (edit with your keys)
3. **✅ Validate Setup**: `./validate-deployment.sh`
4. **✅ Choose Deployment**: Pick strategy based on your needs
5. **✅ Start Platform**: Run appropriate startup script
6. **✅ Verify Access**: Open browser to platform URL
7. **✅ Explore Services**: Use control panel and applications hub

## 🤝 **Contributing**

See [CONTRIBUTING.md](docs/project-meta/CONTRIBUTING.md) for contribution guidelines.

## 📄 **License**

See [LICENSE](LICENSE) for license information.

## 🆘 **Support**

- 📖 **Documentation**: Check guides in `docs/` directory
- 🚨 **Issues**: See troubleshooting guides in `docs/troubleshooting/`
- 🤖 **AI Help**: All instructions available in `CLAUDE.md`
- ✅ **Validation**: Run `./validate-deployment.sh` for diagnostics

---

**🎉 Your AI Research Platform is ready for production use with minimal deployment friction!**