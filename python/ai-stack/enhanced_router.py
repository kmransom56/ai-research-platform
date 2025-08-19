#!/usr/bin/env python3
"""
Enhanced LLM Router for AI Platform
Upgrades existing api_gateway.py with intelligent routing capabilities
Integrates RouteLLM concepts with current architecture
"""

import re
import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # Simple numpy replacement for basic functions
    class SimpleNumPy:
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0.0
    np = SimpleNumPy()

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate" 
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class ModelCapability:
    name: str
    cost_per_token: float
    performance_score: float
    avg_latency: float
    specialties: List[str]
    max_complexity: ComplexityLevel
    fallback_models: List[str]

class IntelligentRouter:
    def __init__(self):
        self.models = {
            'reasoning': ModelCapability(
                name='reasoning',
                cost_per_token=0.001,
                performance_score=0.95,
                avg_latency=2.5,
                specialties=['math', 'logic', 'analysis', 'problem-solving'],
                max_complexity=ComplexityLevel.EXPERT,
                fallback_models=['general']
            ),
            'coding': ModelCapability(
                name='coding',
                cost_per_token=0.0003,
                performance_score=0.92,
                avg_latency=1.8,
                specialties=['programming', 'debug', 'algorithm', 'code'],
                max_complexity=ComplexityLevel.COMPLEX,
                fallback_models=['reasoning', 'general']
            ),
            'general': ModelCapability(
                name='general',
                cost_per_token=0.0002,
                performance_score=0.85,
                avg_latency=1.2,
                specialties=['conversation', 'general', 'summary'],
                max_complexity=ComplexityLevel.MODERATE,
                fallback_models=[]
            ),
            'creative': ModelCapability(
                name='creative',
                cost_per_token=0.0001,
                performance_score=0.80,
                avg_latency=1.0,
                specialties=['story', 'creative', 'writing', 'narrative'],
                max_complexity=ComplexityLevel.MODERATE,
                fallback_models=['general']
            ),
            'advanced': ModelCapability(
                name='advanced',
                cost_per_token=0.0005,
                performance_score=0.88,
                avg_latency=2.0,
                specialties=['multimodal', 'advanced', 'research'],
                max_complexity=ComplexityLevel.COMPLEX,
                fallback_models=['reasoning', 'general']
            )
        }
        
        self.routing_cache = {}
        self.performance_metrics = {}
        
    def analyze_complexity(self, prompt: str) -> ComplexityLevel:
        """Analyze prompt complexity using multiple indicators"""
        
        prompt_lower = prompt.lower()
        
        # Length factor (longer prompts often more complex)
        length_score = min(len(prompt) / 800, 1.0)
        
        # Expert-level indicators
        expert_patterns = [
            r'\b(theorem|proof|lemma|corollary)\b',
            r'\b(quantum|cryptography|optimization|complexity theory)\b',
            r'\b(differential equations|linear algebra|calculus)\b',
            r'[∑∫∂∆∇]',  # Mathematical symbols
            r'\b(algorithm analysis|big o|asymptotic)\b'
        ]
        expert_score = sum(1 for pattern in expert_patterns 
                         if re.search(pattern, prompt_lower))
        
        # Complex-level indicators  
        complex_patterns = [
            r'\b(implement|architecture|design pattern|optimization)\b',
            r'\b(analysis|synthesis|evaluate|compare)\b',
            r'\b(machine learning|neural network|data structure)\b',
            r'\b(database design|system architecture)\b'
        ]
        complex_score = sum(1 for pattern in complex_patterns 
                          if re.search(pattern, prompt_lower))
        
        # Technical indicators
        technical_patterns = [
            r'\b(function|class|method|variable)\b',
            r'\b(calculate|solve|determine|find)\b',
            r'\b(algorithm|programming|debug)\b'
        ]
        technical_score = sum(1 for pattern in technical_patterns 
                            if re.search(pattern, prompt_lower))
        
        # Code blocks or structured content
        structure_score = 0
        if '```' in prompt or prompt.count('\n') > 10:
            structure_score = 1
        
        # Multiple questions or steps
        question_score = min(prompt.count('?') + prompt.count('step') * 0.5, 2)
        
        # Determine complexity level
        if expert_score >= 2 or ('∫' in prompt and 'solve' in prompt_lower):
            return ComplexityLevel.EXPERT
        elif expert_score >= 1 or complex_score >= 2:
            return ComplexityLevel.COMPLEX  
        elif complex_score >= 1 or technical_score >= 2 or structure_score >= 1:
            return ComplexityLevel.MODERATE
        elif technical_score >= 1 or question_score >= 1 or length_score > 0.3:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE
    
    def classify_task_type(self, prompt: str) -> str:
        """Enhanced task classification with better pattern matching"""
        
        prompt_lower = prompt.lower()
        
        # Scoring system for each task type
        scores = {
            'reasoning': 0,
            'coding': 0,
            'creative': 0,
            'advanced': 0,
            'general': 0
        }
        
        # Reasoning indicators
        reasoning_patterns = [
            'solve', 'calculate', 'prove', 'analyze', 'logic', 'theorem',
            'equation', 'mathematical', 'reasoning', 'deduce', 'infer'
        ]
        scores['reasoning'] = sum(1 for pattern in reasoning_patterns if pattern in prompt_lower)
        
        # Coding indicators
        coding_patterns = [
            'code', 'function', 'class', 'python', 'javascript', 'programming',
            'debug', 'algorithm', 'implementation', 'syntax', 'compile'
        ]
        scores['coding'] = sum(1 for pattern in coding_patterns if pattern in prompt_lower)
        
        # Creative indicators
        creative_patterns = [
            'story', 'poem', 'creative', 'write', 'narrative', 'character',
            'plot', 'fiction', 'imagine', 'describe'
        ]
        scores['creative'] = sum(1 for pattern in creative_patterns if pattern in prompt_lower)
        
        # Advanced/research indicators
        advanced_patterns = [
            'research', 'academic', 'paper', 'study', 'analysis', 'review',
            'synthesis', 'comparison', 'evaluation', 'methodology'
        ]
        scores['advanced'] = sum(1 for pattern in advanced_patterns if pattern in prompt_lower)
        
        # Find the highest scoring task type
        max_score = max(scores.values())
        if max_score == 0:
            return 'general'
            
        # Return the task type with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def calculate_routing_score(self, model: ModelCapability, task_type: str, 
                              complexity: ComplexityLevel, budget_factor: float = 1.0) -> float:
        """Calculate routing score for model selection"""
        
        score = 0.0
        
        # Base performance score (higher weight)
        score += model.performance_score * 0.5
        
        # Specialty matching (highest priority)
        if task_type in model.specialties:
            score += 0.4  # Strong bonus for specialization
        elif any(spec in task_type for spec in model.specialties):
            score += 0.2
            
        # Complexity handling (critical factor)
        complexity_levels = [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE, 
                           ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT]
        
        model_complexity_index = complexity_levels.index(model.max_complexity)
        required_complexity_index = complexity_levels.index(complexity)
        
        if model_complexity_index >= required_complexity_index:
            # Bonus for meeting complexity requirements
            if complexity == ComplexityLevel.EXPERT and model_complexity_index == 3:
                score += 0.3  # Strong bonus for expert tasks
            elif complexity == ComplexityLevel.COMPLEX and model_complexity_index >= 2:
                score += 0.25
            else:
                score += 0.15
        else:
            score -= 0.5  # Heavy penalty for insufficient capability
            
        # Cost factor (balanced approach)
        if complexity == ComplexityLevel.SIMPLE and model.cost_per_token < 0.0003:
            score += 0.1  # Bonus for cheap models on simple tasks
        elif complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT]:
            # Don't penalize expensive models for complex tasks
            pass
        else:
            # Slight cost consideration for moderate tasks
            cost_penalty = (model.cost_per_token - 0.0002) * 100
            score -= cost_penalty * 0.05
        
        # Latency factor (minor consideration)
        latency_bonus = max(0, (2.0 - model.avg_latency) * 0.02)
        score += latency_bonus
        
        return max(0.0, score)
    
    def get_optimal_model(self, prompt: str, task_type: Optional[str] = None, 
                         budget_factor: float = 1.0) -> Tuple[str, Dict[str, Any]]:
        """Get optimal model for the given prompt and constraints"""
        
        # Auto-classify if task_type not provided
        if not task_type:
            task_type = self.classify_task_type(prompt)
        
        # Analyze complexity
        complexity = self.analyze_complexity(prompt)
        
        # Calculate scores for all models
        model_scores = {}
        for model_name, model_config in self.models.items():
            score = self.calculate_routing_score(
                model_config, task_type, complexity, budget_factor
            )
            model_scores[model_name] = score
        
        # Select best model
        best_model = max(model_scores, key=model_scores.get)
        
        # Routing metadata
        routing_info = {
            'original_task_type': task_type,
            'detected_complexity': complexity.value,
            'model_scores': model_scores,
            'selected_model': best_model,
            'routing_reason': self._get_routing_reason(best_model, task_type, complexity),
            'estimated_cost': self.models[best_model].cost_per_token,
            'estimated_latency': self.models[best_model].avg_latency,
            'fallback_models': self.models[best_model].fallback_models
        }
        
        return best_model, routing_info
    
    def _get_routing_reason(self, model: str, task_type: str, complexity: ComplexityLevel) -> str:
        """Generate human-readable routing explanation"""
        model_config = self.models[model]
        
        reasons = []
        
        if task_type in model_config.specialties:
            reasons.append(f"specialized in {task_type}")
        
        if complexity == ComplexityLevel.EXPERT and model_config.max_complexity == ComplexityLevel.EXPERT:
            reasons.append("handles expert-level complexity")
        elif complexity == ComplexityLevel.SIMPLE and model_config.cost_per_token < 0.0003:
            reasons.append("cost-efficient for simple tasks")
            
        if model_config.avg_latency < 1.5:
            reasons.append("low latency")
            
        return f"Selected {model} because it's " + " and ".join(reasons) if reasons else f"best overall match"
    
    def update_performance_metrics(self, model: str, latency: float, success: bool):
        """Update model performance metrics based on actual usage"""
        if model not in self.performance_metrics:
            self.performance_metrics[model] = {
                'total_requests': 0,
                'success_rate': 0.0,
                'avg_latency': 0.0,
                'latency_samples': []
            }
        
        metrics = self.performance_metrics[model]
        metrics['total_requests'] += 1
        
        # Update latency (keep last 100 samples)
        metrics['latency_samples'].append(latency)
        if len(metrics['latency_samples']) > 100:
            metrics['latency_samples'].pop(0)
        metrics['avg_latency'] = np.mean(metrics['latency_samples'])
        
        # Update success rate
        success_count = getattr(metrics, 'success_count', 0)
        if success:
            success_count += 1
        metrics['success_count'] = success_count
        metrics['success_rate'] = success_count / metrics['total_requests']
        
        # Update model config with real performance data
        if model in self.models:
            self.models[model].avg_latency = metrics['avg_latency']
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get routing analytics"""
        return {
            'total_models': len(self.models),
            'performance_metrics': self.performance_metrics,
            'cache_size': len(self.routing_cache),
            'model_capabilities': {name: {
                'cost_per_token': config.cost_per_token,
                'performance_score': config.performance_score,
                'avg_latency': config.avg_latency,
                'specialties': config.specialties,
                'max_complexity': config.max_complexity.value
            } for name, config in self.models.items()}
        }

# Global router instance
intelligent_router = IntelligentRouter()