#!/usr/bin/env python3
"""
Platform-Aware LLM Router for AI Research Platform
Routes requests to ALL services across the entire platform including:
- vLLM AI Stack (ports 8000-8002, 5001)
- Chat Copilot (port 11000) 
- AutoGen Studio (port 11001)
- Magentic-One (port 11003)
- Perplexica (port 11020)
- SearXNG (port 11021)  
- Ollama (port 11434)
- Neo4j (port 7474)
- Port Scanner (port 11010)
- And more platform services
"""

import re
import time
import hashlib
import requests
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from comprehensive_service_registry import comprehensive_registry, ServiceType

logger = logging.getLogger(__name__)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    class SimpleNumPy:
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0.0
    np = SimpleNumPy()

class TaskType(Enum):
    # Core LLM Tasks
    REASONING = "reasoning"
    GENERAL = "general" 
    CODING = "coding"
    CREATIVE = "creative"
    
    # Platform-Specific Tasks
    COLLABORATION = "collaboration"
    RESEARCH = "research"
    SEARCH = "search"
    GRAPH_QUERY = "graph_query"
    NETWORK_SCAN = "network_scan"
    MULTI_AGENT = "multi_agent"
    LOCAL_LLM = "local_llm"
    WORKFLOW = "workflow"

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate" 
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class ServiceCapability:
    name: str
    endpoint: str
    port: int
    cost_per_token: float
    performance_score: float
    avg_latency: float
    specialties: List[str]
    max_complexity: ComplexityLevel
    fallback_services: List[str]
    service_type: str  # 'llm', 'search', 'database', 'agent', 'tool'
    api_format: str    # 'openai', 'custom', 'rest', 'graphql'
    description: str

