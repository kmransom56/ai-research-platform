# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AI Research Platform** - a comprehensive multi-agent AI development environment built on Microsoft's Chat Copilot. It combines multiple AI services, local LLMs, and development tools into a unified platform with secure Tailscale networking.

## 🚀 **NEW: Advanced AI Stack Integration**

### **High-Performance AI Services**
The platform now includes an **advanced AI stack** with vLLM, Oobabooga, and KoboldCpp integration:

#### **🎯 AI Stack Services (Ports 8000-9000)**
- **vLLM DeepSeek R1**: http://localhost:8000 (Reasoning and complex analysis)
- **vLLM Mistral Small**: http://localhost:8001 (General purpose, fast responses)  
- **vLLM DeepSeek Coder**: http://localhost:8002 (Code generation and debugging)
- **Oobabooga WebUI**: http://localhost:7860 (Advanced features, multimodal)
- **Oobabooga API**: http://localhost:5000 (API endpoint for integrations)
- **KoboldCpp**: http://localhost:5001 (Creative writing and roleplay)
- **AI Stack Gateway**: http://localhost:9000 (Unified API with smart routing)

#### **🛠️ Integration Requirements**
When working with `application.html` and `control-panel.html`:

1. **Add Advanced AI Stack Services** to the application cards section
2. **Update service monitoring** to include new ports (8000-8002, 5000-5001, 7860, 9000)
3. **Add quick links** for direct access to each service
4. **Include health checks** for all new AI services
5. **Add service descriptions** explaining each AI service's purpose

#### **📝 HTML Integration Code Snippets**

For `application.html`, add these service cards:

```html
<!-- Advanced AI Stack Services -->
<div class="service-section">
    <h3>🚀 Advanced AI Stack</h3>
    
    <!-- vLLM Services -->
    <div class="service-card">
        <h4>🧠 DeepSeek R1 (Reasoning)</h4>
        <p>Ultra-high performance reasoning and complex analysis</p>
        <div class="service-links">
            <a href="http://localhost:8000/docs" class="btn-link">API Docs</a>
            <a href="http://localhost:8000/v1/models" class="btn-link">Models</a>
        </div>
        <div class="service-status" data-url="http://localhost:8000/health">Checking...</div>
    </div>
    
    <div class="service-card">
        <h4>⚡ Mistral Small (General)</h4>
        <p>Fast general-purpose AI for everyday tasks</p>
        <div class="service-links">
            <a href="http://localhost:8001/docs" class="btn-link">API Docs</a>
            <a href="http://localhost:8001/v1/models" class="btn-link">Models</a>
        </div>
        <div class="service-status" data-url="http://localhost:8001/health">Checking...</div>
    </div>
    
    <div class="service-card">
        <h4>💻 DeepSeek Coder</h4>
        <p>Specialized AI for code generation and debugging</p>
        <div class="service-links">
            <a href="http://localhost:8002/docs" class="btn-link">API Docs</a>
            <a href="http://localhost:8002/v1/models" class="btn-link">Models</a>
        </div>
        <div class="service-status" data-url="http://localhost:8002/health">Checking...</div>
    </div>
    
    <!-- Oobabooga -->
    <div class="service-card">
        <h4>🎛️ Oobabooga WebUI</h4>
        <p>Advanced text generation with multimodal support</p>
        <div class="service-links">
            <a href="http://localhost:7860" class="btn-primary">Open WebUI</a>
            <a href="http://localhost:5000/docs" class="btn-link">API Docs</a>
        </div>
        <div class="service-status" data-url="http://localhost:5000/health">Checking...</div>
    </div>
    
    <!-- KoboldCpp -->
    <div class="service-card">
        <h4>✍️ KoboldCpp</h4>
        <p>Creative writing and roleplay AI interface</p>
        <div class="service-links">
            <a href="http://localhost:5001" class="btn-primary">Open KoboldCpp</a>
            <a href="http://localhost:5001/api" class="btn-link">API Info</a>
        </div>
        <div class="service-status" data-url="http://localhost:5001">Checking...</div>
    </div>
    
    <!-- Unified Gateway -->
    <div class="service-card featured">
        <h4>🌐 AI Stack Gateway</h4>
        <p>Unified API with intelligent task routing</p>
        <div class="service-links">
            <a href="http://localhost:9000/health" class="btn-primary">Health Check</a>
            <a href="http://localhost:9000/docs" class="btn-link">API Docs</a>
        </div>
        <div class="service-status" data-url="http://localhost:9000/health">Checking...</div>
    </div>
</div>
```

