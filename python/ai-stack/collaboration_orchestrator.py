#!/usr/bin/env python3
"""
Multi-Agent Collaboration Orchestrator
Coordinates tasks across all AI services and applications in the platform
Enhanced with MCP (Model Context Protocol) server integration
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import uuid
from datetime import datetime, timedelta
from workflow_templates import workflow_manager
from mcp_server_registry import mcp_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Task types for different AI services"""
    REASONING = "reasoning"
    GENERAL = "general"
    CODING = "coding"
    CREATIVE = "creative"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    MULTIMODAL = "multimodal"
    COLLABORATIVE = "collaborative"

class ServiceStatus(Enum):
    """Service status states"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    name: str
    url: str
    port: int
    health_path: str
    capabilities: List[str]
    priority: int = 5
    timeout: int = 30
    retry_count: int = 3

@dataclass
class Task:
    """Task representation for collaboration"""
    id: str
    type: TaskType
    prompt: str
    context: Dict[str, Any]
    dependencies: List[str]
    assigned_services: List[str]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class CollaborationPlan:
    """Plan for multi-service collaboration"""
    id: str
    task_sequence: List[Task]
    service_allocation: Dict[str, List[str]]
    estimated_duration: int
    parallel_execution: bool = False

class ServiceRegistry:
    """Registry of all platform services and their capabilities"""
    
    def __init__(self):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        self.last_health_check: Dict[str, datetime] = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize service registry with all platform services"""
        
        # AI Stack Services
        self.services.update({
            "vllm-reasoning": ServiceEndpoint(
                name="vLLM Reasoning",
                url=os.getenv('REASONING_MODEL_URL', 'http://localhost:8000'),
                port=8000,
                health_path="/health",
                capabilities=["reasoning", "analysis", "math", "logic"],
                priority=9
            ),
            "vllm-general": ServiceEndpoint(
                name="vLLM General",
                url=os.getenv('GENERAL_MODEL_URL', 'http://localhost:8001'),
                port=8001,
                health_path="/health",
                capabilities=["general", "conversation", "qa"],
                priority=8
            ),
            "vllm-coding": ServiceEndpoint(
                name="vLLM Coding",
                url=os.getenv('CODING_MODEL_URL', 'http://localhost:8002'),
                port=8002,
                health_path="/health",
                capabilities=["coding", "programming", "debugging", "review"],
                priority=9
            ),
            "oobabooga": ServiceEndpoint(
                name="Oobabooga",
                url=os.getenv('ADVANCED_MODEL_URL', 'http://localhost:5000'),
                port=5000,
                health_path="/health",
                capabilities=["advanced", "multimodal", "complex"],
                priority=7
            ),
            "koboldcpp": ServiceEndpoint(
                name="KoboldCpp",
                url=os.getenv('CREATIVE_MODEL_URL', 'http://localhost:5001'),
                port=5001,
                health_path="/api/v1/info",
                capabilities=["creative", "writing", "roleplay", "storytelling"],
                priority=8
            ),
            
            # Platform Services
            "chat-copilot": ServiceEndpoint(
                name="Chat Copilot Backend",
                url="http://localhost:11000",
                port=11000,
                health_path="/healthz",
                capabilities=["conversation", "memory", "context"],
                priority=6
            ),
            "autogen-studio": ServiceEndpoint(
                name="AutoGen Studio",
                url="http://localhost:11001",
                port=11001,
                health_path="/",
                capabilities=["multi-agent", "collaboration", "workflow"],
                priority=9
            ),
            "magentic-one": ServiceEndpoint(
                name="Magentic-One",
                url="http://localhost:11003",
                port=11003,
                health_path="/health",
                capabilities=["orchestration", "planning", "coordination"],
                priority=9
            ),
            "perplexica": ServiceEndpoint(
                name="Perplexica",
                url="http://localhost:11020",
                port=11020,
                health_path="/",
                capabilities=["research", "search", "information"],
                priority=7
            ),
            "searxng": ServiceEndpoint(
                name="SearXNG",
                url="http://localhost:11021",
                port=11021,
                health_path="/",
                capabilities=["search", "web", "information"],
                priority=6
            ),
            
            # Infrastructure Services
            "neo4j": ServiceEndpoint(
                name="Neo4j Database",
                url="http://localhost:7474",
                port=7474,
                health_path="/",
                capabilities=["graph", "knowledge", "relationships"],
                priority=5
            ),
            "grafana": ServiceEndpoint(
                name="Grafana",
                url="http://localhost:11002",
                port=11002,
                health_path="/api/health",
                capabilities=["monitoring", "visualization", "metrics"],
                priority=4
            ),
            "prometheus": ServiceEndpoint(
                name="Prometheus",
                url="http://localhost:9090",
                port=9090,
                health_path="/-/healthy",
                capabilities=["metrics", "monitoring", "alerting"],
                priority=4
            )
        })
    
    async def health_check_service(self, session: aiohttp.ClientSession, service_name: str) -> ServiceStatus:
        """Check health of a specific service"""
        if service_name not in self.services:
            return ServiceStatus.UNKNOWN
        
        service = self.services[service_name]
        health_url = f"{service.url.rstrip('/')}{service.health_path}"
        
        try:
            async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    self.service_status[service_name] = ServiceStatus.ONLINE
                    self.last_health_check[service_name] = datetime.now()
                    return ServiceStatus.ONLINE
                else:
                    self.service_status[service_name] = ServiceStatus.ERROR
                    return ServiceStatus.ERROR
        except asyncio.TimeoutError:
            self.service_status[service_name] = ServiceStatus.OFFLINE
            return ServiceStatus.OFFLINE
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            self.service_status[service_name] = ServiceStatus.ERROR
            return ServiceStatus.ERROR
    
    async def health_check_all(self) -> Dict[str, ServiceStatus]:
        """Check health of all services"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.health_check_service(session, service_name)
                for service_name in self.services.keys()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                service_name: result if isinstance(result, ServiceStatus) else ServiceStatus.ERROR
                for service_name, result in zip(self.services.keys(), results)
            }
    
    def get_services_by_capability(self, capability: str) -> List[str]:
        """Get services that support a specific capability"""
        return [
            name for name, service in self.services.items()
            if capability.lower() in [cap.lower() for cap in service.capabilities]
            and self.service_status.get(name) == ServiceStatus.ONLINE
        ]
    
    def get_best_service_for_task(self, task_type: TaskType) -> Optional[str]:
        """Get the best service for a specific task type"""
        capability_map = {
            TaskType.REASONING: "reasoning",
            TaskType.GENERAL: "general", 
            TaskType.CODING: "coding",
            TaskType.CREATIVE: "creative",
            TaskType.RESEARCH: "research",
            TaskType.ANALYSIS: "analysis",
            TaskType.MULTIMODAL: "multimodal",
            TaskType.COLLABORATIVE: "multi-agent"
        }
        
        capability = capability_map.get(task_type, "general")
        available_services = self.get_services_by_capability(capability)
        
        if not available_services:
            # Fallback to general capability services
            available_services = self.get_services_by_capability("general")
        
        if not available_services:
            return None
        
        # Sort by priority (higher is better)
        available_services.sort(
            key=lambda x: self.services[x].priority,
            reverse=True
        )
        
        return available_services[0]

class TaskDecomposer:
    """Decomposes complex tasks into smaller, manageable subtasks"""
    
    @staticmethod
    def decompose_task(prompt: str, context: Dict[str, Any]) -> List[Task]:
        """Decompose a complex task into subtasks"""
        
        # Simple heuristic-based decomposition
        subtasks = []
        task_id_base = str(uuid.uuid4())[:8]
        
        # Check if task requires research
        if any(keyword in prompt.lower() for keyword in ["research", "find", "search", "look up", "investigate"]):
            subtasks.append(Task(
                id=f"{task_id_base}-research",
                type=TaskType.RESEARCH,
                prompt=f"Research information about: {prompt}",
                context=context,
                dependencies=[]
            ))
        
        # Check if task requires coding
        if any(keyword in prompt.lower() for keyword in ["code", "program", "script", "function", "algorithm"]):
            subtasks.append(Task(
                id=f"{task_id_base}-coding",
                type=TaskType.CODING,
                prompt=f"Generate code for: {prompt}",
                context=context,
                dependencies=[f"{task_id_base}-research"] if subtasks else []
            ))
        
        # Check if task requires reasoning/analysis
        if any(keyword in prompt.lower() for keyword in ["analyze", "reason", "solve", "calculate", "evaluate"]):
            subtasks.append(Task(
                id=f"{task_id_base}-reasoning",
                type=TaskType.REASONING,
                prompt=f"Analyze and reason about: {prompt}",
                context=context,
                dependencies=[t.id for t in subtasks] if subtasks else []
            ))
        
        # Check if task requires creative output
        if any(keyword in prompt.lower() for keyword in ["write", "create", "generate", "compose", "story"]):
            subtasks.append(Task(
                id=f"{task_id_base}-creative",
                type=TaskType.CREATIVE,
                prompt=f"Create content for: {prompt}",
                context=context,
                dependencies=[t.id for t in subtasks] if subtasks else []
            ))
        
        # If no specific subtasks identified, create a general task
        if not subtasks:
            subtasks.append(Task(
                id=f"{task_id_base}-general",
                type=TaskType.GENERAL,
                prompt=prompt,
                context=context,
                dependencies=[]
            ))
        
        # Assign services to tasks
        for task in subtasks:
            task.assigned_services = []
        
        return subtasks

class CollaborationOrchestrator:
    """Main orchestrator for multi-agent collaboration with MCP integration"""
    
    def __init__(self):
        self.registry = ServiceRegistry()
        self.decomposer = TaskDecomposer()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.collaboration_plans: Dict[str, CollaborationPlan] = {}
        self.mcp_registry = mcp_registry
    
    async def create_collaboration_plan(self, prompt: str, context: Dict[str, Any] = None, template_name: str = None) -> CollaborationPlan:
        """Create a collaboration plan for a complex task"""
        if context is None:
            context = {}
        
        # Use workflow template if specified or auto-suggest
        if template_name:
            if workflow_manager.get_template(template_name):
                subtasks = workflow_manager.create_tasks_from_template(template_name, prompt, context)
            else:
                logger.warning(f"Template '{template_name}' not found, falling back to decomposition")
                subtasks = self.decomposer.decompose_task(prompt, context)
        else:
            # Auto-suggest template based on prompt
            suggested_template = workflow_manager.suggest_template(prompt)
            logger.info(f"Auto-suggested template: {suggested_template}")
            
            try:
                subtasks = workflow_manager.create_tasks_from_template(suggested_template, prompt, context)
                context["used_template"] = suggested_template
            except Exception as e:
                logger.warning(f"Failed to use suggested template: {e}, falling back to decomposition")
                subtasks = self.decomposer.decompose_task(prompt, context)
        
        # Create collaboration plan
        plan_id = str(uuid.uuid4())
        plan = CollaborationPlan(
            id=plan_id,
            task_sequence=subtasks,
            service_allocation={},
            estimated_duration=len(subtasks) * 30,  # Rough estimate
            parallel_execution=len(subtasks) > 1
        )
        
        # Assign services to tasks
        await self.registry.health_check_all()
        
        for task in subtasks:
            best_service = self.registry.get_best_service_for_task(task.type)
            if best_service:
                task.assigned_services = [best_service]
                if best_service not in plan.service_allocation:
                    plan.service_allocation[best_service] = []
                plan.service_allocation[best_service].append(task.id)
        
        self.collaboration_plans[plan_id] = plan
        return plan
    
    async def execute_task(self, session: aiohttp.ClientSession, task: Task) -> Dict[str, Any]:
        """Execute a single task on assigned service"""
        if not task.assigned_services:
            return {"error": "No service assigned to task"}
        
        service_name = task.assigned_services[0]
        if service_name not in self.registry.services:
            return {"error": f"Service {service_name} not found"}
        
        service = self.registry.services[service_name]
        
        # Prepare payload based on service type
        if "vllm" in service_name or service_name == "oobabooga":
            # OpenAI-compatible format
            payload = {
                "messages": [{"role": "user", "content": task.prompt}],
                "max_tokens": 512,
                "temperature": 0.7
            }
            endpoint = f"{service.url}/v1/chat/completions"
        elif service_name == "koboldcpp":
            # KoboldCpp format
            payload = {
                "prompt": task.prompt,
                "max_length": 512,
                "temperature": 0.8
            }
            endpoint = f"{service.url}/api/v1/generate"
        else:
            # Generic format for other services
            payload = {
                "prompt": task.prompt,
                "context": task.context
            }
            endpoint = f"{service.url}/api/completion"
        
        try:
            async with session.post(
                endpoint,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=service.timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = result
                    return result
                else:
                    error_text = await response.text()
                    return {"error": f"Service returned {response.status}: {error_text}"}
        
        except asyncio.TimeoutError:
            return {"error": f"Timeout waiting for {service_name}"}
        except Exception as e:
            return {"error": f"Error executing task on {service_name}: {str(e)}"}
    
    async def execute_collaboration_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute a collaboration plan"""
        if plan_id not in self.collaboration_plans:
            return {"error": "Collaboration plan not found"}
        
        plan = self.collaboration_plans[plan_id]
        results = {}
        
        async with aiohttp.ClientSession() as session:
            if plan.parallel_execution:
                # Execute independent tasks in parallel
                independent_tasks = [task for task in plan.task_sequence if not task.dependencies]
                
                if independent_tasks:
                    parallel_results = await asyncio.gather(*[
                        self.execute_task(session, task) for task in independent_tasks
                    ], return_exceptions=True)
                    
                    for task, result in zip(independent_tasks, parallel_results):
                        results[task.id] = result
                        if not isinstance(result, Exception):
                            self.completed_tasks[task.id] = task
                
                # Execute dependent tasks sequentially
                dependent_tasks = [task for task in plan.task_sequence if task.dependencies]
                for task in dependent_tasks:
                    # Check if dependencies are completed
                    deps_completed = all(
                        dep_id in self.completed_tasks for dep_id in task.dependencies
                    )
                    
                    if deps_completed:
                        # Add dependency results to task context
                        for dep_id in task.dependencies:
                            if dep_id in results:
                                task.context[f"dependency_{dep_id}"] = results[dep_id]
                        
                        result = await self.execute_task(session, task)
                        results[task.id] = result
                        if "error" not in result:
                            self.completed_tasks[task.id] = task
            else:
                # Execute tasks sequentially
                for task in plan.task_sequence:
                    result = await self.execute_task(session, task)
                    results[task.id] = result
                    if "error" not in result:
                        self.completed_tasks[task.id] = task
        
        return {
            "plan_id": plan_id,
            "status": "completed",
            "results": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary of collaboration results"""
        successful_tasks = [k for k, v in results.items() if "error" not in v]
        failed_tasks = [k for k, v in results.items() if "error" in v]
        
        summary = f"Collaboration completed. {len(successful_tasks)} tasks successful"
        if failed_tasks:
            summary += f", {len(failed_tasks)} tasks failed"
        
        return summary
    
    async def simple_collaboration(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simple collaboration interface for quick tasks"""
        plan = await self.create_collaboration_plan(prompt, context or {})
        return await self.execute_collaboration_plan(plan.id)
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services including MCP servers"""
        ai_status = await self.registry.health_check_all()
        mcp_status = await self.mcp_registry.check_all_servers()
        
        return {
            "ai_services": {
                "total_services": len(self.registry.services),
                "online_services": len([s for s in ai_status.values() if s == ServiceStatus.ONLINE]),
                "offline_services": len([s for s in ai_status.values() if s == ServiceStatus.OFFLINE]),
                "services": {
                    name: {
                        "status": ai_status.get(name, ServiceStatus.UNKNOWN).value,
                        "url": service.url,
                        "capabilities": service.capabilities,
                        "priority": service.priority
                    }
                    for name, service in self.registry.services.items()
                }
            },
            "mcp_servers": {
                "total_servers": len(self.mcp_registry.servers),
                "online_servers": len([s for s in mcp_status.values() if s.get('status') == 'online']),
                "servers": mcp_status
            }
        }
    
    async def execute_mcp_task(self, server_name: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task on an MCP server"""
        try:
            # Check if server is available
            health = await self.mcp_registry.check_server_health(server_name)
            if health.get('status') != 'online':
                return {"error": f"MCP server {server_name} is not available"}
            
            # For now, handle FortiManager directly
            if server_name == 'fortimanager':
                from network_agents.fortimanager_mcp_server import FortiManagerMCPServer
                fm_server = FortiManagerMCPServer()
                await fm_server.start_session()
                try:
                    result = await fm_server.handle_mcp_request(method, params)
                    return result
                finally:
                    await fm_server.close()
            else:
                return {"error": f"MCP server {server_name} not yet supported for direct execution"}
        
        except Exception as e:
            logger.error(f"Error executing MCP task on {server_name}: {e}")
            return {"error": str(e)}
    
    async def collaborate_with_mcp(self, prompt: str, template_name: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Collaboration workflow that includes MCP server integration"""
        if context is None:
            context = {}
        
        # Get template with MCP integrations
        template = workflow_manager.get_template(template_name or workflow_manager.suggest_template(prompt))
        if not template:
            return {"error": "No suitable workflow template found"}
        
        # Check available MCP servers for template capabilities
        mcp_results = {}
        if template.mcp_integrations:
            for capability, servers in template.mcp_integrations.items():
                for server_name in servers:
                    if server_name in self.mcp_registry.servers:
                        # Check server health
                        health = await self.mcp_registry.check_server_health(server_name)
                        if health.get('status') == 'online':
                            mcp_results[f"{capability}_{server_name}"] = health
        
        # Execute regular collaboration plan
        plan = await self.create_collaboration_plan(prompt, context, template_name)
        ai_results = await self.execute_collaboration_plan(plan.id)
        
        # Combine results
        return {
            "collaboration_id": plan.id,
            "template_used": template_name,
            "ai_results": ai_results,
            "mcp_status": mcp_results,
            "mcp_integrations_available": template.mcp_integrations if template else {},
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_restaurant_network_status(self, restaurant: str = None) -> Dict[str, Any]:
        """Get restaurant network status using MCP FortiManager integration"""
        try:
            # Use FortiManager MCP server for restaurant network data
            result = await self.execute_mcp_task('fortimanager', 'get_restaurant_overview', {'restaurant': restaurant})
            
            # Also try to get Meraki data if available
            meraki_result = {}
            if 'meraki' in self.mcp_registry.servers:
                meraki_health = await self.mcp_registry.check_server_health('meraki')
                if meraki_health.get('status') == 'online':
                    # In a real implementation, this would call Meraki MCP server
                    meraki_result = {"status": "available", "note": "Meraki integration ready"}
            
            return {
                "restaurant": restaurant or "all",
                "fortinet_data": result,
                "meraki_data": meraki_result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting restaurant network status: {e}")
            return {"error": str(e)}
    
    def get_available_mcp_capabilities(self) -> Dict[str, List[str]]:
        """Get all available MCP capabilities and their servers"""
        capabilities = {}
        
        for server_name, server in self.mcp_registry.servers.items():
            for capability in server.capabilities:
                if capability not in capabilities:
                    capabilities[capability] = []
                capabilities[capability].append(server_name)
        
        return capabilities

# Global orchestrator instance
orchestrator = CollaborationOrchestrator()

async def main():
    """Test the collaboration orchestrator"""
    # Test service health
    print("Checking service health...")
    status = await orchestrator.get_service_status()
    print(json.dumps(status, indent=2))
    
    # Test simple collaboration
    print("\nTesting simple collaboration...")
    result = await orchestrator.simple_collaboration(
        "Create a Python function to calculate fibonacci numbers and explain how it works"
    )
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())