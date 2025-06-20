**NOTE**: This repository has been **transformed** into a comprehensive **AI Research Platform** with Tailscale network inte## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [🎮 **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator
- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Commercialization strategy
- [🤝 **GitHub Collaboration**](add-github-collaborator.sh) - Team management toolson. This extends the original Chat Copilot sample with multi-agent capabilities, local LLMs, and advanced AI research tools.

# 🤖 AI Research Platform (Based on Chat Copilot)

A comprehensive, self-hosted AI research and development platform with secure remote access, optimized for high-performance GPU systems.

[![GitHub Stars](https://img.shields.io/github/stars/kmransom56/ai-research-platform?style=social)](https://github.com/kmransom56/ai-research-platform)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Ubuntu%2FDebian-orange.svg)](https://ubuntu.com)

## 🚀 Quick Installation

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/kmransom56/ai-research-platform/main/install-ai-platform.sh | bash
```

### Or Clone and Install

```bash
git clone https://github.com/kmransom56/ai-research-platform.git
cd ai-research-platform
./install-ai-platform.sh
```

### System Requirements

- **Minimum**: Ubuntu 20.04+, 16GB RAM, 100GB storage
- **Recommended**: 64GB+ RAM, NVIDIA GPU with 8GB+ VRAM
- **High-Performance**: 72GB+ GPU VRAM, 128GB+ RAM, NVMe SSD

## 📦 Deployment Package

Create portable installation for other systems:

```bash
./create-deployment-package.sh
# Transfer /tmp/ai-research-platform-*.tar.gz to target system
```

Built on Microsoft [Semantic Kernel](https://github.com/microsoft/semantic-kernel), this platform includes:

## 🚀 Platform Components

### Core AI Services

1. **Chat Copilot** - [.NET web API service](./webapi/) + [React web app](./webapp/)
2. **AutoGen Studio** - Multi-agent conversation platform with Ollama integration
3. **OpenWebUI** - Advanced LLM interface with multiple model support
4. **Perplexica** - AI-powered search with real-time internet access
5. **SearchNG** - Privacy-focused search engine

### Research & Development Tools

6. **VS Code Online** - Browser-based development environment
7. **Port Scanner** - Network discovery and monitoring
8. **Material-UI Control Panel** - Centralized system management
9. **GitHub Webhook System** - Automated deployment pipeline

### Multi-Agent AI Capabilities

- **Code Review Teams** - Multi-agent code analysis with specialized roles
- **Research Analysis** - Collaborative research with fact-checking
- **Problem Solving** - Complex problem decomposition and solution design
- **Local LLM Integration** - 7+ Ollama models including llama3.2, mistral, deepseek-coder

### Business & Collaboration Tools

10. **GitHub Collaborator Management** - Interactive scripts for team collaboration
11. **Business Partnership Framework** - Commercialization and revenue strategies
12. **Deployment Package Creator** - Portable installation for client systems
13. **Market Analysis & Legal Framework** - IP protection and business setup

## 🎮 GPU Optimization & Large Models

This platform is optimized for high-memory GPU systems. For systems with 72GB+ VRAM:

### Supported Large Models

```bash
# After installation, install models via Ollama:
ollama pull llama2:70b          # ~40GB VRAM - Complex reasoning
ollama pull codellama:34b       # ~20GB VRAM - Programming tasks
ollama pull mixtral:8x7b        # ~45GB VRAM - Mixture of experts
ollama pull deepseek-coder:33b  # ~20GB VRAM - Code generation
```

### Memory Optimization

- **Conservative**: Use 60GB, leave 12GB free for system
- **Aggressive**: Use 68GB, leave 4GB free for optimal performance
- **Concurrent**: Run multiple models simultaneously

See [GPU_OPTIMIZATION_72GB.md](GPU_OPTIMIZATION_72GB.md) for detailed configuration.

## 🚀 Easy Deployment to New Systems

### Create Deployment Package

```bash
./create-deployment-package.sh
# Creates: /tmp/ai-research-platform-YYYYMMDD.tar.gz
```

### Deploy on Target System

```bash
# Transfer package
scp /tmp/ai-research-platform-*.tar.gz user@target-server:~/

# Extract and deploy
tar -xzf ai-research-platform-*.tar.gz
cd ai-research-platform-*
./quick-deploy.sh
```

### Post-Deployment Configuration

1. Configure API keys in `config/.env`
2. Setup Tailscale: `sudo tailscale up`
3. Update domain in Caddyfile
4. Start platform: `./startup-platform-clean.sh`

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**: Admin, push, or pull access levels
- ✅ **User validation**: Verifies GitHub usernames exist
- ✅ **Batch operations**: Efficient team onboarding

### Commercial Opportunities

This platform addresses high-value markets:

| Market Segment                   | Size  | Our Position           |
| -------------------------------- | ----- | ---------------------- |
| **Enterprise AI Infrastructure** | $50B+ | 72GB GPU optimization  |
| **AI Development Tools**         | $15B+ | Complete AutoGen stack |
| **Privacy-Focused AI**           | $8B+  | On-premises deployment |

### Revenue Models

- **SaaS Licensing**: $200-$50K per client annually
- **Professional Services**: AI implementation consulting
- **Hardware Optimization**: GPU-specific deployment packages

### Business Documentation

- [💼 **Business Partnership Guide**](BUSINESS_PARTNERSHIP_GUIDE.md) - Complete commercialization strategy
- [🤝 **Team Collaboration**](add-github-collaborator.sh) - GitHub repository management
- [🚀 **Market Analysis**](BUSINESS_PARTNERSHIP_GUIDE.md#financial-projections) - Revenue projections and strategy

## 📚 Documentation

- [📋 **Installation Guide**](INSTALLATION_GUIDE.md) - Detailed setup instructions
- [� **GPU Optimization**](GPU_OPTIMIZATION_72GB.md) - High-performance GPU configuration
- [🔧 **Deployment Package**](create-deployment-package.sh) - Portable installation creator

## 🌐 Access URLs (Post-Installation)

**Secure HTTPS Access via Tailscale:**

- **Main Hub**: `https://your-tailscale-domain.ts.net`
- **Chat Copilot**: `https://copilot.your-tailscale-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-tailscale-domain.ts.net`
- **Perplexica**: `https://perplexica.your-tailscale-domain.ts.net`
- **VS Code**: `https://vscode.your-tailscale-domain.ts.net`

**Current Development URLs:**

**Tailscale IP**: `100.123.10.72`  
**Primary Interfaces**:

- Chat Copilot: [http://100.123.10.72:10500](http://100.123.10.72:10500)
- AutoGen Studio: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- OpenWebUI: [https://ubuntuaicodeserver-1.tail5137b4.ts.net](https://ubuntuaicodeserver-1.tail5137b4.ts.net)
- Control Panel: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)

## 📋 Original Chat Copilot Components

This platform extends the original Chat Copilot with three base components:

1. A frontend application [React web app](./webapp/)
2. A backend REST API [.NET web API service](./webapi/)
3. A [.NET worker service](./memorypipeline/) for processing semantic memory.

These quick-start instructions run the sample locally. They can also be found on the official Chat Copilot Microsoft Learn documentation page for [getting started](https://learn.microsoft.com/semantic-kernel/chat-copilot/getting-started).

To deploy the sample to Azure, please view [Deploying Chat Copilot](./scripts/deploy/README.md) after meeting the [requirements](#requirements) described below.

> **IMPORTANT:** This sample is for educational purposes only and is not recommended for production deployments.

> **IMPORTANT:** Each chat interaction will call Azure OpenAI/OpenAI which will use tokens that you may be billed for.

![Chat Copilot answering a question](https://learn.microsoft.com/en-us/semantic-kernel/media/chat-copilot-in-action.gif)

## 🎯 Platform Features

### 🤖 Multi-Agent AI Capabilities

- **AutoGen Studio** - Create AI agent teams with local Ollama models
- **Collaborative Workflows** - Code review, research analysis, problem solving
- **7+ Local Models** - llama3.2:3b, mistral, deepseek-coder, codellama, and more
- **Zero External Dependencies** - All AI processing stays on your network

### 🔧 Integrated Development Environment

- **VS Code Online** - Full browser-based development environment
- **GitHub Webhook Automation** - Auto-deployment on code changes
- **Material-UI Control Panel** - Centralized system management
- **Network Discovery** - Port scanning and service monitoring

### 🔍 Advanced Search & Research

- **Perplexica AI Search** - Chat with the internet using AI
- **SearchNG** - Privacy-focused search engine
- **OpenWebUI** - Multi-model LLM interface
- **Real-time Internet Access** - Current information retrieval

### 🌐 Tailscale Network Integration

- **Mesh Network Access** - Available across all your devices
- **Secure Communication** - End-to-end encrypted connections
- **Remote Development** - Access from anywhere on your Tailscale network
- **Service Discovery** - Automatic network service mapping

## 💼 Business & Collaboration Features

### GitHub Team Management

Add collaborators to repositories for business partnerships:

```bash
# Interactive collaborator management (recommended)
./add-github-collaborator.sh

# Quick single repository addition
./quick-add-collaborator.sh username admin
```

**Features:**

- ✅ **Multi-repository support**: Add collaborators to multiple repos at once
- ✅ **Permission management**
