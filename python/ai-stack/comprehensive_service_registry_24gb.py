#!/usr/bin/env python3
"""
24GB VRAM Optimized Service Registry for AI Research Platform
Optimized service configurations for systems with 24GB VRAM
"""

import requests
import logging
import json
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
    api_format: str
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
    hardware_requirements: Optional[str] = None
    memory_usage: Optional[str] = None

class OptimizedServiceRegistry24GB:
    def __init__(self):
        self.hardware_config = self._load_hardware_config()
        self.services = self._initialize_optimized_services()
        self.service_status = {}
        self.performance_metrics = {}
        
    def _load_hardware_config(self) -> Dict[str, Any]:
        """Load hardware-specific configuration"""
        try:
            with open('/home/keith/chat-copilot/hardware-config-24gb.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Hardware config not found, using defaults")
            return {"gpu_config": {"total_vram": "24GB", "available_gpus": 1}}
    
    def _initialize_optimized_services(self) -> Dict[str, ServiceCapability]:
        """Initialize optimized services for 24GB VRAM systems"""
        return {
            # Optimized LLM Stack for 24GB VRAM
            'reasoning': ServiceCapability(
                name='reasoning',
                endpoint='http://localhost:8000',
                port=8000,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='vLLM DialoGPT-Small optimized for reasoning (24GB system)',
                specialties=['math', 'logic', 'analysis', 'problem-solving', 'reasoning'],
                cost_per_token=0.0008,
                performance_score=0.88,
                avg_latency=2.0,
                max_complexity='complex',
                fallback_services=['general', 'ollama'],
                health_endpoints=['/health', '/v1/models'],
                startup_command='CUDA_VISIBLE_DEVICES=0 vllm serve microsoft/DialoGPT-small --host 0.0.0.0 --port 8000 --gpu-memory-utilization 0.4 --max-model-len 1024',
                startup_directory='/home/keith/chat-copilot/python/ai-stack',
                hardware_requirements='GPU: 8-10GB VRAM',
                memory_usage='9.6GB VRAM'
            ),
            'general': ServiceCapability(
                name='general',
                endpoint='http://localhost:8001',
                port=8001,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='vLLM DistilGPT-2 for general purpose tasks (24GB optimized)',
                specialties=['conversation', 'general', 'summary', 'chat'],
                cost_per_token=0.0001,
                performance_score=0.80,
                avg_latency=1.0,
                max_complexity='moderate',
                fallback_services=['ollama'],
                health_endpoints=['/health', '/v1/models'],
                startup_command='CUDA_VISIBLE_DEVICES=0 vllm serve distilgpt2 --host 0.0.0.0 --port 8001 --gpu-memory-utilization 0.3 --max-model-len 512',
                startup_directory='/home/keith/chat-copilot/python/ai-stack',
                hardware_requirements='GPU: 5-7GB VRAM',
                memory_usage='7.2GB VRAM'
            ),
            'coding': ServiceCapability(
                name='coding',
                endpoint='http://localhost:8002',
                port=8002,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='vLLM DialoGPT-Small for coding tasks (24GB optimized)',
                specialties=['programming', 'debug', 'algorithm', 'code', 'development'],
                cost_per_token=0.0002,
                performance_score=0.85,
                avg_latency=1.5,
                max_complexity='complex',
                fallback_services=['reasoning', 'general', 'ollama'],
                health_endpoints=['/health', '/v1/models'],
                startup_command='CUDA_VISIBLE_DEVICES=0 vllm serve microsoft/DialoGPT-small --host 0.0.0.0 --port 8002 --gpu-memory-utilization 0.3 --max-model-len 1024',
                startup_directory='/home/keith/chat-copilot/python/ai-stack',
                hardware_requirements='GPU: 5-7GB VRAM',
                memory_usage='7.2GB VRAM'
            ),
            
            # CPU-based services for resource efficiency
            'creative': ServiceCapability(
                name='creative',
                endpoint='http://localhost:5001',
                port=5001,
                service_type=ServiceType.LLM,
                api_format='koboldcpp',
                description='KoboldCpp CPU-based creative writing (24GB system)',
                specialties=['story', 'creative', 'writing', 'narrative', 'roleplay'],
                cost_per_token=0.0,
                performance_score=0.70,
                avg_latency=3.0,
                max_complexity='moderate',
                fallback_services=['general', 'ollama'],
                health_endpoints=['/api/v1/info', '/'],
                startup_command='python koboldcpp.py --model models/ggml-gpt4all-j-v1.3-groovy.bin --port 5001 --threads 8',
                startup_directory='/home/keith/chat-copilot/python/ai-stack',
                hardware_requirements='CPU: 8 threads',
                memory_usage='4GB RAM'
            ),
            'advanced': ServiceCapability(
                name='advanced',
                endpoint='http://localhost:5000',
                port=5000,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='Oobabooga CPU-mode for advanced features (24GB system)',
                specialties=['multimodal', 'advanced', 'research', 'complex-reasoning'],
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=4.0,
                max_complexity='complex',
                fallback_services=['reasoning', 'general'],
                health_endpoints=['/v1/models', '/api/v1/info'],
                startup_command='python server.py --api --listen --port 5000 --cpu',
                startup_directory='/home/keith/chat-copilot/python/oobabooga',
                hardware_requirements='CPU: 8+ threads',
                memory_usage='6GB RAM'
            ),

            # AI Gateway & Routing (unchanged)
            'ai_gateway': ServiceCapability(
                name='ai_gateway',
                endpoint='http://localhost:9000',
                port=9000,
                service_type=ServiceType.API,
                api_format='rest',
                description='AI Stack Gateway with intelligent routing (24GB optimized)',
                specialties=['routing', 'load-balancing', 'orchestration'],
                cost_per_token=0.0,
                performance_score=0.95,
                avg_latency=0.1,
                max_complexity='expert',
                fallback_services=[],
                health_endpoints=['/health', '/info'],
                startup_command='python3 api_gateway.py',
                startup_directory='/home/keith/chat-copilot/python/ai-stack',
                hardware_requirements='CPU: 2 cores',
                memory_usage='512MB RAM'
            ),

            # Core Platform Services (memory-optimized)
            'chat_copilot': ServiceCapability(
                name='chat_copilot',
                endpoint='http://localhost:11000',
                port=11000,
                service_type=ServiceType.AGENT,
                api_format='custom',
                description='Microsoft Chat Copilot (24GB memory-optimized)',
                specialties=['conversation', 'semantic-kernel', 'memory', 'plugins'],
                cost_per_token=0.0005,
                performance_score=0.88,
                avg_latency=2.0,
                max_complexity='complex',
                fallback_services=['general'],
                health_endpoints=['/healthz', '/health'],
                startup_command='dotnet run --urls http://0.0.0.0:11000',
                startup_directory='/home/keith/chat-copilot/webapi',
                hardware_requirements='CPU: 4 cores',
                memory_usage='4GB RAM'
            ),
            'autogen_studio': ServiceCapability(
                name='autogen_studio',
                endpoint='http://localhost:11001',
                port=11001,
                service_type=ServiceType.AGENT,
                api_format='custom',
                description='AutoGen Studio (24GB limited agents)',
                specialties=['multi-agent', 'collaboration', 'workflow', 'automation'],
                cost_per_token=0.0008,
                performance_score=0.85,
                avg_latency=3.5,
                max_complexity='complex',
                fallback_services=['chat_copilot'],
                health_endpoints=['/health', '/api/health'],
                startup_command='autogenstudio ui --host 0.0.0.0 --port 11001 --max-agents 3',
                startup_directory='/home/keith/chat-copilot/python/autogen',
                hardware_requirements='CPU: 4 cores',
                memory_usage='2GB RAM'
            ),

            # Local LLM Services (optimized models)
            'ollama': ServiceCapability(
                name='ollama',
                endpoint='http://localhost:11434',
                port=11434,
                service_type=ServiceType.LLM,
                api_format='openai',
                description='Ollama with small models (24GB system)',
                specialties=['local-llm', 'offline', 'llama', 'small-models', 'privacy'],
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=2.0,
                max_complexity='moderate',
                fallback_services=[],
                health_endpoints=['/api/tags', '/health'],
                startup_command='ollama serve',
                systemd_service='ollama',
                hardware_requirements='CPU/GPU: 4GB memory',
                memory_usage='4GB mixed'
            ),

            # Essential Platform Services
            'port_scanner': ServiceCapability(
                name='port_scanner',
                endpoint='http://localhost:11010',
                port=11010,
                service_type=ServiceType.TOOL,
                api_format='rest',
                description='Network port scanner (lightweight)',
                specialties=['network-scan', 'port-discovery', 'security', 'reconnaissance'],
                cost_per_token=0.0,
                performance_score=0.70,
                avg_latency=0.5,
                max_complexity='simple',
                fallback_services=[],
                health_endpoints=['/health', '/status'],
                startup_command='python3 port-scanner.py --host 0.0.0.0 --port 11010',
                startup_directory='/home/keith/chat-copilot/python/tools',
                hardware_requirements='CPU: 1 core',
                memory_usage='256MB RAM'
            ),
            'webhook_server': ServiceCapability(
                name='webhook_server',
                endpoint='http://localhost:11025',
                port=11025,
                service_type=ServiceType.INFRASTRUCTURE,
                api_format='rest',
                description='Webhook server for integrations (lightweight)',
                specialties=['webhooks', 'github-integration', 'notifications'],
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=0.3,
                max_complexity='simple',
                fallback_services=[],
                health_endpoints=['/health', '/'],
                startup_command='node webhook-server.js',
                startup_directory='/home/keith/chat-copilot/runtime-data',
                hardware_requirements='CPU: 1 core',
                memory_usage='128MB RAM'
            ),

            # Docker Services (optional - resource permitting)
            'neo4j': ServiceCapability(
                name='neo4j',
                endpoint='http://localhost:7474',
                port=7474,
                service_type=ServiceType.DATABASE,
                api_format='rest',
                description='Neo4j graph database (24GB memory-limited)',
                specialties=['graph-database', 'cypher', 'relationships', 'knowledge-graph'],
                cost_per_token=0.0,
                performance_score=0.82,
                avg_latency=1.0,
                max_complexity='complex',
                fallback_services=[],
                health_endpoints=['/db/data/', '/'],
                docker_service='neo4j',
                hardware_requirements='CPU: 2 cores',
                memory_usage='2GB RAM'
            )
        }

    def get_hardware_optimized_startup_sequence(self) -> List[List[str]]:
        """Get hardware-optimized startup sequence for 24GB system"""
        return [
            # Phase 1: Essential infrastructure
            ['webhook_server', 'ai_gateway'],
            # Phase 2: Core platform services  
            ['chat_copilot', 'port_scanner'],
            # Phase 3: Primary GPU services (sequential to avoid OOM)
            ['reasoning'],
            # Phase 4: Secondary GPU services
            ['general'],
            # Phase 5: Additional GPU services if memory allows
            ['coding'],
            # Phase 6: CPU-based services
            ['ollama'],
            # Phase 7: Memory-permitting services
            ['creative', 'advanced'],
            # Phase 8: Optional services
            ['autogen_studio'],
            # Phase 9: Docker services (if resources allow)
            ['neo4j']
        ]

    def get_memory_usage_analysis(self) -> Dict[str, Any]:
        """Analyze memory usage for current service configuration"""
        gpu_usage = 0
        ram_usage = 0
        
        for service in self.services.values():
            if service.memory_usage:
                if 'VRAM' in service.memory_usage:
                    gpu_usage += float(service.memory_usage.split('GB')[0])
                elif 'RAM' in service.memory_usage:
                    ram_usage += float(service.memory_usage.split('GB')[0])
        
        return {
            "total_gpu_usage": f"{gpu_usage:.1f}GB",
            "total_ram_usage": f"{ram_usage:.1f}GB",
            "gpu_utilization": f"{(gpu_usage/24)*100:.1f}%",
            "recommended_max_gpu": "22GB",
            "safety_margin": f"{24-gpu_usage:.1f}GB VRAM free",
            "memory_efficient": gpu_usage <= 22
        }

    def get_service_priorities(self) -> Dict[str, str]:
        """Get service priority recommendations for 24GB system"""
        return {
            # High priority - core functionality
            'ai_gateway': 'critical',
            'chat_copilot': 'high',
            'reasoning': 'high',
            'general': 'high',
            
            # Medium priority - enhanced functionality
            'coding': 'medium',
            'ollama': 'medium', 
            'port_scanner': 'medium',
            
            # Low priority - optional/resource-intensive
            'creative': 'low',
            'advanced': 'low',
            'autogen_studio': 'low',
            'neo4j': 'optional'
        }

    def get_fallback_recommendations(self) -> Dict[str, List[str]]:
        """Get fallback service recommendations for resource constraints"""
        return {
            'gpu_memory_exceeded': [
                'Disable coding service',
                'Use creative on CPU only', 
                'Reduce model lengths to 256 tokens',
                'Use ollama for non-critical tasks'
            ],
            'system_memory_low': [
                'Disable autogen_studio',
                'Disable neo4j',
                'Use smaller batch sizes',
                'Reduce concurrent connections'
            ],
            'performance_issues': [
                'Use only reasoning + general services',
                'Enable CPU fallback for all services',
                'Reduce max_model_len to 512',
                'Use ollama for all non-critical tasks'
            ]
        }

    # Inherit all other methods from base comprehensive registry
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
                        "response_time": response.elapsed.total_seconds(),
                        "memory_usage": service.memory_usage,
                        "hardware_requirements": service.hardware_requirements
                    }
            except Exception as e:
                continue
        
        return {
            "status": "offline", 
            "endpoint": service.endpoint,
            "last_error": str(e) if 'e' in locals() else "Connection failed",
            "memory_usage": service.memory_usage,
            "hardware_requirements": service.hardware_requirements
        }

    def get_all_services_health(self) -> Dict[str, Any]:
        """Get health status of all services with memory analysis"""
        health_results = {}
        online_count = 0
        
        for service_name in self.services:
            health = self.check_service_health(service_name)
            health_results[service_name] = health
            if health["status"] == "online":
                online_count += 1
        
        memory_analysis = self.get_memory_usage_analysis()
        
        return {
            "services": health_results,
            "summary": {
                "total_services": len(self.services),
                "online_services": online_count,
                "offline_services": len(self.services) - online_count,
                "health_percentage": (online_count / len(self.services)) * 100
            },
            "hardware_optimization": {
                "system_profile": "24GB_VRAM_System",
                "memory_analysis": memory_analysis,
                "service_priorities": self.get_service_priorities(),
                "fallback_recommendations": self.get_fallback_recommendations()
            }
        }

    def get_startup_commands(self) -> List[Dict[str, Any]]:
        """Get startup commands optimized for 24GB system"""
        startup_commands = []
        
        for service_name, service in self.services.items():
            cmd_info = {
                "service": service_name,
                "port": service.port,
                "description": service.description,
                "hardware_requirements": service.hardware_requirements,
                "memory_usage": service.memory_usage,
                "priority": self.get_service_priorities().get(service_name, 'medium')
            }
            
            if service.startup_command:
                cmd_info.update({
                    "command": service.startup_command,
                    "directory": service.startup_directory
                })
            elif service.docker_service:
                cmd_info["docker_service"] = service.docker_service
            elif service.systemd_service:
                cmd_info["systemd_service"] = service.systemd_service
                
            startup_commands.append(cmd_info)
        
        # Sort by priority for optimal startup order
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'optional': 4}
        startup_commands.sort(key=lambda x: priority_order.get(x['priority'], 5))
        
        return startup_commands

# Global optimized service registry for 24GB systems
optimized_registry_24gb = OptimizedServiceRegistry24GB()