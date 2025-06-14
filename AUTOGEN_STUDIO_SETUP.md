# 🤖 AutoGen Studio Multi-Agent Platform

**AutoGen Studio Integration with Ollama Models**  
**AI Research Platform - Tailscale Network Integration**

---

## 🚀 Overview

AutoGen Studio is now integrated into your AI Research Platform, providing multi-agent conversation capabilities using local Ollama models. Create AI agent teams that collaborate to solve complex problems, review code, conduct research, and more.

### ✅ What's Included

- **AutoGen Studio Web Interface** - Visual multi-agent conversation platform
- **Local Ollama Integration** - 7 pre-configured language models
- **Multi-Agent Workflows** - Pre-built conversation templates
- **Tailscale Network Access** - Available across your mesh network
- **Zero External Dependencies** - Fully local AI agents

---

## 🌐 Access Information

### Primary Access
- **AutoGen Studio**: [http://100.123.10.72:8085](http://100.123.10.72:8085)
- **Network**: Tailscale VPN (`100.123.10.72`)
- **Port**: `8085`
- **Status**: ✅ Active and Integrated

### Quick Access Links
- **Control Panel**: [http://100.123.10.72:10500/control-panel.html](http://100.123.10.72:10500/control-panel.html)
- **Applications Dashboard**: [http://100.123.10.72:10500/applications.html](http://100.123.10.72:10500/applications.html)

---

## 🦙 Available Ollama Models

### Production Models
| Model | Size | Best For | Description |
|-------|------|----------|-------------|
| **llama3.2:3b** | 2.0 GB | General Tasks | Fast, efficient general-purpose assistant |
| **mistral:latest** | 4.1 GB | Research & Analysis | Excellent for research and complex reasoning |
| **deepseek-coder:6.7b** | 3.8 GB | Code & Technical | Specialized programming and code analysis |
| **codellama:7b** | 3.8 GB | Programming | Meta's programming-focused language model |

### Additional Models  
| Model | Size | Specialty |
|-------|------|-----------|
| **qwen2.5-coder:1.5b** | 986 MB | Lightweight Coding |
| **nomic-embed-text** | 274 MB | Text Embeddings |
| **eramax/openhands-lm** | 19 GB | Advanced Development |

---

## 🤝 Pre-Configured Agent Teams

### 1. Code Review Workflow
**Sequential Multi-Agent Code Analysis**

- **Senior Developer** (`deepseek-coder:6.7b`)
  - Reviews code for best practices, security, performance
  - Identifies potential bugs and optimization opportunities

- **Architecture Reviewer** (`mistral:latest`)  
  - Focuses on design patterns, scalability, maintainability
  - Evaluates system architecture and dependencies

- **Code Assistant** (`llama3.2:3b`)
  - Summarizes reviews and suggests improvements
  - Provides final recommendations and next steps

**Example Usage**: "Review this Python function for best practices and suggest improvements"

### 2. Research Analysis Team
**Collaborative Research with Multiple Perspectives**

- **Research Analyst** (`mistral:latest`)
  - Gathers and analyzes information thoroughly
  - Provides detailed research methodology

- **Technical Writer** (`llama3.2:3b`)
  - Creates clear, structured documentation
  - Organizes findings into readable formats

- **Fact Checker** (`deepseek-coder:6.7b`)
  - Verifies claims and ensures accuracy
  - Cross-references technical information

**Example Usage**: "Research the latest developments in AI agent frameworks"

### 3. Problem Solving Team
**Complex Problem Decomposition and Solution**

- **Problem Analyzer** (`mistral:latest`)
  - Breaks down complex problems into manageable parts
  - Identifies core issues and dependencies

- **Solution Designer** (`deepseek-coder:6.7b`)
  - Designs practical solutions and implementation strategies
  - Creates technical implementation plans

- **Implementation Guide** (`llama3.2:3b`)
  - Provides step-by-step implementation guidance
  - Creates actionable task lists

**Example Usage**: "How to integrate multiple AI services in a distributed system"

---

## 🛠️ Configuration Details

### Ollama Integration
```json
{
  "base_url": "http://localhost:11434/v1",
  "api_type": "open_ai",
  "api_key": "ollama",
  "temperature": 0.7
}
```

### Server Configuration
```bash
Host: 0.0.0.0
Port: 8085
CORS: Enabled
Authentication: None (Local Network)
```

### Virtual Environment
```bash
# Location
/home/keith/chat-copilot/autogen-env/

# Activation
source autogen-env/bin/activate

# AutoGen Studio Version
autogenstudio --version
```

---

## 📋 Getting Started Guide

### Step 1: Access AutoGen Studio
1. Open [http://100.123.10.72:8085](http://100.123.10.72:8085)
2. Click "Team Builder" to create your first agent team
3. Select "New Team" to start configuration

### Step 2: Configure Models
1. Add models with these settings:
   ```
   Model Name: llama3.2:3b
   Base URL: http://localhost:11434/v1
   API Key: ollama
   API Type: OpenAI Compatible
   ```

2. Repeat for other models:
   - `mistral:latest`
   - `deepseek-coder:6.7b`
   - `codellama:7b`

### Step 3: Create Agents
1. **General Assistant**
   - Model: `llama3.2:3b`
   - Role: "You are a helpful AI assistant. Provide clear, accurate responses."

2. **Code Specialist**
   - Model: `deepseek-coder:6.7b`
   - Role: "You are an expert programmer. Help with code analysis and development."

3. **Research Analyst**
   - Model: `mistral:latest`
   - Role: "You are a research assistant. Provide detailed analysis and insights."

### Step 4: Start Conversations
1. Go to "Playground"
2. Select your team/workflow
3. Begin multi-agent conversations
4. Watch agents collaborate in real-time

---

## 🔧 Management Commands

### Start AutoGen Studio
```bash
cd /home/keith/chat-copilot
source autogen-env/bin/activate
autogenstudio ui --port 8085 --host 0.0.0.0
```

### Start in Background
```bash
cd /home/keith/chat-copilot
source autogen-env/bin/activate
nohup autogenstudio ui --port 8085 --host 0.0.0.0 > autogen-studio.log 2>&1 &
```

### Check Status
```bash
# Server status
curl http://100.123.10.72:8085

# Ollama models
curl http://localhost:11434/api/tags

# Process status
ps aux | grep autogenstudio
```

### Configuration Scripts
```bash
# Setup configuration
python autogen_config.py

# Create workflow examples
python autogen_examples.py

# Test integration
curl -s http://100.123.10.72:8085 | grep "AutoGen Studio"
```

---

## 🎯 Use Cases & Examples

### Software Development
- **Code Review**: Multi-agent code analysis with different perspectives
- **Architecture Planning**: Collaborative system design discussions
- **Debugging**: Team-based problem solving for complex issues
- **Documentation**: Automated technical writing with review cycles

### Research & Analysis
- **Literature Review**: Multiple agents analyzing different aspects
- **Market Research**: Collaborative data gathering and analysis
- **Technical Investigation**: Deep-dive research with fact-checking
- **Report Writing**: Structured document creation with peer review

### Problem Solving
- **System Design**: Breaking down complex technical challenges
- **Troubleshooting**: Multi-perspective debugging and solution finding
- **Planning**: Collaborative project planning and task breakdown
- **Decision Making**: Structured analysis of options and trade-offs

### Creative Tasks
- **Brainstorming**: Multiple AI perspectives generating ideas
- **Content Creation**: Collaborative writing and editing
- **Strategy Development**: Multi-agent business planning
- **Innovation**: Creative problem solving with diverse viewpoints

---

## 🔍 Monitoring & Troubleshooting

### Health Checks
```bash
# AutoGen Studio status
curl -I http://100.123.10.72:8085

# Ollama API status  
curl http://localhost:11434/api/version

# Available models
curl http://localhost:11434/api/tags | jq '.models[].name'
```

### Common Issues

#### AutoGen Studio Not Starting
```bash
# Check port availability
netstat -tulnp | grep 8085

# Check logs
tail -f autogen-studio.log

# Restart service
pkill -f autogenstudio
source autogen-env/bin/activate && autogenstudio ui --port 8085 --host 0.0.0.0
```

#### Models Not Loading
```bash
# Verify Ollama is running
systemctl status ollama

# Check model availability
ollama list

# Pull missing models
ollama pull llama3.2:3b
ollama pull mistral:latest
ollama pull deepseek-coder:6.7b
```

#### Connection Issues
```bash
# Test network connectivity
ping 100.123.10.72

# Check firewall
sudo ufw status

# Verify Tailscale
tailscale status
```

---

## 📊 Integration Status

### Platform Integration
- ✅ **Control Panel** - Management buttons and status indicators
- ✅ **Applications Dashboard** - Quick access cards
- ✅ **Applications Directory** - Documentation and links
- ✅ **Tailscale Network** - Full mesh network access
- ✅ **Status Monitoring** - Health checks and uptime tracking

### AI Platform Ecosystem  
- ✅ **OpenWebUI** - Primary LLM interface
- ✅ **Chat Copilot** - Microsoft Semantic Kernel chat
- ✅ **Perplexica** - Internet-connected AI search
- ✅ **SearchNG** - Privacy-focused search engine
- ✅ **AutoGen Studio** - Multi-agent conversations
- ✅ **Ollama** - Local model inference engine

---

## 🚀 Advanced Configuration

### Custom Agent Templates
Create specialized agent roles for your specific use cases:

```python
# Research team for academic papers
academic_research_team = {
    "literature_reviewer": {
        "model": "mistral:latest",
        "role": "Academic literature specialist"
    },
    "methodology_expert": {
        "model": "deepseek-coder:6.7b", 
        "role": "Research methodology validator"
    },
    "writing_assistant": {
        "model": "llama3.2:3b",
        "role": "Academic writing specialist"
    }
}
```

### Performance Optimization
```bash
# Allocate more resources to Ollama
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=3

# Optimize for faster responses
export OLLAMA_FLASH_ATTENTION=1
```

### Integration with Other Services
```python
# Connect with existing AI services
import requests

# Send results to Chat Copilot
def send_to_copilot(result):
    response = requests.post(
        "https://100.123.10.72:40443/api/chat",
        json={"message": result}
    )
    return response.json()
```

---

## 📈 Next Steps

### Immediate Actions
1. **Explore the Interface** - Familiarize yourself with AutoGen Studio UI
2. **Create Your First Team** - Set up agents using the pre-configured models  
3. **Test Workflows** - Try the example multi-agent conversations
4. **Customize Agents** - Create specialized agents for your use cases

### Advanced Usage
1. **Custom Workflows** - Design multi-agent processes for specific tasks
2. **Integration Development** - Connect with other platform services
3. **Performance Tuning** - Optimize for your hardware and use patterns
4. **Documentation** - Create team-specific agent configuration guides

### Community & Support
- **GitHub Repository**: [AI_Research_Platform_Tailscale](https://github.com/kmransom56/AI_Research_Platform-_Tailscale)
- **AutoGen Documentation**: [Microsoft AutoGen](https://microsoft.github.io/autogen/)
- **Ollama Models**: [Ollama Library](https://ollama.ai/library)

---

## 🎉 Conclusion

AutoGen Studio is now fully integrated into your AI Research Platform, providing powerful multi-agent conversation capabilities using local Ollama models. This enables:

- **Enhanced Collaboration** - Multiple AI perspectives on every problem
- **Local Privacy** - All processing stays on your Tailscale network
- **Specialized Expertise** - Different models optimized for different tasks
- **Scalable Workflows** - Easily create and manage complex AI teams

Your AI Research Platform now supports the full spectrum of AI-assisted work, from simple chat to complex multi-agent collaboration!

---

*🤖 Generated with AutoGen Studio integration | Last updated: June 14, 2025*