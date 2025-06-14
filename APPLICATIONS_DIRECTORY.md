# 🌐 AI Research Platform - Application Directory

**Tailscale Network Access Point**: `100.123.10.72`  
**Last Updated**: June 14, 2025

## 🤖 AI & Research Applications

### Primary AI Chat & Research
| Application | URL | Description | Status |
|-------------|-----|-------------|---------|
| **OpenWebUI** | [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net) | Advanced LLM Chat Interface with Multiple Models | ✅ Active |
| **Chat Copilot** | [http://100.123.10.72:10500](http://100.123.10.72:10500) | Microsoft Semantic Kernel AI Chat Platform | ✅ Active |
| **Chat Copilot API** | [https://100.123.10.72:40443](https://100.123.10.72:40443) | Backend REST API for AI Chat | ✅ Active |
| **Perplexica** | [http://100.123.10.72:3999/perplexica](http://100.123.10.72:3999/perplexica) | AI Search with Real-time Internet Access | ✅ Active |
| **SearchNG** | [http://100.123.10.72:4000](http://100.123.10.72:4000) | Privacy-focused Search Engine | ✅ Active |

### AI Research URLs
- **OpenWebUI (Primary)**: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- **Chat Interface**: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- **AI Web Search**: [http://100.123.10.72:3999/perplexica](http://100.123.10.72:3999/perplexica)
- **Search Discovery**: [http://100.123.10.72:3999/perplexica/discover](http://100.123.10.72:3999/perplexica/discover)
- **Research Library**: [http://100.123.10.72:3999/perplexica/library](http://100.123.10.72:3999/perplexica/library)

---

## 🛠️ Development & Management Tools

### Development Environment
| Application | URL | Description | Status |
|-------------|-----|-------------|---------|
| **Material-UI Control Panel** | [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html) | Interactive System Management Dashboard | ✅ Active |
| **VS Code Web (Enhanced)** | [http://100.123.10.72:57081](http://100.123.10.72:57081) | Full VS Code Server with AI Development Workspace | ✅ Active |
| **Port Scanner Dashboard** | [http://100.123.10.72:10200](http://100.123.10.72:10200) | Network Discovery & Monitoring | ✅ Active |
| **AutoGen Studio** | [http://100.123.10.72:8085](http://100.123.10.72:8085) | Multi-Agent Conversation Platform with Ollama | ✅ Active |
| **Magentic-One Platform** | [http://100.123.10.72:8086](http://100.123.10.72:8086) | Advanced Multi-Agent Task Solving System | 🟡 Configured |

### Network Management
| Application | URL | Description | Status |
|-------------|-----|-------------|---------|
| **Fortinet Manager** | [http://100.123.10.72:3001](http://100.123.10.72:3001) | Network Security Management UI | ✅ Active |
| **Fortinet API** | [http://100.123.10.72:5000](http://100.123.10.72:5000) | Network Management REST API | ✅ Active |
| **Nginx Gateway** | [http://100.123.10.72:8082](http://100.123.10.72:8082) | Web Services Proxy | ✅ Active |
| **Nginx HTTPS** | [https://100.123.10.72:8443](https://100.123.10.72:8443) | Secure Web Gateway | ✅ Active |

---

## 🔧 Backend Services & APIs

### AI & ML Services
| Service | Endpoint | Description | Status |
|---------|----------|-------------|---------|
| **Chat Copilot API** | `https://100.123.10.72:40443/api` | Semantic Kernel API | ✅ Active |
| **Health Check** | `https://100.123.10.72:40443/healthz` | Service Health Monitor | ✅ Active |
| **Ollama (Local LLM)** | `http://localhost:11434` | Local Language Models | ✅ Ready |

### Infrastructure Services
| Service | Internal Port | Description | Status |
|---------|---------------|-------------|---------|
| **RabbitMQ** | `:5672` | Message Queue (Ready for Chat Copilot) | 🟡 Configured |
| **RabbitMQ Management** | `:15672` | Queue Management UI | 🟡 Configured |
| **Qdrant Vector DB** | `:6333` | Vector Database (Ready for Chat Copilot) | 🟡 Configured |

---

## 📊 Docker Extensions & Tools

### Active Extensions
| Extension | Description | Status |
|-----------|-------------|---------|
| **AI Tools for Devs** | AI-powered development assistance | ✅ Running |
| **Mongo Express** | MongoDB management interface | ✅ Running |
| **Image Tools** | Container image utilities | ✅ Running |
| **VS Code Installer** | VS Code Docker extension | ✅ Running |

---

## 🚀 Quick Access Dashboard

### Most Used Applications
```bash
# AI Research
OpenWebUI:       https://ubuntuaicodeserver-1.tail5137b4.ts.net
Chat Copilot:    http://100.123.10.72:10500
AI Search:       http://100.123.10.72:3999
Code Editor:     http://100.123.10.72:57081

# Network Tools  
Port Scanner:    http://100.123.10.72:10200
Security Mgmt:   http://100.123.10.72:3001
API Gateway:     http://100.123.10.72:8082
```

### API Endpoints
```bash
# Primary APIs
Chat API:        https://100.123.10.72:40443/api
Health Check:    https://100.123.10.72:40443/healthz
Fortinet API:    http://100.123.10.72:5000/api
Search API:      http://100.123.10.72:4000
```

---

## 🔐 Access Information

**Network**: Tailscale VPN (`100.123.10.72`)  
**Authentication**: Most services run without authentication for local development  
**HTTPS**: Available where configured (Chat Copilot, Nginx)  
**CORS**: Configured for Tailscale network access  

---

## 🎯 Available Features

### AI Capabilities
- ✅ OpenAI GPT-4 Integration
- ✅ Internet-connected AI Search
- ✅ Document Processing
- ✅ Multi-modal Chat
- 🟡 Local LLM Support (Ollama configured)

### Development Tools
- ✅ Cloud-based Code Editor
- ✅ Network Discovery
- ✅ Container Management
- ✅ API Development

### Research Tools
- ✅ AI-powered Search
- ✅ Knowledge Management
- ✅ Multi-source Research
- ✅ Real-time Web Access

---

## 🛠️ Deployment Commands

### Start All Services
```bash
# Individual services
docker start perplexica-app-1 perplexica-searxng-1
docker start fortinet-manager_frontend_1 fortinet-manager_backend_1
docker start port-scanner-tailscale

# Check status
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

### Access from Command Line
```bash
# Test connectivity
curl http://100.123.10.72:10500    # Chat Copilot
curl http://100.123.10.72:3999     # Perplexica
curl http://100.123.10.72:10200    # Port Scanner
curl https://100.123.10.72:40443/healthz  # Health Check
```

---

*🎉 Your AI Research Platform is fully operational and accessible across your Tailscale network!*