class PlatformAwareRouter:
    def __init__(self):
        self.services = self._initialize_all_services()
        self.comprehensive_registry = comprehensive_registry
        self.routing_cache = {}
        self.performance_metrics = {}
        
    def _initialize_all_services(self) -> Dict[str, ServiceCapability]:
        return {
            # Core LLM Stack
            'reasoning': ServiceCapability(
                name='reasoning',
                endpoint='http://localhost:8000',
                port=8000,
                cost_per_token=0.001,
                performance_score=0.95,
                avg_latency=2.5,
                specialties=['math', 'logic', 'analysis', 'problem-solving'],
                max_complexity=ComplexityLevel.EXPERT,
                fallback_services=['general'],
                service_type='llm',
                api_format='openai',
                description='vLLM GPT-2 for reasoning and mathematical tasks'
            ),
            'general': ServiceCapability(
                name='general',
                endpoint='http://localhost:8001',
                port=8001,
                cost_per_token=0.0002,
                performance_score=0.85,
                avg_latency=1.2,
                specialties=['conversation', 'general', 'summary'],
                max_complexity=ComplexityLevel.MODERATE,
                fallback_services=[],
                service_type='llm',
                api_format='openai',
                description='vLLM DistilGPT-2 for general conversations'
            ),
            'coding': ServiceCapability(
                name='coding',
                endpoint='http://localhost:8002',
                port=8002,
                cost_per_token=0.0003,
                performance_score=0.92,
                avg_latency=1.8,
                specialties=['programming', 'debug', 'algorithm', 'code'],
                max_complexity=ComplexityLevel.COMPLEX,
                fallback_services=['reasoning', 'general'],
                service_type='llm',
                api_format='openai',
                description='vLLM DialoGPT-Small for coding tasks'
            ),
            'creative': ServiceCapability(
                name='creative',
                endpoint='http://localhost:5001',
                port=5001,
                cost_per_token=0.0001,
                performance_score=0.80,
                avg_latency=1.0,
                specialties=['story', 'creative', 'writing', 'narrative'],
                max_complexity=ComplexityLevel.MODERATE,
                fallback_services=['general'],
                service_type='llm',
                api_format='openai',
                description='vLLM DistilGPT-2 for creative writing'
            ),
            
            # Platform AI Services
            'chat_copilot': ServiceCapability(
                name='chat_copilot',
                endpoint='http://localhost:11000',
                port=11000,
                cost_per_token=0.0005,
                performance_score=0.88,
                avg_latency=2.0,
                specialties=['conversation', 'semantic-kernel', 'memory', 'plugins'],
                max_complexity=ComplexityLevel.COMPLEX,
                fallback_services=['general'],
                service_type='agent',
                api_format='custom',
                description='Microsoft Chat Copilot with Semantic Kernel'
            ),
            'autogen_studio': ServiceCapability(
                name='autogen_studio',
                endpoint='http://localhost:11001',
                port=11001,
                cost_per_token=0.0008,
                performance_score=0.92,
                avg_latency=3.0,
                specialties=['multi-agent', 'collaboration', 'workflow', 'automation'],
                max_complexity=ComplexityLevel.EXPERT,
                fallback_services=['chat_copilot'],
                service_type='agent',
                api_format='custom',
                description='AutoGen Studio for multi-agent AI collaboration'
            ),
            'magentic_one': ServiceCapability(
                name='magentic_one',
                endpoint='http://localhost:11003',
                port=11003,
                cost_per_token=0.0007,
                performance_score=0.90,
                avg_latency=2.8,
                specialties=['orchestration', 'planning', 'web-browsing', 'multi-step'],
                max_complexity=ComplexityLevel.EXPERT,
                fallback_services=['autogen_studio'],
                service_type='agent',
                api_format='custom',
                description='Magentic-One orchestrator for complex workflows'
            ),
            'ollama': ServiceCapability(
                name='ollama',
                endpoint='http://localhost:11434',
                port=11434,
                cost_per_token=0.0001,
                performance_score=0.78,
                avg_latency=1.5,
                specialties=['local-llm', 'offline', 'llama', 'mistral', 'codellama'],
                max_complexity=ComplexityLevel.COMPLEX,
                fallback_services=['general'],
                service_type='llm',
                api_format='openai',
                description='Ollama local LLM server with multiple models'
            ),
            
            # Search & Research Services
            'perplexica': ServiceCapability(
                name='perplexica',
                endpoint='http://localhost:11020',
                port=11020,
                cost_per_token=0.0004,
                performance_score=0.86,
                avg_latency=4.0,
                specialties=['web-search', 'research', 'real-time', 'citations'],
                max_complexity=ComplexityLevel.COMPLEX,
                fallback_services=['searxng'],
                service_type='search',
                api_format='custom',
                description='Perplexica AI-powered search with real-time results'
            ),
            'searxng': ServiceCapability(
                name='searxng',
                endpoint='http://localhost:11021',
                port=11021,
                cost_per_token=0.0,
                performance_score=0.75,
                avg_latency=2.0,
                specialties=['search', 'privacy', 'meta-search', 'aggregation'],
                max_complexity=ComplexityLevel.MODERATE,
                fallback_services=[],
                service_type='search',
                api_format='rest',
                description='SearXNG privacy-focused meta search engine'
            ),
            
            # Database & Graph Services
            'neo4j': ServiceCapability(
                name='neo4j',
                endpoint='http://localhost:7474',
                port=7474,
                cost_per_token=0.0,
                performance_score=0.82,
                avg_latency=1.0,
                specialties=['graph-database', 'cypher', 'relationships', 'knowledge-graph'],
                max_complexity=ComplexityLevel.EXPERT,
                fallback_services=[],
                service_type='database',
                api_format='rest',
                description='Neo4j graph database for knowledge graphs'
            ),
            
            # Utility Services
            'port_scanner': ServiceCapability(
                name='port_scanner',
                endpoint='http://localhost:11010',
                port=11010,
                cost_per_token=0.0,
                performance_score=0.70,
                avg_latency=0.5,
                specialties=['network-scan', 'port-discovery', 'security', 'reconnaissance'],
                max_complexity=ComplexityLevel.SIMPLE,
                fallback_services=[],
                service_type='tool',
                api_format='rest',
                description='Network port scanner for infrastructure discovery'
            ),
        }
    
    def analyze_complexity(self, prompt: str) -> ComplexityLevel:
        """Analyze prompt complexity using multiple indicators"""
        prompt_lower = prompt.lower()
        
        # Expert-level indicators
        expert_patterns = [
            r'\b(theorem|proof|lemma|corollary)\b',
            r'\b(quantum|cryptography|optimization|complexity theory)\b',
            r'\b(differential equations|linear algebra|calculus)\b',
            r'[∑∫∂∆∇]',
            r'\b(algorithm analysis|big o|asymptotic)\b',
            r'\b(multi-agent|orchestrate|workflow|automation)\b'
        ]
        expert_score = sum(1 for pattern in expert_patterns 
                         if re.search(pattern, prompt_lower))
        
        # Complex-level indicators  
        complex_patterns = [
            r'\b(implement|architecture|design pattern|optimization)\b',
            r'\b(analysis|synthesis|evaluate|compare)\b',
            r'\b(machine learning|neural network|data structure)\b',
            r'\b(database design|system architecture)\b',
            r'\b(search|research|investigate|explore)\b',
            r'\b(graph|cypher|relationship|network)\b'
        ]
        complex_score = sum(1 for pattern in complex_patterns 
                          if re.search(pattern, prompt_lower))
        
        if expert_score >= 2 or ('∫' in prompt and 'solve' in prompt_lower):
            return ComplexityLevel.EXPERT
        elif expert_score >= 1 or complex_score >= 2:
            return ComplexityLevel.COMPLEX  
        elif complex_score >= 1:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE
    
    def classify_task_type(self, prompt: str) -> TaskType:
        """Enhanced task classification for all platform services"""
        prompt_lower = prompt.lower()
        
        # Multi-agent/Collaboration indicators
        if any(word in prompt_lower for word in ['multi-agent', 'collaborate', 'workflow', 'orchestrate', 'automate', 'plan']):
            if any(word in prompt_lower for word in ['complex', 'multi-step', 'orchestrate']):
                return TaskType.MULTI_AGENT
            return TaskType.COLLABORATION
        
        # Search/Research indicators
        if any(word in prompt_lower for word in ['search', 'find', 'research', 'look up', 'investigate', 'explore']):
            if any(word in prompt_lower for word in ['web', 'internet', 'recent', 'current', 'latest']):
                return TaskType.RESEARCH
            return TaskType.SEARCH
        
        # Graph/Database indicators
        if any(word in prompt_lower for word in ['graph', 'cypher', 'neo4j', 'relationship', 'node', 'edge']):
            return TaskType.GRAPH_QUERY
        
        # Network/Security indicators
        if any(word in prompt_lower for word in ['scan', 'port', 'network', 'ip', 'security']):
            return TaskType.NETWORK_SCAN
        
        # Local LLM indicators
        if any(word in prompt_lower for word in ['local', 'offline', 'private', 'llama', 'mistral']):
            return TaskType.LOCAL_LLM
        
        # Core LLM task classification
        reasoning_patterns = ['solve', 'calculate', 'prove', 'analyze', 'logic', 'theorem']
        if sum(1 for pattern in reasoning_patterns if pattern in prompt_lower) >= 2:
            return TaskType.REASONING
        
        coding_patterns = ['code', 'function', 'class', 'python', 'javascript', 'programming']
        if sum(1 for pattern in coding_patterns if pattern in prompt_lower) >= 1:
            return TaskType.CODING
        
        creative_patterns = ['story', 'poem', 'creative', 'write', 'narrative', 'character']
        if sum(1 for pattern in creative_patterns if pattern in prompt_lower) >= 1:
            return TaskType.CREATIVE
        
        return TaskType.GENERAL
    
    def calculate_routing_score(self, service: ServiceCapability, task_type: TaskType, 
                              complexity: ComplexityLevel, budget_factor: float = 1.0) -> float:
        """Calculate routing score for service selection"""
        score = 0.0
        
        # Base performance score
        score += service.performance_score * 0.4
        
        # Task type matching (highest priority)
        task_specialty_mapping = {
            TaskType.REASONING: ['math', 'logic', 'analysis', 'problem-solving'],
            TaskType.CODING: ['programming', 'debug', 'algorithm', 'code'],
            TaskType.CREATIVE: ['story', 'creative', 'writing', 'narrative'],
            TaskType.COLLABORATION: ['multi-agent', 'collaboration', 'workflow'],
            TaskType.RESEARCH: ['web-search', 'research', 'real-time'],
            TaskType.SEARCH: ['search', 'meta-search', 'aggregation'],
            TaskType.GRAPH_QUERY: ['graph-database', 'cypher', 'relationships'],
            TaskType.NETWORK_SCAN: ['network-scan', 'port-discovery', 'security'],
            TaskType.MULTI_AGENT: ['multi-agent', 'orchestration', 'planning'],
            TaskType.LOCAL_LLM: ['local-llm', 'offline', 'llama']
        }
        
        expected_specialties = task_specialty_mapping.get(task_type, [])
        specialty_match = len(set(expected_specialties) & set(service.specialties))
        
        if specialty_match > 0:
            score += specialty_match * 0.3  # Strong bonus for specialty matching
        
        # Service type appropriateness
        service_type_scores = {
            'llm': {TaskType.REASONING: 0.2, TaskType.CODING: 0.2, TaskType.CREATIVE: 0.2, TaskType.GENERAL: 0.2},
            'agent': {TaskType.COLLABORATION: 0.3, TaskType.MULTI_AGENT: 0.3, TaskType.WORKFLOW: 0.2},
            'search': {TaskType.RESEARCH: 0.3, TaskType.SEARCH: 0.3},
            'database': {TaskType.GRAPH_QUERY: 0.3},
            'tool': {TaskType.NETWORK_SCAN: 0.3}
        }
        
        type_bonus = service_type_scores.get(service.service_type, {}).get(task_type, 0)
        score += type_bonus
        
        # Complexity handling
        complexity_levels = [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE, 
                           ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT]
        
        model_complexity_index = complexity_levels.index(service.max_complexity)
        required_complexity_index = complexity_levels.index(complexity)
        
        if model_complexity_index >= required_complexity_index:
            if complexity == ComplexityLevel.EXPERT and model_complexity_index == 3:
                score += 0.25
            else:
                score += 0.15
        else:
            score -= 0.4  # Penalty for insufficient capability
            
        # Cost consideration
        if complexity == ComplexityLevel.SIMPLE and service.cost_per_token < 0.0003:
            score += 0.1
        
        # Latency factor
        latency_bonus = max(0, (3.0 - service.avg_latency) * 0.02)
        score += latency_bonus
        
        return max(0.0, score)
    
    def get_optimal_service(self, prompt: str, task_type: Optional[TaskType] = None, 
                           budget_factor: float = 1.0) -> Tuple[str, Dict[str, Any]]:
        """Get optimal service for the given prompt and constraints"""
        
        if not task_type:
            task_type = self.classify_task_type(prompt)
        
        complexity = self.analyze_complexity(prompt)
        
        # Calculate scores for all services
        service_scores = {}
        for service_name, service_config in self.services.items():
            score = self.calculate_routing_score(
                service_config, task_type, complexity, budget_factor
            )
            service_scores[service_name] = score
        
        # Select best service
        best_service = max(service_scores, key=service_scores.get)
        
        # Routing metadata
        routing_info = {
            'detected_task_type': task_type.value if hasattr(task_type, 'value') else str(task_type),
            'detected_complexity': complexity.value,
            'service_scores': service_scores,
            'selected_service': best_service,
            'service_details': {
                'endpoint': self.services[best_service].endpoint,
                'port': self.services[best_service].port,
                'service_type': self.services[best_service].service_type,
                'api_format': self.services[best_service].api_format,
                'description': self.services[best_service].description
            },
            'routing_reason': self._get_routing_reason(best_service, task_type, complexity),
            'estimated_cost': self.services[best_service].cost_per_token,
            'estimated_latency': self.services[best_service].avg_latency,
            'fallback_services': self.services[best_service].fallback_services
        }
        
        return best_service, routing_info
    
    def _get_routing_reason(self, service: str, task_type: TaskType, complexity: ComplexityLevel) -> str:
        """Generate human-readable routing explanation"""
        service_config = self.services[service]
        
        reasons = []
        
        # Check specialties
        task_keywords = {
            TaskType.REASONING: ['math', 'logic', 'analysis'],
            TaskType.CODING: ['programming', 'code'],
            TaskType.CREATIVE: ['creative', 'writing'],
            TaskType.COLLABORATION: ['multi-agent', 'collaboration'],
            TaskType.RESEARCH: ['search', 'research'],
            TaskType.GRAPH_QUERY: ['graph', 'database'],
            TaskType.NETWORK_SCAN: ['network', 'security']
        }
        
        expected_specialties = task_keywords.get(task_type, [])
        if any(spec in service_config.specialties for spec in expected_specialties):
            reasons.append(f"specialized in {task_type.value}")
        
        if complexity == ComplexityLevel.EXPERT and service_config.max_complexity == ComplexityLevel.EXPERT:
            reasons.append("handles expert-level complexity")
        
        if service_config.service_type == 'agent' and task_type in [TaskType.COLLABORATION, TaskType.MULTI_AGENT]:
            reasons.append("AI agent capabilities")
            
        if service_config.cost_per_token == 0.0:
            reasons.append("free service")
        elif service_config.cost_per_token < 0.0003:
            reasons.append("cost-efficient")
            
        return f"Selected {service} because it's " + " and ".join(reasons) if reasons else f"best overall match"
    
    def get_service_health(self) -> Dict[str, Any]:
        """Check health of all platform services using comprehensive registry"""
        return self.comprehensive_registry.get_all_services_health()
    
    def get_service_by_capability(self, capability: str) -> List[str]:
        """Get services by specific capability using comprehensive registry"""
        matching_services = self.comprehensive_registry.get_services_by_specialty(capability)
        return [service.name for service in matching_services]
    
    def get_services_by_type(self, service_type: str) -> List[str]:
        """Get services by type using comprehensive registry"""
        try:
            svc_type = ServiceType(service_type)
            matching_services = self.comprehensive_registry.get_service_by_type(svc_type)
            return [service.name for service in matching_services]
        except ValueError:
            return []
    
    def get_startup_commands(self) -> List[Dict[str, Any]]:
        """Get startup commands for all services"""
        return self.comprehensive_registry.get_startup_commands()
    
    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics from service registry"""
        registry_analytics = self.comprehensive_registry.get_service_analytics()
        platform_analytics = self.get_analytics()
        
        return {
            **registry_analytics,
            "platform_routing": platform_analytics,
            "total_registered_services": len(self.comprehensive_registry.services),
            "routing_enabled_services": len(self.services)
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive platform routing analytics"""
        return {
            'total_services': len(self.services),
            'service_types': {
                service_type: len([s for s in self.services.values() if s.service_type == service_type])
                for service_type in set(s.service_type for s in self.services.values())
            },
            'performance_metrics': self.performance_metrics,
            'cache_size': len(self.routing_cache),
            'service_capabilities': {
                name: {
                    'endpoint': config.endpoint,
                    'port': config.port,
                    'cost_per_token': config.cost_per_token,
                    'performance_score': config.performance_score,
                    'avg_latency': config.avg_latency,
                    'specialties': config.specialties,
                    'max_complexity': config.max_complexity.value,
                    'service_type': config.service_type,
                    'api_format': config.api_format,
                    'description': config.description
                } for name, config in self.services.items()
            }
        }

# Global platform-aware router instance
platform_router = PlatformAwareRouter()