For `control-panel.html`, add these quick actions:

```html
<!-- AI Stack Management -->
<div class="control-section">
    <h3>🚀 Advanced AI Stack</h3>
    
    <div class="control-grid">
        <button onclick="manageAIStack('start')" class="btn-primary">Start AI Stack</button>
        <button onclick="manageAIStack('stop')" class="btn-danger">Stop AI Stack</button>
        <button onclick="manageAIStack('restart')" class="btn-warning">Restart AI Stack</button>
        <button onclick="checkAIStackStatus()" class="btn-info">Check Status</button>
    </div>
    
    <div class="service-grid">
        <div class="service-quick-link">
            <a href="http://localhost:8000/docs">DeepSeek R1 API</a>
            <span class="port">:8000</span>
        </div>
        <div class="service-quick-link">
            <a href="http://localhost:8001/docs">Mistral API</a>
            <span class="port">:8001</span>
        </div>
        <div class="service-quick-link">
            <a href="http://localhost:8002/docs">Coder API</a>
            <span class="port">:8002</span>
        </div>
        <div class="service-quick-link">
            <a href="http://localhost:7860">Oobabooga</a>
            <span class="port">:7860</span>
        </div>
        <div class="service-quick-link">
            <a href="http://localhost:5001">KoboldCpp</a>
            <span class="port">:5001</span>
        </div>
        <div class="service-quick-link featured">
            <a href="http://localhost:9000/health">AI Gateway</a>
            <span class="port">:9000</span>
        </div>
    </div>
</div>

<script>
// AI Stack Management Functions
function manageAIStack(action) {
    fetch('/api/ai-stack/' + action, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            showNotification('AI Stack ' + action + ' initiated', 'info');
            setTimeout(checkAIStackStatus, 5000);
        })
        .catch(error => {
            showNotification('Error managing AI Stack: ' + error.message, 'error');
        });
}

function checkAIStackStatus() {
    fetch('http://localhost:9000/health')
        .then(response => response.json())
        .then(data => {
            displayAIStackStatus(data);
        })
        .catch(error => {
            showNotification('AI Stack Gateway not responding', 'warning');
        });
}

function displayAIStackStatus(status) {
    const statusDiv = document.getElementById('ai-stack-status') || createStatusDiv();
    let html = '<h4>AI Stack Status</h4><div class="status-grid">';
    
    const services = {
        'reasoning': 'DeepSeek R1',
        'general': 'Mistral', 
        'coding': 'DeepSeek Coder',
        'creative': 'KoboldCpp',
        'advanced': 'Oobabooga'
    };
    
    for (const [key, name] of Object.entries(services)) {
        const isOnline = status[key] === 'online';
        html += `<div class="status-item ${isOnline ? 'online' : 'offline'}">
                    <span class="service-name">${name}</span>
                    <span class="status-indicator">${isOnline ? '🟢' : '🔴'}</span>
                 </div>`;
    }
    
    html += '</div>';
    statusDiv.innerHTML = html;
}

function createStatusDiv() {
    const div = document.createElement('div');
    div.id = 'ai-stack-status';
    div.className = 'status-panel';
    document.querySelector('.control-section').appendChild(div);
    return div;
}
</script>
```

#### **🔧 CSS Styling Additions**

Add to your CSS file:

