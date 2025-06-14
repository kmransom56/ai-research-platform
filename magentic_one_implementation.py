#!/usr/bin/env python3
"""
Magentic-One Implementation for AI Research Platform
Using available AutoGen components with Ollama integration
"""

import asyncio
import json
import os
from typing import List, Dict, Any
from datetime import datetime

# Import available AutoGen components
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import available Magentic-One components
try:
    from autogen_ext.agents.magentic_one import MagenticOneCoderAgent
    CODER_AGENT_AVAILABLE = True
except ImportError:
    CODER_AGENT_AVAILABLE = False

class MagenticOnePlatform:
    """Magentic-One inspired multi-agent platform for AI Research Platform"""
    
    def __init__(self):
        self.agents = {}
        self.teams = {}
        self.workflows = {}
        self.config = self._load_config()
        self.ollama_base_url = "http://localhost:11434/v1"
        
    def _load_config(self):
        """Load Magentic-One configuration"""
        return {
            "models": {
                "coordinator": "llama3.2:3b",
                "web_surfer": "mistral:latest", 
                "file_surfer": "deepseek-coder:6.7b",
                "coder": "deepseek-coder:6.7b",
                "terminal": "llama3.2:3b"
            },
            "safety": {
                "enable_approval": True,
                "restricted_commands": [
                    "rm -rf", "sudo rm", "format", "delete", "DROP TABLE"
                ],
                "max_execution_time": 300
            }
        }
    
    def create_ollama_client(self, model: str):
        """Create OpenAI-compatible client for Ollama"""
        return OpenAIChatCompletionClient(
            model=model,
            base_url=self.ollama_base_url,
            api_key="ollama"
        )
    
    def create_coordinator_agent(self):
        """Create Orchestrator/Coordinator agent"""
        client = self.create_ollama_client(self.config["models"]["coordinator"])
        
        agent = AssistantAgent(
            name="Orchestrator",
            model_client=client,
            system_message="""You are the Orchestrator agent in a multi-agent system. Your role is to:
            
1. Break down complex tasks into manageable subtasks
2. Plan the sequence of actions needed
3. Delegate tasks to appropriate specialist agents
4. Coordinate the work between agents
5. Synthesize results into final outputs
6. Monitor progress and adjust plans as needed

Always start by understanding the goal, then create a clear plan with specific steps for each agent."""
        )
        
        self.agents["orchestrator"] = agent
        return agent
    
    def create_web_surfer_agent(self):
        """Create WebSurfer agent for web interactions"""
        client = self.create_ollama_client(self.config["models"]["web_surfer"])
        
        agent = AssistantAgent(
            name="WebSurfer", 
            model_client=client,
            system_message="""You are the WebSurfer agent. Your capabilities include:

1. Navigate websites and web applications
2. Search for information across multiple sources
3. Extract data from web pages
4. Interact with web forms and interfaces
5. Download and process web content
6. Verify information from multiple sources

When given a web research task, break it down into specific URLs to visit, searches to perform, and data to extract. Always verify information from multiple sources."""
        )
        
        self.agents["web_surfer"] = agent
        return agent
    
    def create_file_surfer_agent(self):
        """Create FileSurfer agent for file operations"""
        client = self.create_ollama_client(self.config["models"]["file_surfer"])
        
        agent = AssistantAgent(
            name="FileSurfer",
            model_client=client, 
            system_message="""You are the FileSurfer agent. Your capabilities include:

1. Navigate and explore file systems
2. Read and analyze various file formats (text, JSON, CSV, logs, etc.)
3. Search for specific content within files
4. Organize and categorize files
5. Extract data from documents
6. Create file summaries and reports

When working with files, always provide clear paths, explain file contents, and suggest organization strategies."""
        )
        
        self.agents["file_surfer"] = agent
        return agent
    
    def create_coder_agent(self):
        """Create Coder agent for programming tasks"""
        if CODER_AGENT_AVAILABLE:
            # Use the official Magentic-One coder agent if available
            client = self.create_ollama_client(self.config["models"]["coder"])
            agent = MagenticOneCoderAgent(
                name="Coder",
                model_client=client,
                system_message="""You are the Coder agent. Your capabilities include:

1. Write code in multiple programming languages
2. Analyze and debug existing code
3. Create comprehensive tests
4. Optimize code performance
5. Review code for best practices
6. Generate documentation

Always write clean, well-documented code with proper error handling."""
            )
        else:
            # Fallback to standard AssistantAgent
            client = self.create_ollama_client(self.config["models"]["coder"])
            agent = AssistantAgent(
                name="Coder",
                model_client=client,
                system_message="""You are the Coder agent. Your capabilities include:

1. Write code in multiple programming languages (Python, JavaScript, etc.)
2. Analyze and debug existing code
3. Create comprehensive tests
4. Optimize code performance
5. Review code for best practices and security
6. Generate technical documentation

Always write clean, well-documented code with proper error handling. Explain your reasoning and provide examples."""
            )
        
        self.agents["coder"] = agent
        return agent
    
    def create_terminal_agent(self):
        """Create ComputerTerminal agent for system operations"""
        client = self.create_ollama_client(self.config["models"]["terminal"])
        
        agent = AssistantAgent(
            name="ComputerTerminal",
            model_client=client,
            system_message="""You are the ComputerTerminal agent. Your capabilities include:

1. Execute shell commands and scripts
2. Install packages and dependencies
3. Manage system configurations
4. Monitor system performance
5. Automate routine tasks
6. Test applications and services

SAFETY GUIDELINES:
- Always explain what commands will do before suggesting them
- Avoid destructive operations (rm -rf, format, etc.)
- Use safe practices for file operations
- Request human approval for system-level changes
- Provide alternative approaches when possible

Focus on safe, reversible operations and always explain the impact of commands."""
        )
        
        self.agents["terminal"] = agent
        return agent
    
    def create_research_team(self):
        """Create multi-agent research team"""
        agents = [
            self.create_coordinator_agent(),
            self.create_web_surfer_agent(),
            self.create_file_surfer_agent()
        ]
        
        team = RoundRobinGroupChat(agents)
        self.teams["research"] = team
        return team
    
    def create_development_team(self):
        """Create multi-agent development team"""
        agents = [
            self.create_coordinator_agent(),
            self.create_coder_agent(),
            self.create_terminal_agent(),
            self.create_file_surfer_agent()
        ]
        
        team = RoundRobinGroupChat(agents)
        self.teams["development"] = team
        return team
    
    def create_analysis_team(self):
        """Create multi-agent data analysis team"""
        agents = [
            self.create_coordinator_agent(),
            self.create_file_surfer_agent(),
            self.create_coder_agent()
        ]
        
        team = RoundRobinGroupChat(agents)
        self.teams["analysis"] = team
        return team
    
    async def run_workflow(self, team_name: str, task: str, max_turns: int = 10):
        """Run a multi-agent workflow"""
        if team_name not in self.teams:
            raise ValueError(f"Team '{team_name}' not found")
        
        team = self.teams[team_name]
        
        # Create initial message
        initial_message = TextMessage(content=task, source="user")
        
        print(f"🚀 Starting {team_name} workflow...")
        print(f"📋 Task: {task}")
        print(f"🤖 Agents: {[agent.name for agent in team._agents]}")
        print("=" * 60)
        
        # Run the conversation
        async for message in team.on_messages([initial_message], cancellation_token=None):
            print(f"\n💬 {message.source}: {message.content}")
            
            # Check if we've reached max turns
            max_turns -= 1
            if max_turns <= 0:
                print("\n⏱️ Reached maximum turns, stopping workflow")
                break
        
        print("\n✅ Workflow completed!")

