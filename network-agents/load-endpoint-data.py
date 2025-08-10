#!/usr/bin/env python3
"""
Load endpoint device data from discovery into Neo4j
Quick loader for the discovered restaurant equipment data
"""

import json
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_endpoint_data():
    """Load endpoint device data into Neo4j"""
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    
    try:
        with open("/tmp/endpoint_devices_20250809_222609.json", 'r') as f:
            data = json.load(f)
        
        total_devices = 0
        
        with driver.session() as session:
            for org in data["organizations"]:
                org_name = org["name"]
                
                for network in org["networks"]:
                    network_id = network["id"]
                    
                    for endpoint in network.get("endpoint_devices", []):
                        # Create endpoint device node
                        session.run("""
                            MERGE (e:EndpointDevice {mac: $mac})
                            SET e.description = $description,
                                e.device_type = $device_type,
                                e.category = $category,
                                e.manufacturer = $manufacturer,
                                e.connection_type = $connection_type,
                                e.restaurant_function = $restaurant_function,
                                e.operational_priority = $operational_priority,
                                e.network_id = $network_id,
                                e.organization_name = $organization_name,
                                e.updated_timestamp = datetime()
                        """, {
                            "mac": endpoint["mac"],
                            "description": endpoint.get("description", "Unknown Device"),
                            "device_type": endpoint.get("device_type", "unknown"),
                            "category": endpoint.get("category", "endpoint"),
                            "manufacturer": endpoint.get("manufacturer", "Unknown"),
                            "connection_type": endpoint.get("connection_type", "wireless"),
                            "restaurant_function": endpoint.get("restaurant_function", "unclassified"),
                            "operational_priority": endpoint.get("operational_priority", "medium"),
                            "network_id": network_id,
                            "organization_name": org_name
                        })
                        
                        total_devices += 1
                        
                        if total_devices % 1000 == 0:
                            logger.info(f"Loaded {total_devices} endpoint devices...")
        
        logger.info(f"✅ Successfully loaded {total_devices} endpoint devices into Neo4j")
        
    finally:
        driver.close()

if __name__ == "__main__":
    load_endpoint_data()