```css
/* Advanced AI Stack Styles */
.service-section {
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #f9f9f9;
}

.service-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.service-card.featured {
    border-color: #007bff;
    background: linear-gradient(135deg, #f8f9ff 0%, #fff 100%);
}

.service-links {
    margin: 10px 0;
}

.service-status {
    margin-top: 10px;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

.service-status.online {
    background: #d4edda;
    color: #155724;
}

.service-status.offline {
    background: #f8d7da;
    color: #721c24;
}

.control-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin-bottom: 20px;
}

.service-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
}

.service-quick-link {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    text-decoration: none;
}

.service-quick-link.featured {
    border-color: #007bff;
    background: #f8f9ff;
}

.port {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #666;
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
}

.status-panel {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-radius: 4px;
    background: white;
    border: 1px solid #ddd;
}

.status-item.online {
    border-color: #28a745;
    background: #d4edda;
}

.status-item.offline {
    border-color: #dc3545;
    background: #f8d7da;
}
```

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

### Advanced AI Stack Management
```bash
# Start the complete AI stack
~/ai-stack/manage_stack.sh start

# Check AI stack status
~/ai-stack/manage_stack.sh status

# Stop AI stack
~/ai-stack/manage_stack.sh stop

# Monitor system resources
python3 ~/ai-stack/monitor.py
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

### Advanced AI Stack Services (Ports 8000-9000)
- **vLLM DeepSeek R1**: 8000 (Reasoning)
- **vLLM Mistral Small**: 8001 (General)
- **vLLM DeepSeek Coder**: 8002 (Coding)
- **Oobabooga API**: 5000 (Advanced API)
- **KoboldCpp**: 5001 (Creative Writing)
- **Oobabooga WebUI**: 7860 (Web Interface)
- **AI Stack Gateway**: 9000 (Unified API)

### Restaurant Network Management (Ports 11030-11040)
- **IT & Network Voice Interface**: 11030
- **Restaurant Operations Voice**: 11032
- **Main AI Network Management Hub**: 11040

### Key Technologies
- **.NET 8.0** with ASP.NET Core and SignalR
- **Microsoft Semantic Kernel** for AI orchestration
- **React 18** with TypeScript and Material-UI
- **vLLM** for high-performance LLM inference
- **Oobabooga** for advanced text generation features
- **KoboldCpp** for creative writing and roleplay
- **Docker & Docker Compose** for containerization
- **Neo4j** for graph database and knowledge graphs

## Development Workflow

1. **Check platform status**: `./scripts/platform-management/manage-platform.sh status`
2. **Start development**: Use platform startup scripts
3. **Backend changes**: Work in webapi/ directory, standard .NET development
4. **Frontend changes**: Work in webapp/ directory, React with hot reload
5. **AI Stack management**: Use `~/ai-stack/manage_stack.sh`
6. **Platform services**: Managed via Docker Compose and management scripts

## Important Notes

- **Port standardization**: Core services 11000-12000, AI Stack 8000-9000, Gateway 9000
- **Advanced AI Integration**: vLLM + Oobabooga + KoboldCpp for specialized tasks
- **Task-based routing**: Reasoning, coding, creative, general purpose AI endpoints
- **Hardware optimization**: Optimized for high-memory GPU systems (96GB+ VRAM)
- **Unified API**: Single gateway endpoint for intelligent request routing

## Quick References

### Health Checks
- Backend: http://localhost:11000/healthz
- AI Stack Gateway: http://localhost:9000/health
- Individual AI services: Check ports 8000-8002, 5000-5001, 7860
- Platform status: `./check-platform-status.sh`

### AI Stack Quick Test
```bash
# Test unified gateway
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reasoning",
    "prompt": "Explain the benefits of AI integration",
    "max_tokens": 200
  }'
```

This file contains all the instructions needed to properly integrate the Advanced AI Stack services into your platform's web interface. Copy this to your main project directory and use it to guide the HTML file updates!