#!/usr/bin/env python3
"""
Discover Switch Port Client Devices from Meraki Dashboard
Pulls connected device information from switch ports to identify:
- POS terminals and payment systems
- Kitchen display systems and printers  
- Kiosks and self-service terminals
- Drive-thru equipment and timers
- Digital menu boards and signage
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Any
from datetime import datetime, timedelta
import os
import glob

class SwitchClientDiscovery:
    """
    Discover client devices connected to Meraki switches
    """
    
    def __init__(self):
        self.api_key = os.getenv('MERAKI_API_KEY', 'fd3b9969d25792d90f0789a7e28cc661c81e2150')
        self.base_url = "https://api.meraki.com/api/v1"
        self.headers = {
            'X-Cisco-Meraki-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.session = None
        
        # Enhanced restaurant device classification patterns
        self.device_classifiers = {
            'pos_system': {
                'name_patterns': ['pos', 'register', 'terminal', 'payment', 'aloha', 'micros', 'toast', 'square', 'clover'],
                'mac_patterns': ['00:0C:29', '00:50:56', '00:1B:21'],  # Common POS MAC prefixes
                'manufacturer_patterns': ['aloha', 'micros', 'toast', 'square', 'ncr', 'diebold'],
                'confidence_boost': 40,
                'criticality': 'critical'
            },
            'kitchen_display': {
                'name_patterns': ['kds', 'kitchen', 'display', 'bump', 'expo', 'prep', 'cook'],
                'mac_patterns': ['00:1B:21', '00:0F:EA', '08:00:11'],
                'manufacturer_patterns': ['kitchen', 'display', 'bump'],
                'confidence_boost': 35,
                'criticality': 'critical'
            },
            'self_service_kiosk': {
                'name_patterns': ['kiosk', 'self-order', 'self-service', 'ordering', 'customer'],
                'mac_patterns': ['AC:1F:6B', '00:15:5D'],
                'manufacturer_patterns': ['kiosk', 'self-service'],
                'confidence_boost': 30,
                'criticality': 'high'
            },
            'drive_thru_equipment': {
                'name_patterns': ['drive', 'thru', 'dt', 'timer', 'speaker', 'headset'],
                'mac_patterns': ['00:04:20', '00:30:18'],
                'manufacturer_patterns': ['drive-thru', 'timer', 'speaker'],
                'confidence_boost': 35,
                'criticality': 'critical'
            },
            'receipt_printer': {
                'name_patterns': ['printer', 'receipt', 'zebra', 'epson', 'star', 'print'],
                'mac_patterns': ['00:07:61', '00:22:58', '08:00:11'],
                'manufacturer_patterns': ['zebra', 'epson', 'star', 'brother'],
                'confidence_boost': 25,
                'criticality': 'high'
            },
            'digital_menu_board': {
                'name_patterns': ['menu', 'board', 'digital', 'signage', 'display-board'],
                'mac_patterns': ['00:22:5F', '00:1D:7D'],
                'manufacturer_patterns': ['samsung', 'lg', 'philips'],
                'confidence_boost': 20,
                'criticality': 'medium'
            },
            'security_camera': {
                'name_patterns': ['camera', 'security', 'surveillance', 'video', 'dvr', 'nvr'],
                'mac_patterns': ['00:12:AC', '00:40:8C'],
                'manufacturer_patterns': ['axis', 'bosch', 'hikvision'],
                'confidence_boost': 15,
                'criticality': 'low'
            },
            'back_office_pc': {
                'name_patterns': ['office', 'manager', 'admin', 'pc', 'computer', 'workstation'],
                'mac_patterns': ['00:0C:29', '00:50:56'],
                'manufacturer_patterns': ['dell', 'hp', 'lenovo'],
                'confidence_boost': 10,
                'criticality': 'medium'
            }
        }
    
    async def initialize_session(self):
        """Initialize async HTTP session"""
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=20)
        timeout = aiohttp.ClientTimeout(total=45)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )
    
    async def close_session(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    def classify_client_device(self, client: Dict[str, Any]) -> Dict[str, Any]:
        """Classify client device based on available information"""
        
        # Extract device information
        description = (client.get('description') or client.get('dhcpHostname') or '').lower()
        mac = (client.get('mac') or '').upper()
        manufacturer = (client.get('manufacturer') or '').lower()
        user = (client.get('user') or '').lower()
        
        best_classification = {
            'device_type': 'unknown_endpoint',
            'category': 'Unclassified Device',
            'confidence': 0,
            'criticality': 'low',
            'restaurant_function': 'Unknown'
        }
        
        # Test each classifier
        for device_type, classifier in self.device_classifiers.items():
            confidence = 0
            
            # Check name patterns
            for pattern in classifier['name_patterns']:
                if pattern in description or pattern in user:
                    confidence += 20
            
            # Check MAC patterns
            for pattern in classifier['mac_patterns']:
                if mac.startswith(pattern):
                    confidence += 30
            
            # Check manufacturer patterns
            for pattern in classifier['manufacturer_patterns']:
                if pattern in manufacturer:
                    confidence += classifier['confidence_boost']
            
            # Special scoring rules
            if device_type == 'pos_system':
                if any(term in description for term in ['reg', 'terminal', 'payment']):
                    confidence += 15
                if any(term in manufacturer for term in ['ncr', 'diebold', 'micros']):
                    confidence += 25
            
            elif device_type == 'kitchen_display':
                if any(term in description for term in ['kds', 'bump', 'expo']):
                    confidence += 20
            
            elif device_type == 'receipt_printer':
                if any(term in manufacturer for term in ['zebra', 'epson', 'star']):
                    confidence += 20
            
            # Update if this is the best match
            if confidence > best_classification['confidence']:
                best_classification = {
                    'device_type': device_type,
                    'category': device_type.replace('_', ' ').title(),
                    'confidence': confidence,
                    'criticality': classifier['criticality'],
                    'restaurant_function': self.get_restaurant_function(device_type)
                }
        
        return best_classification
    
    def get_restaurant_function(self, device_type: str) -> str:
        """Map device type to restaurant business function"""
        function_map = {
            'pos_system': 'Payment Processing',
            'kitchen_display': 'Food Preparation',
            'self_service_kiosk': 'Customer Self-Service',
            'drive_thru_equipment': 'Drive-Thru Operations',
            'receipt_printer': 'Order Documentation',
            'digital_menu_board': 'Customer Information',
            'security_camera': 'Security & Monitoring',
            'back_office_pc': 'Management Systems'
        }
        return function_map.get(device_type, 'General Operations')
    
    async def discover_switch_clients(self, device_serial: str, device_name: str, network_id: str, network_name: str, org_name: str) -> List[Dict[str, Any]]:
        """Discover all client devices connected to a specific switch"""
        try:
            # Get switch port statuses to find connected clients
            async with self.session.get(f"{self.base_url}/devices/{device_serial}/switch/ports/statuses") as response:
                if response.status == 200:
                    port_statuses = await response.json()
                    
                    # Get network clients to correlate with switch ports
                    async with self.session.get(f"{self.base_url}/networks/{network_id}/clients?timespan=2592000") as client_response:
                        if client_response.status == 200:
                            network_clients = await client_response.json()
                            
                            # Process connected clients
                            switch_clients = []
                            
                            for client in network_clients:
                                # Check if client is connected to this switch
                                recent_device = client.get('recentDeviceSerial')
                                if recent_device == device_serial:
                                    
                                    # Classify the client device
                                    classification = self.classify_client_device(client)
                                    
                                    # Create comprehensive client record
                                    client_device = {
                                        # Basic device info
                                        'mac': client.get('mac', ''),
                                        'description': client.get('description') or client.get('dhcpHostname') or f"Device_{client.get('mac', 'unknown')}",
                                        'manufacturer': client.get('manufacturer', ''),
                                        'user': client.get('user', ''),
                                        
                                        # Network info
                                        'ip': client.get('ip', ''),
                                        'ip6': client.get('ip6', ''),
                                        'vlan': client.get('vlan', ''),
                                        
                                        # Connection info
                                        'switch_serial': device_serial,
                                        'switch_name': device_name,
                                        'network_id': network_id,
                                        'network_name': network_name,
                                        'organization_name': org_name,
                                        
                                        # Timing info
                                        'first_seen': client.get('firstSeen', ''),
                                        'last_seen': client.get('lastSeen', ''),
                                        
                                        # Usage info
                                        'usage_kb': (client.get('usage', {}).get('recv', 0) + client.get('usage', {}).get('sent', 0)) if client.get('usage') else 0,
                                        'status': client.get('status', 'active'),
                                        
                                        # Classification
                                        'device_type': classification['device_type'],
                                        'category': classification['category'],
                                        'confidence': classification['confidence'],
                                        'criticality': classification['criticality'],
                                        'restaurant_function': classification['restaurant_function'],
                                        
                                        # Additional metadata
                                        'os': client.get('os', ''),
                                        'ssid': client.get('ssid', ''),  # If wireless client
                                        'connection_type': 'wired',  # Connected to switch
                                        'discovery_timestamp': datetime.now().isoformat()
                                    }
                                    
                                    switch_clients.append(client_device)
                            
                            return switch_clients
                        else:
                            return []
                else:
                    return []
                    
        except Exception as e:
            print(f"   ❌ Error getting clients for switch {device_name}: {e}")
            return []
    
    async def discover_all_switch_clients(self) -> Dict[str, Any]:
        """Discover client devices connected to all switches in the enterprise"""
        print("🔌 DISCOVERING SWITCH CLIENT DEVICES")
        print("Finding POS systems, kitchen equipment, and restaurant devices...")
        print("=" * 70)
        
        start_time = datetime.now()
        client_topology = {
            "discovery_timestamp": start_time.isoformat(),
            "organizations": [],
            "total_stats": {
                "switches_scanned": 0,
                "total_clients": 0,
                "by_device_type": {},
                "by_criticality": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "by_function": {}
            }
        }
        
        # Load existing network topology to get switch devices
        try:
            topology_files = glob.glob("/tmp/meraki_topology_*.json")
            if topology_files:
                latest_file = max(topology_files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    network_topology = json.load(f)
            else:
                print("❌ No network topology found. Run discover-real-meraki-data.py first")
                return client_topology
        except Exception as e:
            print(f"❌ Error loading network topology: {e}")
            return client_topology
        
        print(f"📊 Scanning switches across {len(network_topology['organizations'])} organizations...")
        print("-" * 50)
        
        # Process each organization
        for org in network_topology["organizations"]:
            org_data = {
                "id": org["id"],
                "name": org["name"],
                "switches": [],
                "client_stats": {
                    "switches_scanned": 0,
                    "total_clients": 0,
                    "by_type": {},
                    "by_criticality": {"critical": 0, "high": 0, "medium": 0, "low": 0}
                }
            }
            
            print(f"\n🏢 {org['name']}: Scanning switches...")
            
            # Find all switches in this organization (MS models are switches)
            switches = []
            for network in org["networks"]:
                for device in network["devices"]:
                    model = device.get("model", "").upper()
                    if model.startswith("MS") or "switch" in model.lower():
                        switches.append({
                            "serial": device["serial"],
                            "name": device["name"],
                            "model": device["model"],
                            "network_id": network["id"],
                            "network_name": network["name"]
                        })
            
            print(f"   📊 Found {len(switches)} switches to scan for connected devices")
            
            # Process switches in smaller batches to avoid rate limits
            switch_batches = [switches[i:i+3] for i in range(0, len(switches), 3)]
            
            for batch_idx, batch in enumerate(switch_batches):
                print(f"   📋 Processing switch batch {batch_idx + 1}/{len(switch_batches)}...")
                
                # Process batch of switches concurrently
                tasks = []
                for switch in batch:
                    task = self.discover_switch_clients(
                        switch["serial"], 
                        switch["name"], 
                        switch["network_id"], 
                        switch["network_name"], 
                        org["name"]
                    )
                    tasks.append(task)
                
                # Get results for this batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, client_list in enumerate(batch_results):
                    if not isinstance(client_list, Exception) and client_list:
                        switch = batch[i]
                        
                        switch_info = {
                            "serial": switch["serial"],
                            "name": switch["name"],
                            "model": switch["model"],
                            "network_name": switch["network_name"],
                            "client_devices": client_list,
                            "client_count": len(client_list)
                        }
                        
                        org_data["switches"].append(switch_info)
                        org_data["client_stats"]["switches_scanned"] += 1
                        org_data["client_stats"]["total_clients"] += len(client_list)
                        
                        # Update statistics
                        for client in client_list:
                            device_type = client['device_type']
                            criticality = client['criticality']
                            function = client['restaurant_function']
                            
                            # Update org stats
                            org_data["client_stats"]["by_type"][device_type] = org_data["client_stats"]["by_type"].get(device_type, 0) + 1
                            org_data["client_stats"]["by_criticality"][criticality] += 1
                            
                            # Update global stats
                            client_topology["total_stats"]["by_device_type"][device_type] = client_topology["total_stats"]["by_device_type"].get(device_type, 0) + 1
                            client_topology["total_stats"]["by_criticality"][criticality] += 1
                            client_topology["total_stats"]["by_function"][function] = client_topology["total_stats"]["by_function"].get(function, 0) + 1
                            client_topology["total_stats"]["total_clients"] += 1
                
                # Rate limiting between batches
                await asyncio.sleep(3)
            
            client_topology["organizations"].append(org_data)
            client_topology["total_stats"]["switches_scanned"] += org_data["client_stats"]["switches_scanned"]
            
            print(f"   ✅ {org['name']}: Scanned {org_data['client_stats']['switches_scanned']} switches, found {org_data['client_stats']['total_clients']} client devices")
        
        # Calculate final statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        client_topology["discovery_duration"] = duration
        client_topology["discovery_completed"] = end_time.isoformat()
        
        print(f"\n📊 SWITCH CLIENT DISCOVERY SUMMARY:")
        print("=" * 50)
        print(f"🏢 Organizations: {len(client_topology['organizations'])}")
        print(f"🔌 Switches Scanned: {client_topology['total_stats']['switches_scanned']}")
        print(f"📱 Client Devices Found: {client_topology['total_stats']['total_clients']}")
        print(f"🚨 Critical Equipment: {client_topology['total_stats']['by_criticality']['critical']}")
        print(f"⚡ High Priority: {client_topology['total_stats']['by_criticality']['high']}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        return client_topology
    
    def analyze_restaurant_equipment(self, client_topology: Dict[str, Any]):
        """Analyze discovered restaurant equipment"""
        print(f"\n🍴 RESTAURANT EQUIPMENT ANALYSIS:")
        print("=" * 50)
        
        # Show device types
        print(f"\n📊 RESTAURANT EQUIPMENT BY TYPE:")
        for device_type, count in sorted(client_topology["total_stats"]["by_device_type"].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / client_topology["total_stats"]["total_clients"]) * 100 if client_topology["total_stats"]["total_clients"] > 0 else 0
                display_name = device_type.replace('_', ' ').title()
                print(f"   {display_name}: {count:,} devices ({percentage:.1f}%)")
        
        # Show by criticality
        print(f"\n⚠️ BY OPERATIONAL CRITICALITY:")
        for criticality, count in sorted(client_topology["total_stats"]["by_criticality"].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                icon = "🚨" if criticality == "critical" else "⚡" if criticality == "high" else "⚠️" if criticality == "medium" else "ℹ️"
                print(f"   {icon} {criticality.title()}: {count:,} devices")
        
        # Show by restaurant function
        print(f"\n🏪 BY RESTAURANT FUNCTION:")
        for function, count in sorted(client_topology["total_stats"]["by_function"].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"   {function}: {count:,} devices")
        
        # Show organization breakdown
        print(f"\n🏢 BY ORGANIZATION:")
        for org in client_topology["organizations"]:
            if org["client_stats"]["total_clients"] > 0:
                print(f"\n   {org['name']}: {org['client_stats']['total_clients']:,} client devices")
                # Show top device types for this org
                top_types = sorted(org["client_stats"]["by_type"].items(), key=lambda x: x[1], reverse=True)[:3]
                for device_type, count in top_types:
                    if count > 0:
                        print(f"      {device_type.replace('_', ' ').title()}: {count}")
    
    def save_client_data(self, client_topology: Dict[str, Any], filename: str = None):
        """Save client device data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/switch_clients_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(client_topology, f, indent=2, default=str)
            
            print(f"💾 Switch client data saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save client data: {e}")
            return None

