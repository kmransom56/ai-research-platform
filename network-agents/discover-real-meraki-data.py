#!/usr/bin/env python3
"""
Real Meraki Data Discovery
Connects to actual Meraki API to discover tens of thousands of devices
"""

import requests
import json
import os
from typing import Dict, List, Any
from datetime import datetime
import asyncio
import aiohttp

class RealMerakiDiscovery:
    """
    Discover real Meraki network data using actual API
    """
    
    def __init__(self):
        self.api_key = os.getenv('MERAKI_API_KEY', 'fd3b9969d25792d90f0789a7e28cc661c81e2150')
        self.base_url = "https://api.meraki.com/api/v1"
        self.headers = {
            'X-Cisco-Meraki-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.session = None
        
        print(f"🔑 Using Meraki API Key: {self.api_key[:12]}...{self.api_key[-4:]}")
    
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
    
    async def discover_organizations(self) -> List[Dict[str, Any]]:
        """Discover all organizations"""
        print("🏢 Discovering Meraki Organizations...")
        
        try:
            async with self.session.get(f"{self.base_url}/organizations") as response:
                if response.status == 200:
                    orgs = await response.json()
                    print(f"   ✅ Found {len(orgs)} organizations")
                    
                    for i, org in enumerate(orgs[:5]):  # Show first 5
                        print(f"   {i+1}. {org['name']} (ID: {org['id']})")
                    
                    if len(orgs) > 5:
                        print(f"   ... and {len(orgs) - 5} more organizations")
                    
                    return orgs
                else:
                    print(f"   ❌ Failed to get organizations: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    return []
                    
        except Exception as e:
            print(f"   ❌ Error discovering organizations: {e}")
            return []
    
    async def discover_networks_for_org(self, org_id: str, org_name: str) -> List[Dict[str, Any]]:
        """Discover networks for a specific organization"""
        try:
            async with self.session.get(f"{self.base_url}/organizations/{org_id}/networks") as response:
                if response.status == 200:
                    networks = await response.json()
                    print(f"   📊 {org_name}: {len(networks)} networks")
                    return networks
                else:
                    print(f"   ⚠️ Failed to get networks for {org_name}: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"   ❌ Error getting networks for {org_name}: {e}")
            return []
    
    async def discover_devices_for_network(self, network_id: str, network_name: str) -> List[Dict[str, Any]]:
        """Discover devices for a specific network"""
        try:
            async with self.session.get(f"{self.base_url}/networks/{network_id}/devices") as response:
                if response.status == 200:
                    devices = await response.json()
                    return devices
                else:
                    return []
                    
        except Exception as e:
            print(f"   ❌ Error getting devices for {network_name}: {e}")
            return []
    
    async def discover_complete_topology(self) -> Dict[str, Any]:
        """Discover complete Meraki topology"""
        print("🚀 DISCOVERING COMPLETE MERAKI TOPOLOGY")
        print("=" * 60)
        
        start_time = datetime.now()
        topology = {
            "discovery_timestamp": start_time.isoformat(),
            "organizations": [],
            "total_stats": {
                "organizations": 0,
                "networks": 0,
                "devices": 0,
                "by_device_type": {},
                "by_product_type": {}
            }
        }
        
        # Discover organizations
        organizations = await self.discover_organizations()
        topology["total_stats"]["organizations"] = len(organizations)
        
        if not organizations:
            print("❌ No organizations found - check API key permissions")
            return topology
        
        print(f"\n🌐 Discovering Networks and Devices...")
        print("-" * 40)
        
        # Process organizations with rate limiting
        for org in organizations:
            org_data = {
                "id": org["id"],
                "name": org["name"],
                "url": org.get("url", ""),
                "networks": [],
                "device_count": 0,
                "network_count": 0
            }
            
            # Get networks for this organization
            networks = await self.discover_networks_for_org(org["id"], org["name"])
            org_data["network_count"] = len(networks)
            topology["total_stats"]["networks"] += len(networks)
            
            # Process ALL networks for full enterprise scale
            networks_to_process = networks  # Process ALL networks
            print(f"   📋 Processing all {len(networks)} networks for {org['name']}")
            
            # Batch process networks to avoid rate limits
            network_batches = [networks_to_process[i:i+10] for i in range(0, len(networks_to_process), 10)]
            
            for batch in network_batches:
                # Process batch of networks concurrently
                network_tasks = []
                for network in batch:
                    task = self.process_single_network(network, org["name"])
                    network_tasks.append(task)
                
                # Wait for batch to complete
                batch_results = await asyncio.gather(*network_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(batch_results):
                    if not isinstance(result, Exception) and result:
                        org_data["networks"].append(result)
                        org_data["device_count"] += result.get("device_count", 0)
                
                # Rate limiting - small delay between batches
                await asyncio.sleep(1)
            
            topology["organizations"].append(org_data)
            
            # Update global stats
            topology["total_stats"]["devices"] += org_data["device_count"]
            
            print(f"   ✅ {org['name']}: {org_data['network_count']} networks, {org_data['device_count']} devices")
        
        # Calculate final statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        topology["discovery_duration"] = duration
        topology["discovery_completed"] = end_time.isoformat()
        
        print(f"\n📊 DISCOVERY SUMMARY:")
        print("=" * 40)
        print(f"🏢 Organizations: {topology['total_stats']['organizations']}")
        print(f"🌐 Networks: {topology['total_stats']['networks']}")
        print(f"📱 Devices: {topology['total_stats']['devices']}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        return topology
    
    async def process_single_network(self, network: Dict[str, Any], org_name: str) -> Dict[str, Any]:
        """Process a single network and its devices"""
        try:
            network_data = {
                "id": network["id"],
                "name": network["name"],
                "product_types": network.get("productTypes", []),
                "time_zone": network.get("timeZone", ""),
                "tags": network.get("tags", []),
                "organization_name": org_name,
                "devices": [],
                "device_count": 0
            }
            
            # Get devices for this network
            devices = await self.discover_devices_for_network(network["id"], network["name"])
            
            for device in devices:
                device_info = {
                    "serial": device.get("serial", ""),
                    "name": device.get("name", f"Device_{device.get('serial', 'unknown')}"),
                    "model": device.get("model", ""),
                    "mac": device.get("mac", ""),
                    "product_type": device.get("productType", ""),
                    "network_id": network["id"],
                    "network_name": network["name"],
                    "firmware": device.get("firmware", ""),
                    "lan_ip": device.get("lanIp", ""),
                    "url": device.get("url", ""),
                    "tags": device.get("tags", []),
                    "details": device.get("details", {}),
                    "organization_name": org_name
                }
                network_data["devices"].append(device_info)
            
            network_data["device_count"] = len(devices)
            return network_data
            
        except Exception as e:
            print(f"   ❌ Error processing network {network.get('name', 'unknown')}: {e}")
            return None
    
    def save_topology_data(self, topology: Dict[str, Any], filename: str = None):
        """Save topology data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/meraki_topology_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(topology, f, indent=2, default=str)
            
            print(f"💾 Topology data saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save topology data: {e}")
            return None
    
    def analyze_device_distribution(self, topology: Dict[str, Any]):
        """Analyze device distribution across organizations and types"""
        print(f"\n🔍 DEVICE DISTRIBUTION ANALYSIS:")
        print("=" * 50)
        
        # Count devices by type
        device_types = {}
        product_types = {}
        models = {}
        
        for org in topology["organizations"]:
            print(f"\n🏢 {org['name']}:")
            print(f"   Networks: {org['network_count']}")
            print(f"   Devices: {org['device_count']}")
            
            org_device_types = {}
            
            for network in org["networks"]:
                for device in network["devices"]:
                    # Count by product type
                    ptype = device.get("product_type", "unknown")
                    product_types[ptype] = product_types.get(ptype, 0) + 1
                    org_device_types[ptype] = org_device_types.get(ptype, 0) + 1
                    
                    # Count by model
                    model = device.get("model", "unknown")
                    models[model] = models.get(model, 0) + 1
            
            # Show organization device breakdown
            if org_device_types:
                for dtype, count in sorted(org_device_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"      {dtype}: {count}")
        
        print(f"\n📊 OVERALL DEVICE SUMMARY:")
        print("-" * 30)
        for ptype, count in sorted(product_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {ptype}: {count:,} devices")
        
        print(f"\n🔝 TOP DEVICE MODELS:")
        print("-" * 30)
        top_models = sorted(models.items(), key=lambda x: x[1], reverse=True)[:10]
        for model, count in top_models:
            print(f"   {model}: {count:,} devices")

async def main():
    """Main discovery function"""
    print("🔍 REAL MERAKI NETWORK DISCOVERY")
    print("Connecting to actual Meraki API with your credentials...")
    print("=" * 60)
    
    discovery = RealMerakiDiscovery()
    
    try:
        await discovery.initialize_session()
        
        # Discover complete topology
        topology = await discovery.discover_complete_topology()
        
        if topology["total_stats"]["devices"] > 0:
            # Analyze the data
            discovery.analyze_device_distribution(topology)
            
            # Save the data
            filename = discovery.save_topology_data(topology)
            
            print(f"\n🎉 REAL MERAKI DISCOVERY COMPLETED!")
            print(f"✅ Found {topology['total_stats']['devices']:,} devices")
            print(f"✅ Across {topology['total_stats']['networks']:,} networks")
            print(f"✅ In {topology['total_stats']['organizations']} organizations")
            
            if filename:
                print(f"💾 Data saved to: {filename}")
            
            print(f"\n🚀 NEXT STEPS:")
            print("1. Review the discovered device data")
            print("2. Load this real data into Neo4j")
            print("3. Update the network management system with actual topology")
            print("4. Scale queries for tens of thousands of devices")
            
            return topology
        else:
            print("⚠️ No devices found - check API permissions")
            return None
            
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return None
    finally:
        await discovery.close_session()

if __name__ == "__main__":
    asyncio.run(main())