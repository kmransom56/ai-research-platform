#!/usr/bin/env python3
"""
Unified API Gateway for AI Platform Integration
Routes requests to appropriate backends based on task type
Enhanced with MCP (Model Context Protocol) server integration
"""

from flask import Flask, request, jsonify, Response
import requests
import json
import logging
import os
import asyncio
import time
from typing import Dict, Any
from collaboration_orchestrator import orchestrator, TaskType
from workflow_templates import workflow_manager
from mcp_server_registry import mcp_registry
from enhanced_router import intelligent_router

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Backend configurations - use environment variables with fallbacks
BACKENDS = {
    'reasoning': os.getenv('REASONING_MODEL_URL', 'http://localhost:8000'),      # vLLM DeepSeek R1
    'general': os.getenv('GENERAL_MODEL_URL', 'http://localhost:8001'),          # vLLM Mistral
    'coding': os.getenv('CODING_MODEL_URL', 'http://localhost:8002'),            # vLLM DeepSeek Coder
    'creative': os.getenv('CREATIVE_MODEL_URL', 'http://localhost:5001'),        # KoboldCpp
    'advanced': os.getenv('ADVANCED_MODEL_URL', 'http://localhost:5000')         # Oobabooga API
}

def route_request(task_type: str, prompt: str, **kwargs) -> Dict[str, Any]:
    """Route request to appropriate backend using intelligent routing"""
    
    # Use intelligent router to get optimal model
    budget_factor = kwargs.get('budget_factor', 1.0)
    start_time = time.time()
    
    optimal_model, routing_info = intelligent_router.get_optimal_model(
        prompt, task_type, budget_factor
    )
    
    backend_url = BACKENDS.get(optimal_model, BACKENDS['general'])
    logger.info(f"Intelligent routing: {task_type} -> {optimal_model} ({backend_url})")
    logger.info(f"Routing reason: {routing_info['routing_reason']}")
    
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
        result = response.json()
        
        # Update performance metrics
        latency = time.time() - start_time
        intelligent_router.update_performance_metrics(optimal_model, latency, True)
        
        # Add routing info to response
        if isinstance(result, dict):
            result['routing_info'] = routing_info
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error routing request to {backend_url}: {e}")
        
        # Update performance metrics for failure
        latency = time.time() - start_time
        intelligent_router.update_performance_metrics(optimal_model, latency, False)
        
        # Try fallback models
        fallback_models = routing_info.get('fallback_models', [])
        for fallback_model in fallback_models:
            if fallback_model in BACKENDS:
                logger.info(f"Trying fallback model: {fallback_model}")
                try:
                    fallback_url = BACKENDS[fallback_model]
                    if fallback_model == 'creative':
                        payload = {
                            "prompt": prompt,
                            "max_length": kwargs.get('max_tokens', 512),
                            "temperature": kwargs.get('temperature', 0.8)
                        }
                        response = requests.post(f"{fallback_url}/api/v1/generate", json=payload, timeout=30)
                    else:
                        payload = {
                            "model": "auto",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": kwargs.get('max_tokens', 512),
                            "temperature": kwargs.get('temperature', 0.7)
                        }
                        response = requests.post(f"{fallback_url}/v1/chat/completions", json=payload, timeout=30)
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Add fallback info
                    if isinstance(result, dict):
                        routing_info['used_fallback'] = fallback_model
                        result['routing_info'] = routing_info
                    
                    logger.info(f"Fallback to {fallback_model} successful")
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback to {fallback_model} also failed: {fallback_error}")
                    continue
        
        return {"error": f"All backends unavailable. Primary: {str(e)}", "routing_info": routing_info}

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

