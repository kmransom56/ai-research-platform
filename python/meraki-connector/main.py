"""
Meraki API Connector Service
Provides RESTful API interface for Cisco Meraki Dashboard API
Integrates with AI Research Platform services
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import meraki
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import structlog
from contextlib import asynccontextmanager

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Configuration
MERAKI_API_KEY = os.getenv('MERAKI_API_KEY', '')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@postgres:5432/chatcopilot')

class MerakiConnector:
    """Main Meraki API connector class"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.dashboard = None
        self.rate_limiter = asyncio.Semaphore(5)  # 5 requests per second max
        self.last_request_time = {}
        
    async def initialize(self):
        """Initialize Meraki Dashboard API client"""
        if not self.api_key:
            raise ValueError("MERAKI_API_KEY environment variable not set")
            
        self.dashboard = meraki.DashboardAPI(
            api_key=self.api_key,
            base_url='https://api.meraki.com/api/v1/',
            output_log=False,
            print_console=False,
            suppress_logging=True,
            caller='ai-research-platform/1.0'
        )
        logger.info("Meraki Dashboard API initialized")

    async def rate_limit(self, endpoint: str):
        """Rate limiting for API calls"""
        async with self.rate_limiter:
            now = datetime.now()
            if endpoint in self.last_request_time:
                elapsed = (now - self.last_request_time[endpoint]).total_seconds()
                if elapsed < 0.2:  # 200ms minimum between same endpoint calls
                    await asyncio.sleep(0.2 - elapsed)
            self.last_request_time[endpoint] = now

