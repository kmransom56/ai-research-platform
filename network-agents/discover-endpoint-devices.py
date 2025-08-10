#!/usr/bin/env python3
"""
Endpoint Device Discovery for Restaurant Operations
Discovers client devices connected to switches and access points:
- Point of Sale (POS) systems
- Kiosks and self-service terminals
- Kitchen display systems
- Drive-thru timers
- Digital menu boards
- Security cameras
- Printers and receipt systems
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, List, Any
from datetime import datetime, timedelta
import os

class EndpointDeviceDiscovery:
    """
    Discover and categorize endpoint devices connected to network infrastructure
    """
    
    def __init__(self):
        self.api_key = os.getenv('MERAKI_API_KEY', 'fd3b9969d25792d90f0789a7e28cc661c81e2150')
        self.base_url = "https://api.meraki.com/api/v1"
        self.headers = {
            'X-Cisco-Meraki-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.session = None
        
        # Restaurant device type patterns for classification
        self.device_patterns = {
            'pos': {
                'keywords': ['pos', 'point-of-sale', 'register', 'till', 'aloha', 'micros', 'toast', 'square'],
                'mac_prefixes': ['00:0C:29', '00:50:56'],  # Common POS system MACs
                'description': 'Point of Sale Systems'
            },
            'kiosk': {
                'keywords': ['kiosk', 'self-order', 'self-service', 'ordering', 'customer'],
                'mac_prefixes': ['AC:1F:6B', '00:15:5D'],  # Common kiosk MACs
                'description': 'Self-Service Kiosks'
            },
            'kitchen_display': {
                'keywords': ['kds', 'kitchen', 'display', 'cook', 'prep', 'expo', 'bump'],
                'mac_prefixes': ['00:1B:21', '00:0F:EA'],  # Kitchen display systems
                'description': 'Kitchen Display Systems'
            },
            'drive_thru': {
                'keywords': ['drive', 'thru', 'timer', 'dt', 'speaker', 'headset'],
                'mac_prefixes': ['00:04:20', '00:30:18'],  # Drive-thru equipment
                'description': 'Drive-Thru Equipment'
            },
            'menu_board': {
                'keywords': ['menu', 'board', 'digital', 'signage', 'display-board'],
                'mac_prefixes': ['00:22:5F', '00:1D:7D'],  # Digital signage
                'description': 'Digital Menu Boards'
            },
            'printer': {
                'keywords': ['printer', 'receipt', 'zebra', 'epson', 'star'],
                'mac_prefixes': ['00:07:61', '00:22:58', '08:00:11'],  # Printer MACs
                'description': 'Receipt & Label Printers'
            },
            'security_camera': {
                'keywords': ['camera', 'security', 'surveillance', 'video', 'dvr', 'nvr'],
                'mac_prefixes': ['00:12:AC', '00:40:8C'],  # Camera systems
                'description': 'Security Cameras'
            },
            'back_office': {
                'keywords': ['office', 'manager', 'admin', 'pc', 'computer', 'workstation'],
                'mac_prefixes': ['00:0C:29', '00:50:56'],  # Office systems
                'description': 'Back Office Systems'
            },
            'wifi_device': {
                'keywords': ['phone', 'tablet', 'ipad', 'android', 'mobile', 'handheld'],
                'mac_prefixes': ['AC:37:43', 'DC:A6:32', '28:E3:47'],  # Mobile devices
                'description': 'Mobile & WiFi Devices'
            }
        }
    
    async def initialize_session(self):
        """Initialize async HTTP session"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        )
    
    async def close_session(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    def classify_endpoint_device(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Classify endpoint device based on name, MAC, and other attributes"""
        
        device_name = (client_info.get('description') or '').lower()
        mac_address = (client_info.get('mac') or '').upper()
        manufacturer = (client_info.get('manufacturer') or '').lower()
        
        # Default classification
        classification = {
            'device_type': 'unknown_endpoint',
            'category': 'Unknown Device',
            'confidence': 0,
            'restaurant_function': 'unclassified'
        }
        
        # Check each device pattern
        for device_type, pattern_info in self.device_patterns.items():
            confidence = 0
            
            # Check keywords in device name
            for keyword in pattern_info['keywords']:
                if keyword in device_name or keyword in manufacturer:
                    confidence += 20
            
            # Check MAC address prefixes
            for prefix in pattern_info['mac_prefixes']:
                if mac_address.startswith(prefix.upper()):
                    confidence += 30
            
            # Additional scoring based on common patterns
            if device_type == 'pos' and any(term in device_name for term in ['reg', 'terminal', 'station']):
                confidence += 15
            
            if device_type == 'kitchen_display' and any(term in device_name for term in ['kds', 'bump', 'expo']):
                confidence += 25
            
            if device_type == 'wifi_device' and any(term in manufacturer for term in ['apple', 'samsung', 'google']):
                confidence += 20
            
            # Update classification if this is the best match
            if confidence > classification['confidence']:
                classification = {
                    'device_type': device_type,
                    'category': pattern_info['description'],
                    'confidence': confidence,
                    'restaurant_function': self.get_restaurant_function(device_type)
                }
        
        return classification
    
    def get_restaurant_function(self, device_type: str) -> str:
        """Get restaurant business function for device type"""
        function_map = {
            'pos': 'Order Processing & Payment',
            'kiosk': 'Customer Self-Service',
            'kitchen_display': 'Food Preparation',
            'drive_thru': 'Drive-Thru Operations',
            'menu_board': 'Customer Information',
            'printer': 'Receipt & Documentation',
            'security_camera': 'Security & Monitoring',
            'back_office': 'Management & Administration',
            'wifi_device': 'Staff Mobile Operations'
        }
        return function_map.get(device_type, 'General Operations')
    
    async def discover_network_clients(self, network_id: str, network_name: str) -> List[Dict[str, Any]]:
        """Discover all client devices connected to a network"""
        try:
            # Get network clients (devices connected to switches/APs)
            async with self.session.get(f"{self.base_url}/networks/{network_id}/clients") as response:
                if response.status == 200:
                    clients = await response.json()
                    
                    endpoint_devices = []
                    for client in clients:
                        # Classify the endpoint device
                        classification = self.classify_endpoint_device(client)
                        
                        # Create endpoint device record
                        endpoint_device = {
                            'mac': client.get('mac', ''),
                            'description': client.get('description', f"Device_{client.get('mac', 'unknown')}"),
                            'ip': client.get('ip', ''),
                            'ip6': client.get('ip6', ''),
                            'user': client.get('user', ''),
                            'first_seen': client.get('firstSeen', ''),
                            'last_seen': client.get('lastSeen', ''),
                            'manufacturer': client.get('manufacturer', ''),
                            'os': client.get('os', ''),
                            'device_type': classification['device_type'],
                            'category': classification['category'],
                            'confidence': classification['confidence'],
                            'restaurant_function': classification['restaurant_function'],
                            'network_id': network_id,
                            'network_name': network_name,
                            'connection_type': 'wired' if 'switch' in str(client.get('recentDeviceSerial', '')).lower() else 'wireless',
                            'connected_device': client.get('recentDeviceSerial', ''),
                            'vlan': client.get('vlan', ''),
                            'ssid': client.get('ssid', ''),
                            'usage_mb': client.get('usage', {}).get('recv', 0) + client.get('usage', {}).get('sent', 0) if client.get('usage') else 0,
                            'status': client.get('status', 'unknown')
                        }
                        
                        endpoint_devices.append(endpoint_device)
                    
                    return endpoint_devices
                else:
                    return []
        except Exception as e:
            print(f"   ❌ Error getting clients for {network_name}: {e}")
            return []
    
    async def discover_all_endpoint_devices(self) -> Dict[str, Any]:
        """Discover all endpoint devices across the enterprise"""
        print("🔍 DISCOVERING ENDPOINT DEVICES (POS, Kiosks, Kitchen Equipment)")
        print("=" * 70)
        
        start_time = datetime.now()
        endpoint_topology = {
            "discovery_timestamp": start_time.isoformat(),
            "organizations": [],
            "total_stats": {
                "networks_scanned": 0,
                "total_endpoints": 0,
                "by_device_type": {},
                "by_restaurant_function": {},
                "connection_types": {"wired": 0, "wireless": 0}
            }
        }
        
        # Load existing network topology to get organizations and networks
        try:
            import glob
            topology_files = glob.glob("/tmp/meraki_topology_*.json")
            if topology_files:
                latest_file = max(topology_files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    network_topology = json.load(f)
            else:
                print("❌ No network topology found. Run discover-real-meraki-data.py first")
                return endpoint_topology
        except Exception as e:
            print(f"❌ Error loading network topology: {e}")
            return endpoint_topology
        
        print(f"📊 Scanning {len(network_topology['organizations'])} organizations for endpoint devices...")
        print("-" * 50)
        
        # Process each organization
        for org in network_topology["organizations"]:
            org_data = {
                "id": org["id"],
                "name": org["name"],
                "networks": [],
                "endpoint_stats": {
                    "total_endpoints": 0,
                    "by_type": {},
                    "by_function": {}
                }
            }
            
            print(f"\n🏢 {org['name']}: Scanning {len(org['networks'])} networks...")
            
            # Process networks in batches to avoid rate limits
            network_batches = [org["networks"][i:i+5] for i in range(0, len(org["networks"]), 5)]
            
            for batch_idx, batch in enumerate(network_batches):
                print(f"   📊 Processing batch {batch_idx + 1}/{len(network_batches)}...")
                
                # Process batch of networks concurrently
                tasks = []
                for network in batch:
                    task = self.discover_network_clients(network["id"], network["name"])
                    tasks.append(task)
                
                # Get results for this batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for i, endpoint_devices in enumerate(batch_results):
                    if not isinstance(endpoint_devices, Exception) and endpoint_devices:
                        network = batch[i]
                        
                        network_info = {
                            "id": network["id"],
                            "name": network["name"],
                            "organization_name": org["name"],
                            "endpoint_devices": endpoint_devices,
                            "endpoint_count": len(endpoint_devices)
                        }
                        
                        org_data["networks"].append(network_info)
                        org_data["endpoint_stats"]["total_endpoints"] += len(endpoint_devices)
                        
                        # Update statistics
                        for device in endpoint_devices:
                            device_type = device['device_type']
                            function = device['restaurant_function']
                            connection = device['connection_type']
                            
                            # Update org stats
                            org_data["endpoint_stats"]["by_type"][device_type] = org_data["endpoint_stats"]["by_type"].get(device_type, 0) + 1
                            org_data["endpoint_stats"]["by_function"][function] = org_data["endpoint_stats"]["by_function"].get(function, 0) + 1
                            
                            # Update global stats
                            endpoint_topology["total_stats"]["by_device_type"][device_type] = endpoint_topology["total_stats"]["by_device_type"].get(device_type, 0) + 1
                            endpoint_topology["total_stats"]["by_restaurant_function"][function] = endpoint_topology["total_stats"]["by_restaurant_function"].get(function, 0) + 1
                            endpoint_topology["total_stats"]["connection_types"][connection] += 1
                            endpoint_topology["total_stats"]["total_endpoints"] += 1
                
                # Rate limiting between batches
                await asyncio.sleep(2)
            
            endpoint_topology["organizations"].append(org_data)
            endpoint_topology["total_stats"]["networks_scanned"] += len(org["networks"])
            
            print(f"   ✅ {org['name']}: Found {org_data['endpoint_stats']['total_endpoints']} endpoint devices")
        
        # Calculate final statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        endpoint_topology["discovery_duration"] = duration
        endpoint_topology["discovery_completed"] = end_time.isoformat()
        
        print(f"\n📊 ENDPOINT DISCOVERY SUMMARY:")
        print("=" * 50)
        print(f"🏢 Organizations: {len(endpoint_topology['organizations'])}")
        print(f"🌐 Networks Scanned: {endpoint_topology['total_stats']['networks_scanned']}")
        print(f"📱 Total Endpoints: {endpoint_topology['total_stats']['total_endpoints']}")
        print(f"🔌 Wired: {endpoint_topology['total_stats']['connection_types']['wired']}")
        print(f"📶 Wireless: {endpoint_topology['total_stats']['connection_types']['wireless']}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        return endpoint_topology
    
    def analyze_endpoint_distribution(self, endpoint_topology: Dict[str, Any]):
        """Analyze endpoint device distribution"""
        print(f"\n🍴 RESTAURANT ENDPOINT DEVICE ANALYSIS:")
        print("=" * 50)
        
        # Show device types
        print(f"\n📊 BY DEVICE TYPE:")
        for device_type, count in sorted(endpoint_topology["total_stats"]["by_device_type"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / endpoint_topology["total_stats"]["total_endpoints"]) * 100 if endpoint_topology["total_stats"]["total_endpoints"] > 0 else 0
            print(f"   {device_type.replace('_', ' ').title()}: {count:,} devices ({percentage:.1f}%)")
        
        # Show restaurant functions
        print(f"\n🏪 BY RESTAURANT FUNCTION:")
        for function, count in sorted(endpoint_topology["total_stats"]["by_restaurant_function"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / endpoint_topology["total_stats"]["total_endpoints"]) * 100 if endpoint_topology["total_stats"]["total_endpoints"] > 0 else 0
            print(f"   {function}: {count:,} devices ({percentage:.1f}%)")
        
        # Show organization breakdown
        print(f"\n🏢 BY ORGANIZATION:")
        for org in endpoint_topology["organizations"]:
            if org["endpoint_stats"]["total_endpoints"] > 0:
                print(f"\n   {org['name']}: {org['endpoint_stats']['total_endpoints']:,} endpoint devices")
                for device_type, count in sorted(org["endpoint_stats"]["by_type"].items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"      {device_type.replace('_', ' ').title()}: {count}")
    
    def save_endpoint_data(self, endpoint_topology: Dict[str, Any], filename: str = None):
        """Save endpoint device data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/endpoint_devices_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(endpoint_topology, f, indent=2, default=str)
            
            print(f"💾 Endpoint device data saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save endpoint data: {e}")
            return None

async def main():
    """Main endpoint discovery function"""
    print("🍴 RESTAURANT ENDPOINT DEVICE DISCOVERY")
    print("Discovering POS, Kiosks, Kitchen Equipment, and more...")
    print("=" * 70)
    
    discovery = EndpointDeviceDiscovery()
    
    try:
        await discovery.initialize_session()
        
        # Discover all endpoint devices
        endpoint_topology = await discovery.discover_all_endpoint_devices()
        
        if endpoint_topology["total_stats"]["total_endpoints"] > 0:
            # Analyze the data
            discovery.analyze_endpoint_distribution(endpoint_topology)
            
            # Save the data
            filename = discovery.save_endpoint_data(endpoint_topology)
            
            print(f"\n🎉 ENDPOINT DEVICE DISCOVERY COMPLETED!")
            print(f"✅ Found {endpoint_topology['total_stats']['total_endpoints']:,} endpoint devices")
            print(f"✅ Across {endpoint_topology['total_stats']['networks_scanned']:,} networks")
            print(f"✅ Including POS, Kiosks, Kitchen displays, and more")
            
            if filename:
                print(f"💾 Data saved to: {filename}")
            
            print(f"\n🚀 NEXT STEPS:")
            print("1. Load endpoint devices into Neo4j for voice control")
            print("2. Enable restaurant equipment troubleshooting")
            print("3. Add voice commands for POS and kitchen systems")
            
            return endpoint_topology
        else:
            print("⚠️ No endpoint devices found - check network configurations")
            return None
            
    except Exception as e:
        print(f"❌ Endpoint discovery failed: {e}")
        return None
    finally:
        await discovery.close_session()

if __name__ == "__main__":
    asyncio.run(main())