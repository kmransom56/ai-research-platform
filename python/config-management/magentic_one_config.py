#!/usr/bin/env python3
"""
Magentic-One Multi-Agent System Configuration
AI Research Platform - Tailscale Network Integration
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import Magentic-One components
try:
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_ext.agents.magentic_one import (
        MagenticOneCoordinatorAgent,
        MagenticOneWebSurferAgent,
        MagenticOneFileSurferAgent,
        MagenticOneCoderAgent,
        MagenticOneComputerTerminalAgent
    )
    MAGENTIC_ONE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Magentic-One components not available: {e}")
    MAGENTIC_ONE_AVAILABLE = False

# Magentic-One Configuration
MAGENTIC_ONE_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8086,
        "cors_enabled": True
    },
    "models": {
        "coordinator_model": "llama3.2:3b",
        "web_surfer_model": "mistral:latest",
        "file_surfer_model": "deepseek-coder:6.7b",
        "coder_model": "deepseek-coder:6.7b", 
        "terminal_model": "llama3.2:3b",
        "ollama_base_url": "http://localhost:11434/v1",
        "api_key": "ollama"
    },
    "agents": {
        "coordinator": {
            "name": "Orchestrator",
            "description": "Leads task planning and delegation",
            "system_message": "You are the Orchestrator agent. Break down complex tasks, create plans, and coordinate other agents to achieve objectives efficiently."
        },
        "web_surfer": {
            "name": "WebSurfer", 
            "description": "Manages web browser interactions",
            "system_message": "You are the WebSurfer agent. Navigate websites, search for information, and interact with web interfaces to gather data."
        },
        "file_surfer": {
            "name": "FileSurfer",
            "description": "Navigates and reads local files",
            "system_message": "You are the FileSurfer agent. Navigate file systems, read documents, and extract information from local files."
        },
        "coder": {
            "name": "Coder",
            "description": "Writes and analyzes code",
            "system_message": "You are the Coder agent. Write, analyze, debug, and optimize code across multiple programming languages."
        },
        "terminal": {
            "name": "ComputerTerminal",
            "description": "Executes programs and installs libraries",
            "system_message": "You are the ComputerTerminal agent. Execute commands, install packages, and manage system operations safely."
        }
    },
    "workflows": {
        "web_research": {
            "name": "Web Research Project",
            "agents": ["coordinator", "web_surfer", "file_surfer"],
            "description": "Comprehensive web research with file documentation"
        },
        "code_development": {
            "name": "Code Development Team",
            "agents": ["coordinator", "coder", "terminal", "file_surfer"],
            "description": "Full-stack development with testing and deployment"
        },
        "data_analysis": {
            "name": "Data Analysis Pipeline",
            "agents": ["coordinator", "file_surfer", "coder", "terminal"],
            "description": "Data processing and analysis workflow"
        },
        "system_administration": {
            "name": "System Administration",
            "agents": ["coordinator", "terminal", "file_surfer", "coder"],
            "description": "System management and automation tasks"
        }
    },
    "safety": {
        "enable_human_approval": True,
        "restricted_commands": [
            "rm -rf", "sudo rm", "format", "delete", "DROP TABLE", 
            "shutdown", "reboot", "passwd", "adduser", "deluser"
        ],
        "allowed_domains": [
            "github.com", "stackoverflow.com", "python.org", "microsoft.com",
            "docs.python.org", "pypi.org", "wikipedia.org", "arxiv.org"
        ],
        "max_execution_time": 300,  # 5 minutes
        "max_file_size": "100MB"
    }
}

class MagenticOneOllamaClient:
    """Custom Ollama client for Magentic-One agents"""
    
    def __init__(self, model: str, base_url: str = "http://localhost:11434/v1"):
        self.model = model
        self.base_url = base_url
        self.api_key = "ollama"
    
    async def create_chat_completion(self, messages, **kwargs):
        """Create chat completion using Ollama API"""
        import aiohttp
        
        # Convert to Ollama format
        ollama_messages = []
        for msg in messages:
            if hasattr(msg, 'content') and hasattr(msg, 'role'):
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                ollama_messages.append(msg)
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                result = await response.json()
                return result

def create_magentic_one_team_config():
    """Create Magentic-One team configuration"""
    
    if not MAGENTIC_ONE_AVAILABLE:
        print("❌ Magentic-One not available - skipping configuration")
        return None
    
    config = {
        "team_name": "Magentic-One AI Research Team",
        "description": "Multi-agent system for complex task solving",
        "created_at": datetime.now().isoformat(),
        "models": MAGENTIC_ONE_CONFIG["models"],
        "agents": [],
        "safety": MAGENTIC_ONE_CONFIG["safety"]
    }
    
    # Add agent configurations
    for agent_id, agent_config in MAGENTIC_ONE_CONFIG["agents"].items():
        model_key = f"{agent_id}_model"
        model = MAGENTIC_ONE_CONFIG["models"].get(model_key, "llama3.2:3b")
        
        agent_data = {
            "id": agent_id,
            "name": agent_config["name"],
            "description": agent_config["description"],
            "system_message": agent_config["system_message"],
            "model": model,
            "config": {
                "llm_config": {
                    "model": model,
                    "base_url": MAGENTIC_ONE_CONFIG["models"]["ollama_base_url"],
                    "api_key": MAGENTIC_ONE_CONFIG["models"]["api_key"],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }
        }
        config["agents"].append(agent_data)
    
    return config

def create_magentic_one_examples():
    """Create example Magentic-One workflows"""
    
    examples = {
        "web_research_example": {
            "name": "Research Latest AI Developments",
            "description": "Use WebSurfer to research recent AI papers and developments",
            "task": "Research the latest developments in multi-agent AI systems. Search for recent papers, summarize key findings, and create a comprehensive report.",
            "agents_involved": ["Orchestrator", "WebSurfer", "FileSurfer"],
            "expected_workflow": [
                "Orchestrator creates research plan",
                "WebSurfer searches academic databases",
                "WebSurfer visits relevant websites",
                "FileSurfer organizes downloaded papers",
                "Orchestrator compiles final report"
            ]
        },
        
        "code_development_example": {
            "name": "Build Python Web Scraper",
            "description": "Develop and test a web scraping application",
            "task": "Create a Python web scraper that can extract product information from e-commerce websites. Include error handling, rate limiting, and data export features.",
            "agents_involved": ["Orchestrator", "Coder", "ComputerTerminal", "FileSurfer"],
            "expected_workflow": [
                "Orchestrator plans development approach",
                "Coder writes initial scraper code",
                "ComputerTerminal installs required packages",
                "Coder implements error handling and features",
                "ComputerTerminal runs tests",
                "FileSurfer verifies output files"
            ]
        },
        
        "data_analysis_example": {
            "name": "Analyze System Performance Data",
            "description": "Process and analyze system performance logs",
            "task": "Analyze system performance logs to identify bottlenecks and optimization opportunities. Create visualizations and recommendations.",
            "agents_involved": ["Orchestrator", "FileSurfer", "Coder", "ComputerTerminal"],
            "expected_workflow": [
                "Orchestrator defines analysis objectives",
                "FileSurfer loads and examines log files",
                "Coder writes data processing scripts",
                "ComputerTerminal executes analysis",
                "Coder creates visualizations",
                "Orchestrator summarizes findings"
            ]
        },
        
        "system_admin_example": {
            "name": "Setup Development Environment",
            "description": "Automate development environment setup",
            "task": "Set up a complete development environment with specific tools, configurations, and project structure for a new team member.",
            "agents_involved": ["Orchestrator", "ComputerTerminal", "FileSurfer", "Coder"],
            "expected_workflow": [
                "Orchestrator creates setup plan",
                "ComputerTerminal installs required software",
                "FileSurfer creates directory structure",
                "Coder writes configuration files",
                "ComputerTerminal applies configurations",
                "Orchestrator verifies setup completion"
            ]
        }
    }
    
    return examples

def test_ollama_models():
    """Test Ollama models for Magentic-One compatibility"""
    import requests
    
    print("🦙 Testing Ollama Models for Magentic-One...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            available_models = [model['name'] for model in models.get('models', [])]
            
            required_models = [
                MAGENTIC_ONE_CONFIG["models"]["coordinator_model"],
                MAGENTIC_ONE_CONFIG["models"]["web_surfer_model"],
                MAGENTIC_ONE_CONFIG["models"]["file_surfer_model"],
                MAGENTIC_ONE_CONFIG["models"]["coder_model"],
                MAGENTIC_ONE_CONFIG["models"]["terminal_model"]
            ]
            
            print(f"📊 Available Models: {len(available_models)}")
            for model in available_models:
                print(f"   • {model}")
            
            print(f"\n🎯 Required Models for Magentic-One:")
            all_available = True
            for model in set(required_models):  # Remove duplicates
                status = "✅" if model in available_models else "❌"
                print(f"   {status} {model}")
                if model not in available_models:
                    all_available = False
            
            if all_available:
                print("\n🎉 All required models are available!")
                return True
            else:
                print("\n⚠️ Some models are missing. Install with:")
                for model in set(required_models):
                    if model not in available_models:
                        print(f"   ollama pull {model}")
                return False
                
        else:
            print("❌ Cannot connect to Ollama API")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def create_magentic_one_server():
    """Create Magentic-One server configuration"""
    
    server_config = {
        "name": "Magentic-One Multi-Agent Server",
        "description": "Advanced multi-agent system with web, file, and code capabilities",
        "host": MAGENTIC_ONE_CONFIG["server"]["host"],
        "port": MAGENTIC_ONE_CONFIG["server"]["port"],
        "endpoints": {
            "health": f"http://100.123.10.72:{MAGENTIC_ONE_CONFIG['server']['port']}/health",
            "teams": f"http://100.123.10.72:{MAGENTIC_ONE_CONFIG['server']['port']}/teams",
            "workflows": f"http://100.123.10.72:{MAGENTIC_ONE_CONFIG['server']['port']}/workflows",
            "agents": f"http://100.123.10.72:{MAGENTIC_ONE_CONFIG['server']['port']}/agents"
        },
        "capabilities": [
            "Web browsing and interaction",
            "File system navigation and analysis", 
            "Code development and execution",
            "Terminal command execution",
            "Task coordination and planning",
            "Multi-agent collaboration"
        ],
        "safety_features": [
            "Human approval for critical actions",
            "Command restriction and filtering",
            "Domain-based web access control",
            "Execution time limits",
            "File size restrictions"
        ]
    }
    
    return server_config

def main():
    """Main setup and configuration function"""
    
    print("🤖 Magentic-One Multi-Agent System Setup")
    print("=" * 50)
    
    # Test Ollama compatibility
    ollama_ok = test_ollama_models()
    print()
    
    if not ollama_ok:
        print("⚠️ Please install missing Ollama models before proceeding")
        return
    
    if not MAGENTIC_ONE_AVAILABLE:
        print("❌ Magentic-One components not available")
        print("💡 Try: pip install 'autogen-ext[magentic-one,openai]'")
        return
    
    # Create configurations
    print("📝 Creating Magentic-One configurations...")
    
    # Team configuration
    team_config = create_magentic_one_team_config()
    if team_config:
        config_dir = os.path.expanduser("~/.autogenstudio/magentic-one")
        os.makedirs(config_dir, exist_ok=True)
        
        with open(os.path.join(config_dir, "team_config.json"), 'w') as f:
            json.dump(team_config, f, indent=2)
        print("✅ Team configuration created")
    
    # Example workflows
    examples = create_magentic_one_examples()
    with open(os.path.join(config_dir, "workflow_examples.json"), 'w') as f:
        json.dump(examples, f, indent=2)
    print("✅ Workflow examples created")
    
    # Server configuration
    server_config = create_magentic_one_server()
    with open(os.path.join(config_dir, "server_config.json"), 'w') as f:
        json.dump(server_config, f, indent=2)
    print("✅ Server configuration created")
    
    print(f"\n🌐 Magentic-One Configuration Complete!")
    print(f"📁 Config Directory: {config_dir}")
    print(f"🚀 Ready for Multi-Agent Task Solving!")
    
    print(f"\n🎯 Available Workflows:")
    for workflow_id, workflow in MAGENTIC_ONE_CONFIG["workflows"].items():
        print(f"   • {workflow['name']}: {workflow['description']}")
    
    print(f"\n🤖 Agent Capabilities:")
    for agent_id, agent in MAGENTIC_ONE_CONFIG["agents"].items():
        print(f"   • {agent['name']}: {agent['description']}")
    
    print(f"\n🔧 Next Steps:")
    print(f"1. Access platform: http://100.123.10.72:8086 (when server runs)")
    print(f"2. Review workflow examples in config directory")
    print(f"3. Test web browsing and file operations")
    print(f"4. Create custom multi-agent workflows")
    print(f"5. Integrate with existing AI Research Platform")

if __name__ == "__main__":
    main()