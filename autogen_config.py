#!/usr/bin/env python3
"""
AutoGen Studio Configuration for Ollama Integration
AI Research Platform - Tailscale Network Integration
"""

import os
import sys

# AutoGen Studio Configuration for Ollama
AUTOGEN_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8081,
        "enable_cors": True
    },
    "models": {
        "ollama_base_url": "http://localhost:11434",
        "default_model": "llama3.2:3b",
        "available_models": [
            "llama3.2:3b",
            "mistral:latest",
            "deepseek-coder:6.7b",
            "codellama:7b",
            "qwen2.5-coder:1.5b-base"
        ]
    },
    "agents": {
        "assistant": {
            "name": "AI Assistant",
            "model": "llama3.2:3b",
            "system_message": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses."
        },
        "coder": {
            "name": "Code Assistant",
            "model": "deepseek-coder:6.7b",
            "system_message": "You are an expert programmer. Help with code analysis, debugging, and development."
        },
        "researcher": {
            "name": "Research Assistant",
            "model": "mistral:latest",
            "system_message": "You are a research assistant. Help analyze information and provide insights."
        }
    },
    "workflows": {
        "code_review": {
            "name": "Code Review Workflow",
            "agents": ["coder", "researcher"],
            "description": "Multi-agent code review and analysis"
        },
        "research_analysis": {
            "name": "Research Analysis",
            "agents": ["researcher", "assistant"],
            "description": "Collaborative research and analysis"
        }
    }
}

def create_ollama_config():
    """Create AutoGen Studio configuration for Ollama models"""
    
    config_template = """
{
  "models": [
    {
      "model": "llama3.2:3b",
      "base_url": "http://localhost:11434/v1",
      "api_type": "open_ai",
      "api_key": "ollama"
    },
    {
      "model": "mistral:latest", 
      "base_url": "http://localhost:11434/v1",
      "api_type": "open_ai",
      "api_key": "ollama"
    },
    {
      "model": "deepseek-coder:6.7b",
      "base_url": "http://localhost:11434/v1", 
      "api_type": "open_ai",
      "api_key": "ollama"
    }
  ],
  "agents": [
    {
      "name": "Assistant",
      "model": "llama3.2:3b",
      "system_message": "You are a helpful AI assistant.",
      "description": "General purpose AI assistant"
    },
    {
      "name": "Coder",
      "model": "deepseek-coder:6.7b", 
      "system_message": "You are an expert programmer and code analyst.",
      "description": "Specialized coding assistant"
    },
    {
      "name": "Researcher",
      "model": "mistral:latest",
      "system_message": "You are a research analyst who provides detailed insights.",
      "description": "Research and analysis specialist"
    }
  ],
  "skills": [],
  "workflows": [
    {
      "name": "Code Analysis",
      "description": "Multi-agent code review and analysis",
      "agents": ["Coder", "Assistant"],
      "type": "sequential"
    },
    {
      "name": "Research Project", 
      "description": "Collaborative research with multiple perspectives",
      "agents": ["Researcher", "Assistant"],
      "type": "group_chat"
    }
  ]
}
"""
    
    # Write config to AutoGen Studio directory
    autogen_dir = os.path.expanduser("~/.autogenstudio")
    os.makedirs(autogen_dir, exist_ok=True)
    
    config_file = os.path.join(autogen_dir, "ollama_config.json")
    with open(config_file, 'w') as f:
        f.write(config_template)
    
    print(f"✅ AutoGen Studio Ollama config created: {config_file}")
    return config_file

def start_autogen_studio():
    """Start AutoGen Studio with Ollama configuration"""
    import subprocess
    import time
    
    print("🚀 Starting AutoGen Studio with Ollama integration...")
    
    # Activate virtual environment and start server
    cmd = [
        "bash", "-c", 
        "source autogen-env/bin/activate && autogenstudio ui --port 8081 --host 0.0.0.0"
    ]
    
    try:
        process = subprocess.Popen(cmd, 
                                 cwd="/home/keith/chat-copilot",
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print(f"✅ AutoGen Studio started with PID: {process.pid}")
        print("🌐 Access at: http://100.123.10.72:8081")
        print("📊 Ollama models available: llama3.2:3b, mistral:latest, deepseek-coder:6.7b")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start AutoGen Studio: {e}")
        return None

if __name__ == "__main__":
    # Create configuration
    config_file = create_ollama_config()
    
    # Start AutoGen Studio
    process = start_autogen_studio()
    
    if process:
        print("\n🎉 AutoGen Studio is running!")
        print("📝 Configuration created for Ollama integration")
        print("🔗 Ready for multi-agent conversations")