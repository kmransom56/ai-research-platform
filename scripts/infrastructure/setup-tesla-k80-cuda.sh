#!/bin/bash
# NVIDIA Tesla K80 CUDA Setup Script for AI Research Platform
# Supports Ubuntu 24.04 with Tesla K80 GPUs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." &> /dev/null && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Check if running as root or with sudo
check_privileges() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Detect Tesla K80 GPUs
detect_tesla_k80() {
    log "Detecting NVIDIA Tesla K80 GPUs..."
    
    local gpu_count=$(lspci | grep -i "tesla k80" | wc -l)
    
    if [ "$gpu_count" -eq 0 ]; then
        error "No Tesla K80 GPUs detected"
        return 1
    fi
    
    success "Found $gpu_count Tesla K80 GPU(s)"
    lspci | grep -i "tesla k80"
    
    # Tesla K80 specifications
    log "Tesla K80 Specifications:"
    echo "  - Architecture: Kepler (GK210)"
    echo "  - CUDA Compute Capability: 3.7"
    echo "  - Memory: 2x 12GB GDDR5 (24GB total per card)"
    echo "  - CUDA Cores: 2x 2496 (4992 total per card)"
    echo "  - Memory Bandwidth: 2x 240 GB/s"
    echo "  - Total GPUs detected: $gpu_count"
    
    return 0
}

# Check current NVIDIA driver
check_nvidia_driver() {
    log "Checking NVIDIA driver status..."
    
    if nvidia-smi >/dev/null 2>&1; then
        success "NVIDIA driver is working"
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
        return 0
    else
        warning "NVIDIA driver not working properly"
        return 1
    fi
}

# Install/Update NVIDIA drivers
install_nvidia_driver() {
    log "Installing/updating NVIDIA drivers for Tesla K80..."
    
    # Add NVIDIA repository
    apt-get update
    apt-get install -y software-properties-common
    
    # Install recommended driver for Tesla K80 (535 series is good for K80)
    log "Installing NVIDIA driver 535..."
    apt-get install -y nvidia-driver-535 nvidia-dkms-535
    
    # Install additional NVIDIA utilities
    apt-get install -y nvidia-utils-535 nvidia-settings
    
    success "NVIDIA driver installation completed"
    warning "System reboot may be required for driver to take effect"
}

# Install CUDA Toolkit compatible with Tesla K80
install_cuda_toolkit() {
    log "Installing CUDA Toolkit for Tesla K80..."
    
    # Tesla K80 works best with CUDA 11.8 or earlier due to compute capability 3.7
    # CUDA 12+ dropped support for compute capability 3.x
    
    # Download and install CUDA 11.8
    cd /tmp
    
    log "Downloading CUDA 11.8 (compatible with Tesla K80 compute capability 3.7)..."
    wget -q https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
    
    if [ ! -f "cuda_11.8.0_520.61.05_linux.run" ]; then
        error "Failed to download CUDA installer"
        return 1
    fi
    
    log "Installing CUDA 11.8..."
    chmod +x cuda_11.8.0_520.61.05_linux.run
    
    # Install CUDA toolkit without driver (we already have the driver)
    ./cuda_11.8.0_520.61.05_linux.run --silent --toolkit --no-opengl-libs
    
    # Set up environment variables
    log "Configuring CUDA environment..."
    
    cat > /etc/profile.d/cuda.sh << 'EOF'
export CUDA_HOME=/usr/local/cuda-11.8
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0,1,2,3
EOF
    
    # Make it executable
    chmod +x /etc/profile.d/cuda.sh
    
    # Source it for current session
    source /etc/profile.d/cuda.sh
    
    # Create symlink for cuda
    ln -sf /usr/local/cuda-11.8 /usr/local/cuda
    
    success "CUDA 11.8 installation completed"
}

# Install cuDNN for deep learning
install_cudnn() {
    log "Installing cuDNN for deep learning frameworks..."
    
    # Install cuDNN 8.x for CUDA 11.8
    apt-get update
    apt-get install -y libcudnn8 libcudnn8-dev
    
    success "cuDNN installation completed"
}

# Install Python CUDA libraries
install_python_cuda_libs() {
    log "Installing Python CUDA libraries..."
    
    # Install basic CUDA Python packages
    pip3 install --upgrade pip
    
    # Install PyTorch with CUDA 11.8 support
    log "Installing PyTorch with CUDA 11.8 support..."
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    # Install other CUDA-enabled packages
    pip3 install nvidia-ml-py3 pycuda cupy-cuda11x
    
    # Install TensorFlow with CUDA support
    log "Installing TensorFlow with CUDA support..."
    pip3 install tensorflow[and-cuda]
    
    success "Python CUDA libraries installation completed"
}

# Configure Docker for GPU support
configure_docker_gpu() {
    log "Configuring Docker for GPU support..."
    
    # Install NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    apt-get update
    apt-get install -y nvidia-container-toolkit
    
    # Configure Docker daemon
    nvidia-ctk runtime configure --runtime=docker
    
    # Restart Docker
    systemctl restart docker
    
    success "Docker GPU support configured"
}

