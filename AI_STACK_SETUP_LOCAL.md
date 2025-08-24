# Advanced AI Stack Setup Guide

This guide covers the setup and integration of the vLLM + Oobabooga + KoboldCpp AI stack with the Chat Copilot platform.

## Overview

The Advanced AI Stack provides specialized AI services for different task types:

- **vLLM Services**: High-performance inference for reasoning, general tasks, and coding
- **Oobabooga**: Advanced text generation with multimodal capabilities
- **KoboldCpp**: Creative writing and roleplay scenarios
- **API Gateway**: Unified interface with intelligent routing

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   Monitoring    │
│   Port: 9000    │    │  Grafana: 11002 │
└─────────────────┘    └─────────────────┘
         │
    ┌────┴────┐
    │ Router  │
    └────┬────┘
         │
    ┌────┴──────────────────────────┐
    │                               │
┌───▼───┐  ┌──────┐  ┌──────┐  ┌────▼────┐
│ vLLM  │  │vLLM  │  │vLLM  │  │Oobabooga│
│Reason │  │General│ │Coding│  │  API    │
│ :8000 │  │ :8001│  │ :8002│  │  :5000  │
└───────┘  └──────┘  └──────┘  └─────────┘
                                     │
                              ┌──────▼───┐
                              │KoboldCpp │
                              │  :5001   │
                              └──────────┘
```

## Prerequisites

### System Requirements

- **GPU**: NVIDIA GPU with CUDA support (Tesla K80 or better)
- **Memory**: 32GB+ RAM recommended
- **Storage**: 100GB+ free space for models
- **OS**: Linux with Docker support

### Software Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- NVIDIA Container Toolkit
- Git

### API Keys

- **HuggingFace Token**: Required for gated models (some DeepSeek models)
- **OpenAI API Key**: Optional, for fallback services

## Installation

### 1. Clone and Setup

```bash
git clone https://github.com/kmransom56/chat-copilot.git
cd chat-copilot
```

### 2. Environment Configuration

Update `.env` file with required tokens:

```bash
# HuggingFace authentication
HUGGINGFACE_TOKEN=hf_your_token_here

# Neo4j password
NEO4J_PASSWORD=password

# Other existing keys...
```

### 3. GPU Setup

Verify NVIDIA GPU access:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu22.04 nvidia-smi
```

### 4. Start the AI Stack

```bash
# Start complete stack
./start-ai-stack.sh start

# Or with Docker Compose directly
docker-compose -f docker-compose.ai-stack.yml up -d
```

## Service Configuration

### vLLM Services

The stack includes three vLLM instances:

#### Reasoning Service (Port 8000)
- **Model**: DeepSeek-R1-Distill-Qwen-1.5B
- **Purpose**: Complex reasoning and analysis
- **API**: OpenAI-compatible

#### General Service (Port 8001)
- **Model**: Mistral-7B-Instruct-v0.3
- **Purpose**: General conversation and tasks
- **API**: OpenAI-compatible

#### Coding Service (Port 8002)
- **Model**: deepseek-coder-6.7b-instruct
- **Purpose**: Code generation and debugging
- **API**: OpenAI-compatible

### Oobabooga Configuration

- **Web UI**: http://localhost:7860
- **API**: http://localhost:5000
- **Features**: Advanced text generation, multimodal support
- **GPU**: Optimized for Tesla K80 (CUDA 3.7)

### KoboldCpp Configuration

- **Port**: 5001
- **Purpose**: Creative writing and roleplay
- **GPU**: CUDA-accelerated with optimized settings
- **Models**: Downloads default model automatically

## API Usage

### Gateway Endpoints

The AI Gateway provides a unified interface:

```bash
# Health check
curl http://localhost:9000/health

# Completion with task routing
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reasoning",
    "prompt": "Solve: 2x + 5 = 17",
    "max_tokens": 100,
    "temperature": 0.7
  }'

# OpenAI-compatible chat
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "task_type": "general",
    "max_tokens": 100
  }'
```

### Task Types

- `reasoning`: Complex analysis, math, logic problems
- `general`: Conversations, general Q&A
- `coding`: Code generation, debugging, review
- `creative`: Stories, poems, creative writing
- `advanced`: Complex multimodal tasks

## Management Commands

### Startup and Control

```bash
# Start stack
./start-ai-stack.sh start

# Check status
./start-ai-stack.sh status

# View logs
./start-ai-stack.sh logs [service-name]

# Stop stack
./start-ai-stack.sh stop

# Restart stack
./start-ai-stack.sh restart
```

### Health Monitoring