# Global connector instance
meraki_connector = MerakiConnector(MERAKI_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await meraki_connector.initialize()
    logger.info("Meraki connector service started", port=11025)
    yield
    # Shutdown
    logger.info("Meraki connector service shutting down")

# FastAPI application
app = FastAPI(
    title="Meraki API Connector",
    description="AI-powered Cisco Meraki network management service",
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
class NetworkDevice(BaseModel):
    serial: str
    model: str
    name: Optional[str] = None
    mac: Optional[str] = None
    lan_ip: Optional[str] = None
    firmware: Optional[str] = None
    network_id: str
    status: str
    last_reported_at: Optional[datetime] = None

class NetworkInfo(BaseModel):
    id: str
    organization_id: str
    name: str
    product_types: List[str]
    timezone: str
    tags: List[str] = []

class OrganizationInfo(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    api_enabled: bool
    licensing_model: str
    cloud_region_name: str

class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    meraki_api_status: str = "connected"

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test Meraki API connectivity
        if meraki_connector.dashboard:
            await meraki_connector.rate_limit("health")
            orgs = meraki_connector.dashboard.organizations.getOrganizations()
            api_status = "connected" if orgs else "disconnected"
        else:
            api_status = "not_initialized"
            
        return HealthResponse(meraki_api_status=api_status)
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/organizations", response_model=List[OrganizationInfo])
async def get_organizations():
    """Get all accessible organizations"""
    try:
        await meraki_connector.rate_limit("organizations")
        orgs = meraki_connector.dashboard.organizations.getOrganizations()
        
        return [
            OrganizationInfo(
                id=org['id'],
                name=org['name'],
                url=org.get('url'),
                api_enabled=org.get('api', {}).get('enabled', False),
                licensing_model=org.get('licensing', {}).get('model', 'unknown'),
                cloud_region_name=org.get('cloud', {}).get('region', {}).get('name', 'unknown')
            )
            for org in orgs
        ]
    except Exception as e:
        logger.error("Failed to get organizations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/networks", response_model=List[NetworkInfo])
async def get_networks(org_id: str):
    """Get all networks in an organization"""
    try:
        await meraki_connector.rate_limit("networks")
        networks = meraki_connector.dashboard.organizations.getOrganizationNetworks(org_id)
        
        return [
            NetworkInfo(
                id=net['id'],
                organization_id=net['organizationId'],
                name=net['name'],
                product_types=net.get('productTypes', []),
                timezone=net.get('timeZone', 'UTC'),
                tags=net.get('tags', [])
            )
            for net in networks
        ]
    except Exception as e:
        logger.error("Failed to get networks", org_id=org_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/networks/{network_id}/devices", response_model=List[NetworkDevice])
async def get_network_devices(network_id: str):
    """Get all devices in a network"""
    try:
        await meraki_connector.rate_limit("devices")
        devices = meraki_connector.dashboard.networks.getNetworkDevices(network_id)
        
        return [
            NetworkDevice(
                serial=device['serial'],
                model=device.get('model', 'unknown'),
                name=device.get('name'),
                mac=device.get('mac'),
                lan_ip=device.get('lanIp'),
                firmware=device.get('firmware'),
                network_id=network_id,
                status=device.get('status', 'unknown'),
                last_reported_at=datetime.fromisoformat(device['lastReportedAt'].replace('Z', '+00:00')) if device.get('lastReportedAt') else None
            )
            for device in devices
        ]
    except Exception as e:
        logger.error("Failed to get devices", network_id=network_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/networks/{network_id}/clients")
async def get_network_clients(network_id: str, timespan: int = 3600):
    """Get clients connected to a network"""
    try:
        await meraki_connector.rate_limit("clients")
        clients = meraki_connector.dashboard.networks.getNetworkClients(
            network_id, 
            timespan=timespan
        )
        return clients
    except Exception as e:
        logger.error("Failed to get clients", network_id=network_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/networks/{network_id}/traffic")
async def get_network_traffic(network_id: str, timespan: int = 3600):
    """Get network traffic analytics"""
    try:
        await meraki_connector.rate_limit("traffic")
        traffic = meraki_connector.dashboard.networks.getNetworkTrafficAnalysis(
            network_id,
            timespan=timespan
        )
        return traffic
    except Exception as e:
        logger.error("Failed to get traffic", network_id=network_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{serial}/status")
async def get_device_status(serial: str):
    """Get detailed status for a specific device"""
    try:
        await meraki_connector.rate_limit("device_status")
        status = meraki_connector.dashboard.devices.getDeviceStatus(serial)
        return status
    except Exception as e:
        logger.error("Failed to get device status", serial=serial, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai/discovery")
async def ai_discovery_endpoint(background_tasks: BackgroundTasks):
    """AI-powered network discovery for knowledge graph"""
    background_tasks.add_task(run_ai_discovery)
    return {"status": "discovery_started", "message": "AI network discovery initiated"}

async def run_ai_discovery():
    """Background task for AI-powered network discovery"""
    logger.info("Starting AI network discovery")
    try:
        # This will integrate with GenAI Stack and Neo4j
        discovery_data = {
            "timestamp": datetime.now().isoformat(),
            "organizations": [],
            "networks": [],
            "devices": [],
            "topology": []
        }
        
        # Get all organizations
        orgs = meraki_connector.dashboard.organizations.getOrganizations()
        for org in orgs:
            org_data = {
                "id": org['id'],
                "name": org['name'],
                "networks": []
            }
            
            # Get networks for this org
            networks = meraki_connector.dashboard.organizations.getOrganizationNetworks(org['id'])
            for network in networks:
                net_data = {
                    "id": network['id'],
                    "name": network['name'],
                    "devices": []
                }
                
                # Get devices for this network
                devices = meraki_connector.dashboard.networks.getNetworkDevices(network['id'])
                net_data["devices"] = devices
                
                org_data["networks"].append(net_data)
                
            discovery_data["organizations"].append(org_data)
        
        # TODO: Send to GenAI Stack for knowledge graph processing
        # TODO: Store in Neo4j
        # TODO: Create embeddings in Qdrant
        
        logger.info("AI network discovery completed", 
                   orgs_found=len(discovery_data["organizations"]))
                   
    except Exception as e:
        logger.error("AI discovery failed", error=str(e))

@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    # TODO: Implement Prometheus metrics
    return {"message": "Metrics endpoint - TODO: implement Prometheus integration"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11025)