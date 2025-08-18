# Multi-Agent Collaboration System Guide

This guide explains how to use the enhanced API Gateway to orchestrate collaboration across all AI services and applications in the platform.

## Overview

The Multi-Agent Collaboration System allows complex tasks to be automatically decomposed, distributed across appropriate AI services, and coordinated to produce comprehensive results.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Port 9000)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Task Decomposer │  │ Service Registry│  │ Orchestrator │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
   ┌────▼────┐            ┌─────▼─────┐           ┌─────▼─────┐
   │AI Stack │            │ Platform  │           │Infrastructure│
   │Services │            │ Services  │           │  Services   │
   └─────────┘            └───────────┘           └─────────────┘
   • vLLM R1              • Chat Copilot          • Neo4j
   • vLLM General         • AutoGen Studio        • Grafana  
   • vLLM Coder           • Magentic-One          • Prometheus
   • Oobabooga            • Perplexica
   • KoboldCpp            • SearXNG
```

## Collaboration Features

### 🧠 **Task Decomposition**
Automatically breaks complex tasks into specialized subtasks:
- **Research tasks** → Perplexica, SearXNG
- **Coding tasks** → vLLM Coder, Chat Copilot  
- **Creative tasks** → KoboldCpp, Oobabooga
- **Analysis tasks** → vLLM Reasoning
- **General tasks** → vLLM General

### 🎯 **Intelligent Service Selection**
Selects the best AI service for each task based on:
- Service capabilities and specializations
- Current service health and availability
- Task requirements and complexity
- Service priority and performance

### ⚡ **Parallel Execution**
Executes independent tasks concurrently while managing dependencies:
- Research and analysis can run in parallel
- Dependent tasks wait for prerequisites
- Results are aggregated intelligently

### 📋 **Workflow Templates**
Predefined collaboration patterns for common scenarios:
- **Research & Analysis**: Research → Reasoning → Summary
- **Code Development**: Research → Coding → Review → Documentation
- **Creative Projects**: Research → Creative → Refinement
- **Technical Documentation**: Analysis → Documentation → Review

## API Endpoints

### Core Collaboration

#### `POST /v1/collaborate`
Simple collaboration endpoint for quick multi-agent tasks.

```bash
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Research quantum computing and create a Python simulation",
    "context": {"max_tokens": 500}
  }'
```

#### `POST /v1/plan`
Create a collaboration plan without executing it.

```bash
curl -X POST http://localhost:9000/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the blockchain market and write a technical report",
    "template": "research_analysis"
  }'
```

#### `POST /v1/execute/<plan_id>`
Execute a previously created collaboration plan.

```bash
curl -X POST http://localhost:9000/v1/execute/abc123-plan-id
```

### Workflow Templates

#### `GET /workflows`
List all available workflow templates.

```bash
curl http://localhost:9000/workflows
```

Response:
```json
{
  "templates": {
    "research_analysis": "Research a topic and provide comprehensive analysis",
    "code_development": "Research, design, implement, and document code",
    "creative_project": "Research, brainstorm, create, and refine creative content",
    "technical_docs": "Research, analyze code, and create comprehensive documentation"
  },
  "count": 4
}
```

#### `GET /workflows/<template_name>`
Get detailed information about a specific template.

```bash
curl http://localhost:9000/workflows/code_development
```

#### `POST /workflows/suggest`
Get template suggestions for a prompt.

```bash
curl -X POST http://localhost:9000/workflows/suggest \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a web scraper for news articles"}'
```

#### `POST /v1/collaborate/template`
Execute collaboration using a specific template.

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a microservices architecture for e-commerce",
    "template": "code_development",
    "context": {"complexity": "high"}
  }'
```

### Service Management

#### `GET /services`
Get status and capabilities of all platform services.

```bash
curl http://localhost:9000/services
```

#### `GET /health`
Health check for all backend services.

```bash
curl http://localhost:9000/health
```

## Workflow Templates

### 1. Research & Analysis
**Use for**: Market research, academic analysis, technical investigations

