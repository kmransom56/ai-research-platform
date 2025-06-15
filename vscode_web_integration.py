#!/usr/bin/env python3
"""
VS Code Web Integration for AI Research Platform
Enhanced web-based development environment configuration
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

class VSCodeWebIntegration:
    """VS Code Web integration and configuration manager"""
    
    def __init__(self):
        self.vscode_url = "http://100.123.10.72:57081"
        self.config_dir = os.path.expanduser("~/.vscode-server")
        self.platform_config = self._load_platform_config()
    
    def _load_platform_config(self):
        """Load VS Code web platform configuration"""
        return {
            "server": {
                "url": self.vscode_url,
                "host": "100.123.10.72",
                "port": 57081,
                "protocol": "http"
            },
            "features": [
                "Full VS Code editing experience",
                "Extension marketplace access",
                "Integrated terminal",
                "Git integration",
                "IntelliSense and debugging",
                "Multi-language support",
                "Tailscale network access"
            ],
            "recommended_extensions": [
                "ms-python.python",
                "ms-vscode.vscode-typescript-next", 
                "ms-vscode.vscode-json",
                "redhat.vscode-yaml",
                "ms-vscode.hexeditor",
                "ms-vscode.vscode-github-issue-prs",
                "github.copilot",
                "ms-vscode-remote.remote-containers",
                "ms-toolsai.jupyter",
                "bradlc.vscode-tailwindcss"
            ],
            "ai_development_setup": {
                "python_extensions": [
                    "ms-python.python",
                    "ms-python.autopep8", 
                    "ms-python.pylint",
                    "ms-toolsai.jupyter"
                ],
                "web_development": [
                    "ms-vscode.vscode-typescript-next",
                    "esbenp.prettier-vscode",
                    "bradlc.vscode-tailwindcss",
                    "ms-vscode.vscode-html-language-features"
                ],
                "ai_tools": [
                    "github.copilot",
                    "ms-toolsai.vscode-ai",
                    "continue.continue"
                ]
            }
        }
    
    def test_vscode_connection(self) -> Dict[str, Any]:
        """Test VS Code web server connection and capabilities"""
        
        print("🔍 Testing VS Code Web Server...")
        
        try:
            # Test basic connectivity
            response = requests.get(self.vscode_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ VS Code Web Server is accessible")
                
                # Check for VS Code specific content
                content = response.text
                is_vscode = any(term in content.lower() for term in ['vscode', 'code-server', 'visual studio code'])
                
                result = {
                    "status": "active",
                    "url": self.vscode_url,
                    "accessible": True,
                    "is_vscode": is_vscode,
                    "response_time": response.elapsed.total_seconds(),
                    "server_type": self._detect_server_type(content),
                    "capabilities": self._detect_capabilities(content)
                }
                
                print(f"🌐 Server Type: {result['server_type']}")
                print(f"⚡ Response Time: {result['response_time']:.2f}s")
                print(f"🔧 VS Code Features: {'✅ Detected' if is_vscode else '❌ Not detected'}")
                
                return result
                
            else:
                print(f"❌ VS Code Web Server returned status {response.status_code}")
                return {
                    "status": "error",
                    "accessible": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to VS Code Web Server: {e}")
            return {
                "status": "error", 
                "accessible": False,
                "error": str(e)
            }
    
    def _detect_server_type(self, content: str) -> str:
        """Detect the type of VS Code server"""
        content_lower = content.lower()
        
        if 'code-server' in content_lower:
            return "code-server (Community)"
        elif 'vscode-server' in content_lower or 'workbench-web' in content_lower:
            return "VS Code Server (Official)"
        elif 'gitpod' in content_lower:
            return "Gitpod"
        elif 'codespaces' in content_lower:
            return "GitHub Codespaces"
        else:
            return "Unknown VS Code Web Server"
    
    def _detect_capabilities(self, content: str) -> List[str]:
        """Detect available capabilities from page content"""
        capabilities = []
        content_lower = content.lower()
        
        capability_indicators = {
            "Extensions": ["extension", "marketplace"],
            "Terminal": ["terminal", "shell"],
            "Git Integration": ["git", "source control"],
            "Debugging": ["debug", "breakpoint"],
            "IntelliSense": ["intellisense", "autocomplete"],
            "Multi-language": ["language", "syntax"],
            "File Explorer": ["explorer", "file tree"],
            "Search": ["search", "find"],
            "Settings Sync": ["settings sync", "profile"],
            "Themes": ["theme", "color scheme"]
        }
        
        for capability, indicators in capability_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                capabilities.append(capability)
        
        return capabilities
    
    def create_workspace_config(self, workspace_name: str = "ai-research-platform"):
        """Create VS Code workspace configuration for AI development"""
        
        workspace_config = {
            "folders": [
                {
                    "name": "AI Research Platform",
                    "path": "/home/keith/chat-copilot"
                },
                {
                    "name": "AutoGen Environment", 
                    "path": "/home/keith/chat-copilot/autogen-env"
                },
                {
                    "name": "Documentation",
                    "path": "/home/keith/chat-copilot/docs"
                }
            ],
            "settings": {
                "python.pythonPath": "/home/keith/chat-copilot/autogen-env/bin/python",
                "python.terminal.activateEnvironment": True,
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True
                },
                "files.autoSave": "afterDelay",
                "terminal.integrated.defaultProfile.linux": "bash",
                "git.autofetch": True,
                "workbench.colorTheme": "Default Dark+",
                "editor.fontSize": 14,
                "editor.tabSize": 4,
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": True,
                "jupyter.askForKernelRestart": False
            },
            "extensions": {
                "recommendations": self.platform_config["recommended_extensions"]
            },
            "tasks": {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "Start AutoGen Studio",
                        "type": "shell",
                        "command": "source autogen-env/bin/activate && autogenstudio ui --port 8085 --host 0.0.0.0",
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "new"
                        }
                    },
                    {
                        "label": "Run Magentic-One Demo",
                        "type": "shell", 
                        "command": "source autogen-env/bin/activate && python magentic_one_simple.py",
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "new"
                        }
                    },
                    {
                        "label": "Test Ollama Models",
                        "type": "shell",
                        "command": "ollama list",
                        "group": "test",
                        "presentation": {
                            "echo": True,
                            "reveal": "always"
                        }
                    }
                ]
            },
            "launch": {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Python: AutoGen Examples",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/autogen_examples.py",
                        "console": "integratedTerminal",
                        "python": "/home/keith/chat-copilot/autogen-env/bin/python"
                    },
                    {
                        "name": "Python: Magentic-One Platform",
                        "type": "python",
                        "request": "launch", 
                        "program": "${workspaceFolder}/magentic_one_simple.py",
                        "console": "integratedTerminal",
                        "python": "/home/keith/chat-copilot/autogen-env/bin/python"
                    }
                ]
            }
        }
        
        # Save workspace configuration
        workspace_dir = "/home/keith/chat-copilot/.vscode"
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save individual config files
        config_files = {
            "settings.json": workspace_config["settings"],
            "extensions.json": workspace_config["extensions"], 
            "tasks.json": workspace_config["tasks"],
            "launch.json": workspace_config["launch"]
        }
        
        for filename, config in config_files.items():
            filepath = os.path.join(workspace_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Created {filename}")
        
        # Save workspace file
        workspace_file = f"/home/keith/chat-copilot/{workspace_name}.code-workspace"
        with open(workspace_file, 'w') as f:
            json.dump(workspace_config, f, indent=2)
        print(f"✅ Created workspace file: {workspace_file}")
        
        return workspace_config
    
    def create_ai_development_snippets(self):
        """Create VS Code snippets for AI development"""
        
        snippets = {
            "AutoGen Agent Creation": {
                "prefix": "autogen-agent",
                "body": [
                    "from autogen_agentchat.agents import AssistantAgent",
                    "from autogen_ext.models.openai import OpenAIChatCompletionClient",
                    "",
                    "# Create Ollama client",
                    "client = OpenAIChatCompletionClient(",
                    "    model=\"${1:llama3.2:3b}\",",
                    "    base_url=\"http://localhost:11434/v1\",",
                    "    api_key=\"ollama\"",
                    ")",
                    "",
                    "# Create agent",
                    "agent = AssistantAgent(",
                    "    name=\"${2:AgentName}\",",
                    "    model_client=client,",
                    "    system_message=\"${3:You are a helpful AI assistant.}\"",
                    ")"
                ],
                "description": "Create an AutoGen agent with Ollama"
            },
            "Magentic-One Team Setup": {
                "prefix": "magentic-team",
                "body": [
                    "from magentic_one_simple import MagenticOnePlatform",
                    "import asyncio",
                    "",
                    "async def main():",
                    "    platform = MagenticOnePlatform()",
                    "    ",
                    "    # Run workflow",
                    "    task = \"${1:Your task description here}\"",
                    "    result = await platform.run_workflow(\"${2|research,development,analysis,full_team|}\", task)",
                    "    ",
                    "    print(f\"Result: {result['final_result']}\")",
                    "",
                    "if __name__ == \"__main__\":",
                    "    asyncio.run(main())"
                ],
                "description": "Set up a Magentic-One team workflow"
            },
            "Ollama API Call": {
                "prefix": "ollama-api",
                "body": [
                    "import requests",
                    "",
                    "def call_ollama(model: str, prompt: str):",
                    "    response = requests.post(",
                    "        \"http://localhost:11434/api/generate\",",
                    "        json={",
                    "            \"model\": model,",
                    "            \"prompt\": prompt,",
                    "            \"stream\": False",
                    "        }",
                    "    )",
                    "    return response.json()[\"response\"]",
                    "",
                    "# Usage",
                    "result = call_ollama(\"${1:llama3.2:3b}\", \"${2:Your prompt here}\")",
                    "print(result)"
                ],
                "description": "Make a direct Ollama API call"
            },
            "AI Platform Service Test": {
                "prefix": "test-service",
                "body": [
                    "import requests",
                    "",
                    "def test_ai_service(url: str, service_name: str):",
                    "    try:",
                    "        response = requests.get(url, timeout=5)",
                    "        if response.status_code == 200:",
                    "            print(f\"✅ {service_name}: Active\")",
                    "        else:",
                    "            print(f\"❌ {service_name}: Error {response.status_code}\")",
                    "    except Exception as e:",
                    "        print(f\"❌ {service_name}: {e}\")",
                    "",
                    "# Test AI Research Platform services",
                    "services = {",
                    "    \"AutoGen Studio\": \"http://100.123.10.72:8085\",",
                    "    \"OpenWebUI\": \"https://ubuntuaicodeserver-1.tail5137b4.ts.net\",",
                    "    \"Chat Copilot\": \"http://100.123.10.72:11000\",",
                    "    \"Perplexica\": \"http://100.123.10.72:3999/perplexica\"",
                    "}",
                    "",
                    "for name, url in services.items():",
                    "    test_ai_service(url, name)"
                ],
                "description": "Test AI Research Platform services"
            }
        }
        
        # Save snippets
        snippets_dir = "/home/keith/chat-copilot/.vscode"
        os.makedirs(snippets_dir, exist_ok=True)
        
        snippets_file = os.path.join(snippets_dir, "ai-development.code-snippets")
        with open(snippets_file, 'w') as f:
            json.dump(snippets, f, indent=2)
        
        print(f"✅ Created AI development snippets: {snippets_file}")
        return snippets
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive VS Code web integration status"""
        
        connection_test = self.test_vscode_connection()
        
        status = {
            "service_name": "VS Code Web",
            "url": self.vscode_url,
            "tailscale_ip": "100.123.10.72",
            "port": 57081,
            "connection": connection_test,
            "features": self.platform_config["features"],
            "ai_development_ready": True,
            "workspace_configured": os.path.exists("/home/keith/chat-copilot/.vscode/settings.json"),
            "integration_level": "enhanced",
            "recommended_extensions": len(self.platform_config["recommended_extensions"]),
            "ai_snippets_available": os.path.exists("/home/keith/chat-copilot/.vscode/ai-development.code-snippets"),
            "platform_integration": {
                "autogen_studio": "http://100.123.10.72:8085",
                "magentic_one": "http://100.123.10.72:8086", 
                "control_panel": "http://100.123.10.72:11000/control-panel.html"
            }
        }
        
        return status

