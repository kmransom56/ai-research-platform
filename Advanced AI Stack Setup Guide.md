# Advanced AI Stack Setup Guide
## vLLM + Oobabooga + KoboldCpp on Ubuntu 24.04

### System Overview
- **Hardware**: 128GB RAM, 96GB VRAM, i7 processor, Ubuntu 24.04
- **Current Setup**: Ollama + Open WebUI
- **Target Setup**: vLLM (high-performance) + Oobabooga (advanced features) + KoboldCpp (creative writing)
- **Integration**: API endpoints for your AI platform repository

---

## Part 1: Prerequisites & Environment Setup

### 1.1 CUDA Installation (if not already done)
```bash
# Check current CUDA version
nvcc --version
nvidia-smi

# Install CUDA 12.4 (recommended for latest vLLM)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-4

# Add to ~/.bashrc
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 1.2 Python Environment Setup
```bash
# Install UV (fastest Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Create base directory for AI stack
mkdir -p ~/ai-stack
cd ~/ai-stack
```

---

## Part 2: vLLM Installation & Setup (Primary High-Performance Engine)

### 2.1 vLLM Installation
```bash
cd ~/ai-stack
mkdir vllm-setup
cd vllm-setup

# Create environment with UV
uv venv vllm-env --python 3.12 --seed
source vllm-env/bin/activate

# Install vLLM with CUDA support
uv pip install vllm
# Alternative for latest features:
# uv pip install --pre vllm==0.10.1+gptoss --extra-index-url https://wheels.vllm.ai/gpt-oss/

# Verify installation
python -c "import vllm; print('vLLM installed successfully')"
```

### 2.2 vLLM Configuration for DeepSeek R1
```bash
# Enable vLLM V1 for better performance
export VLLM_USE_V1=1

# Create startup script
cat > ~/ai-stack/vllm-setup/start_deepseek.sh << 'EOF'
#!/bin/bash
export VLLM_USE_V1=1
source ~/ai-stack/vllm-setup/vllm-env/bin/activate

# For full DeepSeek R1 (requires ~90GB VRAM)
vllm serve "deepseek-ai/DeepSeek-R1" \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code \
    --tensor-parallel-size 1 \
    --enable-reasoning \
    --reasoning-parser deepseek_r1 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 32768 \
    --disable-log-requests

# Alternative: Smaller distilled version for testing
# vllm serve "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B" \
#     --host 0.0.0.0 \
#     --port 8000 \
#     --max-model-len 4096 \
#     --tensor-parallel-size 1
EOF

chmod +x ~/ai-stack/vllm-setup/start_deepseek.sh
```

### 2.3 vLLM Multi-Model Configuration
```bash
# Create configuration for running multiple models
cat > ~/ai-stack/vllm-setup/start_multi_models.sh << 'EOF'
#!/bin/bash
export VLLM_USE_V1=1
source ~/ai-stack/vllm-setup/vllm-env/bin/activate

# Start DeepSeek R1 on port 8000 (primary reasoning model)
echo "Starting DeepSeek R1..."
vllm serve "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B" \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code \
    --max-model-len 8192 &

# Start Mistral Small 3.1 on port 8001 (fast general purpose)
echo "Starting Mistral Small 3.1..."
vllm serve "mistralai/Mistral-Small-Instruct-2409" \
    --host 0.0.0.0 \
    --port 8001 \
    --max-model-len 16384 &

# Start coding model on port 8002
echo "Starting DeepSeek Coder..."
vllm serve "deepseek-ai/deepseek-coder-6.7b-instruct" \
    --host 0.0.0.0 \
    --port 8002 \
    --max-model-len 8192 &

echo "All models starting... Check status with 'curl http://localhost:8000/v1/models'"
wait
EOF

chmod +x ~/ai-stack/vllm-setup/start_multi_models.sh
```

---

## Part 3: Oobabooga Text-Generation-WebUI Setup

### 3.1 Installation
```bash
cd ~/ai-stack
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui

# Run the installer
./start_linux.sh
# When prompted, select:
# A) NVIDIA
# B) CUDA 12.4 (or your installed version)
# C) Your GPU series (RTX/GTX)
```

### 3.2 Configuration for Your Hardware
```bash
# Create optimized startup script
cat > ~/ai-stack/text-generation-webui/start_optimized.sh << 'EOF'
#!/bin/bash
cd ~/ai-stack/text-generation-webui

# Activate the conda environment
source installer_files/conda/etc/profile.d/conda.sh
conda activate installer_files/env

# Start with optimized settings for your hardware
python server.py \
    --listen \
    --listen-port 7860 \
    --api \
    --api-port 5000 \
    --gpu-memory $(python -c "import torch; print(min(90, int(torch.cuda.get_device_properties(0).total_memory / 1024**3 * 0.9)))") \
    --max-seq-len 32768 \
    --load-in-4bit \
    --use-fast-tokenizer \
    --no-stream \
    --extensions api openai multimodal whisper_stt tts
EOF

