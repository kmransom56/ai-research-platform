#!/usr/bin/env python3
"""
Workflow Templates for Multi-Agent Collaboration
Predefined collaboration patterns for common task types
Enhanced with MCP (Model Context Protocol) server integration
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collaboration_orchestrator import Task, TaskType
import uuid

@dataclass
class WorkflowTemplate:
    """Template for a collaboration workflow"""
    name: str
    description: str
    task_types: List[str]
    dependencies: Dict[str, List[str]]
    parallel_sections: List[List[str]]
    estimated_duration: int
    required_capabilities: List[str]
    mcp_integrations: Optional[Dict[str, List[str]]] = None  # MCP servers by capability

class WorkflowManager:
    """Manages predefined workflow templates"""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, WorkflowTemplate]:
        """Load default workflow templates"""
        templates = {}
        
        # Research & Analysis Workflow
        templates["research_analysis"] = WorkflowTemplate(
            name="Research & Analysis",
            description="Research a topic and provide comprehensive analysis",
            task_types=["research", "reasoning", "general"],
            dependencies={
                "reasoning": ["research"],
                "general": ["research", "reasoning"]
            },
            parallel_sections=[],
            estimated_duration=120,
            required_capabilities=["search", "reasoning", "analysis"],
            mcp_integrations={
                "api_testing": ["apidog"],
                "design_operations": ["figma"]
            }
        )
        
        # Code Development Workflow
        templates["code_development"] = WorkflowTemplate(
            name="Code Development",
            description="Research, design, implement, and document code",
            task_types=["research", "coding", "reasoning", "general"],
            dependencies={
                "coding": ["research"],
                "reasoning": ["coding"],
                "general": ["reasoning"]
            },
            parallel_sections=[],
            estimated_duration=180,
            required_capabilities=["search", "coding", "reasoning", "documentation"],
            mcp_integrations={
                "code_management": ["github"],
                "container_management": ["docker"],
                "api_testing": ["apidog"],
                "design_operations": ["figma"]
            }
        )
        
        # Creative Project Workflow
        templates["creative_project"] = WorkflowTemplate(
            name="Creative Project",
            description="Research, brainstorm, create, and refine creative content",
            task_types=["research", "creative", "reasoning", "general"],
            dependencies={
                "creative": ["research"],
                "reasoning": ["creative"],
                "general": ["reasoning"]
            },
            parallel_sections=[],
            estimated_duration=150,
            required_capabilities=["search", "creative", "reasoning", "general"],
            mcp_integrations={
                "design_operations": ["figma"],
                "api_testing": ["apidog"]
            }
        )
        
        # Technical Documentation Workflow
        templates["technical_docs"] = WorkflowTemplate(
            name="Technical Documentation",
            description="Research, analyze code, and create comprehensive documentation",
            task_types=["research", "coding", "reasoning", "general"],
            dependencies={
                "coding": ["research"],
                "reasoning": ["coding"],
                "general": ["reasoning"]
            },
            parallel_sections=[["research"], ["coding", "reasoning"]],
            estimated_duration=100,
            required_capabilities=["search", "coding", "analysis", "documentation"]
        )
        
        # Multi-Domain Analysis Workflow
        templates["multi_domain"] = WorkflowTemplate(
            name="Multi-Domain Analysis",
            description="Parallel analysis across multiple domains with synthesis",
            task_types=["research", "reasoning", "coding", "creative", "general"],
            dependencies={
                "general": ["research", "reasoning", "coding", "creative"]
            },
            parallel_sections=[["research", "reasoning", "coding", "creative"]],
            estimated_duration=200,
            required_capabilities=["search", "reasoning", "coding", "creative", "synthesis"]
        )
        
        # Problem Solving Workflow
        templates["problem_solving"] = WorkflowTemplate(
            name="Problem Solving",
            description="Systematic approach to complex problem solving",
            task_types=["research", "reasoning", "coding", "general"],
            dependencies={
                "reasoning": ["research"],
                "coding": ["reasoning"],
                "general": ["coding"]
            },
            parallel_sections=[],
            estimated_duration=160,
            required_capabilities=["search", "reasoning", "coding", "problem-solving"],
            mcp_integrations={
                "code_management": ["github"],
                "container_management": ["docker"],
                "api_testing": ["apidog"]
            }
        )
        
        # Restaurant Network Management Workflow
        templates["restaurant_network"] = WorkflowTemplate(
            name="Restaurant Network Management",
            description="Comprehensive restaurant network monitoring and management",
            task_types=["research", "reasoning", "general"],
            dependencies={
                "reasoning": ["research"],
                "general": ["reasoning"]
            },
            parallel_sections=[],
            estimated_duration=90,
            required_capabilities=["network_management", "device_monitoring", "security_analysis"],
            mcp_integrations={
                "network_management": ["meraki", "fortimanager"],
                "restaurant_networks": ["fortimanager"],
                "device_monitoring": ["meraki"]
            }
        )
        
        # Network Security Assessment Workflow
        templates["network_security"] = WorkflowTemplate(
            name="Network Security Assessment",
            description="Comprehensive security analysis for restaurant networks",
            task_types=["research", "reasoning", "general"],
            dependencies={
                "reasoning": ["research"],
                "general": ["reasoning"]
            },
            parallel_sections=[["research"], ["reasoning"]],
            estimated_duration=120,
            required_capabilities=["security_analysis", "policy_management", "threat_detection"],
            mcp_integrations={
                "fortinet_management": ["fortimanager"],
                "network_management": ["meraki", "fortimanager"],
                "api_testing": ["apidog"]
            }
        )
        
        # DevOps Infrastructure Workflow
        templates["devops_infrastructure"] = WorkflowTemplate(
            name="DevOps Infrastructure Management",
            description="Container and infrastructure management with deployment",
            task_types=["research", "coding", "reasoning", "general"],
            dependencies={
                "coding": ["research"],
                "reasoning": ["coding"],
                "general": ["reasoning"]
            },
            parallel_sections=[],
            estimated_duration=180,
            required_capabilities=["container_management", "code_management", "infrastructure"],
            mcp_integrations={
                "container_management": ["docker"],
                "code_management": ["github"],
                "api_testing": ["apidog"],
                "design_operations": ["figma"]
            }
        )
        
        return templates
    
    def get_template(self, template_name: str) -> WorkflowTemplate:
        """Get a specific workflow template"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> Dict[str, str]:
        """List all available templates with descriptions"""
        return {
            name: template.description 
            for name, template in self.templates.items()
        }
    
    def suggest_template(self, prompt: str) -> str:
        """Suggest the best template based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Keywords for different templates
        template_keywords = {
            "research_analysis": ["research", "analyze", "study", "investigate", "examine"],
            "code_development": ["code", "program", "develop", "implement", "function", "algorithm"],
            "creative_project": ["write", "create", "story", "poem", "creative", "generate"],
            "technical_docs": ["document", "documentation", "explain", "guide", "manual"],
            "multi_domain": ["compare", "contrast", "multiple", "different", "various"],
            "problem_solving": ["solve", "solution", "problem", "fix", "resolve"],
            "restaurant_network": ["restaurant", "network", "meraki", "fortinet", "device", "monitoring"],
            "network_security": ["security", "firewall", "policy", "threat", "vulnerability", "fortinet"],
            "devops_infrastructure": ["docker", "container", "deploy", "infrastructure", "devops", "ci/cd"]
        }
        
        # Score templates based on keyword matches
        scores = {}
        for template_name, keywords in template_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                scores[template_name] = score
        
        if scores:
            # Return template with highest score
            return max(scores, key=scores.get)
        else:
            # Default to research_analysis for unknown patterns
            return "research_analysis"
    
    def create_tasks_from_template(self, template_name: str, prompt: str, context: Dict[str, Any] = None) -> List[Task]:
        """Create tasks based on a workflow template"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        if context is None:
            context = {}
        
        tasks = []
        task_id_base = str(uuid.uuid4())[:8]
        
        # Create tasks for each type in the template
        for i, task_type_str in enumerate(template.task_types):
            task_type = TaskType(task_type_str)
            task_id = f"{task_id_base}-{task_type_str}-{i}"
            
            # Generate specific prompt for this task type
            task_prompt = self._generate_task_prompt(task_type, prompt, template)
            
            # Determine dependencies
            dependencies = []
            if task_type_str in template.dependencies:
                for dep_type in template.dependencies[task_type_str]:
                    # Find the task ID for this dependency type
                    for existing_task in tasks:
                        if existing_task.type.value == dep_type:
                            dependencies.append(existing_task.id)
                            break
            
            task = Task(
                id=task_id,
                type=task_type,
                prompt=task_prompt,
                context=context.copy(),
                dependencies=dependencies,
                assigned_services=[]
            )
            
            tasks.append(task)
        
        return tasks
    
    def _generate_task_prompt(self, task_type: TaskType, original_prompt: str, template: WorkflowTemplate) -> str:
        """Generate a specific prompt for a task type based on the original prompt"""
        
        prompt_templates = {
            TaskType.RESEARCH: f"Research and gather information about: {original_prompt}",
            TaskType.REASONING: f"Analyze and reason about: {original_prompt}. Consider the research findings and provide logical conclusions.",
            TaskType.CODING: f"Develop code or technical solution for: {original_prompt}. Use research insights to inform the implementation.",
            TaskType.CREATIVE: f"Create creative content related to: {original_prompt}. Draw inspiration from research and analysis.",
            TaskType.GENERAL: f"Provide a comprehensive summary and final response for: {original_prompt}. Integrate insights from all previous analyses.",
            TaskType.ANALYSIS: f"Perform detailed analysis of: {original_prompt}",
            TaskType.MULTIMODAL: f"Process and analyze multimodal content for: {original_prompt}"
        }
        
        return prompt_templates.get(task_type, f"Process the following request: {original_prompt}")
    
    def get_workflow_config(self, template_name: str) -> Dict[str, Any]:
        """Get complete workflow configuration as dictionary"""
        template = self.get_template(template_name)
        if not template:
            return {}
        
        return {
            "template": asdict(template),
            "parallel_execution": len(template.parallel_sections) > 0,
            "total_tasks": len(template.task_types),
            "complexity": "high" if len(template.task_types) > 3 else "medium" if len(template.task_types) > 1 else "low"
        }