async def main():
    """Main switch client discovery function"""
    print("🔌 RESTAURANT EQUIPMENT DISCOVERY")
    print("Finding POS systems, kitchen equipment, and connected devices...")
    print("=" * 70)
    
    discovery = SwitchClientDiscovery()
    
    try:
        await discovery.initialize_session()
        
        # Discover all switch clients
        client_topology = await discovery.discover_all_switch_clients()
        
        if client_topology["total_stats"]["total_clients"] > 0:
            # Analyze the data
            discovery.analyze_restaurant_equipment(client_topology)
            
            # Save the data
            filename = discovery.save_client_data(client_topology)
            
            print(f"\n🎉 RESTAURANT EQUIPMENT DISCOVERY COMPLETED!")
            print(f"✅ Found {client_topology['total_stats']['total_clients']:,} client devices")
            print(f"✅ Including {client_topology['total_stats']['by_criticality']['critical']} critical restaurant systems")
            print(f"✅ Scanned {client_topology['total_stats']['switches_scanned']} switches")
            
            if filename:
                print(f"💾 Data saved to: {filename}")
            
            print(f"\n🚀 NEXT STEPS:")
            print("1. Load restaurant equipment into Neo4j for voice control")
            print("2. Enable POS and kitchen equipment troubleshooting")
            print("3. Test voice commands for restaurant operations")
            
            return client_topology
        else:
            print("⚠️ No client devices found - check switch configurations")
            return None
            
    except Exception as e:
        print(f"❌ Client discovery failed: {e}")
        return None
    finally:
        await discovery.close_session()

if __name__ == "__main__":
    asyncio.run(main())