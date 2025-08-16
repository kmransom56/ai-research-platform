#!/usr/bin/env python3
"""
Python SDK for Advanced AI Stack Integration
Provides easy access to the AI stack services from other Python applications
"""

import requests
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Response from AI service"""
    content: str
    task_type: str
    backend: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AdvancedAIStack:
    """Client for the Advanced AI Stack Gateway"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def complete(self, 
                prompt: str, 
                task_type: str = "general",
                max_tokens: int = 512,
                temperature: float = 0.7,
                **kwargs) -> AIResponse:
        """
        Send completion request to AI stack
        
        Args:
            prompt: The text prompt to send
            task_type: Type of task ('reasoning', 'general', 'coding', 'creative', 'advanced')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
        
        Returns:
            AIResponse object with the completion
        """
        payload = {
            "task_type": task_type,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/completions", 
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                return AIResponse(
                    content="",
                    task_type=task_type,
                    backend="unknown",
                    error=data["error"]
                )
            
            # Extract content based on response format
            content = ""
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")
                elif "text" in choice:
                    content = choice["text"]
            elif "results" in data and data["results"]:
                content = data["results"][0].get("text", "")
            
            return AIResponse(
                content=content,
                task_type=task_type,
                backend=task_type,
                metadata=data
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return AIResponse(
                content="",
                task_type=task_type,
                backend="unknown",
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return AIResponse(
                content="",
                task_type=task_type,
                backend="unknown",
                error=str(e)
            )
    
    def chat_complete(self,
                     messages: List[Dict[str, str]],
                     task_type: str = "general",
                     **kwargs) -> AIResponse:
        """
        Send chat completion request (OpenAI format)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            task_type: Type of task
            **kwargs: Additional parameters
        
        Returns:
            AIResponse object
        """
        payload = {
            "messages": messages,
            "task_type": task_type,
            **kwargs
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                return AIResponse(
                    content="",
                    task_type=task_type,
                    backend="unknown",
                    error=data["error"]
                )
            
            # Extract content from OpenAI format
            content = ""
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]
                if "message" in choice:
                    content = choice["message"].get("content", "")
            
            return AIResponse(
                content=content,
                task_type=task_type,
                backend=task_type,
                metadata=data
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat request failed: {e}")
            return AIResponse(
                content="",
                task_type=task_type,
                backend="unknown",
                error=str(e)
            )
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all backend services"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "gateway_unreachable"}
    
    def list_models(self) -> Dict[str, Any]:
        """List available models from all backends"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """Get gateway information"""
        try:
            response = self.session.get(f"{self.base_url}/info", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Convenience functions for common tasks
def reasoning_complete(prompt: str, **kwargs) -> AIResponse:
    """Quick reasoning completion"""
    ai = AdvancedAIStack()
    return ai.complete(prompt, task_type="reasoning", **kwargs)

def coding_complete(prompt: str, **kwargs) -> AIResponse:
    """Quick coding completion"""
    ai = AdvancedAIStack()
    return ai.complete(prompt, task_type="coding", **kwargs)

def creative_complete(prompt: str, **kwargs) -> AIResponse:
    """Quick creative writing completion"""
    ai = AdvancedAIStack()
    return ai.complete(prompt, task_type="creative", **kwargs)

def general_complete(prompt: str, **kwargs) -> AIResponse:
    """Quick general completion"""
    ai = AdvancedAIStack()
    return ai.complete(prompt, task_type="general", **kwargs)

# Example usage
if __name__ == "__main__":
    # Initialize client
    ai = AdvancedAIStack()
    
    # Health check
    print("Health Check:")
    health = ai.health_check()
    print(json.dumps(health, indent=2))
    
    # Test different task types
    test_prompts = {
        "reasoning": "If a train travels at 80 mph for 2.5 hours, how far does it go?",
        "coding": "Write a Python function to sort a list of numbers",
        "creative": "Write a haiku about artificial intelligence",
        "general": "Explain the concept of machine learning in simple terms"
    }
    
    for task_type, prompt in test_prompts.items():
        print(f"\n{task_type.upper()} TEST:")
        result = ai.complete(prompt, task_type=task_type, max_tokens=200)
        
        if result.error:
            print(f"Error: {result.error}")
        else:
            print(f"Response: {result.content}")