chmod +x ~/ai-stack/text-generation-webui/start_optimized.sh
```

### 3.3 Model Downloads for Oobabooga
```bash
cd ~/ai-stack/text-generation-webui
source installer_files/conda/etc/profile.d/conda.sh
conda activate installer_files/env

# Download models using the built-in script
python download-model.py deepseek-ai/deepseek-llm-7b-chat
python download-model.py microsoft/DialoGPT-medium
python download-model.py NousResearch/Llama-2-7b-chat-hf
```

---

## Part 4: KoboldCpp Setup (Creative Writing & Roleplay)

### 4.1 Installation
```bash
cd ~/ai-stack
mkdir koboldcpp
cd koboldcpp

# Download latest release
wget https://github.com/LostRuins/koboldcpp/releases/latest/download/koboldcpp-linux-x64-cuda1215.tar.gz
tar -xzf koboldcpp-linux-x64-cuda1215.tar.gz

# Or compile from source for optimal performance
git clone https://github.com/LostRuins/koboldcpp.git
cd koboldcpp
make LLAMA_CUBLAS=1

# Create startup script
cat > ~/ai-stack/koboldcpp/start_kobold.sh << 'EOF'
#!/bin/bash
cd ~/ai-stack/koboldcpp

# Start KoboldCpp with GPU acceleration
./koboldcpp \
    --model ./models/your-model.gguf \
    --port 5001 \
    --host 0.0.0.0 \
    --gpulayers 32 \
    --usecuda \
    --contextsize 8192 \
    --blasbatchsize 512 \
    --highpriority
EOF

chmod +x ~/ai-stack/koboldcpp/start_kobold.sh
```

### 4.2 Model Setup for KoboldCpp
```bash
# Create models directory
mkdir -p ~/ai-stack/koboldcpp/models

# Download GGUF models (examples)
cd ~/ai-stack/koboldcpp/models

# Download recommended creative writing models
wget https://huggingface.co/TheBloke/L3-8B-Stheno-v3.2-GGUF/resolve/main/l3-8b-stheno-v3.2.Q4_K_M.gguf
wget https://huggingface.co/bartowski/gemma-3-27b-abliterated-GGUF/resolve/main/gemma-3-27b-abliterated-Q4_K_M.gguf
```

---

## Part 5: Integration with Your AI Platform

### 5.1 API Gateway Setup
```bash
# Create a unified API gateway script
cat > ~/ai-stack/api_gateway.py << 'EOF'
#!/usr/bin/env python3
"""
Unified API Gateway for AI Platform Integration
Routes requests to appropriate backends based on task type
"""

from flask import Flask, request, jsonify, Response
import requests
import json
from typing import Dict, Any

app = Flask(__name__)

# Backend configurations
BACKENDS = {
    'reasoning': 'http://localhost:8000',      # vLLM DeepSeek R1
    'general': 'http://localhost:8001',        # vLLM Mistral
    'coding': 'http://localhost:8002',         # vLLM DeepSeek Coder
    'creative': 'http://localhost:5001',       # KoboldCpp
    'advanced': 'http://localhost:5000'        # Oobabooga API
}

def route_request(task_type: str, prompt: str, **kwargs) -> Dict[str, Any]:
    """Route request to appropriate backend based on task type"""
    
    backend_url = BACKENDS.get(task_type, BACKENDS['general'])
    
    if task_type == 'creative':
        # KoboldCpp API format
        payload = {
            "prompt": prompt,
            "max_length": kwargs.get('max_tokens', 512),
            "temperature": kwargs.get('temperature', 0.8)
        }
        response = requests.post(f"{backend_url}/api/v1/generate", json=payload)
    else:
        # OpenAI-compatible format for vLLM and Oobabooga
        payload = {
            "model": "auto",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get('max_tokens', 512),
            "temperature": kwargs.get('temperature', 0.7)
        }
        response = requests.post(f"{backend_url}/v1/chat/completions", json=payload)
    
    return response.json()

@app.route('/v1/completions', methods=['POST'])
def completions():
    data = request.json
    task_type = data.get('task_type', 'general')
    prompt = data.get('prompt', '')
    
    result = route_request(task_type, prompt, **data)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    status = {}
    for name, url in BACKENDS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            status[name] = "online" if response.status_code == 200 else "offline"
        except:
            status[name] = "offline"
    
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)
EOF

chmod +x ~/ai-stack/api_gateway.py
```

### 5.2 System Management Scripts
```bash
# Create system management script
cat > ~/ai-stack/manage_stack.sh << 'EOF'
#!/bin/bash
# AI Stack Management Script

STACK_DIR="$HOME/ai-stack"

start_all() {
    echo "Starting AI Stack..."
    
    # Start vLLM models
    echo "Starting vLLM services..."
    cd "$STACK_DIR/vllm-setup"
    ./start_multi_models.sh &
    
    # Start Oobabooga
    echo "Starting Oobabooga..."
    cd "$STACK_DIR/text-generation-webui"
    ./start_optimized.sh &
    
    # Start KoboldCpp
    echo "Starting KoboldCpp..."
    cd "$STACK_DIR/koboldcpp"
    ./start_kobold.sh &
    
    # Wait for services to initialize
    sleep 30
    
    # Start API Gateway
    echo "Starting API Gateway..."
    cd "$STACK_DIR"
    python3 api_gateway.py &
    
    echo "AI Stack started! Check status with: $0 status"
}

