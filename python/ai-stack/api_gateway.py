#!/usr/bin/env python3
"""
Unified API Gateway for AI Platform Integration
Routes requests to appropriate backends based on task type
"""

from flask import Flask, request, jsonify, Response
import requests
import json
import logging
from typing import Dict, Any

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Backend configurations
BACKENDS = {
    'reasoning': 'http://localhost:8000',      # vLLM DeepSeek R1
    'general': 'http://localhost:8001',        # vLLM Mistral
    'coding': 'http://localhost:8002',         # vLLM DeepSeek Coder
    'creative': 'http://localhost:5001',       # KoboldCpp
    'advanced': 'http://localhost:5000'        # Oobabooga API
}

def route_request(task_type: str, prompt: str, **kwargs) -> Dict[str, Any]:
    """Route request to appropriate backend based on task type"""
    
    backend_url = BACKENDS.get(task_type, BACKENDS['general'])
    logger.info(f"Routing {task_type} request to {backend_url}")
    
    try:
        if task_type == 'creative':
            # KoboldCpp API format
            payload = {
                "prompt": prompt,
                "max_length": kwargs.get('max_tokens', 512),
                "temperature": kwargs.get('temperature', 0.8)
            }
            response = requests.post(f"{backend_url}/api/v1/generate", json=payload, timeout=30)
        else:
            # OpenAI-compatible format for vLLM and Oobabooga
            payload = {
                "model": "auto",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', 512),
                "temperature": kwargs.get('temperature', 0.7)
            }
            response = requests.post(f"{backend_url}/v1/chat/completions", json=payload, timeout=30)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error routing request to {backend_url}: {e}")
        return {"error": f"Backend {task_type} unavailable: {str(e)}"}

@app.route('/v1/completions', methods=['POST'])
def completions():
    """Main completion endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        task_type = data.get('task_type', 'general')
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        result = route_request(task_type, prompt, **data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in completions endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # Extract the last user message as prompt
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        if not user_messages:
            return jsonify({"error": "No user message found"}), 400
            
        prompt = user_messages[-1].get('content', '')
        task_type = data.get('task_type', 'general')
        
        result = route_request(task_type, prompt, **data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in chat completions endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for all backends"""
    status = {}
    overall_health = True
    
    for name, url in BACKENDS.items():
        try:
            # Try different health endpoints
            health_endpoints = ['/health', '/v1/models', '/api/v1/info']
            backend_healthy = False
            
            for endpoint in health_endpoints:
                try:
                    response = requests.get(f"{url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        backend_healthy = True
                        break
                except:
                    continue
            
            status[name] = {
                "status": "online" if backend_healthy else "offline",
                "url": url
            }
            
            if not backend_healthy:
                overall_health = False
                
        except Exception as e:
            status[name] = {
                "status": "error",
                "url": url,
                "error": str(e)
            }
            overall_health = False
    
    return jsonify({
        "overall_status": "healthy" if overall_health else "unhealthy",
        "backends": status,
        "gateway": "online"
    })

@app.route('/models', methods=['GET'])
def list_models():
    """List available models from all backends"""
    models = {}
    
    for name, url in BACKENDS.items():
        try:
            response = requests.get(f"{url}/v1/models", timeout=5)
            if response.status_code == 200:
                backend_models = response.json()
                models[name] = backend_models
        except:
            models[name] = {"error": "Could not fetch models"}
    
    return jsonify(models)

@app.route('/info', methods=['GET'])
def gateway_info():
    """Gateway information endpoint"""
    return jsonify({
        "name": "Advanced AI Stack Gateway",
        "version": "1.0.0",
        "backends": list(BACKENDS.keys()),
        "endpoints": {
            "/v1/completions": "Main completion endpoint",
            "/v1/chat/completions": "OpenAI-compatible chat endpoint",
            "/health": "Health check for all backends",
            "/models": "List available models",
            "/info": "This information endpoint"
        }
    })

if __name__ == '__main__':
    logger.info("Starting Advanced AI Stack Gateway on port 9000")
    app.run(host='0.0.0.0', port=9000, debug=False)