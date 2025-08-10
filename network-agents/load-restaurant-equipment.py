#!/usr/bin/env python3
"""
Restaurant Equipment Neo4j Loader
Loads discovered endpoint devices into Neo4j for topology visualization

Features:
- Batch loading of endpoint devices
- Restaurant-specific device classification  
- Connection to infrastructure devices
- Performance optimization for large datasets
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RestaurantEquipmentLoader:
    """Load discovered restaurant equipment into Neo4j"""
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.batch_size = 100
        
    def load_endpoint_devices_from_files(self, data_directory: str = ".") -> Dict[str, Any]:
        """Load all endpoint device files and insert into Neo4j"""
        logger.info("🏭 RESTAURANT EQUIPMENT NEO4J LOADER")
        logger.info("=" * 60)
        
        results = {
            "files_processed": 0,
            "total_endpoint_devices": 0,
            "organizations_updated": 0,
            "processing_time": 0,
            "errors": []
        }
        
        start_time = time.time()
        
        # Find all endpoint device files
        data_path = Path(data_directory)
        endpoint_files = list(data_path.glob("endpoint_devices_*.json"))
        
        if not endpoint_files:
            logger.warning(f"No endpoint device files found in {data_directory}")
            return results
            
        logger.info(f"📁 Found {len(endpoint_files)} endpoint device files")
        
        for file_path in endpoint_files:
            try:
                logger.info(f"📄 Processing {file_path.name}...")
                
                with open(file_path, 'r') as f:
                    endpoint_data = json.load(f)
                
                # Load data into Neo4j
                org_results = self.load_organization_endpoints(endpoint_data)
                
                results["files_processed"] += 1
                results["total_endpoint_devices"] += org_results["endpoint_devices_loaded"]
                results["organizations_updated"] += 1
                
                logger.info(f"✅ Loaded {org_results['endpoint_devices_loaded']} devices for {endpoint_data.get('organization_name', 'Unknown')}")
                
            except Exception as e:
                error_msg = f"Failed to process {file_path.name}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                results["errors"].append(error_msg)
        
        results["processing_time"] = time.time() - start_time
        
        logger.info(f"\n📊 LOADING SUMMARY:")
        logger.info(f"   Files Processed: {results['files_processed']}")
        logger.info(f"   Total Endpoint Devices: {results['total_endpoint_devices']}")
        logger.info(f"   Organizations Updated: {results['organizations_updated']}")
        logger.info(f"   Processing Time: {results['processing_time']:.2f} seconds")
        logger.info(f"   Errors: {len(results['errors'])}")
        
        return results
    
    def load_organization_endpoints(self, endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load endpoint devices for a specific organization"""
        org_name = endpoint_data.get("organization_name", "Unknown")
        endpoint_devices = endpoint_data.get("endpoint_devices", [])
        
        if not endpoint_devices:
            return {"endpoint_devices_loaded": 0}
        
        # Process in batches for better performance
        devices_loaded = 0
        
        for i in range(0, len(endpoint_devices), self.batch_size):
            batch = endpoint_devices[i:i + self.batch_size]
            batch_loaded = self.load_endpoint_batch(org_name, batch)
            devices_loaded += batch_loaded
            
            if i % (self.batch_size * 10) == 0:  # Progress every 1000 devices
                logger.info(f"   📊 Loaded {devices_loaded}/{len(endpoint_devices)} devices...")
        
        return {"endpoint_devices_loaded": devices_loaded}
    
    def load_endpoint_batch(self, org_name: str, endpoint_batch: List[Dict[str, Any]]) -> int:
        """Load a batch of endpoint devices"""
        with self.driver.session() as session:
            return session.execute_write(self._create_endpoint_devices_tx, org_name, endpoint_batch)
    
    def _create_endpoint_devices_tx(self, tx, org_name: str, endpoint_batch: List[Dict[str, Any]]) -> int:
        """Transaction to create endpoint devices and connect to infrastructure"""
        devices_created = 0
        
        for device in endpoint_batch:
            try:
                # Create endpoint device node
                result = tx.run("""
                    MERGE (e:EndpointDevice {mac: $mac})
                    SET e.description = $description,
                        e.device_type = $device_type,
                        e.category = $category,
                        e.manufacturer = $manufacturer,
                        e.connection_type = $connection_type,
                        e.last_seen = $last_seen,
                        e.signal_strength = $signal_strength,
                        e.restaurant_function = $restaurant_function,
                        e.operational_priority = $operational_priority,
                        e.business_impact = $business_impact,
                        e.network_id = $network_id,
                        e.organization_name = $organization_name,
                        e.discovered_timestamp = datetime($discovered_timestamp),
                        e.updated_timestamp = datetime()
                    RETURN e.mac as mac
                """, {
                    "mac": device["mac"],
                    "description": device.get("description", "Unknown Device"),
                    "device_type": device.get("device_type", "unknown"),
                    "category": device.get("category", "endpoint"),
                    "manufacturer": device.get("manufacturer", "Unknown"),
                    "connection_type": device.get("connection_type", "wired"),
                    "last_seen": device.get("last_seen", ""),
                    "signal_strength": device.get("signal_strength", 0),
                    "restaurant_function": device.get("restaurant_function", "general"),
                    "operational_priority": device.get("operational_priority", "medium"),
                    "business_impact": device.get("business_impact", "medium"),
                    "network_id": device.get("network_id", ""),
                    "organization_name": org_name,
                    "discovered_timestamp": device.get("discovered_timestamp", datetime.now().isoformat())
                })
                
                if result.single():
                    devices_created += 1
                    
                    # Connect endpoint to infrastructure device (switch/AP)
                    if device.get("connected_device_serial"):
                        tx.run("""
                            MATCH (e:EndpointDevice {mac: $mac})
                            MATCH (d:Device {serial: $device_serial})
                            MERGE (d)-[:CONNECTS_TO]->(e)
                        """, {
                            "mac": device["mac"],
                            "device_serial": device["connected_device_serial"]
                        })
                    
                    # Connect endpoint to network
                    if device.get("network_id"):
                        tx.run("""
                            MATCH (e:EndpointDevice {mac: $mac})
                            MATCH (n:Network {id: $network_id})
                            MERGE (n)-[:HAS_ENDPOINT]->(e)
                        """, {
                            "mac": device["mac"],
                            "network_id": device["network_id"]
                        })
                
            except Exception as e:
                logger.error(f"Failed to create endpoint device {device.get('mac', 'Unknown')}: {e}")
                continue
        
        return devices_created
    
    def update_device_statistics(self):
        """Update device statistics and relationships"""
        logger.info("📊 Updating device statistics...")
        
        with self.driver.session() as session:
            # Update network endpoint counts
            session.run("""
                MATCH (n:Network)
                OPTIONAL MATCH (n)-[:HAS_ENDPOINT]->(e:EndpointDevice)
                SET n.endpoint_count = count(e)
            """)
            
            # Update organization endpoint counts
            session.run("""
                MATCH (o:Organization)
                OPTIONAL MATCH (o)-[:HAS_NETWORK]->(n:Network)-[:HAS_ENDPOINT]->(e:EndpointDevice)
                SET o.endpoint_count = count(e)
            """)
            
            # Update device endpoint counts (switches/APs)
            session.run("""
                MATCH (d:Device)
                OPTIONAL MATCH (d)-[:CONNECTS_TO]->(e:EndpointDevice)
                SET d.endpoint_count = count(e)
            """)
            
        logger.info("✅ Device statistics updated")
    
    def generate_endpoint_summary(self) -> Dict[str, Any]:
        """Generate summary of loaded endpoint devices"""
        with self.driver.session() as session:
            # Total counts
            total_result = session.run("""
                MATCH (e:EndpointDevice)
                RETURN count(e) as total_endpoints
            """).single()
            
            # By device type
            type_result = session.run("""
                MATCH (e:EndpointDevice)
                RETURN e.device_type as device_type, count(e) as count
                ORDER BY count DESC
            """)
            
            # By organization
            org_result = session.run("""
                MATCH (e:EndpointDevice)
                RETURN e.organization_name as organization, count(e) as count
                ORDER BY count DESC
            """)
            
            # By operational priority
            priority_result = session.run("""
                MATCH (e:EndpointDevice)
                RETURN e.operational_priority as priority, count(e) as count
                ORDER BY count DESC
            """)
            
            return {
                "total_endpoints": total_result["total_endpoints"] if total_result else 0,
                "by_device_type": [dict(record) for record in type_result],
                "by_organization": [dict(record) for record in org_result],
                "by_priority": [dict(record) for record in priority_result]
            }
    
    def close(self):
        """Close database connection"""
        self.driver.close()

