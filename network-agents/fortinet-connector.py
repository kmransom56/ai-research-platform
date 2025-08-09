"""
Fortinet API Connector Service
Provides unified network management across Meraki and Fortinet platforms
Integrates FortiGate, FortiSwitch, and FortiAP management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
import structlog
from contextlib import asynccontextmanager
import json

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Configuration
FORTINET_API_KEY = os.getenv('FORTINET_API_KEY', '')
FORTINET_BASE_URL = os.getenv('FORTINET_BASE_URL', 'https://fortigate.local')
VERIFY_SSL = os.getenv('FORTINET_VERIFY_SSL', 'false').lower() == 'true'

class FortinetConnector:
    """Main Fortinet API connector class"""
    
    def __init__(self, api_key: str, base_url: str = FORTINET_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.verify = VERIFY_SSL
        self.rate_limiter = asyncio.Semaphore(10)  # 10 concurrent requests max
        self.last_request_time = {}
        
    async def initialize(self):
        """Initialize Fortinet API connection"""
        if not self.api_key:
            raise ValueError("FORTINET_API_KEY environment variable not set")
        
        # Test API connectivity
        try:
            response = await self._make_request('GET', '/api/v2/monitor/system/status')
            if response.get('status') == 'success':
                logger.info("Fortinet API connection established")
            else:
                raise Exception("API test failed")
        except Exception as e:
            logger.error(f"Fortinet API initialization failed: {e}")
            raise

    async def rate_limit(self, endpoint: str):
        """Rate limiting for API calls"""
        async with self.rate_limiter:
            now = datetime.now()
            if endpoint in self.last_request_time:
                elapsed = (now - self.last_request_time[endpoint]).total_seconds()
                if elapsed < 0.1:  # 100ms minimum between same endpoint calls
                    await asyncio.sleep(0.1 - elapsed)
            self.last_request_time[endpoint] = now

    async def _make_request(self, method: str, endpoint: str, 
                          params: Optional[Dict] = None, 
                          data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Fortinet API"""
        await self.rate_limit(endpoint)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fortinet API request failed: {e}")
            raise

    # System Information
    async def get_system_status(self) -> Dict[str, Any]:
        """Get FortiGate system status"""
        return await self._make_request('GET', '/api/v2/monitor/system/status')

    async def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return await self._make_request('GET', '/api/v2/monitor/system/performance')

    async def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource utilization"""
        return await self._make_request('GET', '/api/v2/monitor/system/resource/usage')

    # Network Interfaces
    async def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all network interfaces"""
        result = await self._make_request('GET', '/api/v2/monitor/system/interface')
        return result.get('results', [])

    async def get_interface_details(self, interface_name: str) -> Dict[str, Any]:
        """Get detailed interface information"""
        params = {'interface': interface_name}
        return await self._make_request('GET', '/api/v2/monitor/system/interface', params=params)

    # Security Policies
    async def get_firewall_policies(self) -> List[Dict[str, Any]]:
        """Get firewall policies"""
        result = await self._make_request('GET', '/api/v2/cmdb/firewall/policy')
        return result.get('results', [])

    async def get_security_events(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events"""
        params = {'count': count}
        result = await self._make_request('GET', '/api/v2/log/memory', params=params)
        return result.get('results', [])

    # VPN Information
    async def get_vpn_tunnels(self) -> List[Dict[str, Any]]:
        """Get VPN tunnel status"""
        result = await self._make_request('GET', '/api/v2/monitor/vpn/ipsec')
        return result.get('results', [])

    async def get_ssl_vpn_users(self) -> List[Dict[str, Any]]:
        """Get SSL VPN connected users"""
        result = await self._make_request('GET', '/api/v2/monitor/vpn/ssl')
        return result.get('results', [])

    # Traffic and Sessions
    async def get_active_sessions(self) -> Dict[str, Any]:
        """Get active network sessions"""
        return await self._make_request('GET', '/api/v2/monitor/firewall/session')

    async def get_traffic_statistics(self) -> Dict[str, Any]:
        """Get traffic statistics"""
        return await self._make_request('GET', '/api/v2/monitor/system/interface/traffic')

    # FortiSwitch Integration (if available)
    async def get_managed_switches(self) -> List[Dict[str, Any]]:
        """Get managed FortiSwitch devices"""
        try:
            result = await self._make_request('GET', '/api/v2/monitor/switch-controller/managed-switch')
            return result.get('results', [])
        except:
            return []  # Not all FortiGate units manage switches

    # FortiAP Integration (if available)  
    async def get_managed_access_points(self) -> List[Dict[str, Any]]:
        """Get managed FortiAP devices"""
        try:
            result = await self._make_request('GET', '/api/v2/monitor/wifi/managed_ap')
            return result.get('results', [])
        except:
            return []  # Not all FortiGate units manage APs

    # Health and Diagnostics
    async def get_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        health_data = {}
        
        try:
            # System status
            health_data['system_status'] = await self.get_system_status()
            
            # Performance metrics
            health_data['performance'] = await self.get_system_performance()
            
            # Resource usage
            health_data['resources'] = await self.get_system_resources()
            
            # Interface status
            health_data['interfaces'] = await self.get_interfaces()
            
            # Calculate health score
            health_data['health_score'] = self._calculate_health_score(health_data)
            
            return health_data
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'error': str(e), 'health_score': 0}

    def _calculate_health_score(self, health_data: Dict[str, Any]) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        try:
            # Check system status
            if health_data.get('system_status', {}).get('status') != 'success':
                score -= 30
            
            # Check resource usage
            resources = health_data.get('resources', {})
            cpu_usage = resources.get('cpu', 0)
            memory_usage = resources.get('memory', 0)
            
            if cpu_usage > 80:
                score -= 20
            elif cpu_usage > 60:
                score -= 10
            
            if memory_usage > 80:
                score -= 20
            elif memory_usage > 60:
                score -= 10
            
            # Check interface status
            interfaces = health_data.get('interfaces', [])
            down_interfaces = [i for i in interfaces if i.get('status') != 'up']
            if down_interfaces:
                score -= min(len(down_interfaces) * 5, 20)
            
            return max(0, score)
            
        except Exception:
            return 50.0  # Default score if calculation fails

# Global connector instance
fortinet_connector = FortinetConnector(FORTINET_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    try:
        await fortinet_connector.initialize()
        logger.info("Fortinet connector service started", port=11031)
    except Exception as e:
        logger.warning(f"Fortinet connector initialization failed: {e}")
    yield
    # Shutdown
    logger.info("Fortinet connector service shutting down")

# FastAPI application
app = FastAPI(
    title="Fortinet API Connector",
    description="Unified Fortinet network management service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class FortinetDevice(BaseModel):
    name: str
    model: str
    serial: str
    version: str
    status: str
    uptime: Optional[int] = None
    interfaces: List[Dict[str, Any]] = []

class SecurityPolicy(BaseModel):
    policy_id: int
    name: str
    source: List[str]
    destination: List[str]
    service: List[str]
    action: str
    status: str

class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    fortinet_api_status: str = "connected"
    health_score: float = 100.0

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        if fortinet_connector.api_key:
            health_data = await fortinet_connector.get_system_health()
            health_score = health_data.get('health_score', 100.0)
            api_status = "connected" if health_score > 0 else "disconnected"
        else:
            health_score = 0.0
            api_status = "not_configured"
            
        return HealthResponse(
            fortinet_api_status=api_status,
            health_score=health_score
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/system/status")
async def get_system_status():
    """Get FortiGate system status"""
    try:
        return await fortinet_connector.get_system_status()
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/health")
async def get_system_health():
    """Get comprehensive system health"""
    try:
        return await fortinet_connector.get_system_health()
    except Exception as e:
        logger.error("Failed to get system health", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interfaces")
async def get_interfaces():
    """Get all network interfaces"""
    try:
        return await fortinet_connector.get_interfaces()
    except Exception as e:
        logger.error("Failed to get interfaces", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interfaces/{interface_name}")
async def get_interface_details(interface_name: str):
    """Get detailed interface information"""
    try:
        return await fortinet_connector.get_interface_details(interface_name)
    except Exception as e:
        logger.error("Failed to get interface details", interface=interface_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/policies")
async def get_firewall_policies():
    """Get firewall security policies"""
    try:
        return await fortinet_connector.get_firewall_policies()
    except Exception as e:
        logger.error("Failed to get firewall policies", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/events")
async def get_security_events(count: int = 100):
    """Get recent security events"""
    try:
        return await fortinet_connector.get_security_events(count)
    except Exception as e:
        logger.error("Failed to get security events", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vpn/tunnels")
async def get_vpn_tunnels():
    """Get VPN tunnel status"""
    try:
        return await fortinet_connector.get_vpn_tunnels()
    except Exception as e:
        logger.error("Failed to get VPN tunnels", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vpn/ssl-users")
async def get_ssl_vpn_users():
    """Get SSL VPN connected users"""
    try:
        return await fortinet_connector.get_ssl_vpn_users()
    except Exception as e:
        logger.error("Failed to get SSL VPN users", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def get_active_sessions():
    """Get active network sessions"""
    try:
        return await fortinet_connector.get_active_sessions()
    except Exception as e:
        logger.error("Failed to get active sessions", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/traffic/statistics")
async def get_traffic_statistics():
    """Get traffic statistics"""
    try:
        return await fortinet_connector.get_traffic_statistics()
    except Exception as e:
        logger.error("Failed to get traffic statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/switches")
async def get_managed_switches():
    """Get managed FortiSwitch devices"""
    try:
        return await fortinet_connector.get_managed_switches()
    except Exception as e:
        logger.error("Failed to get managed switches", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/access-points")
async def get_managed_access_points():
    """Get managed FortiAP devices"""
    try:
        return await fortinet_connector.get_managed_access_points()
    except Exception as e:
        logger.error("Failed to get managed access points", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/unified/overview")
async def get_unified_overview():
    """Get unified overview of Fortinet infrastructure"""
    try:
        overview = {}
        
        # System information
        overview['system'] = await fortinet_connector.get_system_status()
        overview['health'] = await fortinet_connector.get_system_health()
        
        # Network components
        overview['interfaces'] = await fortinet_connector.get_interfaces()
        overview['switches'] = await fortinet_connector.get_managed_switches()
        overview['access_points'] = await fortinet_connector.get_managed_access_points()
        
        # Security information
        overview['security_policies'] = await fortinet_connector.get_firewall_policies()
        overview['vpn_tunnels'] = await fortinet_connector.get_vpn_tunnels()
        
        # Calculate summary statistics
        overview['summary'] = {
            'total_interfaces': len(overview['interfaces']),
            'active_interfaces': len([i for i in overview['interfaces'] if i.get('status') == 'up']),
            'managed_switches': len(overview['switches']),
            'managed_access_points': len(overview['access_points']),
            'security_policies': len(overview['security_policies']),
            'active_vpn_tunnels': len([t for t in overview['vpn_tunnels'] if t.get('status') == 'up']),
            'overall_health_score': overview['health'].get('health_score', 0)
        }
        
        return overview
        
    except Exception as e:
        logger.error("Failed to get unified overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    try:
        health_data = await fortinet_connector.get_system_health()
        
        metrics = []
        
        # System health score
        health_score = health_data.get('health_score', 0)
        metrics.append(f'fortinet_health_score {health_score}')
        
        # Resource usage
        resources = health_data.get('resources', {})
        if 'cpu' in resources:
            metrics.append(f'fortinet_cpu_usage {resources["cpu"]}')
        if 'memory' in resources:
            metrics.append(f'fortinet_memory_usage {resources["memory"]}')
        
        # Interface status
        interfaces = health_data.get('interfaces', [])
        up_interfaces = len([i for i in interfaces if i.get('status') == 'up'])
        total_interfaces = len(interfaces)
        metrics.append(f'fortinet_interfaces_up {up_interfaces}')
        metrics.append(f'fortinet_interfaces_total {total_interfaces}')
        
        return '\n'.join(metrics)
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11031)