```bash
# Gateway health
curl http://localhost:9000/health

# Individual service health
curl http://localhost:8000/health  # vLLM Reasoning
curl http://localhost:8001/health  # vLLM General
curl http://localhost:8002/health  # vLLM Coding

# Container status
docker-compose -f docker-compose.ai-stack.yml ps
```

### Testing

```bash
# Run integration tests
./test-ai-stack.sh

# Test specific functionality
./scripts/platform-management/manage-ai-stack.sh test
```

## Performance Optimization

### Tesla K80 Optimizations

The stack is optimized for Tesla K80 GPUs:

- **Memory Management**: Conservative GPU memory allocation
- **Quantization**: 8-bit quantization when needed
- **Context Length**: Optimized context windows
- **Batch Size**: Single-batch processing

### Memory Configuration

```yaml
# GPU memory limits per service
vLLM Services: 24GB limit (8GB per service)
Oobabooga: 16GB limit
KoboldCpp: 16GB limit
```

### Model Loading

Models are loaded on-demand:
- vLLM models: Downloaded from HuggingFace automatically
- KoboldCpp: Downloads default model if none present
- Oobabooga: Uses configured models directory

## Troubleshooting

### Common Issues

#### GPU Access Problems
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu22.04 nvidia-smi

# Check container GPU allocation
docker exec ai-platform-vllm-reasoning nvidia-smi
```

#### Memory Issues
```bash
# Check GPU memory usage
nvidia-smi

# Reduce memory allocation in docker-compose.ai-stack.yml
# Lower gpu-memory-utilization values
```

#### Model Loading Failures
```bash
# Check HuggingFace token
echo $HUGGINGFACE_TOKEN

# Check model download logs
docker-compose -f docker-compose.ai-stack.yml logs vllm-reasoning

# Manual token authentication
huggingface-cli login
```

#### Service Communication
```bash
# Test network connectivity
docker network ls
docker network inspect chatcopilot_ai-platform

# Check service DNS resolution
docker exec ai-platform-ai-gateway nslookup vllm-reasoning
```

### Log Analysis

```bash
# Gateway logs
docker-compose -f docker-compose.ai-stack.yml logs ai-gateway

# vLLM service logs
docker-compose -f docker-compose.ai-stack.yml logs vllm-reasoning
docker-compose -f docker-compose.ai-stack.yml logs vllm-general
docker-compose -f docker-compose.ai-stack.yml logs vllm-coding

# Oobabooga logs
docker-compose -f docker-compose.ai-stack.yml logs oobabooga

# KoboldCpp logs
docker-compose -f docker-compose.ai-stack.yml logs koboldcpp
```

## Security Considerations

### API Access
- Gateway runs on localhost by default
- Add authentication for production use
- Use environment variables for sensitive tokens

### Model Security
- Models downloaded from trusted sources (HuggingFace)
- Local model caching for offline operation
- No telemetry data sent to external services

### Network Security
- Internal Docker network isolation
- No external network access required after setup
- Configurable firewall rules

## Production Deployment

### Scaling

```bash
# Scale gateway instances
docker-compose -f docker-compose.ai-stack.yml up -d --scale ai-gateway=3

# Load balancer configuration (nginx example)
upstream ai_gateway {
    server localhost:9000;
    server localhost:9001;
    server localhost:9002;
}
```

### Monitoring

- **Grafana**: http://localhost:11002 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Health Endpoints**: Built-in health checks for all services

### Backup and Recovery

```bash
# Backup models and configuration
tar -czf ai-stack-backup.tar.gz models/ python/ai-stack/ .env

# Restore from backup
tar -xzf ai-stack-backup.tar.gz
```

## Integration with Chat Copilot

The AI Stack integrates seamlessly with the main Chat Copilot application:

1. **Backend Integration**: Add AI Stack endpoints to `appsettings.json`
2. **Frontend Integration**: Configure endpoints in `webapp/.env`
3. **Routing**: Use task-specific routing for optimal model selection

### Configuration Updates

```json
// webapi/appsettings.json
{
  "AIStack": {
    "GatewayUrl": "http://localhost:9000",
    "EnableTaskRouting": true,
    "DefaultTaskType": "general"
  }
}
```

```bash
# webapp/.env
REACT_APP_AI_STACK_URL=http://localhost:9000
REACT_APP_AI_STACK_ENABLED=true
```

## Support and Contributing

For issues and contributions:
- **Issues**: GitHub Issues on the main repository
- **Documentation**: This file and inline code comments
- **Community**: Discord/Slack channels (if available)

---

**Last Updated**: August 2025
**Version**: 1.0.0
**Compatible with**: Chat Copilot v2.0+