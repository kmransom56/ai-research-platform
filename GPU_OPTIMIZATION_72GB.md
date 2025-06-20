# GPU Optimization Configuration for 72GB VRAM Systems
# AI Research Platform - High-Memory GPU Setup

## System Optimization

### Environment Variables (add to ~/.bashrc or config/.env)
```bash
# CUDA Configuration
export CUDA_VISIBLE_DEVICES=0
export CUDA_CACHE_PATH=/tmp/cuda_cache

# Memory Management
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,expandable_segments:True
export TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_GPU_MEMORY_FRACTION=0.9

# Performance Optimization
export OMP_NUM_THREADS=8
export CUDA_LAUNCH_BLOCKING=0
export PYTHONUNBUFFERED=1
```

## Recommended Model Configurations

### Large Language Models (Ollama)

With 72GB VRAM, you can run multiple large models simultaneously:

```bash
# Install multiple models
ollama pull llama2:70b          # ~40GB VRAM
ollama pull codellama:34b       # ~20GB VRAM
ollama pull mixtral:8x7b        # ~45GB VRAM
ollama pull deepseek-coder:33b  # ~20GB VRAM
ollama pull yi:34b              # ~20GB VRAM

# Efficient models for quick responses
ollama pull llama2:13b          # ~7GB VRAM
ollama pull codellama:13b       # ~7GB VRAM
ollama pull mistral:7b          # ~4GB VRAM
ollama pull phi:latest          # ~3GB VRAM
```

### Concurrent Model Serving

You can run multiple models simultaneously:

```bash
# Terminal 1: Large model for complex tasks
CUDA_VISIBLE_DEVICES=0 ollama run llama2:70b

# Terminal 2: Code model for programming
CUDA_VISIBLE_DEVICES=0 ollama run codellama:34b

# Terminal 3: Fast model for quick queries  
CUDA_VISIBLE_DEVICES=0 ollama run mistral:7b
```

## Memory Allocation Strategies

### Conservative (60GB usage, 12GB free)
```python
# For PyTorch applications
import torch
torch.cuda.set_per_process_memory_fraction(0.83)  # ~60GB of 72GB
```

### Aggressive (68GB usage, 4GB free)
```python
# Maximum utilization
import torch
torch.cuda.set_per_process_memory_fraction(0.95)  # ~68GB of 72GB
```

### Dynamic Allocation
```python
# Let PyTorch manage memory dynamically
import torch
torch.cuda.empty_cache()  # Clear cache
# PyTorch will allocate as needed
```

## AutoGen Studio Configuration

Create specific configurations for your GPU:

```python
# High-performance AutoGen config
config_list_72gb = [
    {
        "model": "gpt-4",
        "api_key": "your-openai-key",
        "api_type": "openai"
    },
    {
        "model": "llama2:70b",
        "api_base": "http://localhost:11434/v1",
        "api_key": "ollama",
        "api_type": "openai"
    },
    {
        "model": "codellama:34b", 
        "api_base": "http://localhost:11434/v1",
        "api_key": "ollama",
        "api_type": "openai"
    }
]
```

## Monitoring GPU Usage

### Real-time Monitoring
```bash
# Watch GPU memory usage
watch -n 1 'nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv'

# Detailed memory breakdown
nvidia-smi dmon -s mut -d 1

# Python GPU monitoring
python3 -c "
import torch
print(f'GPU: {torch.cuda.get_device_name()}')
print(f'Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
print(f'Available: {torch.cuda.memory_reserved(0) / 1024**3:.1f} GB')
print(f'Used: {torch.cuda.memory_allocated(0) / 1024**3:.1f} GB')
"
```

### Automated Alerts
```bash
# Create GPU monitoring script
cat > /home/$USER/chat-copilot/scripts/gpu-monitor.sh << 'EOF'
#!/bin/bash
while true; do
    USAGE=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
    if [ $USAGE -gt 65536 ]; then  # Alert if >64GB used
        echo "$(date): WARNING - GPU memory usage: ${USAGE}MB" >> /var/log/gpu-usage.log
    fi
    sleep 30
done
EOF
chmod +x /home/$USER/chat-copilot/scripts/gpu-monitor.sh
```

## Performance Benchmarks

Expected performance on 72GB system:

### Inference Speed (tokens/second)
- **LLaMA 2 70B**: 15-25 tokens/sec
- **Code Llama 34B**: 30-45 tokens/sec  
- **Mixtral 8x7B**: 25-35 tokens/sec
- **LLaMA 2 13B**: 60-100 tokens/sec

### Concurrent Models
- 2x Large models (70B + 34B): Possible with reduced batch sizes
- 1x Large + 2x Medium: Optimal for mixed workloads
- 4x Medium models: Maximum throughput setup

## Optimization Scripts

### GPU Memory Cleaner
```bash
# Create cleanup script
cat > /home/$USER/chat-copilot/scripts/gpu-cleanup.sh << 'EOF'
#!/bin/bash
echo "Cleaning GPU memory..."
python3 -c "
import torch
import gc
torch.cuda.empty_cache()
gc.collect()
print('GPU cache cleared')
"
# Restart Ollama if needed
sudo systemctl restart ollama
echo "GPU cleanup complete"
EOF
chmod +x /home/$USER/chat-copilot/scripts/gpu-cleanup.sh
```

### Model Preloader
```bash
# Create model preloader
cat > /home/$USER/chat-copilot/scripts/preload-models.sh << 'EOF'
#!/bin/bash
echo "Preloading optimized model set for 72GB GPU..."

# Load primary models
ollama run llama2:70b "Hello" > /dev/null 2>&1 &
sleep 10
ollama run codellama:34b "def hello():" > /dev/null 2>&1 &
sleep 10
ollama run mistral:7b "Hi" > /dev/null 2>&1 &

echo "Models preloaded and ready for inference"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
EOF
chmod +x /home/$USER/chat-copilot/scripts/preload-models.sh
```

## Docker GPU Configuration

For containerized deployments:

```yaml
# docker-compose.yml for GPU services
version: '3.8'
services:
  ollama-gpu:
    image: ollama/ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
      - OLLAMA_GPU_MEMORY=68GB
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

## Troubleshooting

### Common GPU Issues

1. **Out of Memory Errors**
   ```bash
   # Check current usage
   nvidia-smi
   
   # Clear PyTorch cache
   python3 -c "import torch; torch.cuda.empty_cache()"
   
   # Restart Ollama
   sudo systemctl restart ollama
   ```

2. **Slow Inference**
   ```bash
   # Check GPU utilization
   nvidia-smi dmon -s ut -d 1
   
   # Verify CUDA version
   nvcc --version
   nvidia-smi
   ```

3. **Multiple Model Conflicts**
   ```bash
   # Use different GPU memory fractions
   export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
   ```

## Power and Thermal Management

With 72GB VRAM, monitor power consumption:

```bash
# Power monitoring
nvidia-smi -q -d POWER | grep "Power Draw"

# Temperature monitoring  
nvidia-smi -q -d TEMPERATURE | grep "GPU Current Temp"

# Set power limit if needed (adjust based on your PSU)
sudo nvidia-smi -pl 400  # Set to 400W limit
```

This configuration will help you maximize the potential of your 72GB GPU system for AI research and development!