class MagenticOneWorkflows:
    """Pre-defined workflows for common tasks"""
    
    @staticmethod
    def web_research_workflow():
        return {
            "name": "Web Research Project",
            "description": "Comprehensive web research with documentation",
            "team": "research",
            "example_tasks": [
                "Research the latest developments in AI agent frameworks",
                "Find information about sustainable energy solutions",
                "Analyze competitor products and market trends",
                "Gather data on programming language adoption rates"
            ],
            "expected_agents": ["Orchestrator", "WebSurfer", "FileSurfer"],
            "typical_flow": [
                "Orchestrator creates research plan",
                "WebSurfer searches and gathers information",
                "FileSurfer organizes and documents findings",
                "Orchestrator compiles final report"
            ]
        }
    
    @staticmethod
    def code_development_workflow():
        return {
            "name": "Code Development Project",
            "description": "Full development lifecycle with testing",
            "team": "development", 
            "example_tasks": [
                "Create a Python web scraper with error handling",
                "Build a REST API with authentication",
                "Develop a data analysis script with visualizations",
                "Implement a task automation system"
            ],
            "expected_agents": ["Orchestrator", "Coder", "ComputerTerminal", "FileSurfer"],
            "typical_flow": [
                "Orchestrator plans development approach",
                "Coder writes initial implementation",
                "ComputerTerminal sets up environment",
                "Coder implements features and tests",
                "FileSurfer organizes project files",
                "ComputerTerminal runs final tests"
            ]
        }
    
    @staticmethod
    def data_analysis_workflow():
        return {
            "name": "Data Analysis Project",
            "description": "Comprehensive data processing and analysis",
            "team": "analysis",
            "example_tasks": [
                "Analyze system performance logs for bottlenecks",
                "Process customer feedback data for insights",
                "Examine financial data for trends and patterns",
                "Evaluate A/B test results and recommendations"
            ],
            "expected_agents": ["Orchestrator", "FileSurfer", "Coder"],
            "typical_flow": [
                "Orchestrator defines analysis objectives",
                "FileSurfer loads and examines data",
                "Coder creates analysis scripts",
                "FileSurfer validates data quality",
                "Coder generates reports and visualizations",
                "Orchestrator summarizes insights"
            ]
        }

