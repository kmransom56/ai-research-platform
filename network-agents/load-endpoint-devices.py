#!/usr/bin/env python3
"""
Load Restaurant Endpoint Devices into Neo4j
Creates relationships between network infrastructure and restaurant equipment
"""

import json
import os
import glob
from neo4j import GraphDatabase
from datetime import datetime
from typing import Dict, List, Any

class EndpointDeviceLoader:
    """
    Load endpoint devices (POS, kiosks, kitchen equipment) into Neo4j
    """
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.batch_size = 1000  # Process endpoints in batches
        
    def load_endpoint_topology_file(self, filename: str) -> Dict[str, Any]:
        """Load endpoint topology data from JSON file"""
        print(f"📂 Loading endpoint device data from: {filename}")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Loaded endpoint data:")
            print(f"   🏢 Organizations: {len(data['organizations'])}")
            print(f"   🌐 Networks Scanned: {data['total_stats']['networks_scanned']}")
            print(f"   📱 Endpoint Devices: {data['total_stats']['total_endpoints']}")
            print(f"   🔌 Wired: {data['total_stats']['connection_types']['wired']}")
            print(f"   📶 Wireless: {data['total_stats']['connection_types']['wireless']}")
            
            return data
            
        except Exception as e:
            print(f"❌ Failed to load endpoint topology file: {e}")
            return None
    
    def create_endpoint_indexes(self):
        """Create indexes for endpoint devices"""
        print("🔍 Creating indexes for endpoint devices...")
        
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX endpoint_mac IF NOT EXISTS FOR (e:EndpointDevice) ON (e.mac)",
                "CREATE INDEX endpoint_type IF NOT EXISTS FOR (e:EndpointDevice) ON (e.device_type)",
                "CREATE INDEX endpoint_function IF NOT EXISTS FOR (e:EndpointDevice) ON (e.restaurant_function)",
                "CREATE INDEX endpoint_network IF NOT EXISTS FOR (e:EndpointDevice) ON (e.network_id)",
                "CREATE INDEX endpoint_status IF NOT EXISTS FOR (e:EndpointDevice) ON (e.status)"
            ]
            
            for index_query in indexes:
                try:
                    session.run(index_query)
                except:
                    pass  # Index might already exist
        
        print("✅ Endpoint device indexes created")
    
    def load_endpoint_devices_batch(self, endpoint_devices: List[Dict[str, Any]], org_name: str):
        """Load a batch of endpoint devices into Neo4j"""
        
        with self.driver.session() as session:
            # Create endpoint devices
            session.run("""
                UNWIND $devices as device
                CREATE (e:EndpointDevice {
                    mac: device.mac,
                    description: device.description,
                    ip: device.ip,
                    ip6: device.ip6,
                    user: device.user,
                    first_seen: datetime(device.first_seen),
                    last_seen: datetime(device.last_seen),
                    manufacturer: device.manufacturer,
                    os: device.os,
                    device_type: device.device_type,
                    category: device.category,
                    confidence: device.confidence,
                    restaurant_function: device.restaurant_function,
                    network_id: device.network_id,
                    network_name: device.network_name,
                    connection_type: device.connection_type,
                    connected_device: device.connected_device,
                    vlan: device.vlan,
                    ssid: device.ssid,
                    usage_mb: device.usage_mb,
                    status: device.status,
                    organization_name: device.organization_name,
                    discovery_timestamp: datetime()
                })
            """, {"devices": endpoint_devices})
            
            # Create relationships to networks
            session.run("""
                MATCH (n:Network)
                MATCH (e:EndpointDevice {network_id: n.id})
                WHERE NOT (n)-[:HOSTS]->(e)
                CREATE (n)-[:HOSTS]->(e)
            """)
            
            # Create relationships to connected infrastructure devices
            session.run("""
                MATCH (d:Device)
                MATCH (e:EndpointDevice {connected_device: d.serial})
                WHERE NOT (d)-[:CONNECTS]->(e)
                CREATE (d)-[:CONNECTS]->(e)
            """)
            
            # Create relationships to organizations
            session.run("""
                MATCH (o:Organization {name: $org_name})
                MATCH (e:EndpointDevice {organization_name: $org_name})
                WHERE NOT (o)-[:HAS_ENDPOINT]->(e)
                CREATE (o)-[:HAS_ENDPOINT]->(e)
            """, {"org_name": org_name})
    
    def create_restaurant_equipment_categories(self):
        """Create equipment category nodes for better organization"""
        print("🍴 Creating restaurant equipment categories...")
        
        with self.driver.session() as session:
            # Create equipment category nodes
            categories = [
                {"type": "pos", "name": "Point of Sale Systems", "function": "Order Processing & Payment", "criticality": "high"},
                {"type": "kiosk", "name": "Self-Service Kiosks", "function": "Customer Self-Service", "criticality": "medium"},
                {"type": "kitchen_display", "name": "Kitchen Display Systems", "function": "Food Preparation", "criticality": "high"},
                {"type": "drive_thru", "name": "Drive-Thru Equipment", "function": "Drive-Thru Operations", "criticality": "high"},
                {"type": "menu_board", "name": "Digital Menu Boards", "function": "Customer Information", "criticality": "medium"},
                {"type": "printer", "name": "Receipt & Label Printers", "function": "Receipt & Documentation", "criticality": "medium"},
                {"type": "security_camera", "name": "Security Cameras", "function": "Security & Monitoring", "criticality": "low"},
                {"type": "back_office", "name": "Back Office Systems", "function": "Management & Administration", "criticality": "medium"},
                {"type": "wifi_device", "name": "Mobile & WiFi Devices", "function": "Staff Mobile Operations", "criticality": "low"}
            ]
            
            session.run("""
                UNWIND $categories as cat
                CREATE (ec:EquipmentCategory {
                    type: cat.type,
                    name: cat.name,
                    function: cat.function,
                    criticality: cat.criticality
                })
            """, {"categories": categories})
            
            # Create relationships from endpoints to categories
            session.run("""
                MATCH (e:EndpointDevice)
                MATCH (ec:EquipmentCategory {type: e.device_type})
                WHERE NOT (e)-[:BELONGS_TO]->(ec)
                CREATE (e)-[:BELONGS_TO]->(ec)
            """)
        
        print("✅ Equipment categories created")
    
    def load_complete_endpoint_topology(self, endpoint_data: Dict[str, Any]):
        """Load complete endpoint device topology"""
        print(f"🚀 LOADING RESTAURANT ENDPOINT DEVICES INTO NEO4J")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Create indexes
        self.create_endpoint_indexes()
        
        # Load endpoint devices by organization
        total_endpoints = 0
        
        for org in endpoint_data["organizations"]:
            if org["endpoint_stats"]["total_endpoints"] == 0:
                continue
                
            org_name = org["name"]
            print(f"\n📊 Processing {org_name}...")
            
            # Collect all endpoint devices for this organization
            all_endpoints = []
            for network in org["networks"]:
                for endpoint in network["endpoint_devices"]:
                    endpoint["organization_name"] = org_name
                    all_endpoints.append(endpoint)
            
            # Process endpoints in batches
            for i in range(0, len(all_endpoints), self.batch_size):
                endpoint_batch = all_endpoints[i:i+self.batch_size]
                self.load_endpoint_devices_batch(endpoint_batch, org_name)
                
                print(f"   ✅ Batch {i//self.batch_size + 1}: {len(endpoint_batch)} endpoint devices")
            
            total_endpoints += len(all_endpoints)
        
        # Create equipment categories
        self.create_restaurant_equipment_categories()
        
        # Create summary statistics
        self.create_endpoint_analytics(endpoint_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n🎉 ENDPOINT DEVICE LOADING COMPLETED!")
        print("=" * 40)
        print(f"✅ Organizations: {len(endpoint_data['organizations'])}")
        print(f"✅ Networks: {endpoint_data['total_stats']['networks_scanned']}")
        print(f"✅ Endpoint Devices: {total_endpoints:,}")
        print(f"⏱️ Loading time: {duration:.2f} seconds")
        
        # Verify the data
        self.verify_endpoint_data()
    
    def create_endpoint_analytics(self, endpoint_data: Dict[str, Any]):
        """Create analytics for endpoint devices"""
        print("📈 Creating endpoint device analytics...")
        
        with self.driver.session() as session:
            # Add operational status based on device type and usage
            session.run("""
                MATCH (e:EndpointDevice)
                SET e.operational_priority = CASE e.device_type
                    WHEN 'pos' THEN 'critical'
                    WHEN 'kitchen_display' THEN 'critical' 
                    WHEN 'drive_thru' THEN 'critical'
                    WHEN 'kiosk' THEN 'high'
                    WHEN 'printer' THEN 'high'
                    WHEN 'menu_board' THEN 'medium'
                    WHEN 'back_office' THEN 'medium'
                    WHEN 'security_camera' THEN 'low'
                    WHEN 'wifi_device' THEN 'low'
                    ELSE 'medium'
                END,
                e.troubleshoot_priority = CASE 
                    WHEN e.device_type IN ['pos', 'kitchen_display', 'drive_thru'] THEN 1
                    WHEN e.device_type IN ['kiosk', 'printer'] THEN 2
                    WHEN e.device_type IN ['menu_board', 'back_office'] THEN 3
                    ELSE 4
                END
            """)
            
            # Mark devices that may need attention based on usage patterns
            session.run("""
                MATCH (e:EndpointDevice)
                WHERE e.last_seen < datetime() - duration('P1D')
                SET e.status = 'offline',
                    e.alert_level = 'warning'
            """)
            
            # Mark high-usage devices
            session.run("""
                MATCH (e:EndpointDevice)
                WHERE e.usage_mb > 1000
                SET e.usage_level = 'high'
            """)
        
        print("✅ Endpoint analytics created")
    
    def verify_endpoint_data(self):
        """Verify the loaded endpoint data"""
        print("\n🔍 VERIFYING ENDPOINT DEVICE DATA:")
        print("-" * 30)
        
        with self.driver.session() as session:
            # Count total endpoints
            result = session.run("MATCH (e:EndpointDevice) RETURN count(e) as count")
            endpoint_count = result.single()["count"]
            print(f"📱 Total Endpoints: {endpoint_count:,}")
            
            # Count by device type
            result = session.run("""
                MATCH (e:EndpointDevice)
                RETURN e.device_type as type, count(e) as count
                ORDER BY count DESC
            """)
            
            print(f"\n🍴 Restaurant Equipment by Type:")
            for record in result:
                device_type = record['type'].replace('_', ' ').title()
                print(f"   {device_type}: {record['count']:,} devices")
            
            # Count by organization
            result = session.run("""
                MATCH (o:Organization)
                OPTIONAL MATCH (o)-[:HAS_ENDPOINT]->(e:EndpointDevice)
                RETURN o.name as org, count(e) as endpoints
                ORDER BY endpoints DESC
            """)
            
            print(f"\n🏢 Endpoints by Organization:")
            for record in result:
                if record['endpoints'] > 0:
                    print(f"   {record['org']}: {record['endpoints']:,} endpoint devices")
            
            # Count by restaurant function
            result = session.run("""
                MATCH (e:EndpointDevice)
                RETURN e.restaurant_function as function, count(e) as count
                ORDER BY count DESC
                LIMIT 5
            """)
            
            print(f"\n🏪 Top Restaurant Functions:")
            for record in result:
                print(f"   {record['function']}: {record['count']:,} devices")
            
            # Count critical equipment
            result = session.run("""
                MATCH (e:EndpointDevice)
                WHERE e.operational_priority = 'critical'
                RETURN count(e) as critical_count
            """)
            
            critical_count = result.single()["critical_count"]
            print(f"\n⚠️ Critical Restaurant Equipment: {critical_count:,} devices")
            print("   (POS systems, Kitchen displays, Drive-thru equipment)")
    
    def close(self):
        """Close the Neo4j connection"""
        self.driver.close()

async def main():
    """Main function to load endpoint devices"""
    print("🍴 LOADING RESTAURANT ENDPOINT DEVICES INTO NEO4J")
    print("=" * 60)
    
    # Find the most recent endpoint topology file
    endpoint_files = glob.glob("/tmp/endpoint_devices_*.json")
    
    if not endpoint_files:
        print("❌ No endpoint device files found!")
        print("   Run: python3 discover-endpoint-devices.py first")
        return
    
    # Use the most recent file
    latest_file = max(endpoint_files, key=os.path.getctime)
    print(f"📂 Using endpoint file: {latest_file}")
    
    # Load and process the data
    loader = EndpointDeviceLoader()
    
    try:
        # Load endpoint data
        endpoint_data = loader.load_endpoint_topology_file(latest_file)
        
        if endpoint_data:
            # Load into Neo4j
            loader.load_complete_endpoint_topology(endpoint_data)
            
            print(f"\n🌟 SUCCESS! Restaurant endpoint devices loaded into Neo4j")
            print(f"🌐 Access Neo4j Browser: http://localhost:7474")
            print(f"🔑 Credentials: neo4j / password")
            
            print(f"\n💡 Sample Queries for Restaurant Equipment:")
            print("   // All POS systems by location")
            print("   MATCH (e:EndpointDevice {device_type: 'pos'}) RETURN e.network_name, count(e)")
            print()
            print("   // Kitchen equipment needing attention")
            print("   MATCH (e:EndpointDevice) WHERE e.device_type = 'kitchen_display' AND e.status = 'offline'")
            print("   RETURN e.network_name, e.description")
            print()
            print("   // Critical restaurant equipment")
            print("   MATCH (e:EndpointDevice) WHERE e.operational_priority = 'critical'")
            print("   RETURN e.device_type, e.restaurant_function, count(e)")
        else:
            print("❌ Failed to load endpoint data")
            
    finally:
        loader.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())