@app.route('/v1/collaborate', methods=['POST'])
def collaborate():
    """Multi-agent collaboration endpoint"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        prompt = data.get('prompt', '')
        context = data.get('context', {})
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Run collaboration asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.simple_collaboration(prompt, context)
            )
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in collaboration endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/router/analytics', methods=['GET'])
def get_routing_analytics():
    """Get intelligent routing analytics"""
    try:
        analytics = intelligent_router.get_analytics()
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/router/optimal-model', methods=['POST'])
def get_optimal_model():
    """Get optimal model recommendation without executing"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        prompt = data.get('prompt', '')
        task_type = data.get('task_type')
        budget_factor = data.get('budget_factor', 1.0)
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        optimal_model, routing_info = intelligent_router.get_optimal_model(
            prompt, task_type, budget_factor
        )
        
        return jsonify({
            "optimal_model": optimal_model,
            "routing_info": routing_info,
            "backend_url": BACKENDS.get(optimal_model)
        })
        
    except Exception as e:
        logger.error(f"Error getting optimal model: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/plan', methods=['POST'])
def create_plan():
    """Create a collaboration plan without executing it"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        prompt = data.get('prompt', '')
        context = data.get('context', {})
        template_name = data.get('template', None)
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Create collaboration plan
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            plan = loop.run_until_complete(
                orchestrator.create_collaboration_plan(prompt, context, template_name)
            )
            
            # Convert plan to dict for JSON serialization
            plan_dict = {
                "id": plan.id,
                "task_sequence": [
                    {
                        "id": task.id,
                        "type": task.type.value,
                        "prompt": task.prompt,
                        "dependencies": task.dependencies,
                        "assigned_services": task.assigned_services
                    }
                    for task in plan.task_sequence
                ],
                "service_allocation": plan.service_allocation,
                "estimated_duration": plan.estimated_duration,
                "parallel_execution": plan.parallel_execution
            }
            
            return jsonify(plan_dict)
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error creating collaboration plan: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/execute/<plan_id>', methods=['POST'])
def execute_plan(plan_id):
    """Execute a previously created collaboration plan"""
    try:
        # Execute collaboration plan
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.execute_collaboration_plan(plan_id)
            )
            return jsonify(result)
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error executing collaboration plan: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/services', methods=['GET'])
def get_services():
    """Get status and information about all platform services"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            status = loop.run_until_complete(orchestrator.get_service_status())
            return jsonify(status)
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/workflows', methods=['GET'])
def list_workflows():
    """List available workflow templates"""
    try:
        templates = workflow_manager.list_templates()
        return jsonify({
            "templates": templates,
            "count": len(templates)
        })
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/workflows/<template_name>', methods=['GET'])
def get_workflow(template_name):
    """Get detailed information about a specific workflow template"""
    try:
        config = workflow_manager.get_workflow_config(template_name)
        if not config:
            return jsonify({"error": f"Template '{template_name}' not found"}), 404
        
        return jsonify(config)
    except Exception as e:
        logger.error(f"Error getting workflow {template_name}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/workflows/suggest', methods=['POST'])
def suggest_workflow():
    """Suggest the best workflow template for a given prompt"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        suggested = workflow_manager.suggest_template(prompt)
        template_info = workflow_manager.get_workflow_config(suggested)
        
        return jsonify({
            "suggested_template": suggested,
            "template_info": template_info,
            "prompt": prompt
        })
    except Exception as e:
        logger.error(f"Error suggesting workflow: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/collaborate/template', methods=['POST'])
def collaborate_with_template():
    """Multi-agent collaboration using a specific template"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        prompt = data.get('prompt', '')
        template_name = data.get('template')
        context = data.get('context', {})
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        if not template_name:
            return jsonify({"error": "No template specified"}), 400
        
        # Validate template exists
        if not workflow_manager.get_template(template_name):
            return jsonify({"error": f"Template '{template_name}' not found"}), 404
        
        # Run collaboration with specific template
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            plan = loop.run_until_complete(
                orchestrator.create_collaboration_plan(prompt, context, template_name)
            )
            result = loop.run_until_complete(
                orchestrator.execute_collaboration_plan(plan.id)
            )
            
            # Add template information to result
            result["template_used"] = template_name
            result["template_info"] = workflow_manager.get_workflow_config(template_name)
            
            return jsonify(result)
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in template collaboration endpoint: {e}")
        return jsonify({"error": str(e)}), 500

# MCP Server Endpoints
@app.route('/mcp', methods=['GET'])
def list_mcp_servers():
    """List all registered MCP servers"""
    try:
        servers = mcp_registry.list_all_servers()
        return jsonify({
            "mcp_servers": servers,
            "server_count": len(servers)
        })
    except Exception as e:
        logger.error(f"Error listing MCP servers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/<server_name>', methods=['GET'])
def get_mcp_server_info(server_name):
    """Get detailed information about a specific MCP server"""
    try:
        server_info = mcp_registry.get_server_info(server_name)
        if not server_info:
            return jsonify({"error": f"MCP server '{server_name}' not found"}), 404
        
        return jsonify(server_info)
    except Exception as e:
        logger.error(f"Error getting MCP server info for {server_name}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/<server_name>/health', methods=['GET'])
def check_mcp_server_health(server_name):
    """Check health of a specific MCP server"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            health = loop.run_until_complete(
                mcp_registry.check_server_health(server_name)
            )
            return jsonify(health)
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error checking MCP server health for {server_name}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/health', methods=['GET'])
def check_all_mcp_servers_health():
    """Check health of all MCP servers"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            health_results = loop.run_until_complete(
                mcp_registry.check_all_servers()
            )
            
            online_count = sum(1 for result in health_results.values() 
                             if result.get('status') == 'online')
            
            return jsonify({
                "overall_status": "healthy" if online_count > 0 else "unhealthy",
                "online_servers": online_count,
                "total_servers": len(health_results),
                "servers": health_results
            })
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error checking all MCP server health: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/<server_name>/invoke', methods=['POST'])
def invoke_mcp_server(server_name):
    """Invoke a method on a specific MCP server"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        method = data.get('method')
        params = data.get('params', {})
        
        if not method:
            return jsonify({"error": "No method specified"}), 400
        
        # Check if server exists
        server_info = mcp_registry.get_server_info(server_name)
        if not server_info:
            return jsonify({"error": f"MCP server '{server_name}' not found"}), 404
        
        # For now, handle FortiManager server directly
        if server_name == 'fortimanager':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                from network_agents.fortimanager_mcp_server import FortiManagerMCPServer
                fm_server = FortiManagerMCPServer()
                loop.run_until_complete(fm_server.start_session())
                result = loop.run_until_complete(
                    fm_server.handle_mcp_request(method, params)
                )
                loop.run_until_complete(fm_server.close())
                return jsonify(result)
            finally:
                loop.close()
        else:
            return jsonify({
                "error": f"Direct invocation not yet implemented for {server_name}",
                "available_servers": ["fortimanager"]
            }), 501
        
    except Exception as e:
        logger.error(f"Error invoking MCP server {server_name}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/capabilities/<capability>', methods=['GET'])
def get_servers_by_capability(capability):
    """Get MCP servers that support a specific capability"""
    try:
        servers = mcp_registry.get_servers_by_capability(capability)
        
        return jsonify({
            "capability": capability,
            "servers": servers,
            "server_count": len(servers)
        })
    except Exception as e:
        logger.error(f"Error getting servers by capability {capability}: {e}")
        return jsonify({"error": str(e)}), 500

# Restaurant Network Management Endpoints
@app.route('/v1/restaurant/network', methods=['GET'])
def get_restaurant_network_overview():
    """Get overview of restaurant networks"""
    try:
        restaurant = request.args.get('restaurant')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.get_restaurant_network_status(restaurant)
            )
            return jsonify(result)
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error getting restaurant network overview: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/restaurant/monitor', methods=['POST'])
def monitor_restaurant_network():
    """Real-time monitoring of restaurant network"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        restaurant = data.get('restaurant')
        duration = data.get('duration', 60)
        
        if not restaurant:
            return jsonify({"error": "Restaurant parameter required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.execute_mcp_task('fortimanager', 'monitor_restaurant_network', {
                    'restaurant': restaurant,
                    'duration': duration
                })
            )
            return jsonify(result)
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error monitoring restaurant network: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/restaurant/security', methods=['GET'])
def get_restaurant_security_alerts():
    """Get security alerts for restaurant networks"""
    try:
        restaurant = request.args.get('restaurant', 'all')
        severity = request.args.get('severity', 'all')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.execute_mcp_task('fortimanager', 'get_security_alerts', {
                    'restaurant': restaurant,
                    'severity': severity
                })
            )
            return jsonify(result)
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Error getting restaurant security alerts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/collaborate/mcp', methods=['POST'])
def collaborate_with_mcp():
    """Multi-agent collaboration with MCP server integration"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        prompt = data.get('prompt', '')
        template_name = data.get('template')
        context = data.get('context', {})
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                orchestrator.collaborate_with_mcp(prompt, template_name, context)
            )
            return jsonify(result)
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in MCP collaboration: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/info', methods=['GET'])
def gateway_info():
    """Gateway information endpoint"""
    return jsonify({
        "name": "Advanced AI Stack Gateway with Multi-Agent Collaboration & MCP Integration",
        "version": "2.1.0",
        "backends": list(BACKENDS.keys()),
        "endpoints": {
            "/v1/completions": "Main completion endpoint",
            "/v1/chat/completions": "OpenAI-compatible chat endpoint",
            "/v1/collaborate": "Multi-agent collaboration endpoint",
            "/v1/collaborate/template": "Collaboration with specific template",
            "/v1/collaborate/mcp": "Collaboration with MCP server integration",
            "/v1/plan": "Create collaboration plan",
            "/v1/execute/<plan_id>": "Execute collaboration plan",
            "/v1/restaurant/network": "Restaurant network overview",
            "/v1/restaurant/monitor": "Real-time restaurant network monitoring",
            "/v1/restaurant/security": "Restaurant security alerts",
            "/workflows": "List available workflow templates",
            "/workflows/<name>": "Get specific workflow template info",
            "/workflows/suggest": "Suggest best template for prompt",
            "/health": "Health check for all backends",
            "/services": "Status of all platform services",
            "/models": "List available models",
            "/mcp": "List all MCP servers",
            "/mcp/<server>/health": "Check MCP server health",
            "/mcp/<server>/invoke": "Invoke MCP server method",
            "/mcp/capabilities/<capability>": "Get servers by capability",
            "/info": "This information endpoint"
        },
        "collaboration_features": {
            "task_decomposition": "Automatic breaking down of complex tasks",
            "service_orchestration": "Intelligent routing across AI services",
            "parallel_execution": "Concurrent task processing when possible",
            "dependency_management": "Task dependency resolution",
            "health_monitoring": "Real-time service health tracking",
            "mcp_integration": "Model Context Protocol server integration"
        },
        "mcp_features": {
            "server_registry": "Centralized MCP server management",
            "health_monitoring": "Real-time MCP server health checks",
            "capability_routing": "Route requests based on server capabilities",
            "secure_credentials": "GitHub secrets integration",
            "restaurant_networks": "FortiManager integration for restaurant networks",
            "github_integration": "Code management and repository operations",
            "docker_operations": "Container management and deployment",
            "api_testing": "API testing and documentation platform",
            "figma_design": "Design operations and UI generation"
        },
        "restaurant_network_features": {
            "multi_vendor_support": "Cisco Meraki + FortiManager integration",
            "device_monitoring": "25,000+ devices across restaurant chains",
            "security_analysis": "Real-time threat detection and policy management",
            "voice_interfaces": "Natural language network management",
            "brand_coverage": "Arby's, Buffalo Wild Wings, Sonic Drive-In networks"
        }
    })

if __name__ == '__main__':
    logger.info("Starting Advanced AI Stack Gateway on port 9000")
    app.run(host='0.0.0.0', port=9000, debug=False)