**Flow**: Research → Reasoning → Summary
- Gathers information from multiple sources
- Analyzes and synthesizes findings
- Provides comprehensive conclusions

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the current state of renewable energy technology",
    "template": "research_analysis"
  }'
```

### 2. Code Development
**Use for**: Software development, algorithm implementation, technical solutions

**Flow**: Research → Coding → Review → Documentation
- Researches best practices and requirements
- Implements code solutions
- Reviews and optimizes code
- Creates documentation

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a REST API for a task management system",
    "template": "code_development"
  }'
```

### 3. Creative Project
**Use for**: Content creation, storytelling, artistic projects

**Flow**: Research → Creative → Reasoning → Refinement
- Researches inspiration and requirements
- Creates original content
- Analyzes and improves content
- Finalizes creative output

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a science fiction story about AI consciousness",
    "template": "creative_project"
  }'
```

### 4. Technical Documentation
**Use for**: API docs, user guides, technical specifications

**Flow**: Research → Analysis → Documentation → Review
- Researches existing documentation and standards
- Analyzes technical requirements
- Creates comprehensive documentation
- Reviews for clarity and completeness

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Document the authentication API endpoints",
    "template": "technical_docs"
  }'
```

### 5. Multi-Domain Analysis
**Use for**: Cross-functional analysis, comparative studies

**Flow**: Parallel Research & Analysis → Synthesis
- Concurrent analysis across multiple domains
- Comprehensive synthesis of findings
- Comparative insights and recommendations

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Compare cloud platforms for machine learning workloads",
    "template": "multi_domain"
  }'
```

### 6. Problem Solving
**Use for**: Complex troubleshooting, systematic problem resolution

**Flow**: Research → Reasoning → Implementation → Validation
- Systematic problem analysis
- Logical reasoning and solution design
- Implementation of solutions
- Validation and optimization

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Optimize the performance of a slow database query",
    "template": "problem_solving"
  }'
```

## Service Capabilities

### AI Stack Services
- **vLLM Reasoning** (Port 8000): Mathematical reasoning, logical analysis
- **vLLM General** (Port 8001): General conversation, Q&A, summaries
- **vLLM Coding** (Port 8002): Code generation, debugging, review
- **Oobabooga** (Port 5000): Advanced text generation, multimodal tasks
- **KoboldCpp** (Port 5001): Creative writing, storytelling, roleplay

### Platform Services
- **Chat Copilot** (Port 11000): Conversational AI with memory
- **AutoGen Studio** (Port 11001): Multi-agent orchestration
- **Magentic-One** (Port 11003): Task planning and coordination
- **Perplexica** (Port 11020): AI-powered research and search
- **SearXNG** (Port 11021): Meta-search engine

### Infrastructure Services
- **Neo4j** (Port 7474): Graph database for knowledge relationships
- **Grafana** (Port 11002): Monitoring and visualization
- **Prometheus** (Port 9090): Metrics collection and alerting

## Advanced Usage Examples

### 1. Complex Research Project
```bash
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Research the impact of artificial intelligence on employment, analyze the data, create visualizations, and write a comprehensive report with policy recommendations",
    "context": {
      "depth": "comprehensive",
      "format": "academic_report",
      "visualizations": true
    }
  }'
```

### 2. Full-Stack Development
```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design and implement a real-time chat application with React frontend, Node.js backend, WebSocket communication, and MongoDB storage",
    "template": "code_development",
    "context": {
      "technologies": ["React", "Node.js", "WebSocket", "MongoDB"],
      "features": ["real-time", "authentication", "message_history"]
    }
  }'
```

### 3. Multi-Modal Creative Project
```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create an interactive story about space exploration that includes character development, plot branching, and educational content about astronomy",
    "template": "creative_project",
    "context": {
      "interactive": true,
      "educational": true,
      "target_audience": "young_adults"
    }
  }'
```

