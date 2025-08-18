# Enhanced API Gateway User Guide

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Authentication & Configuration](#authentication--configuration)
4. [Core API Endpoints](#core-api-endpoints)
5. [Multi-Agent Collaboration](#multi-agent-collaboration)
6. [Workflow Templates](#workflow-templates)
7. [Service Management](#service-management)
8. [Advanced Usage](#advanced-usage)
9. [Error Handling](#error-handling)
10. [Performance Optimization](#performance-optimization)
11. [Integration Examples](#integration-examples)
12. [Troubleshooting](#troubleshooting)
13. [Best Practices](#best-practices)

---

## Overview

The Enhanced API Gateway is a powerful orchestration layer that enables multi-agent collaboration across all AI services and applications in the platform. It provides intelligent task decomposition, automatic service selection, and coordinated execution across multiple AI models and tools.

### Key Capabilities

- **🧠 Intelligent Task Routing**: Automatically selects the best AI service for each task
- **🔀 Multi-Agent Collaboration**: Coordinates complex workflows across multiple services
- **📋 Workflow Templates**: Predefined patterns for common collaboration scenarios
- **⚡ Parallel Execution**: Concurrent processing of independent tasks
- **🔍 Service Discovery**: Real-time monitoring of service health and capabilities
- **🛡️ Error Handling**: Graceful fallbacks and retry mechanisms

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                Enhanced API Gateway (Port 9000)             │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Task Decomposer │ Service Registry│ Collaboration Engine   │
├─────────────────┼─────────────────┼─────────────────────────┤
│ Workflow Engine │ Health Monitor  │ Load Balancer          │
└─────────────────┴─────────────────┴─────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐
   │AI Models│          │ Platform  │        │Infrastructure│
   │         │          │ Services  │        │  Services   │
   │• vLLM   │          │• Copilot  │        │• Neo4j      │
   │• Oobabooga│        │• AutoGen  │        │• Grafana    │
   │• KoboldCpp│        │• Perplexica│       │• Prometheus │
   └─────────┘          └───────────┘        └─────────────┘
```

---

## Getting Started

### Prerequisites

1. **Platform Running**: Ensure the AI Research Platform is running
2. **Services Online**: Verify core services are available
3. **Network Access**: Gateway accessible on `http://localhost:9000`

### Quick Health Check

```bash
# Check if gateway is responding
curl http://localhost:9000/info

# Check service status
curl http://localhost:9000/services

# Verify health of all backends
curl http://localhost:9000/health
```

### First Collaboration Request

```bash
# Simple collaboration example
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing and write a simple Python example",
    "context": {"audience": "beginners"}
  }'
```

---

## Authentication & Configuration

### Environment Variables

The gateway uses environment variables for service configuration:

```bash
# Core AI service URLs
REASONING_MODEL_URL=http://vllm-reasoning:8000
GENERAL_MODEL_URL=http://vllm-general:8000
CODING_MODEL_URL=http://vllm-coding:8000
CREATIVE_MODEL_URL=http://koboldcpp:5001
ADVANCED_MODEL_URL=http://oobabooga:5000

# Authentication tokens
HUGGINGFACE_TOKEN=hf_your_token_here
OPENAI_API_KEY=sk-your_key_here

# Service timeouts and limits
SERVICE_TIMEOUT=30
MAX_RETRIES=3
DEFAULT_MAX_TOKENS=512
```

### API Key Configuration

Currently, the gateway operates without authentication for local development. For production deployment:

1. **Add API Key Header**: `X-API-Key: your-api-key`
2. **JWT Authentication**: Bearer token support
3. **Rate Limiting**: Request limits per API key

```bash
# Future authenticated request format
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"prompt": "Your request"}'
```

---

## Core API Endpoints

### Base URL
All endpoints are relative to: `http://localhost:9000`

### Endpoint Categories

| Category | Base Path | Description |
|----------|-----------|-------------|
| Information | `/info`, `/health` | Gateway status and service health |
| Collaboration | `/v1/collaborate*` | Multi-agent task execution |
| Planning | `/v1/plan`, `/v1/execute` | Workflow planning and execution |
| Templates | `/workflows*` | Workflow template management |
| Services | `/services` | Service discovery and status |
| Legacy | `/v1/completions` | Single-service completions |

---

## Multi-Agent Collaboration

### Basic Collaboration

The simplest way to use multi-agent collaboration:

#### `POST /v1/collaborate`

Automatically decomposes tasks and coordinates execution across appropriate services.

**Request Format:**
```json
{
  "prompt": "Your complex task description",
  "context": {
    "max_tokens": 500,
    "temperature": 0.7,
    "domain": "technology",
    "audience": "technical"
  }
}
```

**Example Requests:**

1. **Research and Analysis**
```bash
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Research the latest developments in renewable energy technology and create a comprehensive analysis with recommendations",
    "context": {
      "depth": "comprehensive",
      "include_sources": true,
      "format": "business_report"
    }
  }'
```

2. **Software Development**
```bash
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design and implement a RESTful API for a book library management system with user authentication and search functionality",
    "context": {
      "language": "Python",
      "framework": "FastAPI",
      "database": "PostgreSQL",
      "include_tests": true
    }
  }'
```

3. **Creative Project**
```bash
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create an interactive science fiction story about space exploration with educational content about real space missions",
    "context": {
      "target_age": "12-16",
      "interactive_elements": true,
      "educational_focus": "astronomy"
    }
  }'
```

**Response Format:**
```json
{
  "plan_id": "abc123-def456",
  "status": "completed",
  "results": {
    "task_1_research": {
      "content": "Research findings...",
      "sources": ["url1", "url2"],
      "confidence": 0.95
    },
    "task_2_analysis": {
      "content": "Analysis results...",
      "key_insights": ["insight1", "insight2"]
    }
  },
  "summary": "Collaboration completed successfully with 2 tasks",
  "execution_time": 45.2,
  "services_used": ["perplexica", "vllm-reasoning", "vllm-general"]
}
```

### Template-Based Collaboration

Use predefined workflow templates for optimized task execution.

#### `POST /v1/collaborate/template`

Execute collaboration using a specific workflow template.

**Request Format:**
```json
{
  "prompt": "Your task description",
  "template": "template_name",
  "context": {
    "custom_parameters": "value"
  }
}
```

**Available Templates:**
- `research_analysis`: Research → Analysis → Summary
- `code_development`: Research → Coding → Review → Documentation
- `creative_project`: Research → Creative → Refinement
- `technical_docs`: Analysis → Documentation → Review
- `multi_domain`: Parallel analysis → Synthesis
- `problem_solving`: Research → Reasoning → Implementation

**Example:**
```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a machine learning model to predict customer churn",
    "template": "code_development",
    "context": {
      "data_type": "tabular",
      "algorithm_preference": "ensemble",
      "deployment": "production"
    }
  }'
```

### Advanced Planning Workflow

For complex projects requiring review before execution:

#### `POST /v1/plan` - Create Execution Plan

Creates a detailed collaboration plan without executing it.

```bash
curl -X POST http://localhost:9000/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Develop a complete e-commerce platform with microservices architecture",
    "template": "code_development",
    "context": {"scale": "enterprise"}
  }'
```

**Response:**
```json
{
  "id": "plan_789xyz",
  "task_sequence": [
    {
      "id": "task_1_research",
      "type": "research",
      "prompt": "Research e-commerce microservices best practices...",
      "dependencies": [],
      "assigned_services": ["perplexica"]
    },
    {
      "id": "task_2_coding",
      "type": "coding", 
      "prompt": "Implement microservices architecture...",
      "dependencies": ["task_1_research"],
      "assigned_services": ["vllm-coding"]
    }
  ],
  "service_allocation": {
    "perplexica": ["task_1_research"],
    "vllm-coding": ["task_2_coding"]
  },
  "estimated_duration": 180,
  "parallel_execution": false
}
```

#### `POST /v1/execute/<plan_id>` - Execute Plan

Execute a previously created plan:

```bash
curl -X POST http://localhost:9000/v1/execute/plan_789xyz
```

---

## Workflow Templates

### Template Management

#### `GET /workflows` - List All Templates

```bash
curl http://localhost:9000/workflows
```

**Response:**
```json
{
  "templates": {
    "research_analysis": "Research a topic and provide comprehensive analysis",
    "code_development": "Research, design, implement, and document code",
    "creative_project": "Research, brainstorm, create, and refine creative content",
    "technical_docs": "Research, analyze code, and create comprehensive documentation",
    "multi_domain": "Parallel analysis across multiple domains with synthesis", 
    "problem_solving": "Systematic approach to complex problem solving"
  },
  "count": 6
}
```

#### `GET /workflows/<template_name>` - Template Details

```bash
curl http://localhost:9000/workflows/code_development
```

**Response:**
```json
{
  "template": {
    "name": "Code Development",
    "description": "Research, design, implement, and document code",
    "task_types": ["research", "coding", "reasoning", "general"],
    "dependencies": {
      "coding": ["research"],
      "reasoning": ["coding"],
      "general": ["reasoning"]
    },
    "estimated_duration": 180,
    "required_capabilities": ["search", "coding", "reasoning", "documentation"]
  },
  "parallel_execution": false,
  "total_tasks": 4,
  "complexity": "high"
}
```

#### `POST /workflows/suggest` - Template Recommendation

Get template suggestions based on your prompt:

```bash
curl -X POST http://localhost:9000/workflows/suggest \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write unit tests for my Python application"}'
```

**Response:**
```json
{
  "suggested_template": "code_development",
  "template_info": {
    "name": "Code Development",
    "complexity": "high",
    "estimated_duration": 180
  },
  "prompt": "Write unit tests for my Python application"
}
```

### Template Usage Patterns

#### 1. Research & Analysis Template

**Best for:** Market research, academic analysis, technical investigations

**Flow:** Research → Reasoning → Summary

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the competitive landscape of AI chatbot platforms",
    "template": "research_analysis",
    "context": {
      "focus": "business_analysis",
      "competitors": ["OpenAI", "Anthropic", "Google"],
      "metrics": ["features", "pricing", "performance"]
    }
  }'
```

#### 2. Code Development Template

**Best for:** Software development, algorithm implementation, technical solutions

**Flow:** Research → Coding → Review → Documentation

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a distributed task queue system using Redis and Python",
    "template": "code_development", 
    "context": {
      "requirements": ["high_availability", "fault_tolerance"],
      "technologies": ["Redis", "Python", "Celery"],
      "deployment": "Docker"
    }
  }'
```

#### 3. Creative Project Template

**Best for:** Content creation, storytelling, artistic projects

**Flow:** Research → Creative → Reasoning → Refinement

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a podcast series about the history of computing",
    "template": "creative_project",
    "context": {
      "episodes": 6,
      "duration": "30_minutes_each",
      "target_audience": "tech_enthusiasts",
      "format": "narrative_storytelling"
    }
  }'
```

#### 4. Technical Documentation Template

**Best for:** API documentation, user guides, technical specifications

**Flow:** Research → Analysis → Documentation → Review

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create comprehensive API documentation for our REST endpoints",
    "template": "technical_docs",
    "context": {
      "api_version": "v2",
      "include_examples": true,
      "authentication": "JWT",
      "formats": ["OpenAPI", "Markdown"]
    }
  }'
```

#### 5. Multi-Domain Analysis Template

**Best for:** Comparative studies, cross-functional analysis

**Flow:** Parallel Research & Analysis → Synthesis

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Compare cloud platforms for machine learning workloads across cost, performance, and ease of use",
    "template": "multi_domain",
    "context": {
      "platforms": ["AWS", "GCP", "Azure"],
      "criteria": ["cost", "performance", "usability"],
      "use_case": "ML_training_inference"
    }
  }'
```

#### 6. Problem Solving Template

**Best for:** Troubleshooting, optimization, systematic problem resolution

**Flow:** Research → Reasoning → Implementation → Validation

```bash
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Optimize our database queries that are causing performance bottlenecks",
    "template": "problem_solving",
    "context": {
      "database": "PostgreSQL",
      "symptoms": ["slow_queries", "high_CPU", "connection_timeouts"],
      "constraints": ["minimal_downtime", "backward_compatibility"]
    }
  }'
```

---

## Service Management

### Service Discovery

#### `GET /services` - Service Status and Capabilities

Get comprehensive information about all platform services:

```bash
curl http://localhost:9000/services | jq
```

**Response:**
```json
{
  "total_services": 15,
  "online_services": 12,
  "offline_services": 3,
  "services": {
    "vllm-reasoning": {
      "status": "online",
      "url": "http://localhost:8000",
      "capabilities": ["reasoning", "analysis", "math", "logic"],
      "priority": 9
    },
    "vllm-coding": {
      "status": "online", 
      "url": "http://localhost:8002",
      "capabilities": ["coding", "programming", "debugging", "review"],
      "priority": 9
    },
    "perplexica": {
      "status": "online",
      "url": "http://localhost:11020",
      "capabilities": ["research", "search", "information"],
      "priority": 7
    }
  }
}
```

### Health Monitoring

#### `GET /health` - Health Check All Services

Monitor the health of all backend services:

```bash
curl http://localhost:9000/health | jq
```

**Response:**
```json
{
  "overall_status": "healthy",
  "backends": {
    "reasoning": {
      "status": "online",
      "url": "http://vllm-reasoning:8000"
    },
    "general": {
      "status": "online", 
      "url": "http://vllm-general:8000"
    },
    "coding": {
      "status": "online",
      "url": "http://vllm-coding:8000"
    },
    "creative": {
      "status": "offline",
      "url": "http://koboldcpp:5001",
      "error": "Connection timeout"
    }
  },
  "gateway": "online"
}
```

### Service Selection Logic

The gateway automatically selects services based on:

1. **Task Type Matching**: Service capabilities vs. task requirements
2. **Service Priority**: Higher priority services preferred
3. **Health Status**: Only online services are selected
4. **Load Balancing**: Distribution across available instances

**Capability Mapping:**
```
Task Type → Service Capabilities
reasoning → ["reasoning", "analysis", "math", "logic"]
coding    → ["coding", "programming", "debugging"]
creative  → ["creative", "writing", "storytelling"]
research  → ["research", "search", "information"]
general   → ["general", "conversation", "qa"]
```

---

## Advanced Usage

### Custom Context Parameters

Enhance your requests with detailed context:

```json
{
  "prompt": "Your task",
  "context": {
    // Output formatting
    "format": "json|markdown|html|plain",
    "max_tokens": 1000,
    "temperature": 0.7,
    
    // Domain-specific
    "domain": "technology|business|science|creative",
    "audience": "technical|business|general|academic",
    "complexity": "low|medium|high",
    
    // Collaboration settings
    "parallel_execution": true,
    "service_preferences": ["vllm-coding", "perplexica"],
    "exclude_services": ["oobabooga"],
    
    // Custom parameters
    "language": "Python",
    "framework": "FastAPI", 
    "include_tests": true,
    "deployment": "Docker"
  }
}
```

### Batch Processing

Process multiple requests efficiently:

```bash
# Create multiple plans
for prompt in "${prompts[@]}"; do
  curl -X POST http://localhost:9000/v1/plan \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$prompt\"}" \
    > "plan_${i}.json"
done

# Execute plans in parallel
for plan_file in plan_*.json; do
  plan_id=$(jq -r '.id' "$plan_file")
  curl -X POST "http://localhost:9000/v1/execute/$plan_id" &
done
wait
```

### Service-Specific Requests

For direct service access (bypassing collaboration):

#### `POST /v1/completions` - Single Service Completion

```bash
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "coding",
    "prompt": "Write a Python function to merge two sorted lists",
    "max_tokens": 200,
    "temperature": 0.3
  }'
```

#### `POST /v1/chat/completions` - OpenAI-Compatible

```bash
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain recursion with examples"}
    ],
    "task_type": "reasoning",
    "max_tokens": 300
  }'
```

---

## Error Handling

### Common Error Types

#### 1. Service Unavailable
```json
{
  "error": "Backend reasoning unavailable: Connection timeout",
  "error_code": "SERVICE_UNAVAILABLE",
  "suggested_action": "Try again or use a different service"
}
```

#### 2. Invalid Template
```json
{
  "error": "Template 'invalid_template' not found",
  "error_code": "TEMPLATE_NOT_FOUND", 
  "available_templates": ["research_analysis", "code_development", "..."]
}
```

#### 3. Plan Not Found
```json
{
  "error": "Collaboration plan not found",
  "error_code": "PLAN_NOT_FOUND",
  "plan_id": "abc123"
}
```

#### 4. Task Timeout
```json
{
  "error": "Task execution timeout after 60 seconds",
  "error_code": "EXECUTION_TIMEOUT",
  "completed_tasks": ["task_1", "task_2"],
  "failed_tasks": ["task_3"]
}
```

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE_CONSTANT",
  "details": {
    "service": "service_name",
    "task_id": "task_123",
    "timestamp": "2025-08-17T18:30:00Z"
  },
  "suggested_actions": [
    "Check service health",
    "Retry with different parameters"
  ]
}
```

### Retry Strategies

#### Automatic Retries
The gateway automatically retries:
- Failed service connections (3 retries)
- Temporary service errors (2 retries) 
- Network timeouts (1 retry)

#### Manual Retry Patterns

```bash
# Retry with exponential backoff
for i in {1..3}; do
  if result=$(curl -s -X POST http://localhost:9000/v1/collaborate \
    -H "Content-Type: application/json" \
    -d "$payload"); then
    
    if ! echo "$result" | grep -q '"error"'; then
      echo "Success: $result"
      break
    fi
  fi
  
  sleep $((2**i))  # 2, 4, 8 seconds
done
```

---

## Performance Optimization

### Request Optimization

#### 1. Use Appropriate Templates
Choose the right template for your task:
- Simple tasks: Direct `/v1/completions`
- Research-heavy: `research_analysis` template
- Code projects: `code_development` template

#### 2. Parallel Execution
Enable parallel processing for independent tasks:
```json
{
  "prompt": "Research AI trends and write three separate articles",
  "context": {
    "parallel_execution": true,
    "task_independence": true
  }
}
```

#### 3. Service Preferences
Specify preferred services for faster routing:
```json
{
  "context": {
    "service_preferences": ["vllm-coding", "vllm-reasoning"],
    "exclude_services": ["oobabooga"]
  }
}
```

### Monitoring Performance

#### Response Time Tracking
```bash
# Measure collaboration response time
time curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Simple test task"}'
```

#### Service Load Monitoring
```bash
# Monitor service health periodically
watch -n 5 'curl -s http://localhost:9000/health | jq ".backends[].status"'
```

### Caching Strategies

#### Result Caching
The gateway caches:
- Service health status (30 seconds)
- Template configurations (until restart)
- Frequently used service responses (5 minutes)

#### Cache Headers
```bash
# Check if response was cached
curl -I http://localhost:9000/workflows
# Look for: X-Cache: HIT|MISS
```

---

## Integration Examples

### Python Integration

#### Simple Client
```python
import requests
import json
from typing import Dict, Any, Optional

class AIGatewayClient:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def collaborate(self, prompt: str, context: Optional[Dict] = None, 
                   template: Optional[str] = None) -> Dict[str, Any]:
        """Execute multi-agent collaboration"""
        endpoint = "/v1/collaborate/template" if template else "/v1/collaborate"
        
        payload = {"prompt": prompt}
        if context:
            payload["context"] = context
        if template:
            payload["template"] = template
        
        response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_services(self) -> Dict[str, Any]:
        """Get service status and capabilities"""
        response = self.session.get(f"{self.base_url}/services")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all services"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

# Usage example
client = AIGatewayClient()

# Simple collaboration
result = client.collaborate(
    prompt="Create a Python web scraper for news articles",
    template="code_development",
    context={"language": "Python", "include_tests": True}
)

print(f"Collaboration completed: {result['summary']}")
for task_id, task_result in result['results'].items():
    print(f"Task {task_id}: {task_result.get('content', '')[:100]}...")
```

#### Advanced Python Client with Async
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class AsyncAIGatewayClient:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def collaborate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Async collaboration request"""
        payload = {"prompt": prompt, **kwargs}
        
        async with self.session.post(
            f"{self.base_url}/v1/collaborate", 
            json=payload
        ) as response:
            return await response.json()
    
    async def batch_collaborate(self, requests: List[Dict]) -> List[Dict]:
        """Process multiple collaboration requests in parallel"""
        tasks = [self.collaborate(**req) for req in requests]
        return await asyncio.gather(*tasks)

# Usage
async def main():
    requests = [
        {"prompt": "Analyze AI trends", "template": "research_analysis"},
        {"prompt": "Build a chatbot", "template": "code_development"},
        {"prompt": "Write a story", "template": "creative_project"}
    ]
    
    async with AsyncAIGatewayClient() as client:
        results = await client.batch_collaborate(requests)
        
        for i, result in enumerate(results):
            print(f"Request {i+1}: {result['summary']}")

# Run async example
# asyncio.run(main())
```

### JavaScript/Node.js Integration

#### Simple Client
```javascript
const axios = require('axios');

class AIGatewayClient {
    constructor(baseUrl = 'http://localhost:9000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            timeout: 60000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    
    async collaborate(prompt, options = {}) {
        const { template, context = {} } = options;
        
        const endpoint = template ? '/v1/collaborate/template' : '/v1/collaborate';
        const payload = { prompt, context };
        
        if (template) {
            payload.template = template;
        }
        
        try {
            const response = await this.client.post(endpoint, payload);
            return response.data;
        } catch (error) {
            throw new Error(`Collaboration failed: ${error.response?.data?.error || error.message}`);
        }
    }
    
    async getWorkflowTemplates() {
        const response = await this.client.get('/workflows');
        return response.data;
    }
    
    async suggestTemplate(prompt) {
        const response = await this.client.post('/workflows/suggest', { prompt });
        return response.data;
    }
    
    async getServiceStatus() {
        const response = await this.client.get('/services');
        return response.data;
    }
}

// Usage examples
const gateway = new AIGatewayClient();

// Simple collaboration
gateway.collaborate('Build a REST API for user management')
    .then(result => {
        console.log('Collaboration Result:', result.summary);
        Object.entries(result.results).forEach(([taskId, taskResult]) => {
            console.log(`${taskId}: ${taskResult.content?.substring(0, 100)}...`);
        });
    })
    .catch(error => console.error('Error:', error.message));

// Template-based collaboration
gateway.collaborate(
    'Create a machine learning model for sentiment analysis', 
    {
        template: 'code_development',
        context: {
            dataset: 'twitter',
            algorithm: 'transformer',
            deployment: 'cloud'
        }
    }
).then(result => console.log('ML Project:', result.summary));

// Get template suggestions
gateway.suggestTemplate('Write documentation for my API')
    .then(suggestion => {
        console.log('Suggested template:', suggestion.suggested_template);
        return gateway.collaborate(
            'Write documentation for my API',
            { template: suggestion.suggested_template }
        );
    })
    .then(result => console.log('Documentation created:', result.summary));
```

#### React Integration
```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AICollaborationComponent = () => {
    const [prompt, setPrompt] = useState('');
    const [template, setTemplate] = useState('');
    const [templates, setTemplates] = useState({});
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const gatewayUrl = 'http://localhost:9000';
    
    useEffect(() => {
        // Load available templates
        axios.get(`${gatewayUrl}/workflows`)
            .then(response => setTemplates(response.data.templates))
            .catch(err => setError(err.message));
    }, []);
    
    const handleCollaboration = async () => {
        if (!prompt.trim()) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const endpoint = template ? '/v1/collaborate/template' : '/v1/collaborate';
            const payload = { prompt };
            
            if (template) {
                payload.template = template;
            }
            
            const response = await axios.post(`${gatewayUrl}${endpoint}`, payload);
            setResult(response.data);
        } catch (err) {
            setError(err.response?.data?.error || err.message);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="ai-collaboration">
            <h2>AI Multi-Agent Collaboration</h2>
            
            <div className="input-section">
                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Describe your complex task..."
                    rows={4}
                    cols={60}
                />
                
                <select 
                    value={template} 
                    onChange={(e) => setTemplate(e.target.value)}
                >
                    <option value="">Auto-select template</option>
                    {Object.entries(templates).map(([key, description]) => (
                        <option key={key} value={key}>{key}: {description}</option>
                    ))}
                </select>
                
                <button 
                    onClick={handleCollaboration} 
                    disabled={loading || !prompt.trim()}
                >
                    {loading ? 'Processing...' : 'Start Collaboration'}
                </button>
            </div>
            
            {error && (
                <div className="error">
                    <strong>Error:</strong> {error}
                </div>
            )}
            
            {result && (
                <div className="results">
                    <h3>Collaboration Results</h3>
                    <p><strong>Status:</strong> {result.status}</p>
                    <p><strong>Summary:</strong> {result.summary}</p>
                    
                    {result.template_used && (
                        <p><strong>Template Used:</strong> {result.template_used}</p>
                    )}
                    
                    <div className="task-results">
                        <h4>Task Results:</h4>
                        {Object.entries(result.results || {}).map(([taskId, taskResult]) => (
                            <div key={taskId} className="task-result">
                                <h5>{taskId}</h5>
                                <pre>{JSON.stringify(taskResult, null, 2)}</pre>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AICollaborationComponent;
```

### Shell Script Integration

#### Comprehensive Shell Client
```bash
#!/bin/bash
# AI Gateway Shell Client

GATEWAY_URL="${GATEWAY_URL:-http://localhost:9000}"
TIMEOUT=60

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Check if gateway is available
check_gateway() {
    if curl -s --max-time 5 "$GATEWAY_URL/info" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# List available templates
list_templates() {
    log_info "Available workflow templates:"
    
    if ! check_gateway; then
        log_error "Gateway not available at $GATEWAY_URL"
        return 1
    fi
    
    templates=$(curl -s "$GATEWAY_URL/workflows" | jq -r '.templates | to_entries[] | "\(.key): \(.value)"' 2>/dev/null)
    
    if [ -n "$templates" ]; then
        echo "$templates" | while read -r line; do
            echo "  • $line"
        done
    else
        log_error "Could not retrieve templates"
        return 1
    fi
}

# Suggest template for prompt
suggest_template() {
    local prompt="$1"
    
    if [ -z "$prompt" ]; then
        log_error "No prompt provided"
        return 1
    fi
    
    log_info "Getting template suggestion for: '$prompt'"
    
    suggestion=$(curl -s -X POST "$GATEWAY_URL/workflows/suggest" \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$prompt\"}" | jq -r '.suggested_template' 2>/dev/null)
    
    if [ -n "$suggestion" ] && [ "$suggestion" != "null" ]; then
        log_success "Suggested template: $suggestion"
        echo "$suggestion"
    else
        log_warning "No template suggestion available"
        return 1
    fi
}

# Execute collaboration
collaborate() {
    local prompt="$1"
    local template="$2"
    local output_file="$3"
    
    if [ -z "$prompt" ]; then
        log_error "Usage: collaborate \"prompt\" [template] [output_file]"
        return 1
    fi
    
    if ! check_gateway; then
        log_error "Gateway not available at $GATEWAY_URL"
        return 1
    fi
    
    log_info "Starting collaboration..."
    log_info "Prompt: $prompt"
    
    # Prepare payload
    local payload="{\"prompt\": \"$prompt\""
    
    if [ -n "$template" ]; then
        payload="$payload, \"template\": \"$template\""
        log_info "Template: $template"
    fi
    
    payload="$payload}"
    
    # Choose endpoint
    local endpoint="/v1/collaborate"
    if [ -n "$template" ]; then
        endpoint="/v1/collaborate/template"
    fi
    
    # Execute request
    log_info "Sending request to gateway..."
    
    result=$(curl -s -X POST "$GATEWAY_URL$endpoint" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time "$TIMEOUT")
    
    if [ $? -ne 0 ]; then
        log_error "Request failed or timed out"
        return 1
    fi
    
    # Check for errors
    if echo "$result" | jq -e '.error' >/dev/null 2>&1; then
        error_msg=$(echo "$result" | jq -r '.error' 2>/dev/null)
        log_error "Collaboration failed: $error_msg"
        return 1
    fi
    
    # Parse and display results
    if echo "$result" | jq -e '.summary' >/dev/null 2>&1; then
        summary=$(echo "$result" | jq -r '.summary' 2>/dev/null)
        status=$(echo "$result" | jq -r '.status' 2>/dev/null)
        
        log_success "Collaboration completed: $summary"
        log_info "Status: $status"
        
        # Show task results
        echo "$result" | jq -r '.results | to_entries[] | "\(.key): \(.value.content // .value | tostring)"' 2>/dev/null | while read -r line; do
            echo "  • ${line:0:100}..."
        done
        
        # Save to file if specified
        if [ -n "$output_file" ]; then
            echo "$result" | jq . > "$output_file"
            log_success "Results saved to: $output_file"
        fi
        
        return 0
    else
        log_error "Invalid response format"
        return 1
    fi
}

# Check service status
check_services() {
    log_info "Checking service status..."
    
    if ! check_gateway; then
        log_error "Gateway not available at $GATEWAY_URL"
        return 1
    fi
    
    services=$(curl -s "$GATEWAY_URL/services" 2>/dev/null)
    
    if [ -n "$services" ]; then
        online=$(echo "$services" | jq -r '.online_services' 2>/dev/null)
        total=$(echo "$services" | jq -r '.total_services' 2>/dev/null)
        
        log_info "Services online: $online/$total"
        
        echo "$services" | jq -r '.services | to_entries[] | select(.value.status == "online") | "  ✓ \(.key)"' 2>/dev/null
        echo "$services" | jq -r '.services | to_entries[] | select(.value.status != "online") | "  ✗ \(.key) (\(.value.status))"' 2>/dev/null
    else
        log_error "Could not retrieve service status"
        return 1
    fi
}

# Main command handler
main() {
    case "${1:-help}" in
        "collaborate"|"c")
            collaborate "$2" "$3" "$4"
            ;;
        "templates"|"t")
            list_templates
            ;;
        "suggest"|"s")
            suggest_template "$2"
            ;;
        "status"|"st")
            check_services
            ;;
        "health"|"h")
            curl -s "$GATEWAY_URL/health" | jq .
            ;;
        "help"|"--help"|"-h")
            echo "AI Gateway Shell Client"
            echo ""
            echo "Usage: $0 <command> [arguments]"
            echo ""
            echo "Commands:"
            echo "  collaborate, c  \"prompt\" [template] [output_file]  Execute collaboration"
            echo "  templates, t                                        List available templates"
            echo "  suggest, s      \"prompt\"                            Suggest template for prompt"
            echo "  status, st                                          Check service status"
            echo "  health, h                                           Check gateway health"
            echo "  help                                                Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 collaborate \"Build a web scraper\" code_development"
            echo "  $0 suggest \"Write unit tests\""
            echo "  $0 templates"
            echo ""
            echo "Environment:"
            echo "  GATEWAY_URL     Gateway URL (default: http://localhost:9000)"
            ;;
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    log_error "curl is required but not installed"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    log_error "jq is required but not installed"
    exit 1
fi

# Run main function
main "$@"
```

### cURL Examples Collection

#### Basic Operations
```bash
# Gateway information
curl http://localhost:9000/info | jq

# Service status
curl http://localhost:9000/services | jq

# Health check
curl http://localhost:9000/health | jq

# List templates
curl http://localhost:9000/workflows | jq
```

#### Collaboration Examples
```bash
# Simple collaboration
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze the benefits and drawbacks of remote work and create a comprehensive report",
    "context": {"format": "business_report", "length": "comprehensive"}
  }' | jq

# Code development with template
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python Flask API for a todo list application with database integration",
    "template": "code_development",
    "context": {
      "database": "SQLite",
      "include_tests": true,
      "authentication": "JWT"
    }
  }' | jq

# Creative project
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write an interactive mystery story set in Victorian London",
    "template": "creative_project",
    "context": {
      "genre": "mystery",
      "setting": "Victorian London",
      "interactive": true,
      "length": "short_story"
    }
  }' | jq

# Multi-domain analysis
curl -X POST http://localhost:9000/v1/collaborate/template \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Compare programming languages for web development: Python, JavaScript, and Go",
    "template": "multi_domain",
    "context": {
      "criteria": ["performance", "developer_experience", "ecosystem"],
      "use_case": "web_development"
    }
  }' | jq
```

#### Template Management
```bash
# Get specific template info
curl http://localhost:9000/workflows/code_development | jq

# Suggest template
curl -X POST http://localhost:9000/workflows/suggest \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Optimize database performance"}' | jq

# Get all template details
for template in research_analysis code_development creative_project technical_docs multi_domain problem_solving; do
  echo "=== $template ==="
  curl -s http://localhost:9000/workflows/$template | jq .template
  echo
done
```

#### Plan Creation and Execution
```bash
# Create a plan
plan_response=$(curl -s -X POST http://localhost:9000/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design and implement a microservices architecture for an e-commerce platform",
    "template": "code_development"
  }')

echo "Plan created:"
echo "$plan_response" | jq

# Extract plan ID and execute
plan_id=$(echo "$plan_response" | jq -r '.id')
echo "Executing plan: $plan_id"

curl -X POST "http://localhost:9000/v1/execute/$plan_id" | jq
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Gateway Not Responding

**Symptoms:**
- Connection refused
- Timeout errors
- No response from gateway

**Diagnosis:**
```bash
# Check if gateway is running
curl -I http://localhost:9000/info

# Check Docker container status
docker ps | grep ai-gateway

# Check gateway logs
docker logs ai-platform-ai-gateway
```

**Solutions:**
```bash
# Restart AI stack
./start-ai-stack.sh restart

# Check gateway specifically
docker-compose -f docker-compose.ai-stack.yml restart ai-gateway

# Verify port availability
netstat -tlnp | grep :9000
```

#### 2. Services Unavailable

**Symptoms:**
- "Backend unavailable" errors
- Service status shows offline
- Collaboration fails consistently

**Diagnosis:**
```bash
# Check service health
curl http://localhost:9000/services | jq '.services[] | select(.status != "online")'

# Check individual service health
curl http://localhost:8000/health  # vLLM Reasoning
curl http://localhost:8001/health  # vLLM General
curl http://localhost:8002/health  # vLLM Coding
```

**Solutions:**
```bash
# Restart specific services
docker-compose -f docker-compose.ai-stack.yml restart vllm-reasoning
docker-compose -f docker-compose.ai-stack.yml restart vllm-general
docker-compose -f docker-compose.ai-stack.yml restart vllm-coding

# Check service logs
docker-compose -f docker-compose.ai-stack.yml logs vllm-reasoning

# Verify GPU availability (for vLLM services)
nvidia-smi
```

#### 3. Template Errors

**Symptoms:**
- "Template not found" errors
- Invalid template responses
- Template suggestion failures

**Diagnosis:**
```bash
# List available templates
curl http://localhost:9000/workflows

# Test template suggestion
curl -X POST http://localhost:9000/workflows/suggest \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test prompt"}'
```

**Solutions:**
```bash
# Use correct template names
curl http://localhost:9000/workflows | jq -r '.templates | keys[]'

# Fallback to auto-suggestion
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "your task without template"}'
```

#### 4. Task Timeouts

**Symptoms:**
- Requests timeout
- Partial results returned
- Long response times

**Diagnosis:**
```bash
# Check service load
curl http://localhost:9000/services | jq '.services[].status'

# Monitor system resources
htop
nvidia-smi  # For GPU usage

# Check network latency
ping localhost
```

**Solutions:**
```bash
# Increase timeout (in client)
curl --max-time 120 http://localhost:9000/v1/collaborate ...

# Break complex tasks into smaller parts
# Use parallel execution
{
  "context": {
    "parallel_execution": true,
    "max_tokens": 200  # Reduce token count
  }
}

# Exclude slow services
{
  "context": {
    "exclude_services": ["oobabooga"]
  }
}
```

#### 5. Memory Issues

**Symptoms:**
- Out of memory errors
- Service crashes
- GPU memory errors

**Diagnosis:**
```bash
# Check system memory
free -h

# Check GPU memory
nvidia-smi

# Check Docker memory usage
docker stats

# Check service logs for memory errors
docker logs ai-platform-vllm-reasoning | grep -i memory
```

**Solutions:**
```bash
# Reduce model memory usage
# Edit docker-compose.ai-stack.yml
--gpu-memory-utilization 0.6  # Reduce from 0.8

# Restart services with lower memory allocation
docker-compose -f docker-compose.ai-stack.yml down
docker-compose -f docker-compose.ai-stack.yml up -d

# Use smaller models or reduce batch sizes
```

### Debug Mode

#### Enable Detailed Logging
```bash
# Set environment variables
export FLASK_ENV=development
export LOG_LEVEL=DEBUG

# Restart gateway with debug mode
docker-compose -f docker-compose.ai-stack.yml restart ai-gateway
```

#### Monitor Real-time Logs
```bash
# Follow gateway logs
docker logs -f ai-platform-ai-gateway

# Monitor all services
docker-compose -f docker-compose.ai-stack.yml logs -f

# Filter for errors
docker-compose -f docker-compose.ai-stack.yml logs | grep -i error
```

### Performance Monitoring

#### Real-time Monitoring
```bash
# Monitor service health continuously
watch -n 5 'curl -s http://localhost:9000/health | jq ".backends | map_values(.status)"'

# Monitor collaboration performance
time curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Simple test task"}'

# Monitor system resources
watch -n 2 'docker stats --no-stream'
```

#### Performance Benchmarking
```bash
#!/bin/bash
# Performance benchmark script

GATEWAY_URL="http://localhost:9000"
ITERATIONS=10

echo "Benchmarking Gateway Performance"
echo "================================"

# Test simple collaboration
echo "Testing simple collaboration..."
for i in $(seq 1 $ITERATIONS); do
  start_time=$(date +%s.%N)
  
  curl -s -X POST "$GATEWAY_URL/v1/collaborate" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Write a hello world program", "context": {"max_tokens": 50}}' \
    >/dev/null
  
  end_time=$(date +%s.%N)
  duration=$(echo "$end_time - $start_time" | bc)
  echo "Iteration $i: ${duration}s"
done

# Test template-based collaboration
echo "Testing template collaboration..."
for i in $(seq 1 $ITERATIONS); do
  start_time=$(date +%s.%N)
  
  curl -s -X POST "$GATEWAY_URL/v1/collaborate/template" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Create a simple calculator", "template": "code_development", "context": {"max_tokens": 100}}' \
    >/dev/null
  
  end_time=$(date +%s.%N)
  duration=$(echo "$end_time - $start_time" | bc)
  echo "Template iteration $i: ${duration}s"
done
```

---

## Best Practices

### Request Design

#### 1. Clear and Specific Prompts
```bash
# Good: Specific and actionable
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python Flask REST API for user authentication with JWT tokens, including registration, login, and password reset endpoints",
    "context": {
      "framework": "Flask",
      "authentication": "JWT",
      "database": "PostgreSQL",
      "include_tests": true
    }
  }'

# Avoid: Vague and unclear
curl -X POST http://localhost:9000/v1/collaborate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build something with Python"}'
```

#### 2. Appropriate Context
```json
{
  "context": {
    // Output preferences
    "max_tokens": 1000,
    "format": "markdown",
    "detail_level": "comprehensive",
    
    // Domain context
    "target_audience": "developers",
    "complexity": "intermediate",
    "industry": "fintech",
    
    // Technical requirements
    "technologies": ["Python", "FastAPI", "PostgreSQL"],
    "deployment": "Docker",
    "include_tests": true,
    
    // Collaboration preferences
    "parallel_execution": true,
    "preferred_services": ["vllm-coding", "perplexica"]
  }
}
```

#### 3. Template Selection
```bash
# Use appropriate templates for task types
# Research tasks
template: "research_analysis"

# Software development
template: "code_development" 

# Documentation
template: "technical_docs"

# Creative content
template: "creative_project"

# Complex analysis
template: "multi_domain"

# Troubleshooting
template: "problem_solving"
```

### Error Handling Patterns

#### 1. Client-Side Retry Logic
```python
import time
import requests
from typing import Optional, Dict, Any

def robust_collaborate(prompt: str, max_retries: int = 3, 
                      backoff_factor: float = 2.0) -> Optional[Dict[str, Any]]:
    """Collaborate with automatic retry logic"""
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'http://localhost:9000/v1/collaborate',
                json={'prompt': prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'error' not in result:
                    return result
                else:
                    print(f"API error: {result['error']}")
            else:
                print(f"HTTP error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
        except requests.exceptions.ConnectionError:
            print(f"Connection error on attempt {attempt + 1}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        if attempt < max_retries - 1:
            sleep_time = backoff_factor ** attempt
            print(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    
    print("All retry attempts failed")
    return None
```

#### 2. Service Health Checking
```bash
#!/bin/bash
# Health check before making requests

check_gateway_health() {
    local health_response
    health_response=$(curl -s http://localhost:9000/health 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$health_response" | jq -e '.overall_status == "healthy"' >/dev/null 2>&1; then
        return 0
    else
        echo "Gateway health check failed"
        return 1
    fi
}

# Use before important requests
if check_gateway_health; then
    echo "Gateway is healthy, proceeding with collaboration"
    curl -X POST http://localhost:9000/v1/collaborate \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Your important task"}'
else
    echo "Gateway not healthy, skipping request"
    exit 1
fi
```

### Performance Optimization

#### 1. Service Preferences
```json
{
  "context": {
    // Prefer faster services for simple tasks
    "service_preferences": ["vllm-general", "vllm-coding"],
    
    // Exclude slower services for time-sensitive requests
    "exclude_services": ["oobabooga"],
    
    // Enable parallel execution
    "parallel_execution": true
  }
}
```

#### 2. Batch Processing
```python
import asyncio
import aiohttp
from typing import List, Dict

async def batch_collaborate(requests: List[Dict]) -> List[Dict]:
    """Process multiple collaboration requests efficiently"""
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for req in requests:
            task = session.post(
                'http://localhost:9000/v1/collaborate',
                json=req,
                timeout=aiohttp.ClientTimeout(total=60)
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        results = []
        
        for response in responses:
            if isinstance(response, Exception):
                results.append({'error': str(response)})
            else:
                results.append(await response.json())
        
        return results

# Usage
requests = [
    {'prompt': 'Task 1', 'template': 'research_analysis'},
    {'prompt': 'Task 2', 'template': 'code_development'},
    {'prompt': 'Task 3', 'template': 'creative_project'}
]

results = asyncio.run(batch_collaborate(requests))
```

#### 3. Caching Strategies
```python
import time
import hashlib
from typing import Dict, Any, Optional

class CollaborationCache:
    def __init__(self, ttl: int = 300):  # 5 minutes TTL
        self.cache: Dict[str, tuple] = {}
        self.ttl = ttl
    
    def _get_key(self, prompt: str, template: Optional[str] = None) -> str:
        """Generate cache key"""
        content = f"{prompt}:{template or 'auto'}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, template: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached result if still valid"""
        key = self._get_key(prompt, template)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                del self.cache[key]
        
        return None
    
    def set(self, prompt: str, result: Dict[str, Any], template: Optional[str] = None):
        """Cache result"""
        key = self._get_key(prompt, template)
        self.cache[key] = (result, time.time())

# Usage with caching
cache = CollaborationCache()

def cached_collaborate(prompt: str, template: Optional[str] = None) -> Dict[str, Any]:
    # Check cache first
    cached_result = cache.get(prompt, template)
    if cached_result:
        print("Using cached result")
        return cached_result
    
    # Make request
    result = make_collaboration_request(prompt, template)
    
    # Cache successful results
    if 'error' not in result:
        cache.set(prompt, result, template)
    
    return result
```

### Security Considerations

#### 1. Input Validation
```python
import re
from typing import Dict, Any

def validate_prompt(prompt: str) -> bool:
    """Validate prompt for security concerns"""
    
    # Check length
    if len(prompt) > 10000:
        return False
    
    # Check for potential injection patterns
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'data:text/html',
        r'eval\s*\(',
        r'exec\s*\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False
    
    return True

def safe_collaborate(prompt: str, **kwargs) -> Dict[str, Any]:
    """Safely execute collaboration with input validation"""
    
    if not validate_prompt(prompt):
        return {'error': 'Invalid or potentially unsafe prompt'}
    
    # Sanitize context
    context = kwargs.get('context', {})
    safe_context = {
        k: v for k, v in context.items() 
        if isinstance(v, (str, int, float, bool)) and len(str(v)) < 1000
    }
    
    return make_collaboration_request(prompt, context=safe_context, **kwargs)
```

#### 2. Rate Limiting
```python
import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] < now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        return False

# Usage
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

def rate_limited_collaborate(client_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
    """Rate-limited collaboration"""
    
    if not rate_limiter.is_allowed(client_id):
        return {
            'error': 'Rate limit exceeded',
            'retry_after': 60
        }
    
    return make_collaboration_request(prompt, **kwargs)
```

### Monitoring and Logging

#### 1. Request Logging
```python
import logging
import time
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('collaboration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('collaboration_client')

def logged_collaborate(prompt: str, **kwargs) -> Dict[str, Any]:
    """Collaboration with comprehensive logging"""
    
    start_time = time.time()
    request_id = f"req_{int(start_time)}_{hash(prompt) % 10000}"
    
    logger.info(f"Starting collaboration {request_id}: {prompt[:100]}...")
    
    try:
        result = make_collaboration_request(prompt, **kwargs)
        
        execution_time = time.time() - start_time
        
        if 'error' in result:
            logger.error(f"Collaboration {request_id} failed: {result['error']}")
        else:
            logger.info(f"Collaboration {request_id} completed in {execution_time:.2f}s")
            
            # Log task summary
            if 'results' in result:
                task_count = len(result['results'])
                logger.info(f"Collaboration {request_id}: {task_count} tasks completed")
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.exception(f"Collaboration {request_id} exception after {execution_time:.2f}s: {e}")
        return {'error': f'Client exception: {str(e)}'}
```

#### 2. Metrics Collection
```python
import time
from collections import defaultdict
from typing import Dict, Any

class CollaborationMetrics:
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.template_usage = defaultdict(int)
        self.service_usage = defaultdict(int)
    
    def record_request(self, template: str, execution_time: float, 
                      success: bool, services_used: list = None):
        """Record metrics for a collaboration request"""
        
        self.request_count += 1
        self.total_execution_time += execution_time
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        
        if template:
            self.template_usage[template] += 1
        
        if services_used:
            for service in services_used:
                self.service_usage[service] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_time = self.total_execution_time / max(self.request_count, 1)
        success_rate = self.success_count / max(self.request_count, 1)
        
        return {
            'total_requests': self.request_count,
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'template_usage': dict(self.template_usage),
            'service_usage': dict(self.service_usage)
        }

# Global metrics instance
metrics = CollaborationMetrics()

def metrics_aware_collaborate(prompt: str, **kwargs) -> Dict[str, Any]:
    """Collaboration with metrics collection"""
    
    start_time = time.time()
    template = kwargs.get('template')
    
    try:
        result = make_collaboration_request(prompt, **kwargs)
        
        execution_time = time.time() - start_time
        success = 'error' not in result
        services_used = result.get('services_used', [])
        
        metrics.record_request(template, execution_time, success, services_used)
        
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        metrics.record_request(template, execution_time, False)
        raise
```

---

## Conclusion

The Enhanced API Gateway provides a powerful and flexible platform for multi-agent AI collaboration. By leveraging intelligent task decomposition, service orchestration, and workflow templates, you can tackle complex projects that require coordination across multiple AI services and domains.

### Key Takeaways

1. **Start Simple**: Use basic collaboration endpoints before moving to complex workflows
2. **Choose Appropriate Templates**: Select templates that match your task requirements
3. **Provide Rich Context**: Include relevant context to improve results
4. **Handle Errors Gracefully**: Implement retry logic and fallback strategies
5. **Monitor Performance**: Track service health and collaboration metrics
6. **Optimize for Scale**: Use batch processing and caching for high-volume scenarios

### Next Steps

1. **Explore Examples**: Try the provided integration examples
2. **Create Custom Workflows**: Develop templates for your specific use cases  
3. **Monitor and Optimize**: Implement logging and metrics collection
4. **Scale Gradually**: Start with simple collaborations and expand complexity
5. **Contribute**: Share your templates and improvements with the community

### Support Resources

- **Documentation**: Complete guides in the repository
- **Examples**: Integration examples in multiple languages
- **Testing**: Comprehensive test suites and validation scripts
- **Monitoring**: Health checks and performance monitoring tools

For additional help, check the troubleshooting section, review the logs, and ensure all services are properly configured and running.

---

**Last Updated**: August 2025  
**Version**: 2.0.0  
**Gateway URL**: http://localhost:9000  
**Repository**: [AI Research Platform](https://github.com/kmransom56/chat-copilot)