# Create Tesla K80 optimization script
create_k80_optimization() {
    log "Creating Tesla K80 optimization script..."
    
    cat > "${PROJECT_ROOT}/scripts/infrastructure/optimize-tesla-k80.sh" << 'EOF'
#!/bin/bash
# Tesla K80 GPU Optimization Script

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Set GPU performance mode
set_performance_mode() {
    log "Setting Tesla K80 performance mode..."
    
    # Set persistence mode (keeps driver loaded)
    nvidia-smi -pm 1
    
    # Set power limit to maximum (300W per GPU)
    for i in {0..3}; do
        nvidia-smi -i $i -pl 300 2>/dev/null || true
    done
    
    # Set memory and graphics clocks to maximum stable values for K80
    for i in {0..3}; do
        # Tesla K80 stable clocks
        nvidia-smi -i $i -ac 2505,875 2>/dev/null || true
    done
    
    log "Tesla K80 optimization completed"
}

# Monitor GPU status
monitor_gpus() {
    log "Tesla K80 GPU Status:"
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits
}

case "${1:-status}" in
    "optimize")
        set_performance_mode
        ;;
    "monitor"|"status")
        monitor_gpus
        ;;
    *)
        echo "Usage: $0 {optimize|monitor|status}"
        exit 1
        ;;
esac
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/infrastructure/optimize-tesla-k80.sh"
    success "Tesla K80 optimization script created"
}

