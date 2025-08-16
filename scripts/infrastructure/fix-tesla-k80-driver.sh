#!/bin/bash
# Fix NVIDIA Tesla K80 Driver - Install Legacy 470.xx Driver
# Tesla K80 requires legacy drivers, not the newer 535+ series

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root or with sudo"
    exit 1
fi

log "🔧 Fixing NVIDIA Tesla K80 Driver Issue"
log "Tesla K80 requires legacy 470.xx driver, not 535.xx"

# Step 1: Remove current NVIDIA packages
log "Removing current NVIDIA driver packages..."
apt-get purge -y 'nvidia-*' || true
apt-get autoremove -y || true

# Step 2: Install legacy 470 driver
log "Installing NVIDIA Legacy 470 driver for Tesla K80..."
apt-get update
apt-get install -y nvidia-driver-470 nvidia-dkms-470 nvidia-utils-470

# Step 3: Blacklist nouveau driver (just in case)
log "Configuring driver blacklist..."
cat > /etc/modprobe.d/blacklist-nouveau.conf << 'EOF'
blacklist nouveau
options nouveau modeset=0
EOF

# Step 4: Update initramfs
log "Updating initramfs..."
update-initramfs -u

# Step 5: Install CUDA 11.8 (compatible with both Tesla K80 and 470 driver)
log "Installing CUDA 11.8 for Tesla K80..."
cd /tmp

# Remove any existing CUDA first
rm -rf /usr/local/cuda*

# Download CUDA 11.8
if [ ! -f "cuda_11.8.0_520.61.05_linux.run" ]; then
    log "Downloading CUDA 11.8..."
    wget -q https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
fi

# Install CUDA toolkit without driver (we have our own)
log "Installing CUDA 11.8 toolkit..."
chmod +x cuda_11.8.0_520.61.05_linux.run
./cuda_11.8.0_520.61.05_linux.run --silent --toolkit --no-opengl-libs --no-man-page

# Step 6: Set up environment
log "Setting up CUDA environment..."
cat > /etc/profile.d/cuda.sh << 'EOF'
export CUDA_HOME=/usr/local/cuda-11.8
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0,1,2,3
EOF

chmod +x /etc/profile.d/cuda.sh

# Create symlink
ln -sf /usr/local/cuda-11.8 /usr/local/cuda

# Step 7: Install Python CUDA libraries compatible with Tesla K80
log "Installing Python CUDA libraries..."
pip3 install --upgrade pip

# Install PyTorch with CUDA 11.8 support
pip3 install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# Install other CUDA libraries
pip3 install nvidia-ml-py3 cupy-cuda11x

# Install older TensorFlow version that supports Tesla K80
pip3 install tensorflow==2.12.0

# Step 8: Create Tesla K80 test script
cat > /usr/local/bin/test-tesla-k80 << 'EOF'
#!/usr/bin/env python3
import sys
import os

def test_driver():
    """Test NVIDIA driver"""
    try:
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0 and 'Tesla K80' in result.stdout:
            print("✅ NVIDIA Driver: Working with Tesla K80")
            return True
        else:
            print("❌ NVIDIA Driver: Not working properly")
            return False
    except Exception as e:
        print(f"❌ NVIDIA Driver: Error - {e}")
        return False

def test_cuda():
    """Test CUDA"""
    try:
        import subprocess
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0 and '11.8' in result.stdout:
            print("✅ CUDA: Version 11.8 installed")
            return True
        else:
            print("❌ CUDA: Not properly installed")
            return False
    except Exception as e:
        print(f"❌ CUDA: Error - {e}")
        return False

def test_pytorch():
    """Test PyTorch CUDA"""
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            print(f"✅ PyTorch CUDA: {device_count} devices available")
            
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                print(f"  GPU {i}: {props.name} (Compute {props.major}.{props.minor})")
            return True
        else:
            print("❌ PyTorch CUDA: Not available")
            return False
    except Exception as e:
        print(f"❌ PyTorch CUDA: Error - {e}")
        return False

def main():
    print("🧪 Tesla K80 CUDA Test Suite")
    print("=" * 40)
    
    tests = [
        ("NVIDIA Driver", test_driver),
        ("CUDA Toolkit", test_cuda), 
        ("PyTorch CUDA", test_pytorch)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Tesla K80 setup is working perfectly!")
        return 0
    else:
        print("⚠️  Some issues detected. May need system reboot.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x /usr/local/bin/test-tesla-k80

success "Tesla K80 driver fix completed!"
echo
warning "IMPORTANT: System reboot is required for the new driver to take effect"
echo "After reboot, run: test-tesla-k80"
echo
log "Reboot now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    log "Rebooting system..."
    reboot
else
    log "Remember to reboot manually before testing"
fi