async def main():
    """Main function to load restaurant equipment data"""
    loader = RestaurantEquipmentLoader()
    
    try:
        # Load endpoint devices from JSON files
        results = loader.load_endpoint_devices_from_files()
        
        if results["total_endpoint_devices"] > 0:
            # Update statistics
            loader.update_device_statistics()
            
            # Generate summary report
            summary = loader.generate_endpoint_summary()
            
            print(f"\n🎯 ENDPOINT DEVICE SUMMARY:")
            print(f"   Total Endpoint Devices: {summary['total_endpoints']}")
            
            if summary["by_device_type"]:
                print(f"\n   📱 By Device Type:")
                for item in summary["by_device_type"][:10]:  # Top 10
                    print(f"      {item['device_type']}: {item['count']}")
            
            if summary["by_organization"]:
                print(f"\n   🏢 By Organization:")
                for item in summary["by_organization"]:
                    print(f"      {item['organization']}: {item['count']}")
            
            if summary["by_priority"]:
                print(f"\n   ⚡ By Priority:")
                for item in summary["by_priority"]:
                    print(f"      {item['priority']}: {item['count']}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/tmp/restaurant_equipment_loading_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "loading_results": results,
                "endpoint_summary": summary if results["total_endpoint_devices"] > 0 else None,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: {results_file}")
        
    finally:
        loader.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())