# Create CUDA test script
create_cuda_test() {
    log "Creating CUDA functionality test script..."
    
    cat > "${PROJECT_ROOT}/scripts/infrastructure/test-cuda-k80.py" << 'EOF'
#!/usr/bin/env python3
"""
CUDA Functionality Test for Tesla K80 GPUs
Tests CUDA installation and Tesla K80 compatibility
"""

import sys
import subprocess
import json

def test_nvidia_smi():
    """Test nvidia-smi command"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,compute_cap,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, check=True)
        print("✅ nvidia-smi working")
        print("GPU Information:")
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")
        return True
    except Exception as e:
        print(f"❌ nvidia-smi failed: {e}")
        return False

def test_cuda_python():
    """Test CUDA Python libraries"""
    tests_passed = 0
    total_tests = 0
    
    # Test pynvml
    total_tests += 1
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        print(f"✅ NVIDIA-ML-Py3: {device_count} GPUs detected")
        tests_passed += 1
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            print(f"  GPU {i}: {name}, Memory: {memory_info.total // 1024**3} GB")
    except Exception as e:
        print(f"❌ NVIDIA-ML-Py3 failed: {e}")
    
    # Test PyTorch CUDA
    total_tests += 1
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count()
        print(f"✅ PyTorch CUDA: Available={cuda_available}, Devices={device_count}")
        
        if cuda_available:
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                print(f"  GPU {i}: {props.name}, Compute: {props.major}.{props.minor}, Memory: {props.total_memory // 1024**3} GB")
        tests_passed += 1
    except Exception as e:
        print(f"❌ PyTorch CUDA failed: {e}")
    
    # Test TensorFlow CUDA
    total_tests += 1
    try:
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        print(f"✅ TensorFlow CUDA: {len(gpus)} GPUs detected")
        for i, gpu in enumerate(gpus):
            print(f"  GPU {i}: {gpu.name}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ TensorFlow CUDA failed: {e}")
    
    return tests_passed, total_tests

def test_cuda_compute():
    """Test CUDA compute capability with Tesla K80"""
    try:
        import torch
        if not torch.cuda.is_available():
            print("❌ CUDA not available for compute test")
            return False
        
        device = torch.device('cuda:0')
        
        # Simple matrix multiplication test
        print("🧪 Testing CUDA compute with matrix multiplication...")
        a = torch.randn(1000, 1000, device=device)
        b = torch.randn(1000, 1000, device=device)
        
        import time
        start_time = time.time()
        c = torch.mm(a, b)
        torch.cuda.synchronize()  # Wait for GPU computation to complete
        end_time = time.time()
        
        print(f"✅ Matrix multiplication completed in {end_time - start_time:.4f} seconds")
        print(f"   Result shape: {c.shape}")
        return True
        
    except Exception as e:
        print(f"❌ CUDA compute test failed: {e}")
        return False

def main():
    print("🚀 Tesla K80 CUDA Test Suite")
    print("=" * 50)
    
    # Test 1: nvidia-smi
    print("\n1. Testing NVIDIA Driver...")
    smi_ok = test_nvidia_smi()
    
    # Test 2: Python CUDA libraries
    print("\n2. Testing Python CUDA Libraries...")
    python_passed, python_total = test_cuda_python()
    
    # Test 3: CUDA compute
    print("\n3. Testing CUDA Compute...")
    compute_ok = test_cuda_compute()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  NVIDIA Driver: {'✅' if smi_ok else '❌'}")
    print(f"  Python CUDA:   {python_passed}/{python_total} passed")
    print(f"  CUDA Compute:  {'✅' if compute_ok else '❌'}")
    
    if smi_ok and python_passed >= python_total * 0.5 and compute_ok:
        print("\n🎉 Tesla K80 CUDA setup is working!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF
    
    chmod +x "${PROJECT_ROOT}/scripts/infrastructure/test-cuda-k80.py"
    success "CUDA test script created"
}

# Update AI stack configuration for Tesla K80
update_ai_stack_config() {
    log "Updating AI stack configuration for Tesla K80..."
    
    # Create Tesla K80 specific configuration
    cat > "${PROJECT_ROOT}/python/ai-stack/tesla_k80_config.py" << 'EOF'
# Tesla K80 Configuration for AI Stack
# Optimized settings for NVIDIA Tesla K80 GPUs

TESLA_K80_CONFIG = {
    # GPU specifications
    "compute_capability": "3.7",
    "memory_per_gpu_gb": 12,  # Each Tesla K80 has 2x 12GB
    "cuda_cores_per_gpu": 4992,  # 2x 2496
    "memory_bandwidth_gb_s": 480,  # 2x 240 GB/s
    
    # Optimized settings for Tesla K80
    "recommended_batch_size": 32,  # Conservative for 12GB memory
    "max_sequence_length": 2048,   # Reasonable for available memory
    "fp16_enabled": True,          # Use half precision to save memory
    "gradient_checkpointing": True, # Save memory during training
    
    # vLLM settings optimized for Tesla K80
    "vllm_config": {
        "gpu_memory_utilization": 0.85,  # Leave some memory for system
        "max_model_len": 4096,           # Conservative for memory
        "tensor_parallel_size": 1,        # Single GPU per process
        "dtype": "float16",              # Use FP16
        "quantization": "awq",           # Use quantization to fit larger models
        "enforce_eager": True,           # Better compatibility with older GPUs
    },
    
    # Model recommendations for Tesla K80
    "recommended_models": {
        "small": [
            "microsoft/DialoGPT-small",
            "gpt2",
            "distilbert-base-uncased"
        ],
        "medium": [
            "microsoft/DialoGPT-medium", 
            "gpt2-medium",
            "bert-base-uncased"
        ],
        "large": [
            "EleutherAI/gpt-j-6b",  # With quantization
            "bigscience/bloom-3b",
            "facebook/opt-2.7b"
        ]
    },
    
    # Performance optimizations
    "torch_settings": {
        "torch.backends.cudnn.benchmark": True,
        "torch.backends.cudnn.deterministic": False,
        "torch.backends.cuda.matmul.allow_tf32": True,
        "torch.backends.cudnn.allow_tf32": True,
    }
}

def apply_tesla_k80_optimizations():
    """Apply Tesla K80 specific optimizations"""
    import torch
    import os
    
    # Set environment variables
    os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Async kernel launches
    os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'
    
    # Apply PyTorch optimizations
    if torch.cuda.is_available():
        for key, value in TESLA_K80_CONFIG["torch_settings"].items():
            exec(f"{key} = {value}")
        
        print("✅ Tesla K80 optimizations applied")
    else:
        print("⚠️  CUDA not available, skipping optimizations")

if __name__ == "__main__":
    apply_tesla_k80_optimizations()
EOF
    
    success "Tesla K80 AI stack configuration created"
}

# Main installation function
main() {
    log "Starting NVIDIA Tesla K80 CUDA setup..."
    
    check_privileges
    
    # Step 1: Detect Tesla K80 GPUs
    if ! detect_tesla_k80; then
        exit 1
    fi
    
    # Step 2: Check/install NVIDIA driver
    if ! check_nvidia_driver; then
        warning "NVIDIA driver issues detected, installing/updating..."
        install_nvidia_driver
    fi
    
    # Step 3: Install CUDA Toolkit (11.8 for Tesla K80 compatibility)
    if ! command -v nvcc &> /dev/null; then
        log "CUDA compiler not found, installing CUDA 11.8..."
        install_cuda_toolkit
    else
        success "CUDA compiler already installed"
        nvcc --version
    fi
    
    # Step 4: Install cuDNN
    install_cudnn
    
    # Step 5: Install Python CUDA libraries
    install_python_cuda_libs
    
    # Step 6: Configure Docker for GPU support
    configure_docker_gpu
    
    # Step 7: Create optimization and test scripts
    create_k80_optimization
    create_cuda_test
    update_ai_stack_config
    
    success "Tesla K80 CUDA setup completed!"
    
    echo
    log "Next steps:"
    echo "1. Reboot the system if prompted: sudo reboot"
    echo "2. Test the installation: python3 ${PROJECT_ROOT}/scripts/infrastructure/test-cuda-k80.py"
    echo "3. Optimize GPUs: ${PROJECT_ROOT}/scripts/infrastructure/optimize-tesla-k80.sh optimize"
    echo "4. Monitor GPUs: ${PROJECT_ROOT}/scripts/infrastructure/optimize-tesla-k80.sh monitor"
    echo
    warning "Note: Tesla K80 requires CUDA 11.8 or earlier due to compute capability 3.7"
    warning "Some newer models may not support Tesla K80. Use recommended models in tesla_k80_config.py"
}

# Run main function
main "$@"