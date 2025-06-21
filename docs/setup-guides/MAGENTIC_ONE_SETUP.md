# 🌟 Magentic-One Multi-Agent Platform Setup Guide

**Version**: 1.0.0  
**Platform**: AI Research Platform on Tailscale Network  
**Network Access**: `100.123.10.72:8086`  
**Last Updated**: June 14, 2025

## Overview

Magentic-One is a powerful multi-agent orchestration system inspired by Microsoft's research, designed to tackle complex tasks through collaborative AI agents. This implementation provides a FastAPI web interface with 5 specialized agents working together on your Tailscale network.

## 🤖 Agent Architecture

### Core Agents

| Agent | Role | Model | Specialty |
|-------|------|-------|-----------|
| **Orchestrator** | Coordinator | `llama3.2:3b` | Task planning and agent coordination |
| **WebSurfer** | Research | `mistral:latest` | Web research and information gathering |
| **FileSurfer** | Analysis | `deepseek-coder:6.7b` | File analysis and document processing |
| **Coder** | Development | `deepseek-coder:6.7b` | Code development and technical solutions |
| **ComputerTerminal** | Operations | `llama3.2:3b` | System operations and command execution |

### Team Configurations

- **Research Team**: Orchestrator + WebSurfer + FileSurfer
- **Development Team**: Orchestrator + Coder + Terminal + FileSurfer  
- **Analysis Team**: Orchestrator + FileSurfer + Coder
- **Full Team**: All 5 agents for complex multi-domain tasks

## 🚀 Installation and Setup

### Prerequisites

```bash
# Ensure AutoGen environment is activated
source /home/keith/chat-copilot/autogen-env/bin/activate

# Verify required dependencies
pip install fastapi uvicorn pydantic
```

### Core Files

| File | Purpose | Location |
|------|---------|----------|
| `magentic_one_simple.py` | Core multi-agent system | `/home/keith/chat-copilot/` |
| `magentic_one_server.py` | FastAPI web server | `/home/keith/chat-copilot/` |
| `startup-platform.sh` | Auto-startup script | `/home/keith/chat-copilot/` |

### Configuration

The system automatically configures itself with:
- **Port**: 8086 (HTTP)
- **Host**: 0.0.0.0 (Tailscale accessible)
- **CORS**: Enabled for cross-origin requests
- **Logging**: INFO level with rotation

## 🌐 Web Interface

### Dashboard Access

**Primary URL**: [http://100.123.10.72:8086](http://100.123.10.72:8086)

### API Endpoints

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/` | GET | Main dashboard | Interactive web interface |
| `/api/status` | GET | System status | Health and agent info |
| `/api/chat` | POST | Multi-agent chat | Send tasks to agents |
| `/api/agents` | GET | Agent information | List all available agents |
| `/health` | GET | Health check | Service monitoring |

### Chat API Usage

```bash
# Send a task to the multi-agent system
curl -X POST http://100.123.10.72:8086/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me build a Python web scraper",
    "session_id": "my-session",
    "agent_type": "coordinator"
  }'
```

## 🔄 Workflow Types

### 1. Web Research (`web_research`)
**Team**: Research Team  
**Best For**: Information gathering, competitive analysis, documentation research
**Example**: "Research the latest developments in AI agent frameworks"

### 2. Code Development (`code_development`)
**Team**: Development Team  
**Best For**: Software development, debugging, testing
**Example**: "Create a Python web scraper with error handling"

### 3. Data Analysis (`data_analysis`)
**Team**: Analysis Team  
**Best For**: Data processing, performance analysis, system optimization
**Example**: "Analyze system performance logs for bottlenecks"

### 4. Complex Tasks (`complex_task`)
**Team**: Full Team (All 5 agents)  
**Best For**: Multi-domain projects, comprehensive solutions
**Example**: "Build and deploy a complete web application with monitoring"

## 🛠️ Service Management

### Start Magentic-One Service

```bash
# Manual start
cd /home/keith/chat-copilot
source autogen-env/bin/activate
python magentic_one_server.py

# Via startup script
./startup-platform.sh
```

### Auto-Startup Configuration

The service is automatically included in the platform startup script:

```bash
# Magentic-One startup entry in startup-platform.sh
start_service "Magentic-One" \
    "source /home/keith/chat-copilot/autogen-env/bin/activate && python /home/keith/chat-copilot/magentic_one_server.py" \
    "/home/keith/chat-copilot/pids/magentic-one.pid"
```

### Service Monitoring

```bash
# Check service status
curl http://100.123.10.72:8086/health

# View logs
tail -f /home/keith/chat-copilot/magentic_one.log

