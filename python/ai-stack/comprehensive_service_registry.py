#!/usr/bin/env python3
"""
Comprehensive Service Registry for AI Research Platform
Complete registry of all platform services with intelligent routing capabilities
"""

import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    LLM = "llm"
    AGENT = "agent"
    SEARCH = "search"
    DATABASE = "database"
    TOOL = "tool"
    WEB_UI = "web_ui"
    API = "api"
    MONITORING = "monitoring"
    INFRASTRUCTURE = "infrastructure"
    NETWORK = "network"

class ServiceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline" 
    STARTING = "starting"
    ERROR = "error"

@dataclass
class ServiceCapability:
    name: str
    endpoint: str
    port: int
    service_type: ServiceType
    api_format: str  # 'openai', 'rest', 'custom', 'graphql', 'grpc'
    description: str
    specialties: List[str]
    cost_per_token: float
    performance_score: float
    avg_latency: float
    max_complexity: str
    fallback_services: List[str]
    health_endpoints: List[str]
    startup_command: Optional[str] = None
    startup_directory: Optional[str] = None
    docker_service: Optional[str] = None
    systemd_service: Optional[str] = None

class ComprehensiveServiceRegistry:
    def __init__(self):
        self.services = self._initialize_all_platform_services()
        self.service_status = {}
        self.performance_metrics = {}
        
    def _initialize_all_platform_services(self) -> Dict[str, ServiceCapability]:
        """Initialize complete registry of all platform services"""
        return {
            # Core LLM Stack
            'reasoning': ServiceCapability(
                name='reasoning',
                endpoint='http://localhost:8000',
                port=8000,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='vLLM DeepSeek R1 for reasoning and complex analysis',
                specialties=['math', 'logic', 'analysis', 'problem-solving', 'reasoning'],
                cost_per_token=0.001,
                performance_score=0.95,
                avg_latency=2.5,
                max_complexity='expert',
                fallback_services=['general', 'coding'],
                health_endpoints=['/health', '/v1/models'],
                startup_command='CUDA_VISIBLE_DEVICES=0 vllm serve deepseek-ai/DeepSeek-R1-Distill-Llama-8B --host 0.0.0.0 --port 8000',
                startup_directory='/home/keith/chat-copilot/python/ai-stack'
            ),
            'general': ServiceCapability(
                name='general',
                endpoint='http://localhost:8001',
                port=8001,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='vLLM Mistral Small for general purpose tasks',
                specialties=['conversation', 'general', 'summary', 'chat'],
                cost_per_token=0.0002,
                performance_score=0.85,
                avg_latency=1.2,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/health', '/v1/models'],
                startup_command='CUDA_VISIBLE_DEVICES=1 vllm serve mistralai/Mistral-7B-Instruct-v0.1 --host 0.0.0.0 --port 8001',
                startup_directory='/home/keith/chat-copilot/python/ai-stack'
            ),
            'coding': ServiceCapability(
                name='coding',
                endpoint='http://localhost:8002',
                port=8002,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='vLLM DeepSeek Coder for programming tasks',
                specialties=['programming', 'debug', 'algorithm', 'code', 'development'],
                cost_per_token=0.0003,
                performance_score=0.92,
                avg_latency=1.8,
                max_complexity='complex',
                fallback_services=['reasoning', 'general'],
                health_endpoints=['/health', '/v1/models'],
                startup_command='CUDA_VISIBLE_DEVICES=0 vllm serve deepseek-ai/deepseek-coder-6.7b-instruct --host 0.0.0.0 --port 8002',
                startup_directory='/home/keith/chat-copilot/python/ai-stack'
            ),
            'creative': ServiceCapability(
                name='creative',
                endpoint='http://localhost:5001',
                port=5001,
                service_type=ServiceType.LLM,
                api_format='koboldcpp',
                description='KoboldCpp for creative writing and roleplay',
                specialties=['story', 'creative', 'writing', 'narrative', 'roleplay'],
                cost_per_token=0.0001,
                performance_score=0.80,
                avg_latency=1.0,
                max_complexity='moderate',
                fallback_services=['general'],
                health_endpoints=['/api/v1/info', '/'],
                startup_command='python koboldcpp.py --model models/creative-model.gguf --port 5001',
                startup_directory='/home/keith/chat-copilot/python/ai-stack'
            ),
            'advanced': ServiceCapability(
                name='advanced',
                endpoint='http://localhost:5000',
                port=5000,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='Oobabooga TextGen WebUI API for advanced features',
                specialties=['multimodal', 'advanced', 'research', 'complex-reasoning'],
                cost_per_token=0.0005,
                performance_score=0.88,
                avg_latency=2.0,
                max_complexity='expert',
                fallback_services=['reasoning', 'general'],
                health_endpoints=['/v1/models', '/api/v1/info'],
                startup_command='python server.py --api --listen --port 5000',
                startup_directory='/home/keith/chat-copilot/python/oobabooga'
            ),

            # AI Gateway & Routing
            'ai_gateway': ServiceCapability(
                name='ai_gateway',
                endpoint='http://localhost:9000',
                port=9000,
                service_type=ServiceType.API,
                api_format='rest',
                description='AI Stack Gateway with intelligent routing',
                specialties=['routing', 'load-balancing', 'orchestration'],
                cost_per_token=0.0,
                performance_score=0.95,
                avg_latency=0.1,
                max_complexity='expert',
                fallback_services=[],
                health_endpoints=['/health', '/info'],
                startup_command='python3 api_gateway.py',
                startup_directory='/home/keith/chat-copilot/python/ai-stack'
            ),
            'ai_monitor': ServiceCapability(
                name='ai_monitor',
                endpoint='http://localhost:8090',
                port=8090,
                service_type=ServiceType.MONITORING,
                api_format='rest',
                description='AI Stack monitoring and metrics collection',
                specialties=['monitoring', 'metrics', 'health-checks'],
                cost_per_token=0.0,
                performance_score=0.85,
                avg_latency=0.2,
                max_complexity='simple',
                fallback_services=[],
                health_endpoints=['/health', '/metrics'],
                startup_command='python3 ai_monitor.py',
                startup_directory='/home/keith/chat-copilot/python/ai-stack'
            ),

            # Core Platform Services
            'chat_copilot': ServiceCapability(
                name='chat_copilot',
                endpoint='http://localhost:11000',
                port=11000,
                service_type=ServiceType.AGENT,
                api_format='custom',
                description='Microsoft Chat Copilot with Semantic Kernel integration',
                specialties=['conversation', 'semantic-kernel', 'memory', 'plugins'],
                cost_per_token=0.0005,
                performance_score=0.88,
                avg_latency=2.0,
                max_complexity='complex',
                fallback_services=['general'],
                health_endpoints=['/healthz', '/health'],
                startup_command='dotnet run --urls http://0.0.0.0:11000',
                startup_directory='/home/keith/chat-copilot/webapi'
            ),
            'autogen_studio': ServiceCapability(
                name='autogen_studio',
                endpoint='http://localhost:11001',
                port=11001,
                service_type=ServiceType.AGENT,
                api_format='custom',
                description='AutoGen Studio for multi-agent AI collaboration',
                specialties=['multi-agent', 'collaboration', 'workflow', 'automation'],
                cost_per_token=0.0008,
                performance_score=0.92,
                avg_latency=3.0,
                max_complexity='expert',
                fallback_services=['chat_copilot'],
                health_endpoints=['/health', '/api/health'],
                startup_command='autogenstudio ui --host 0.0.0.0 --port 11001',
                startup_directory='/home/keith/chat-copilot/python/autogen'
            ),
            'magentic_one': ServiceCapability(
                name='magentic_one',
                endpoint='http://localhost:11003',
                port=11003,
                service_type=ServiceType.AGENT,
                api_format='custom',
                description='Magentic-One orchestrator for complex multi-step workflows',
                specialties=['orchestration', 'planning', 'web-browsing', 'multi-step', 'task-planning'],
                cost_per_token=0.0007,
                performance_score=0.90,
                avg_latency=2.8,
                max_complexity='expert',
                fallback_services=['autogen_studio'],
                health_endpoints=['/health', '/status'],
                startup_command='python3 magentic_one_server.py --host 0.0.0.0 --port 11003',
                startup_directory='/home/keith/chat-copilot/python/magentic-one'
            ),

            # Search & Research Services
            'perplexica': ServiceCapability(
                name='perplexica',
                endpoint='http://localhost:11020',
                port=11020,
                service_type=ServiceType.SEARCH,
                api_format='custom',
                description='Perplexica AI-powered search with real-time results',
                specialties=['web-search', 'research', 'real-time', 'citations', 'fact-checking'],
                cost_per_token=0.0004,
                performance_score=0.86,
                avg_latency=4.0,
                max_complexity='complex',
                fallback_services=['searxng'],
                health_endpoints=['/health', '/api/health'],
                docker_service='perplexica-stack'
            ),
            'searxng': ServiceCapability(
                name='searxng',
                endpoint='http://localhost:11021',
                port=11021,
                service_type=ServiceType.SEARCH,
                api_format='rest',
                description='SearXNG privacy-focused meta search engine',
                specialties=['search', 'privacy', 'meta-search', 'aggregation'],
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=2.0,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/healthz', '/'],
                docker_service='searxng'
            ),

            # Local LLM Services  
            'ollama': ServiceCapability(
                name='ollama',
                endpoint='http://localhost:11434',
                port=11434,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='Ollama local LLM server with multiple models',
                specialties=['local-llm', 'offline', 'llama', 'mistral', 'codellama', 'privacy'],
                cost_per_token=0.0001,
                performance_score=0.78,
                avg_latency=1.5,
                max_complexity='complex',
                fallback_services=['general'],
                health_endpoints=['/api/tags', '/health'],
                startup_command='ollama serve',
                systemd_service='ollama'
            ),

            # Database Services
            'neo4j': ServiceCapability(
                name='neo4j',
                endpoint='http://localhost:7474',
                port=7474,
                service_type=ServiceType.DATABASE,
                api_format='rest',
                description='Neo4j graph database for knowledge graphs',
                specialties=['graph-database', 'cypher', 'relationships', 'knowledge-graph', 'data-modeling'],
                cost_per_token=0.0,
                performance_score=0.82,
                avg_latency=1.0,
                max_complexity='expert',
                fallback_services=[],
                health_endpoints=['/db/data/', '/'],
                docker_service='neo4j'
            ),

            # Monitoring & Dashboards
            'grafana': ServiceCapability(
                name='grafana',
                endpoint='http://localhost:11002',
                port=11002,
                service_type=ServiceType.MONITORING,
                api_format='rest',
                description='Grafana dashboards for monitoring and visualization',
                specialties=['monitoring', 'dashboards', 'visualization', 'metrics'],
                cost_per_token=0.0,
                performance_score=0.80,
                avg_latency=0.8,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/api/health', '/'],
                docker_service='grafana'
            ),
            'prometheus': ServiceCapability(
                name='prometheus',
                endpoint='http://localhost:9090',
                port=9090,
                service_type=ServiceType.MONITORING,
                api_format='rest',
                description='Prometheus metrics collection and alerting',
                specialties=['metrics', 'alerting', 'time-series', 'monitoring'],
                cost_per_token=0.0,
                performance_score=0.85,
                avg_latency=0.5,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/-/healthy', '/api/v1/status'],
                docker_service='prometheus'
            ),

            # Utility & Infrastructure Services
            'port_scanner': ServiceCapability(
                name='port_scanner',
                endpoint='http://localhost:11010',
                port=11010,
                service_type=ServiceType.TOOL,
                api_format='rest',
                description='Network port scanner for infrastructure discovery',
                specialties=['network-scan', 'port-discovery', 'security', 'reconnaissance'],
                cost_per_token=0.0,
                performance_score=0.70,
                avg_latency=0.5,
                max_complexity='simple',
                fallback_services=[],
                health_endpoints=['/health', '/status'],
                startup_command='python3 port-scanner.py --host 0.0.0.0 --port 11010',
                startup_directory='/home/keith/chat-copilot/python/tools'
            ),
            'webhook_server': ServiceCapability(
                name='webhook_server',
                endpoint='http://localhost:11025',
                port=11025,
                service_type=ServiceType.INFRASTRUCTURE,
                api_format='rest',
                description='Webhook server for GitHub and external integrations',
                specialties=['webhooks', 'github-integration', 'notifications'],
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=0.3,
                max_complexity='simple',
                fallback_services=[],
                health_endpoints=['/health', '/'],
                startup_command='node webhook-server.js',
                startup_directory='/home/keith/chat-copilot/runtime-data'
            ),

            # Workflow & Automation  
            'windmill': ServiceCapability(
                name='windmill',
                endpoint='https://localhost:11005',
                port=11005,
                service_type=ServiceType.WEB_UI,
                api_format='rest',
                description='Windmill workflow automation engine',
                specialties=['workflow', 'automation', 'scripting', 'scheduling'],
                cost_per_token=0.0,
                performance_score=0.82,
                avg_latency=1.0,
                max_complexity='complex',
                fallback_services=[],
                health_endpoints=['/api/health', '/health'],
                docker_service='windmill'
            ),

            # Restaurant Network Management
            'restaurant_network_voice': ServiceCapability(
                name='restaurant_network_voice',
                endpoint='http://localhost:11032',
                port=11032,
                service_type=ServiceType.WEB_UI,
                api_format='rest',
                description='Restaurant operations voice interface for equipment monitoring',
                specialties=['restaurant-ops', 'voice-commands', 'equipment-monitoring', 'pos-systems'],
                cost_per_token=0.0,
                performance_score=0.78,
                avg_latency=1.2,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/health', '/'],
                startup_command='python3 restaurant-equipment-voice-interface.py',
                startup_directory='/home/keith/chat-copilot/network-agents'
            ),
            'network_management_voice': ServiceCapability(
                name='network_management_voice',
                endpoint='http://localhost:11030',
                port=11030,
                service_type=ServiceType.WEB_UI,
                api_format='rest',
                description='IT & Network management voice interface',
                specialties=['network-management', 'voice-commands', 'fortimanager', 'meraki'],
                cost_per_token=0.0,
                performance_score=0.80,
                avg_latency=1.5,
                max_complexity='complex',
                fallback_services=[],
                health_endpoints=['/health', '/'],
                startup_command='python3 speech-web-interface.py',
                startup_directory='/home/keith/chat-copilot/network-agents'
            ),
            'network_hub': ServiceCapability(
                name='network_hub',
                endpoint='http://localhost:11040',
                port=11040,
                service_type=ServiceType.WEB_UI,
                api_format='rest',
                description='Main AI Network Management Hub',
                specialties=['network-overview', 'multi-vendor', 'dashboard'],
                cost_per_token=0.0,
                performance_score=0.82,
                avg_latency=1.0,
                max_complexity='complex',
                fallback_services=[],
                health_endpoints=['/health', '/'],
                startup_command='python3 network-management-hub.py',
                startup_directory='/home/keith/chat-copilot/network-agents'
            ),

            # GenAI Stack Services
            'genai_stack_bot': ServiceCapability(
                name='genai_stack_bot',
                endpoint='http://localhost:8501',
                port=8501,
                service_type=ServiceType.AGENT,
                api_format='custom',
                description='GenAI Stack support bot with knowledge graphs',
                specialties=['support', 'knowledge-graphs', 'qa', 'documentation'],
                cost_per_token=0.0003,
                performance_score=0.85,
                avg_latency=2.0,
                max_complexity='complex',
                fallback_services=['chat_copilot'],
                health_endpoints=['/health', '/'],
                docker_service='genai-stack'
            ),
            'genai_stack_loader': ServiceCapability(
                name='genai_stack_loader',
                endpoint='http://localhost:8502',
                port=8502,
                service_type=ServiceType.TOOL,
                api_format='rest',
                description='GenAI Stack document loader',
                specialties=['document-loading', 'data-ingestion', 'knowledge-graphs'],
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=3.0,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/health', '/'],
                docker_service='genai-stack'
            )
        }

    def get_service_by_type(self, service_type: ServiceType) -> List[ServiceCapability]:
        """Get all services of a specific type"""
        return [service for service in self.services.values() 
                if service.service_type == service_type]

    def get_services_by_specialty(self, specialty: str) -> List[ServiceCapability]:
        """Get services that have a specific specialty"""
        return [service for service in self.services.values() 
                if specialty.lower() in [s.lower() for s in service.specialties]]

    def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        if service_name not in self.services:
            return {"status": "unknown", "error": "Service not found"}
        
        service = self.services[service_name]
        
        for health_endpoint in service.health_endpoints:
            try:
                url = f"{service.endpoint}{health_endpoint}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return {
                        "status": "online",
                        "endpoint": url,
                        "response_time": response.elapsed.total_seconds()
                    }
            except Exception as e:
                continue
        
        return {
            "status": "offline", 
            "endpoint": service.endpoint,
            "last_error": str(e) if 'e' in locals() else "Connection failed"
        }

    def get_all_services_health(self) -> Dict[str, Any]:
        """Get health status of all services"""
        health_results = {}
        online_count = 0
        
        for service_name in self.services:
            health = self.check_service_health(service_name)
            health_results[service_name] = health
            if health["status"] == "online":
                online_count += 1
        
        return {
            "services": health_results,
            "summary": {
                "total_services": len(self.services),
                "online_services": online_count,
                "offline_services": len(self.services) - online_count,
                "health_percentage": (online_count / len(self.services)) * 100
            }
        }

    def get_optimal_service_for_task(self, task_description: str, 
                                   preferred_types: List[ServiceType] = None) -> Tuple[str, Dict[str, Any]]:
        """Get optimal service for a given task"""
        task_lower = task_description.lower()
        
        # Score services based on task description
        service_scores = {}
        
        for service_name, service in self.services.items():
            score = 0.0
            
            # Type preference
            if preferred_types and service.service_type in preferred_types:
                score += 0.3
            
            # Specialty matching
            specialty_matches = sum(1 for specialty in service.specialties 
                                  if specialty.lower() in task_lower)
            score += specialty_matches * 0.4
            
            # Performance and latency
            score += service.performance_score * 0.2
            score += max(0, (3.0 - service.avg_latency) * 0.05)
            
            # Check if service is online
            health = self.check_service_health(service_name)
            if health["status"] == "online":
                score += 0.1
            else:
                score -= 0.5  # Heavy penalty for offline services
            
            service_scores[service_name] = score
        
        # Select best service
        best_service = max(service_scores, key=service_scores.get) if service_scores else None
        
        routing_info = {
            "task_description": task_description,
            "service_scores": service_scores,
            "selected_service": best_service,
            "service_details": self.services[best_service].__dict__ if best_service else None,
            "reasoning": f"Selected {best_service} based on specialty matching and availability"
        }
        
        return best_service, routing_info

    def get_startup_commands(self) -> List[Dict[str, Any]]:
        """Get startup commands for all services"""
        startup_commands = []
        
        for service_name, service in self.services.items():
            if service.startup_command:
                startup_commands.append({
                    "service": service_name,
                    "command": service.startup_command,
                    "directory": service.startup_directory,
                    "port": service.port,
                    "description": service.description
                })
            elif service.docker_service:
                startup_commands.append({
                    "service": service_name, 
                    "docker_service": service.docker_service,
                    "port": service.port,
                    "description": service.description
                })
            elif service.systemd_service:
                startup_commands.append({
                    "service": service_name,
                    "systemd_service": service.systemd_service,
                    "port": service.port,
                    "description": service.description
                })
        
        return startup_commands

    def get_service_analytics(self) -> Dict[str, Any]:
        """Get comprehensive service analytics"""
        service_types_count = {}
        for service in self.services.values():
            service_type = service.service_type.value
            service_types_count[service_type] = service_types_count.get(service_type, 0) + 1
        
        return {
            "total_services": len(self.services),
            "service_types": service_types_count,
            "services_by_port": {service.port: service.name for service in self.services.values()},
            "llm_services": len(self.get_service_by_type(ServiceType.LLM)),
            "agent_services": len(self.get_service_by_type(ServiceType.AGENT)),
            "search_services": len(self.get_service_by_type(ServiceType.SEARCH)),
            "monitoring_services": len(self.get_service_by_type(ServiceType.MONITORING)),
            "performance_metrics": self.performance_metrics
        }

# Global comprehensive service registry
comprehensive_registry = ComprehensiveServiceRegistry()