stop_all() {
    echo "Stopping AI Stack..."
    pkill -f "vllm serve"
    pkill -f "server.py"
    pkill -f "koboldcpp"
    pkill -f "api_gateway.py"
    echo "AI Stack stopped."
}

status() {
    echo "AI Stack Status:"
    curl -s http://localhost:9000/health | python3 -m json.tool
}

case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 5
        start_all
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF

chmod +x ~/ai-stack/manage_stack.sh
```

---

## Part 6: Testing & Validation

### 6.1 Test Individual Services
```bash
# Test vLLM DeepSeek R1
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    "messages": [{"role": "user", "content": "Solve: 2x + 5 = 17"}],
    "max_tokens": 256
  }'

# Test Oobabooga API
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain quantum computing"}],
    "max_tokens": 200
  }'

# Test KoboldCpp
curl -X POST http://localhost:5001/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a creative story about AI",
    "max_length": 200
  }'
```

### 6.2 Test Unified API Gateway
```bash
# Test reasoning task
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "reasoning",
    "prompt": "If a train travels at 80 mph for 2.5 hours, how far does it go?",
    "max_tokens": 150
  }'

# Test creative task
curl -X POST http://localhost:9000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "creative",
    "prompt": "Write a haiku about artificial intelligence",
    "max_tokens": 100
  }'
```

---

## Part 7: Integration Points for Your AI Platform Repository

### 7.1 Python SDK for Your Repository
```python
# Add this to your AI platform repository
import requests
from typing import Optional, Dict, Any

class AdvancedAIStack:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
    
    def complete(self, 
                prompt: str, 
                task_type: str = "general",
                max_tokens: int = 512,
                temperature: float = 0.7) -> Dict[str, Any]:
        """
        Send completion request to AI stack
        
        task_types: 'reasoning', 'general', 'coding', 'creative', 'advanced'
        """
        payload = {
            "task_type": task_type,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(f"{self.base_url}/v1/completions", json=payload)
        return response.json()
    
    def health_check(self) -> Dict[str, str]:
        """Check health of all backend services"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage example in your applications
ai = AdvancedAIStack()

# For complex reasoning
result = ai.complete("Analyze the pros and cons of renewable energy", task_type="reasoning")

# For code generation
code_result = ai.complete("Write a Python function to sort a list", task_type="coding")

# For creative writing
story = ai.complete("Write a short sci-fi story", task_type="creative")
```

### 7.2 Environment Variables for Configuration
```bash
# Add to your repository's .env file
AI_STACK_BASE_URL=http://localhost:9000
REASONING_MODEL_URL=http://localhost:8000
GENERAL_MODEL_URL=http://localhost:8001
CODING_MODEL_URL=http://localhost:8002
CREATIVE_MODEL_URL=http://localhost:5001
ADVANCED_MODEL_URL=http://localhost:5000
```

---

## Part 8: Performance Optimization Tips

### 8.1 Memory Management
- **DeepSeek R1**: Use quantization (4-bit) if you want to run multiple large models
- **GPU Memory Allocation**: Reserve ~90GB for DeepSeek R1, ~6GB for other models
- **CPU Memory**: Utilize your 128GB RAM for model caching and preprocessing

### 8.2 Monitoring Setup
```bash
# Install monitoring tools
pip install nvidia-ml-py3 psutil

# Create monitoring script
cat > ~/ai-stack/monitor.py << 'EOF'
import nvidia_ml_py3 as nvml
import psutil
import time
import json

def get_system_stats():
    nvml.nvmlInit()
    handle = nvml.nvmlDeviceGetHandleByIndex(0)
    
    gpu_mem = nvml.nvmlDeviceGetMemoryInfo(handle)
    gpu_util = nvml.nvmlDeviceGetUtilizationRates(handle)
    
    return {
        "gpu_memory_used": gpu_mem.used // 1024**3,  # GB
        "gpu_memory_total": gpu_mem.total // 1024**3,  # GB
        "gpu_utilization": gpu_util.gpu,
        "cpu_percent": psutil.cpu_percent(),
        "ram_used": psutil.virtual_memory().used // 1024**3,  # GB
        "ram_total": psutil.virtual_memory().total // 1024**3  # GB
    }

if __name__ == "__main__":
    while True:
        stats = get_system_stats()
        print(json.dumps(stats, indent=2))
        time.sleep(5)
EOF
```

---

## Summary

This setup gives you:

1. **vLLM**: Ultra-high performance inference for production workloads
2. **Oobabooga**: Advanced features like file attachments, web search, multimodal support
3. **KoboldCpp**: Specialized creative writing and roleplay capabilities
4. **Unified API**: Single endpoint for your AI platform to route requests intelligently
5. **Full Integration**: Python SDK and environment configuration for your repository

The system is designed to complement your existing Ollama setup while providing significantly more power and flexibility for your AI platform development work.