#!/usr/bin/env python3
"""
vLLM Configuration and Launcher for Tesla K80 GPUs
Optimized settings for NVIDIA Tesla K80 (Compute Capability 3.7)
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Tesla K80 specific configuration
TESLA_K80_CONFIG = {
    "compute_capability": "3.7",
    "memory_per_gpu_gb": 12,
    "recommended_models": {
        # Small models that work well on Tesla K80
        "small": [
            "microsoft/DialoGPT-small",
            "gpt2",
            "facebook/opt-125m",
            "EleutherAI/pythia-160m"
        ],
        # Medium models (with quantization)
        "medium": [
            "microsoft/DialoGPT-medium",
            "gpt2-medium", 
            "facebook/opt-1.3b",
            "EleutherAI/pythia-1.4b"
        ],
        # Large models (heavily quantized)
        "large": [
            "facebook/opt-2.7b",  # With AWQ quantization
            "EleutherAI/pythia-2.8b",
            "bigscience/bloom-1b7"
        ]
    }
}

def get_vllm_args_for_tesla_k80(model_name: str, port: int = 8000, 
                               max_model_len: int = 2048, 
                               gpu_memory_utilization: float = 0.85):
    """
    Generate optimized vLLM arguments for Tesla K80
    
    Args:
        model_name: HuggingFace model name
        port: Port to serve on
        max_model_len: Maximum sequence length
        gpu_memory_utilization: GPU memory utilization ratio
    
    Returns:
        List of vLLM command arguments
    """
    
    args = [
        "vllm", "serve", model_name,
        "--host", "0.0.0.0",
        "--port", str(port),
        "--max-model-len", str(max_model_len),
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--dtype", "float16",  # Use FP16 for memory savings
        "--enforce-eager",     # Better compatibility with older GPUs
        "--disable-log-requests",
        "--tensor-parallel-size", "1",  # Single GPU
        "--disable-custom-all-reduce",  # Better stability on older hardware
    ]
    
    # Add quantization for larger models
    model_size = estimate_model_size(model_name)
    if model_size > 2:  # Models larger than 2B parameters
        args.extend([
            "--quantization", "awq",  # Use AWQ quantization
        ])
    
    # Tesla K80 specific optimizations
    args.extend([
        "--max-num-batched-tokens", str(min(8192, max_model_len * 4)),
        "--max-num-seqs", "32",  # Conservative batch size
        "--trust-remote-code",
    ])
    
    return args

def estimate_model_size(model_name: str) -> float:
    """
    Estimate model size in billions of parameters based on name
    """
    name_lower = model_name.lower()
    
    # Common model size indicators
    size_indicators = {
        "125m": 0.125, "160m": 0.16, "350m": 0.35, "760m": 0.76,
        "1.3b": 1.3, "1.4b": 1.4, "1b7": 1.7, "2.7b": 2.7, "2.8b": 2.8,
        "6b": 6, "7b": 7, "13b": 13, "30b": 30, "65b": 65,
        "small": 0.3, "medium": 1.0, "large": 3.0, "xl": 6.0
    }
    
    for indicator, size in size_indicators.items():
        if indicator in name_lower:
            return size
    
    # Default estimate
    return 1.0

def check_tesla_k80_compatibility():
    """Check if system has Tesla K80 GPUs and proper CUDA setup"""
    try:
        # Check for Tesla K80 GPUs
        import pynvml
        pynvml.nvmlInit()
        
        tesla_k80_count = 0
        total_memory_gb = 0
        
        for i in range(pynvml.nvmlDeviceGetCount()):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            
            if "Tesla K80" in name:
                tesla_k80_count += 1
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                total_memory_gb += memory_info.total // 1024**3
        
        if tesla_k80_count == 0:
            print("⚠️  No Tesla K80 GPUs detected")
            return False
        
        print(f"✅ Found {tesla_k80_count} Tesla K80 GPU(s)")
        print(f"📊 Total GPU memory: {total_memory_gb} GB")
        
        # Check CUDA version compatibility
        try:
            result = subprocess.run(['nvcc', '--version'], 
                                  capture_output=True, text=True)
            if 'V11.' in result.stdout:
                print("✅ CUDA 11.x detected (compatible with Tesla K80)")
                return True
            elif 'V12.' in result.stdout:
                print("⚠️  CUDA 12.x detected - Tesla K80 needs CUDA 11.x")
                return False
            else:
                print("⚠️  Could not determine CUDA version")
                return False
                
        except FileNotFoundError:
            print("❌ NVCC not found - CUDA toolkit not installed")
            return False
            
    except ImportError:
        print("❌ pynvml not available - install with: pip install nvidia-ml-py3")
        return False
    except Exception as e:
        print(f"❌ Error checking Tesla K80 compatibility: {e}")
        return False

def recommend_model_for_tesla_k80(task_type: str = "general") -> str:
    """
    Recommend appropriate model for Tesla K80 based on task type
    
    Args:
        task_type: Type of task (general, coding, creative)
        
    Returns:
        Recommended model name
    """
    
    recommendations = {
        "general": "microsoft/DialoGPT-medium",
        "coding": "EleutherAI/pythia-1.4b", 
        "creative": "gpt2-medium",
        "reasoning": "facebook/opt-1.3b"
    }
    
    return recommendations.get(task_type, "microsoft/DialoGPT-medium")

def launch_vllm_tesla_k80(model_name: str, port: int = 8000, 
                         task_type: str = "general"):
    """
    Launch vLLM optimized for Tesla K80
    
    Args:
        model_name: Model to serve
        port: Port to serve on
        task_type: Task type for optimization
    """
    
    print(f"🚀 Launching vLLM for Tesla K80")
    print(f"   Model: {model_name}")
    print(f"   Port: {port}")
    print(f"   Task Type: {task_type}")
    
    # Check compatibility
    if not check_tesla_k80_compatibility():
        print("❌ Tesla K80 compatibility check failed")
        sys.exit(1)
    
    # Get optimized arguments
    estimated_size = estimate_model_size(model_name)
    
    # Adjust settings based on model size
    if estimated_size <= 0.5:  # Very small models
        max_len = 4096
        gpu_util = 0.9
    elif estimated_size <= 1.5:  # Small-medium models
        max_len = 2048
        gpu_util = 0.85
    else:  # Larger models
        max_len = 1024
        gpu_util = 0.8
        print(f"⚠️  Large model ({estimated_size}B params) - using conservative settings")
    
    args = get_vllm_args_for_tesla_k80(
        model_name=model_name,
        port=port,
        max_model_len=max_len,
        gpu_memory_utilization=gpu_util
    )
    
    print(f"📝 vLLM command: {' '.join(args)}")
    
    try:
        # Launch vLLM
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ vLLM launch failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 vLLM stopped by user")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="vLLM Tesla K80 Launcher")
    parser.add_argument("--model", type=str, help="Model name to serve")
    parser.add_argument("--port", type=int, default=8000, help="Port to serve on")
    parser.add_argument("--task-type", type=str, default="general",
                       choices=["general", "coding", "creative", "reasoning"],
                       help="Task type for optimization")
    parser.add_argument("--recommend", action="store_true", 
                       help="Show recommended models for Tesla K80")
    parser.add_argument("--check", action="store_true",
                       help="Check Tesla K80 compatibility")
    
    args = parser.parse_args()
    
    if args.check:
        check_tesla_k80_compatibility()
        return
    
    if args.recommend:
        print("🎯 Recommended Models for Tesla K80:")
        print("=" * 40)
        for category, models in TESLA_K80_CONFIG["recommended_models"].items():
            print(f"\n{category.upper()}:")
            for model in models:
                size = estimate_model_size(model)
                print(f"  • {model} (~{size}B params)")
        return
    
    # Use provided model or recommend one
    model_name = args.model
    if not model_name:
        model_name = recommend_model_for_tesla_k80(args.task_type)
        print(f"🎯 Using recommended model for {args.task_type}: {model_name}")
    
    # Launch vLLM
    launch_vllm_tesla_k80(model_name, args.port, args.task_type)

if __name__ == "__main__":
    main()