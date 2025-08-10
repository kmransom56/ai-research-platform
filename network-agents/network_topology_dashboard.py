#!/usr/bin/env python3
"""
Network Topology Dashboard with Endpoint Device Integration
Interactive visualization of network infrastructure with restaurant equipment

Features:
- Real-time network topology maps
- Endpoint device visualization (POS, kiosks, kitchen equipment)
- Health status indicators
- Business impact analysis
- Interactive drill-down capabilities
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime, timedelta
from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class NetworkTopologyService:
    """Service for generating network topology data with endpoint devices"""
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    def get_network_topology(self, organization_filter: str = None) -> Dict[str, Any]:
        """Get complete network topology with endpoint devices"""
        with self.driver.session() as session:
            
            # Base query for network infrastructure - use actual relationship names in database
            infrastructure_query = """
            MATCH (o:Organization)
            OPTIONAL MATCH (o)-[:HAS_NETWORK]->(n:Network)
            OPTIONAL MATCH (n)-[:CONTAINS]->(d:Device)
            WHERE ($org_filter IS NULL OR o.name = $org_filter)
            RETURN o, n, d
            """
            
            result = session.run(infrastructure_query, {"org_filter": organization_filter})
            
            # Build topology structure
            topology = {
                "organizations": {},
                "network_stats": {
                    "total_organizations": 0,
                    "total_networks": 0,
                    "total_infrastructure_devices": 0,
                    "total_endpoint_devices": 0,
                    "device_health": {"healthy": 0, "warning": 0, "critical": 0}
                },
                "endpoint_breakdown": {
                    "pos_systems": 0,
                    "kitchen_displays": 0,
                    "kiosks": 0,
                    "drive_thru_equipment": 0,
                    "menu_boards": 0,
                    "printers": 0,
                    "security_cameras": 0,
                    "unknown_devices": 0
                }
            }
            
            for record in result:
                org = record.get("o")
                network = record.get("n") 
                device = record.get("d")
                # endpoint = record.get("e")  # Not available yet
                
                if org:
                    org_id = org["id"]
                    if org_id not in topology["organizations"]:
                        topology["organizations"][org_id] = {
                            "id": org_id,
                            "name": org["name"],
                            "networks": {},
                            "org_stats": {
                                "networks": 0,
                                "infrastructure_devices": 0,
                                "endpoint_devices": 0,
                                "health_score": 0
                            }
                        }
                        topology["network_stats"]["total_organizations"] += 1
                    
                    org_data = topology["organizations"][org_id]
                    
                    if network:
                        network_id = network["id"]
                        if network_id not in org_data["networks"]:
                            org_data["networks"][network_id] = {
                                "id": network_id,
                                "name": network["name"],
                                "devices": {},
                                "network_stats": {
                                    "infrastructure_devices": 0,
                                    "endpoint_devices": 0,
                                    "health_score": 0
                                }
                            }
                            org_data["org_stats"]["networks"] += 1
                            topology["network_stats"]["total_networks"] += 1
                        
                        network_data = org_data["networks"][network_id]
                        
                        if device:
                            device_serial = device["serial"]
                            if device_serial not in network_data["devices"]:
                                health_score = device.get("health_score", 0)
                                health_status = self.get_health_status(health_score)
                                
                                network_data["devices"][device_serial] = {
                                    "serial": device_serial,
                                    "name": device.get("name", ""),
                                    "model": device.get("model", ""),
                                    "product_type": device.get("product_type", ""),
                                    "health_score": health_score,
                                    "health_status": health_status,
                                    "status": device.get("status", "unknown"),
                                    "endpoint_devices": [],
                                    "device_type": self.classify_infrastructure_device(device)
                                }
                                
                                network_data["network_stats"]["infrastructure_devices"] += 1
                                org_data["org_stats"]["infrastructure_devices"] += 1
                                topology["network_stats"]["total_infrastructure_devices"] += 1
                                topology["network_stats"]["device_health"][health_status] += 1
                            
                            # Endpoint devices will be loaded later - for now just show infrastructure
                            # device_data = network_data["devices"][device_serial]
            
            # Calculate organization health scores
            for org_data in topology["organizations"].values():
                if org_data["org_stats"]["infrastructure_devices"] > 0:
                    # Calculate average health across all devices in organization
                    total_health = 0
                    device_count = 0
                    
                    for network_data in org_data["networks"].values():
                        for device_data in network_data["devices"].values():
                            total_health += device_data["health_score"]
                            device_count += 1
                    
                    org_data["org_stats"]["health_score"] = total_health / device_count if device_count > 0 else 0
            
            return topology
    
    def get_health_status(self, health_score: float) -> str:
        """Convert health score to status category"""
        if health_score >= 95:
            return "healthy"
        elif health_score >= 80:
            return "warning"
        else:
            return "critical"
    
    def classify_infrastructure_device(self, device: Dict[str, Any]) -> str:
        """Classify infrastructure device type"""
        model = device.get("model", "").upper()
        product_type = device.get("product_type", "").lower()
        
        if model.startswith("MX") or "appliance" in product_type:
            return "security_appliance"
        elif model.startswith("MS") or "switch" in product_type:
            return "switch"
        elif model.startswith("MR") or "wireless" in product_type:
            return "wireless_access_point"
        elif model.startswith("MC") or "camera" in product_type:
            return "security_camera"
        else:
            return "network_device"
    
    def get_network_map_data(self, organization_id: str = None) -> Dict[str, Any]:
        """Get network map visualization data"""
        topology = self.get_network_topology(organization_id)
        
        # Convert to visualization format
        nodes = []
        edges = []
        node_id_counter = 0
        
        for org_id, org_data in topology["organizations"].items():
            # Organization node
            org_node_id = f"org_{org_id}"
            nodes.append({
                "id": org_node_id,
                "label": org_data["name"],
                "type": "organization",
                "size": 40,
                "color": "#1f77b4",
                "health_score": org_data["org_stats"]["health_score"],
                "stats": org_data["org_stats"]
            })
            
            for network_id, network_data in org_data["networks"].items():
                # Network node
                network_node_id = f"net_{network_id}"
                nodes.append({
                    "id": network_node_id,
                    "label": network_data["name"],
                    "type": "network",
                    "size": 30,
                    "color": "#ff7f0e",
                    "stats": network_data["network_stats"]
                })
                
                # Edge from org to network
                edges.append({
                    "source": org_node_id,
                    "target": network_node_id,
                    "type": "owns"
                })
                
                for device_serial, device_data in network_data["devices"].items():
                    # Infrastructure device node
                    device_node_id = f"dev_{device_serial}"
                    
                    # Color by device type
                    device_colors = {
                        "security_appliance": "#d62728",
                        "switch": "#2ca02c", 
                        "wireless_access_point": "#9467bd",
                        "security_camera": "#8c564b",
                        "network_device": "#e377c2"
                    }
                    
                    device_color = device_colors.get(device_data["device_type"], "#7f7f7f")
                    
                    # Size by health status
                    health_sizes = {"healthy": 25, "warning": 20, "critical": 15}
                    device_size = health_sizes.get(device_data["health_status"], 20)
                    
                    nodes.append({
                        "id": device_node_id,
                        "label": f"{device_data['name']}\n({device_data['model']})",
                        "type": "infrastructure_device",
                        "device_type": device_data["device_type"],
                        "size": device_size,
                        "color": device_color,
                        "health_score": device_data["health_score"],
                        "health_status": device_data["health_status"],
                        "endpoint_count": len(device_data["endpoint_devices"])
                    })
                    
                    # Edge from network to device
                    edges.append({
                        "source": network_node_id,
                        "target": device_node_id,
                        "type": "contains"
                    })
                    
                    # Endpoint device nodes
                    for endpoint in device_data["endpoint_devices"]:
                        endpoint_node_id = f"endpoint_{endpoint['mac']}"
                        
                        # Color by restaurant function
                        endpoint_colors = {
                            "pos": "#ff6b35",           # Orange for POS
                            "kitchen_display": "#2ecc71", # Green for kitchen
                            "kiosk": "#3498db",         # Blue for kiosks
                            "drive_thru": "#e74c3c",    # Red for drive-thru
                            "menu_board": "#9b59b6",    # Purple for menu boards
                            "printer": "#f39c12",       # Yellow for printers
                            "security_camera": "#34495e", # Dark for cameras
                            "unknown": "#95a5a6"        # Gray for unknown
                        }
                        
                        endpoint_color = endpoint_colors.get(endpoint["device_type"], "#95a5a6")
                        
                        # Size by operational priority
                        priority_sizes = {"critical": 20, "high": 15, "medium": 12, "low": 8}
                        endpoint_size = priority_sizes.get(endpoint["operational_priority"], 10)
                        
                        nodes.append({
                            "id": endpoint_node_id,
                            "label": endpoint["description"],
                            "type": "endpoint_device",
                            "device_type": endpoint["device_type"],
                            "category": endpoint["category"],
                            "restaurant_function": endpoint["restaurant_function"],
                            "size": endpoint_size,
                            "color": endpoint_color,
                            "operational_priority": endpoint["operational_priority"],
                            "connection_type": endpoint["connection_type"]
                        })
                        
                        # Edge from infrastructure device to endpoint
                        edges.append({
                            "source": device_node_id,
                            "target": endpoint_node_id,
                            "type": "connects"
                        })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": topology["network_stats"],
            "endpoint_breakdown": topology["endpoint_breakdown"]
        }

# Initialize service
topology_service = NetworkTopologyService()

@app.route('/')
def dashboard():
    """Main network topology dashboard"""
    return render_template('network_topology_dashboard.html')

@app.route('/api/topology')
def get_topology():
    """API endpoint for network topology data"""
    organization_filter = request.args.get('organization')
    try:
        topology = topology_service.get_network_topology(organization_filter)
        return jsonify({
            "success": True,
            "data": topology
        })
    except Exception as e:
        logger.error(f"Error getting topology: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/network-map')
def get_network_map():
    """API endpoint for network map visualization data"""
    organization_id = request.args.get('organization_id')
    try:
        map_data = topology_service.get_network_map_data(organization_id)
        return jsonify({
            "success": True,
            "data": map_data
        })
    except Exception as e:
        logger.error(f"Error getting network map: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/organizations')
def get_organizations():
    """API endpoint for organization list"""
    try:
        with topology_service.driver.session() as session:
            result = session.run("MATCH (o:Organization) RETURN o.id as id, o.name as name ORDER BY o.name")
            organizations = [{"id": record["id"], "name": record["name"]} for record in result]
        
        return jsonify({
            "success": True,
            "data": organizations
        })
    except Exception as e:
        logger.error(f"Error getting organizations: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health-summary')
def get_health_summary():
    """API endpoint for network health summary"""
    try:
        with topology_service.driver.session() as session:
            # Infrastructure device health
            device_health = session.run("""
                MATCH (d:Device)
                RETURN 
                    count(CASE WHEN d.health_score >= 95 THEN 1 END) as healthy,
                    count(CASE WHEN d.health_score >= 80 AND d.health_score < 95 THEN 1 END) as warning,
                    count(CASE WHEN d.health_score < 80 THEN 1 END) as critical,
                    avg(d.health_score) as avg_health
            """).single()
            
            # Endpoint device summary - check if EndpointDevice nodes exist
            try:
                endpoint_summary = session.run("""
                    MATCH (e:EndpointDevice)
                    RETURN 
                        e.device_type as type,
                        count(e) as count,
                        count(CASE WHEN e.operational_priority = 'critical' THEN 1 END) as critical_count
                    ORDER BY count DESC
                """)
            except Exception:
                # EndpointDevice nodes don't exist yet
                endpoint_summary = []
            
            endpoint_data = [dict(record) for record in endpoint_summary]
            
            return jsonify({
                "success": True,
                "data": {
                    "infrastructure_health": dict(device_health) if device_health else {},
                    "endpoint_breakdown": endpoint_data
                }
            })
    except Exception as e:
        logger.error(f"Error getting health summary: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🗺️  NETWORK TOPOLOGY DASHBOARD")
    print("Interactive visualization with endpoint device integration")
    print("=" * 60)
    print("🌐 Access at: http://localhost:11050")
    print("📊 Features:")
    print("   - Real-time network topology maps")
    print("   - Restaurant equipment visualization")  
    print("   - Health status indicators")
    print("   - Business impact analysis")
    print("   - Interactive drill-down")
    
    app.run(host='0.0.0.0', port=11050, debug=False)