# Check process
ps aux | grep magentic_one_server
```

## 📊 Integration with Platform

### Dashboard Integration

The Magentic-One platform is integrated into the main AI Research Platform:

- **Control Panel**: Accessible via Material-UI dashboard
- **Application Directory**: Listed in `APPLICATIONS_DIRECTORY.md`
- **Startup Script**: Included in `startup-platform.sh`

### AutoGen Studio Integration

Magentic-One works alongside AutoGen Studio:
- **AutoGen Studio**: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- **Magentic-One**: [http://100.123.10.72:8086](http://100.123.10.72:8086)

Both platforms share the same Ollama models and can be used for different types of multi-agent tasks.

## 🔧 Customization

### Adding New Agents

```python
# In magentic_one_simple.py, add to MagenticOnePlatform._initialize_platform()
self.agents["new_agent"] = MagenticOneAgent(
    "NewAgent",
    "custom_role",
    "llama3.2:3b",
    "Your custom agent system message"
)
```

### Creating Custom Teams

```python
# Add to self.teams dictionary
self.teams["custom_team"] = MagenticOneTeam("Custom Team", [
    self.agents["orchestrator"],
    self.agents["new_agent"]
])
```

### Custom Workflows

```python
# Add to self.workflows dictionary
self.workflows["custom_workflow"] = {
    "name": "Custom Workflow",
    "team": "custom_team",
    "description": "Description of your workflow",
    "example": "Example task for this workflow"
}
```

## 🔒 Security and Access

### Network Security
- **Tailscale VPN**: All traffic secured through Tailscale network
- **CORS Policy**: Configured for Tailscale network access
- **No Authentication**: Running in trusted network environment

### Safety Features
- **Command Validation**: Terminal agent includes safety protocols
- **Error Handling**: Comprehensive error handling in all agents
- **Logging**: All operations logged for audit trail

## 📈 Performance Monitoring

### System Metrics

The platform provides real-time monitoring through:
- **Health Endpoint**: `/health` for service status
- **Status API**: `/api/status` for detailed system information
- **Logs**: Real-time logging in `/home/keith/chat-copilot/magentic_one.log`

### Usage Analytics

```bash
# View conversation logs
grep "Multi-Agent Task Summary" /home/keith/chat-copilot/magentic_one.log

# Monitor API usage
grep "POST /api/chat" /home/keith/chat-copilot/magentic_one.log
```

## 🔗 External Integrations

### Ollama Integration
All agents use Ollama models running on `localhost:11434`:
- **llama3.2:3b**: General coordination and terminal operations
- **mistral:latest**: Web research and information processing
- **deepseek-coder:6.7b**: Code development and file analysis

### GitHub Integration
Project repository: [https://github.com/kmransom56/AI_Research_Platform-_Tailscale](https://github.com/kmransom56/AI_Research_Platform-_Tailscale)

## 🚨 Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check if port is in use
sudo netstat -tlnp | grep :8086

# Check Python environment
source /home/keith/chat-copilot/autogen-env/bin/activate
which python
```

**Agents Not Responding**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/version

# Check agent configuration
python -c "from magentic_one_simple import MagenticOnePlatform; p=MagenticOnePlatform(); print(p.get_platform_status())"
```

**Connection Refused**
```bash
# Verify Tailscale connectivity
ping 100.123.10.72

# Check firewall rules
sudo ufw status
```

### Log Analysis

```bash
# View recent activity
tail -50 /home/keith/chat-copilot/magentic_one.log

# Search for errors
grep -i error /home/keith/chat-copilot/magentic_one.log

# Monitor real-time
tail -f /home/keith/chat-copilot/magentic_one.log
```

## 📚 Example Usage

### Research Task
```bash
curl -X POST http://100.123.10.72:8086/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Research best practices for microservices architecture",
    "session_id": "research-001"
  }'
```

### Development Task
```bash
curl -X POST http://100.123.10.72:8086/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a REST API with authentication",
    "session_id": "dev-001"
  }'
```

### Complex Multi-Domain Task
```bash
curl -X POST http://100.123.10.72:8086/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Design and implement a monitoring dashboard for our AI platform",
    "session_id": "complex-001"
  }'
```

## 🎯 Future Enhancements

### Planned Features
- **Real-time collaboration**: Multiple users working with agents simultaneously
- **Advanced workflows**: Custom workflow designer and execution engine
- **Agent learning**: Persistent memory and learning capabilities
- **Tool integration**: Direct integration with development tools and APIs
- **Enhanced security**: Authentication and authorization for multi-user environments

### Roadmap
1. **Phase 1**: Enhanced web interface with real-time updates
2. **Phase 2**: Agent memory and context persistence
3. **Phase 3**: External tool and API integrations
4. **Phase 4**: Advanced workflow orchestration
5. **Phase 5**: Multi-user collaboration features

---

## 📞 Support

For issues or questions about the Magentic-One platform:

1. **Check Logs**: Review `/home/keith/chat-copilot/magentic_one.log`
2. **Health Check**: Test `http://100.123.10.72:8086/health`
3. **GitHub Issues**: Report issues in the platform repository
4. **Platform Status**: Check overall platform status at the control panel

---

*🌟 Magentic-One Multi-Agent Platform - Bringing collaborative AI to your Tailscale network*