def main():
    """Main VS Code web integration setup"""
    
    print("🌐 VS Code Web Integration Setup")
    print("=" * 40)
    
    # Initialize integration
    vscode_integration = VSCodeWebIntegration()
    
    # Test current setup
    print("\n🔍 Testing Current VS Code Web Setup...")
    status = vscode_integration.get_integration_status()
    
    if status["connection"]["accessible"]:
        print("✅ VS Code Web is accessible and running")
        print(f"🌐 Access URL: {status['url']}")
        print(f"🔧 Server Type: {status['connection']['server_type']}")
        print(f"⚡ Response Time: {status['connection']['response_time']:.2f}s")
        
        if status["connection"]["capabilities"]:
            print(f"🎯 Detected Capabilities: {', '.join(status['connection']['capabilities'])}")
    else:
        print("❌ VS Code Web is not accessible")
        return
    
    # Create workspace configuration
    print(f"\n📁 Creating AI Development Workspace...")
    workspace_config = vscode_integration.create_workspace_config()
    
    # Create AI development snippets
    print(f"\n🎨 Creating AI Development Snippets...")
    snippets = vscode_integration.create_ai_development_snippets()
    
    # Show final status
    final_status = vscode_integration.get_integration_status()
    
    print(f"\n🎉 VS Code Web Integration Complete!")
    print(f"\n📊 Integration Summary:")
    print(f"   🌐 Service: {final_status['service_name']}")
    print(f"   🔗 URL: {final_status['url']}")
    print(f"   ⚙️ Workspace: {'✅ Configured' if final_status['workspace_configured'] else '❌ Not configured'}")
    print(f"   🎨 Snippets: {'✅ Available' if final_status['ai_snippets_available'] else '❌ Not available'}")
    print(f"   🔌 Extensions: {final_status['recommended_extensions']} recommended")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Open VS Code Web: {final_status['url']}")
    print(f"2. Install recommended extensions for AI development")
    print(f"3. Open workspace: ai-research-platform.code-workspace")
    print(f"4. Use AI development snippets for faster coding")
    print(f"5. Access integrated terminals for AutoGen and Magentic-One")

if __name__ == "__main__":
    main()