# Example usage and workflow definitions
WORKFLOW_EXAMPLES = {
    "software_design": {
        "prompt": "Design a microservices architecture for an e-commerce platform",
        "template": "code_development",
        "expected_tasks": ["research", "reasoning", "coding", "general"]
    },
    "market_research": {
        "prompt": "Analyze the current state of the electric vehicle market",
        "template": "research_analysis", 
        "expected_tasks": ["research", "reasoning", "general"]
    },
    "creative_writing": {
        "prompt": "Write a science fiction story about time travel",
        "template": "creative_project",
        "expected_tasks": ["research", "creative", "reasoning", "general"]
    },
    "api_documentation": {
        "prompt": "Create comprehensive documentation for a REST API",
        "template": "technical_docs",
        "expected_tasks": ["research", "coding", "reasoning", "general"]
    }
}

# Global workflow manager instance
workflow_manager = WorkflowManager()

if __name__ == "__main__":
    # Test the workflow manager
    print("Available Workflow Templates:")
    for name, description in workflow_manager.list_templates().items():
        print(f"  • {name}: {description}")
    
    print("\nTesting template suggestion:")
    test_prompts = [
        "Research quantum computing and implement a quantum algorithm",
        "Write a story about robots",
        "Document this API thoroughly",
        "Solve this complex mathematical problem"
    ]
    
    for prompt in test_prompts:
        suggested = workflow_manager.suggest_template(prompt)
        print(f"  '{prompt[:40]}...' → {suggested}")
    
    print("\nTesting task creation:")
    tasks = workflow_manager.create_tasks_from_template(
        "code_development",
        "Create a web scraper for news articles"
    )
    
    for task in tasks:
        print(f"  • {task.type.value}: {task.prompt[:60]}...")
        if task.dependencies:
            print(f"    Dependencies: {task.dependencies}")