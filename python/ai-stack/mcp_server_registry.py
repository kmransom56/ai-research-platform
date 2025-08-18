#!/usr/bin/env python3
"""
MCP Server Registry for AI Collaboration System
Secure integration of Model Context Protocol servers with the AI stack
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    """MCP Server configuration and status"""
    name: str
    type: str  # 'docker', 'url', 'command'
    status: str = 'unknown'  # 'online', 'offline', 'error', 'unknown'
    capabilities: List[str] = None
    last_checked: Optional[str] = None
    endpoint: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

class MCPServerRegistry:
    """Registry and manager for MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._load_server_configurations()
    
    def _load_server_configurations(self):
        """Load MCP server configurations with secure credential handling"""
        
        # Docker MCP Server
        self.servers['docker'] = MCPServer(
            name='Docker Operations',
            type='docker',
            capabilities=['container_management', 'image_operations', 'network_management'],
            command='docker',
            args=[
                'run', '-l', 'mcp.client=ai-platform', '--rm',
                '--add-host=host.docker.internal:host-gateway',
                '-i', 'alpine/socat', 'STDIO',
                'TCP:host.docker.internal:8811'
            ]
        )
        
        # GitHub MCP Server (using GitHub secrets)
        github_token = self._get_secure_credential('GITHUB_PERSONAL_ACCESS_TOKEN')
        if github_token:
            self.servers['github'] = MCPServer(
                name='GitHub Integration',
                type='url',
                endpoint='https://api.githubcopilot.com/mcp/',
                capabilities=['code_management', 'repository_operations', 'issue_tracking'],
                headers={'Authorization': f'Bearer {github_token}'}
            )
        
        # API Dog MCP Server
        apidog_token = self._get_secure_credential('APIDOG_ACCESS_TOKEN')
        if apidog_token:
            self.servers['apidog'] = MCPServer(
                name='API Testing Platform',
                type='command',
                command='npx',
                args=['-y', 'apidog-mcp-server@latest', '--project=950315'],
                env={'APIDOG_ACCESS_TOKEN': apidog_token},
                capabilities=['api_testing', 'documentation', 'mock_services']
            )
        
        # Meraki MCP Server
        meraki_key = self._get_secure_credential('MERAKI_API_KEY')
        if meraki_key:
            self.servers['meraki'] = MCPServer(
                name='Cisco Meraki Network Management',
                type='command',
                command='node',
                args=['/home/keith/meraki-mcp-server/meraki.js'],
                env={'MERAKI_API_KEY': meraki_key},
                capabilities=['network_management', 'device_monitoring', 'restaurant_networks']
            )
        
        # Figma MCP Server (via Composio)
        self.servers['figma'] = MCPServer(
            name='Figma Design Integration',
            type='url',
            endpoint='https://mcp.composio.dev/composio/server/83664951-9d36-4818-90cc-a7e9060ddab1/mcp?include_composio_helper_actions=true&agent=ai-platform',
            capabilities=['design_operations', 'ui_generation', 'prototype_management']
        )
        
        # FortiManager MCP Server (for restaurant network management)
        fortinet_key = self._get_secure_credential('FORTINET_API_KEY')
        if fortinet_key:
            self.servers['fortimanager'] = MCPServer(
                name='FortiManager Network Control',
                type='command',
                command='python3',
                args=['/home/keith/chat-copilot/network-agents/fortimanager_mcp_server.py'],
                env={
                    'FORTINET_API_KEY': fortinet_key,
                    'FORTIMANAGER_HOST': os.getenv('FORTIMANAGER_HOST', 'localhost'),
                    'FORTIMANAGER_USERNAME': os.getenv('FORTIMANAGER_USERNAME', 'admin')
                },
                capabilities=['fortinet_management', 'restaurant_security', 'policy_management']
            )
    
    def _get_secure_credential(self, key: str) -> Optional[str]:
        """Get credential from environment with fallback to GitHub secrets"""
        # First try environment variable
        value = os.getenv(key)
        if value:
            return value
        
        # Try GitHub secrets if available
        try:
            result = subprocess.run([
                'gh', 'secret', 'get', key
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning(f"Could not retrieve GitHub secret for {key}")
        
        return None
    
    async def check_server_health(self, server_name: str) -> Dict[str, Any]:
        """Check health of a specific MCP server"""
        if server_name not in self.servers:
            return {'status': 'not_found', 'error': f'Server {server_name} not registered'}
        
        server = self.servers[server_name]
        
        try:
            if server.type == 'url':
                return await self._check_url_server(server)
            elif server.type == 'command':
                return await self._check_command_server(server)
            elif server.type == 'docker':
                return await self._check_docker_server(server)
            else:
                return {'status': 'unsupported', 'error': f'Server type {server.type} not supported'}
        
        except Exception as e:
            logger.error(f"Health check failed for {server_name}: {e}")
            server.status = 'error'
            return {'status': 'error', 'error': str(e)}
    
    async def _check_url_server(self, server: MCPServer) -> Dict[str, Any]:
        """Check health of URL-based MCP server"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            headers = server.headers or {}
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with self.session.get(
                server.endpoint + '/health',
                headers=headers,
                timeout=timeout
            ) as response:
                
                if response.status == 200:
                    server.status = 'online'
                    server.last_checked = datetime.now().isoformat()
                    return {'status': 'online', 'response_time': response.headers.get('X-Response-Time')}
                else:
                    server.status = 'error'
                    return {'status': 'error', 'http_status': response.status}
        
        except asyncio.TimeoutError:
            server.status = 'timeout'
            return {'status': 'timeout', 'error': 'Request timed out'}
        except Exception as e:
            server.status = 'error'
            return {'status': 'error', 'error': str(e)}
    
    async def _check_command_server(self, server: MCPServer) -> Dict[str, Any]:
        """Check health of command-based MCP server"""
        try:
            # For command servers, we'll try a simple ping or version check
            env = os.environ.copy()
            if server.env:
                env.update(server.env)
            
            # Simple process check
            process = await asyncio.create_subprocess_exec(
                'pgrep', '-f', server.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5)
            
            if process.returncode == 0:
                server.status = 'online'
                server.last_checked = datetime.now().isoformat()
                return {'status': 'online', 'processes': len(stdout.decode().strip().split('\n'))}
            else:
                server.status = 'offline'
                return {'status': 'offline', 'error': 'Process not running'}
        
        except asyncio.TimeoutError:
            server.status = 'timeout'
            return {'status': 'timeout', 'error': 'Health check timed out'}
        except Exception as e:
            server.status = 'error'
            return {'status': 'error', 'error': str(e)}
    
    async def _check_docker_server(self, server: MCPServer) -> Dict[str, Any]:
        """Check health of Docker-based MCP server"""
        try:
            # Check if Docker is available
            process = await asyncio.create_subprocess_exec(
                'docker', 'info',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                server.status = 'online'
                server.last_checked = datetime.now().isoformat()
                return {'status': 'online', 'docker_available': True}
            else:
                server.status = 'error'
                return {'status': 'error', 'error': 'Docker not available'}
        
        except Exception as e:
            server.status = 'error'
            return {'status': 'error', 'error': str(e)}
    
    async def check_all_servers(self) -> Dict[str, Any]:
        """Check health of all registered MCP servers"""
        results = {}
        
        # Check all servers concurrently
        tasks = [
            self.check_server_health(name) 
            for name in self.servers.keys()
        ]
        
        server_names = list(self.servers.keys())
        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(server_names, health_results):
            if isinstance(result, Exception):
                results[name] = {'status': 'error', 'error': str(result)}
            else:
                results[name] = result
        
        return results
    
    def get_servers_by_capability(self, capability: str) -> List[str]:
        """Get list of server names that support a specific capability"""
        return [
            name for name, server in self.servers.items()
            if capability in server.capabilities
        ]
    
    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a server"""
        if server_name not in self.servers:
            return None
        
        server = self.servers[server_name]
        info = asdict(server)
        
        # Remove sensitive information
        if 'headers' in info and info['headers']:
            info['headers'] = {k: '***' for k in info['headers'].keys()}
        if 'env' in info and info['env']:
            info['env'] = {k: '***' for k in info['env'].keys()}
        
        return info
    
    def list_all_servers(self) -> Dict[str, Any]:
        """List all registered servers with their basic info"""
        return {
            name: {
                'name': server.name,
                'type': server.type,
                'status': server.status,
                'capabilities': server.capabilities,
                'last_checked': server.last_checked
            }
            for name, server in self.servers.items()
        }
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

# Global registry instance
mcp_registry = MCPServerRegistry()

async def get_mcp_registry() -> MCPServerRegistry:
    """Get the global MCP registry instance"""
    return mcp_registry