### 4. Technical Analysis and Solutions
```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the scalability bottlenecks in our microservices architecture, design solutions, implement optimizations, and create monitoring dashboards",
    "template": "problem_solving",
    "context": {
      "architecture": "microservices",
      "scale": "enterprise",
      "monitoring": "required"
    }
  }'
```

## Monitoring and Debugging

### Service Health Monitoring
```bash
# Check overall service status
curl http://localhost:9000/services

# Check specific service health  
curl http://localhost:9000/health

# Gateway information
curl http://localhost:9000/info
```

### Collaboration Logs
Check the gateway logs for collaboration details:
```bash
docker-compose -f docker-compose.ai-stack.yml logs ai-gateway
```

### Task Execution Tracking
Each collaboration returns detailed information:
- Plan ID for tracking
- Task sequence and dependencies
- Service allocation
- Execution results and errors
- Performance metrics

## Integration Examples

### Python Client
```python
import requests
import json

# Simple collaboration
response = requests.post('http://localhost:9000/v1/collaborate', json={
    'prompt': 'Analyze customer feedback and suggest improvements',
    'context': {'domain': 'customer_service'}
})

result = response.json()
print(f"Collaboration completed: {result['summary']}")
```

### JavaScript/Node.js Client
```javascript
const axios = require('axios');

async function collaborate(prompt, template = null) {
    const payload = { prompt };
    if (template) payload.template = template;
    
    try {
        const response = await axios.post('http://localhost:9000/v1/collaborate', payload);
        return response.data;
    } catch (error) {
        console.error('Collaboration failed:', error.response?.data || error.message);
    }
}

// Usage
collaborate('Design a mobile app for fitness tracking', 'code_development')
    .then(result => console.log('Results:', result));
```

### cURL Integration
```bash
#!/bin/bash
# Collaboration script

GATEWAY_URL="http://localhost:9000"
PROMPT="$1"
TEMPLATE="${2:-}"

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 \"prompt\" [template]"
    exit 1
fi

if [ -n "$TEMPLATE" ]; then
    ENDPOINT="/v1/collaborate/template"
    PAYLOAD="{\"prompt\": \"$PROMPT\", \"template\": \"$TEMPLATE\"}"
else
    ENDPOINT="/v1/collaborate"
    PAYLOAD="{\"prompt\": \"$PROMPT\"}"
fi

curl -X POST "$GATEWAY_URL$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" | jq .
```

## Performance Optimization

### Service Allocation
- High-priority services are selected first
- Load balancing across available instances
- Automatic failover to backup services

### Parallel Execution
- Independent tasks run concurrently
- Dependency resolution prevents blocking
- Resource optimization across services

### Caching and Memory
- Service status caching
- Task result caching for similar requests
- Efficient memory management

## Troubleshooting

### Common Issues

1. **Service Unavailable**
   - Check service health: `curl http://localhost:9000/services`
   - Restart services: `./start-ai-stack.sh restart`

2. **Task Timeouts**
   - Increase timeout in service configuration
   - Break complex tasks into smaller parts

3. **Dependency Errors**
   - Verify all required services are running
   - Check service capabilities match task requirements

### Debug Mode
Enable detailed logging in the gateway:
```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

### Health Checks
Regular health monitoring:
```bash
# Monitor continuously
watch -n 5 'curl -s http://localhost:9000/health | jq .'

# Service status dashboard
curl -s http://localhost:9000/services | jq '.services[] | select(.status != "online")'
```

## Best Practices

1. **Task Design**
   - Be specific about requirements
   - Provide relevant context
   - Use appropriate templates

2. **Service Selection**
   - Let the system auto-select unless specific needs
   - Monitor service performance
   - Use parallel execution for independent tasks

3. **Error Handling**
   - Always check response status
   - Implement retry logic for transient failures
   - Have fallback strategies

4. **Performance**
   - Use templates for common patterns
   - Cache frequently used results
   - Monitor resource usage

---

**Last Updated**: August 2025  
**Version**: 2.0.0  
**Compatible with**: AI Research Platform v3.1+

For support and issues, check the gateway logs and service health endpoints.