def create_magentic_one_demo():
    """Create and demonstrate Magentic-One platform"""
    
    print("🤖 Magentic-One Multi-Agent Platform Demo")
    print("=" * 50)
    
    # Initialize platform
    platform = MagenticOnePlatform()
    
    # Create teams
    print("👥 Creating agent teams...")
    research_team = platform.create_research_team()
    development_team = platform.create_development_team()
    analysis_team = platform.create_analysis_team()
    
    print("✅ Teams created successfully!")
    print(f"   🔍 Research Team: {[agent.name for agent in research_team._agents]}")
    print(f"   💻 Development Team: {[agent.name for agent in development_team._agents]}")
    print(f"   📊 Analysis Team: {[agent.name for agent in analysis_team._agents]}")
    
    # Show available workflows
    print(f"\n📋 Available Workflows:")
    
    workflows = [
        MagenticOneWorkflows.web_research_workflow(),
        MagenticOneWorkflows.code_development_workflow(), 
        MagenticOneWorkflows.data_analysis_workflow()
    ]
    
    for workflow in workflows:
        print(f"\n🎯 {workflow['name']}")
        print(f"   📝 {workflow['description']}")
        print(f"   🤖 Agents: {', '.join(workflow['expected_agents'])}")
        print(f"   💡 Example: {workflow['example_tasks'][0]}")
    
    # Create configuration files
    config_dir = os.path.expanduser("~/.autogenstudio/magentic-one")
    os.makedirs(config_dir, exist_ok=True)
    
    # Save workflows
    with open(os.path.join(config_dir, "workflows.json"), 'w') as f:
        json.dump({f"workflow_{i}": wf for i, wf in enumerate(workflows)}, f, indent=2)
    
    # Save platform config
    platform_config = {
        "name": "Magentic-One Multi-Agent Platform",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "models": platform.config["models"],
        "safety": platform.config["safety"],
        "access_url": "http://100.123.10.72:8086",
        "capabilities": [
            "Multi-agent task coordination",
            "Web research and data gathering",
            "Code development and testing",
            "File analysis and organization",
            "System command execution",
            "Complex problem solving"
        ]
    }
    
    with open(os.path.join(config_dir, "platform_config.json"), 'w') as f:
        json.dump(platform_config, f, indent=2)
    
    print(f"\n📁 Configuration saved to: {config_dir}")
    print(f"🌐 Platform ready for integration!")
    
    return platform

async def demo_workflow():
    """Demonstrate a simple workflow"""
    platform = create_magentic_one_demo()
    
    print(f"\n🚀 Running Demo Workflow...")
    
    # Simple research task
    task = "Explain the benefits of multi-agent AI systems for software development"
    
    try:
        await platform.run_workflow("research", task, max_turns=5)
    except Exception as e:
        print(f"⚠️ Demo workflow error: {e}")
        print("💡 This is expected in a configuration demo")

def main():
    """Main function"""
    platform = create_magentic_one_demo()
    
    print(f"\n🎉 Magentic-One Platform Setup Complete!")
    print(f"\n🔧 Next Steps:")
    print(f"1. Integrate with AutoGen Studio dashboard")
    print(f"2. Add to AI Research Platform interface")
    print(f"3. Test multi-agent workflows")
    print(f"4. Create custom team configurations")
    print(f"5. Deploy as service on port 8086")
    
    # Optionally run demo
    print(f"\n💡 To test a workflow, run:")
    print(f"   python -c 'import asyncio; asyncio.run(demo_workflow())'")

if __name__ == "__main__":
    main()