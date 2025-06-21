# AI Research Platform - Installation Guide

## Quick Installation

For a fresh Ubuntu/Debian system, run:

```bash
wget https://raw.githubusercontent.com/your-repo/ai-platform/main/scripts/platform-management/install-ai-platform.sh
chmod +x install-ai-platform.sh
./install-ai-platform.sh
```

Or copy the installer from an existing installation:

```bash
scp your-user@source-server:/home/user/chat-copilot/scripts/platform-management/install-ai-platform.sh ./
./install-ai-platform.sh
```

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ or Debian-based Linux
- **RAM**: 16GB (32GB+ recommended)
- **Storage**: 100GB free space
- **CPU**: 4+ cores
- **Network**: Internet connection for downloads

### Recommended for AI Workloads
- **RAM**: 64GB+ (especially for large language models)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (your 72GB system is excellent!)
- **Storage**: SSD with 500GB+ free space
- **CPU**: 8+ cores (AMD Ryzen or Intel Core i7/i9)

## GPU Optimization

Your system with 72GB GPU RAM is perfect for:

### Large Language Models
- **LLaMA 2 70B**: Requires ~40GB VRAM
- **Code Llama 34B**: Requires ~20GB VRAM  
- **Mixtral 8x7B**: Requires ~45GB VRAM
- **GPT-J 6B**: Requires ~12GB VRAM

### Recommended Ollama Models for 72GB GPU
```bash
# After installation, run these:
ollama pull llama2:70b          # 70B parameter model
ollama pull codellama:34b       # Code generation
ollama pull mixtral:8x7b        # Mixture of experts
ollama pull llama2:13b          # Faster inference
ollama pull phi:latest          # Microsoft's efficient model
```

## Installation Process

The installer will:

1. **System Check**: Verify requirements and detect GPU
2. **Dependencies**: Install Docker, .NET, Node.js, Python
3. **GPU Support**: Install NVIDIA Container Toolkit if GPU detected
4. **Web Server**: Install and configure Caddy with SSL
5. **Networking**: Install Tailscale for secure remote access
6. **AI Tools**: Install Ollama, AutoGen Studio, Python packages
7. **Platform**: Set up the AI research platform structure
8. **Security**: Configure firewall rules

## Post-Installation Configuration

### 1. API Keys Configuration
Edit `/home/user/chat-copilot/config/.env`:

```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here

# Optional but recommended
HUGGINGFACE_TOKEN=hf_your-huggingface-token
GOOGLE_API_KEY=your-google-api-key
```

### 2. Tailscale Setup
```bash
# Connect to your Tailscale network
sudo tailscale up

# Get your Tailscale domain
tailscale status
# Note the domain (e.g., machine-name.tail12345.ts.net)
```

### 3. Domain Configuration
Update your domain in:
- `/home/user/chat-copilot/config/Caddyfile`
- `/home/user/chat-copilot/scripts/platform-management/startup-platform-clean.sh`

Replace `your_tailscale_domain_here` with your actual Tailscale domain.

### 4. SSL Certificate Setup
Caddy automatically handles Let's Encrypt certificates for Tailscale domains.

## Starting the Platform

```bash
cd /home/user/chat-copilot
./scripts/platform-management/startup-platform-clean.sh
```

## Service URLs (after configuration)

### Core AI Services
- **Chat Copilot**: `https://copilot.your-domain.ts.net`
- **AutoGen Studio**: `https://autogen.your-domain.ts.net`
- **Magentic-One**: `https://magentic.your-domain.ts.net`

### AI Tools & Models
- **Ollama API**: `https://ollama.your-domain.ts.net`
- **OpenWebUI**: `https://openwebui.your-domain.ts.net`
- **Perplexica**: `https://perplexica.your-domain.ts.net`

### Development Tools
- **VS Code Web**: `https://vscode.your-domain.ts.net`
- **Port Scanner**: `https://portscanner.your-domain.ts.net`

## GPU Memory Optimization

For your 72GB system, consider these memory allocation strategies:

### Conservative (Leave 8GB free)
```bash
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
```

### Aggressive (Use most available memory)
```bash
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## Monitoring & Management

### Check System Status
```bash
./check-installation.sh
```

### View Logs
```bash
# Platform logs
tail -f logs/platform.log

# Service-specific logs
tail -f logs/autogen-studio.log
tail -f logs/chat-copilot.log

# System logs
sudo journalctl -u caddy -f
sudo journalctl -u ollama -f
```

### GPU Monitoring
```bash
# Real-time GPU usage
watch -n 1 nvidia-smi

# GPU memory usage
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

## Backup & Restore

### Create Backup
```bash
cd /home/user/chat-copilot
./scripts/backup-recovery/backup-configs.sh
```

### Restore Configuration
```bash
# Copy backup to new system
scp -r backups/ user@new-server:/home/user/chat-copilot/

# Restore
./scripts/backup-recovery/restore-config.sh backup-date
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Check with `sudo netstat -tulpn | grep :PORT`
2. **Permission Issues**: Ensure user is in docker group: `sudo usermod -aG docker $USER`
3. **GPU Not Detected**: Verify NVIDIA drivers: `nvidia-smi`
4. **Tailscale Connection**: Check with `tailscale status`
5. **SSL Errors**: Verify Caddy is running: `sudo systemctl status caddy`

### Performance Optimization

For 72GB GPU systems:

```bash
# Optimize Python for GPU
export PYTHONPATH="/usr/local/cuda/lib64:$PYTHONPATH"
export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"

# Enable GPU memory growth for TensorFlow
export TF_FORCE_GPU_ALLOW_GROWTH=true

# PyTorch optimizations
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## Multi-System Deployment

### Master-Worker Setup

1. **Master Node**: Full installation with web interface
2. **Worker Nodes**: Compute-only nodes for model inference

### Distributed AI Workloads

Your 72GB system could serve as:
- **Model Server**: Host large models via Ollama
- **Training Node**: Fine-tune models with your data
- **Inference Engine**: Serve multiple smaller models simultaneously

## Security Considerations

- All services run behind Caddy with SSL
- Tailscale provides secure networking
- Firewall configured with minimal open ports
- API keys stored in environment files (not in code)
- Regular backups include configuration only (not secrets)

## Support & Updates

Check for updates:
```bash
git pull origin main  # If using git
./scripts/platform-management/install-ai-platform.sh --update  # Will be implemented
```

For issues:
1. Check logs in `/home/user/chat-copilot/logs/`
2. Verify system requirements
3. Review firewall and network settings
4. Check GPU drivers and CUDA installation
