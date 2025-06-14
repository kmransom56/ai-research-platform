#!/usr/bin/env python3
"""
AutoGen Studio Multi-Agent Examples
AI Research Platform - Tailscale Network
"""

import os
import json
from datetime import datetime

# Example workflows for AutoGen Studio
WORKFLOW_EXAMPLES = {
    "code_review": {
        "name": "Code Review Workflow",
        "description": "Multi-agent code review with Ollama models",
        "agents": [
            {
                "name": "Senior Developer",
                "model": "deepseek-coder:6.7b",
                "system_message": "You are a senior software developer. Review code for best practices, security, and performance.",
                "role": "reviewer"
            },
            {
                "name": "Architecture Reviewer", 
                "model": "mistral:latest",
                "system_message": "You are a software architect. Focus on design patterns, scalability, and maintainability.",
                "role": "architect"
            },
            {
                "name": "Code Assistant",
                "model": "llama3.2:3b",
                "system_message": "You are a helpful code assistant. Summarize reviews and suggest improvements.",
                "role": "assistant"
            }
        ],
        "workflow_type": "sequential",
        "example_task": "Review this Python function for best practices and suggest improvements"
    },
    
    "research_analysis": {
        "name": "Research Analysis Team",
        "description": "Collaborative research with multiple AI perspectives",
        "agents": [
            {
                "name": "Research Analyst",
                "model": "mistral:latest", 
                "system_message": "You are a research analyst. Gather and analyze information thoroughly.",
                "role": "researcher"
            },
            {
                "name": "Technical Writer",
                "model": "llama3.2:3b",
                "system_message": "You are a technical writer. Create clear, structured documentation.",
                "role": "writer"
            },
            {
                "name": "Fact Checker",
                "model": "deepseek-coder:6.7b",
                "system_message": "You are a fact checker. Verify claims and ensure accuracy.",
                "role": "validator"
            }
        ],
        "workflow_type": "group_chat",
        "example_task": "Research the latest developments in AI agent frameworks"
    },
    
    "problem_solving": {
        "name": "Problem Solving Team",
        "description": "Multi-agent problem decomposition and solution",
        "agents": [
            {
                "name": "Problem Analyzer",
                "model": "mistral:latest",
                "system_message": "You break down complex problems into smaller, manageable parts.",
                "role": "analyzer"
            },
            {
                "name": "Solution Designer",
                "model": "deepseek-coder:6.7b", 
                "system_message": "You design practical solutions and implementation strategies.",
                "role": "designer"
            },
            {
                "name": "Implementation Guide",
                "model": "llama3.2:3b",
                "system_message": "You provide step-by-step implementation guidance.",
                "role": "guide"
            }
        ],
        "workflow_type": "sequential",
        "example_task": "How to integrate multiple AI services in a distributed system"
    }
}

def create_autogen_workflows():
    """Create AutoGen Studio workflow configuration files"""
    
    workflows_dir = os.path.expanduser("~/.autogenstudio/workflows")
    os.makedirs(workflows_dir, exist_ok=True)
    
    print("🤖 Creating AutoGen Studio workflow examples...")
    
    for workflow_id, workflow in WORKFLOW_EXAMPLES.items():
        workflow_file = os.path.join(workflows_dir, f"{workflow_id}.json")
        
        # AutoGen Studio workflow format
        autogen_workflow = {
            "name": workflow["name"],
            "description": workflow["description"],
            "summary_method": "last_msg",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "agents": [],
            "type": workflow["workflow_type"]
        }
        
        # Convert agents to AutoGen Studio format
        for agent in workflow["agents"]:
            autogen_agent = {
                "name": agent["name"],
                "model": agent["model"],
                "system_message": agent["system_message"],
                "description": f"{agent['role'].title()} agent using {agent['model']}",
                "created_at": datetime.now().isoformat(),
                "config": {
                    "llm_config": {
                        "model": agent["model"],
                        "api_type": "open_ai",
                        "base_url": "http://localhost:11434/v1",
                        "api_key": "ollama",
                        "temperature": 0.7
                    }
                }
            }
            autogen_workflow["agents"].append(autogen_agent)
        
        # Save workflow
        with open(workflow_file, 'w') as f:
            json.dump(autogen_workflow, f, indent=2)
        
        print(f"✅ Created workflow: {workflow['name']}")
        print(f"   📁 File: {workflow_file}")
        print(f"   🤝 Agents: {len(workflow['agents'])}")
        print(f"   📋 Type: {workflow['workflow_type']}")
        print()

def test_ollama_connection():
    """Test connection to Ollama API"""
    import requests
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("🦙 Ollama Connection: ✅ Active")
            print(f"📊 Available Models: {len(models.get('models', []))}")
            for model in models.get('models', []):
                print(f"   • {model['name']} ({model['size'] // (1024**3)} GB)")
            return True
        else:
            print("❌ Ollama API error:", response.status_code)
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_autogen_studio():
    """Test AutoGen Studio server"""
    import requests
    
    try:
        response = requests.get("http://100.123.10.72:8085", timeout=5)
        if response.status_code == 200:
            print("🤖 AutoGen Studio: ✅ Running")
            print("🌐 URL: http://100.123.10.72:8085")
            return True
        else:
            print(f"❌ AutoGen Studio error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to AutoGen Studio: {e}")
        return False

def main():
    """Main setup and test function"""
    
    print("🚀 AutoGen Studio Multi-Agent Setup")
    print("=" * 50)
    
    # Test connections
    ollama_ok = test_ollama_connection()
    print()
    autogen_ok = test_autogen_studio()
    print()
    
    if ollama_ok and autogen_ok:
        print("🎉 All systems operational!")
        print()
        
        # Create workflow examples
        create_autogen_workflows()
        
        print("📋 Next Steps:")
        print("1. Open AutoGen Studio: http://100.123.10.72:8085")
        print("2. Create a new team in Team Builder")
        print("3. Add agents with Ollama models:")
        print("   • llama3.2:3b (General assistant)")
        print("   • mistral:latest (Research & analysis)")
        print("   • deepseek-coder:6.7b (Code & technical)")
        print("4. Configure model settings:")
        print("   • Base URL: http://localhost:11434/v1")
        print("   • API Key: ollama")
        print("   • API Type: OpenAI Compatible")
        print("5. Start multi-agent conversations!")
        print()
        print("🤖 Example workflows created in ~/.autogenstudio/workflows/")
        
    else:
        print("⚠️ Setup incomplete - check service status")

if __name__ == "__main__":
    main()