#!/usr/bin/env python3
"""
Full-Scale Meraki Discovery for Tens of Thousands of Devices
Optimized for complete restaurant chain infrastructure discovery
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Any
from datetime import datetime
import time

class FullScaleMerakiDiscovery:
    """
    Full-scale discovery for tens of thousands of devices with optimizations
    """
    
    def __init__(self):
        self.api_key = os.getenv('MERAKI_API_KEY', 'fd3b9969d25792d90f0789a7e28cc661c81e2150')
        self.base_url = "https://api.meraki.com/api/v1"
        self.headers = {
            'X-Cisco-Meraki-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.session = None
        
        # Optimization settings for large-scale discovery
        self.max_concurrent_requests = 20  # Increased for faster discovery
        self.batch_size = 100  # Process more networks per batch
        self.networks_per_org_limit = None  # Remove limit for full discovery
        self.rate_limit_delay = 0.5  # Reduced delay between batches
        
        print(f"🚀 FULL-SCALE MERAKI DISCOVERY INITIALIZED")
        print(f"🔑 API Key: {self.api_key[:12]}...{self.api_key[-4:]}")
        print(f"⚡ Max Concurrent: {self.max_concurrent_requests}")
        print(f"📦 Batch Size: {self.batch_size}")
        
    async def initialize_session(self):
        """Initialize optimized async HTTP session"""
        connector = aiohttp.TCPConnector(
            limit=200,  # Increased connection pool
            limit_per_host=50,  # More connections per host
            ttl_dns_cache=300,  # DNS cache for 5 minutes
            use_dns_cache=True
        )
        timeout = aiohttp.ClientTimeout(total=60, connect=30)  # Longer timeouts
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
        print("🏢 Discovering all organizations...")
        
        try:
            async with self.session.get(f"{self.base_url}/organizations") as response:
                if response.status == 200:
                    orgs = await response.json()
                    print(f"   ✅ Found {len(orgs)} organizations")
                    
                    # Show all organizations for full discovery
                    for i, org in enumerate(orgs):
                        print(f"   {i+1:2d}. {org['name']} (ID: {org['id']})")
                    
                    return orgs
                else:
                    print(f"   ❌ Failed to get organizations: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"   ❌ Error discovering organizations: {e}")
            return []
    
    async def get_organization_networks(self, org_id: str, org_name: str) -> List[Dict[str, Any]]:
        """Get all networks for an organization"""
        try:
            async with self.session.get(f"{self.base_url}/organizations/{org_id}/networks") as response:
                if response.status == 200:
                    networks = await response.json()
                    print(f"   📊 {org_name}: {len(networks):,} networks discovered")
                    return networks
                else:
                    print(f"   ⚠️ Failed to get networks for {org_name}: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"   ❌ Error getting networks for {org_name}: {e}")
            return []
    
    async def get_network_devices(self, network_id: str, network_name: str) -> List[Dict[str, Any]]:
        """Get all devices for a network"""
        try:
            async with self.session.get(f"{self.base_url}/networks/{network_id}/devices") as response:
                if response.status == 200:
                    devices = await response.json()
                    return devices
                else:
                    return []
                    
        except Exception as e:
            return []
    
    async def process_network_batch(self, networks: List[Dict[str, Any]], org_name: str) -> List[Dict[str, Any]]:
        """Process a batch of networks concurrently"""
        tasks = []
        for network in networks:
            task = self.process_single_network(network, org_name)
            tasks.append(task)
        
        # Process batch concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = []
        for result in results:
            if not isinstance(result, Exception) and result:
                successful_results.append(result)
        
        return successful_results
    
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
            devices = await self.get_network_devices(network["id"], network["name"])
            
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
            return None
    
    async def discover_complete_infrastructure(self) -> Dict[str, Any]:
        """Discover complete infrastructure at full scale"""
        print("🚀 FULL-SCALE MERAKI INFRASTRUCTURE DISCOVERY")
        print("=" * 60)
        print("⚡ Optimized for tens of thousands of devices")
        print("🏢 Processing ALL networks for ALL organizations")
        print("=" * 60)
        
        start_time = datetime.now()
        topology = {
            "discovery_timestamp": start_time.isoformat(),
            "discovery_mode": "full_scale",
            "optimization_settings": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "batch_size": self.batch_size,
                "rate_limit_delay": self.rate_limit_delay,
                "networks_limit": "UNLIMITED"
            },
            "organizations": [],
            "total_stats": {
                "organizations": 0,
                "networks": 0,
                "devices": 0,
                "by_device_type": {},
                "by_product_type": {},
                "processing_stats": {
                    "networks_processed": 0,
                    "networks_with_devices": 0,
                    "empty_networks": 0,
                    "api_calls_made": 0,
                    "errors_encountered": 0
                }
            }
        }
        
        # Discover organizations
        organizations = await self.discover_organizations()
        topology["total_stats"]["organizations"] = len(organizations)
        
        if not organizations:
            print("❌ No organizations found - check API key permissions")
            return topology
        
        print(f"\n🌐 FULL-SCALE NETWORK DISCOVERY")
        print(f"📊 Processing {len(organizations)} organizations...")
        print("-" * 50)
        
        total_networks_processed = 0
        total_api_calls = len(organizations)  # One call per org for networks
        
        # Process each organization completely
        for org_idx, org in enumerate(organizations):
            org_start_time = time.time()
            
            org_data = {
                "id": org["id"],
                "name": org["name"],
                "url": org.get("url", ""),
                "networks": [],
                "device_count": 0,
                "network_count": 0,
                "processing_stats": {
                    "networks_processed": 0,
                    "devices_discovered": 0,
                    "processing_time": 0
                }
            }
            
            print(f"\n🏢 [{org_idx+1}/{len(organizations)}] {org['name']}")
            print(f"   🔍 Discovering networks...")
            
            # Get ALL networks for this organization
            networks = await self.get_organization_networks(org["id"], org["name"])
            org_data["network_count"] = len(networks)
            topology["total_stats"]["networks"] += len(networks)
            total_api_calls += 1  # Network discovery API call
            
            if not networks:
                print(f"   ⚠️  No networks found for {org['name']}")
                topology["organizations"].append(org_data)
                continue
            
            print(f"   📊 Processing {len(networks):,} networks in batches...")
            
            # Process networks in optimized batches
            networks_processed = 0
            org_devices = 0
            
            for batch_start in range(0, len(networks), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(networks))
                network_batch = networks[batch_start:batch_end]
                
                batch_start_time = time.time()
                
                # Process batch concurrently
                batch_results = await self.process_network_batch(network_batch, org["name"])
                total_api_calls += len(network_batch)  # Device discovery API calls
                
                # Add successful results
                org_data["networks"].extend(batch_results)
                
                # Count devices in this batch
                batch_devices = sum(net.get("device_count", 0) for net in batch_results)
                org_devices += batch_devices
                networks_processed += len(batch_results)
                
                batch_time = time.time() - batch_start_time
                
                # Progress update
                progress = (batch_end / len(networks)) * 100
                print(f"   ⏳ Batch {batch_start//self.batch_size + 1}: {len(batch_results)}/{len(network_batch)} networks, {batch_devices} devices ({progress:.1f}% complete)")
                
                # Rate limiting
                if batch_start + self.batch_size < len(networks):
                    await asyncio.sleep(self.rate_limit_delay)
            
            org_data["device_count"] = org_devices
            org_data["processing_stats"]["networks_processed"] = networks_processed
            org_data["processing_stats"]["devices_discovered"] = org_devices
            org_data["processing_stats"]["processing_time"] = time.time() - org_start_time
            
            topology["organizations"].append(org_data)
            topology["total_stats"]["devices"] += org_devices
            total_networks_processed += networks_processed
            
            print(f"   ✅ {org['name']} completed:")
            print(f"      📊 Networks: {networks_processed:,}/{len(networks):,}")
            print(f"      📱 Devices: {org_devices:,}")
            print(f"      ⏱️  Time: {org_data['processing_stats']['processing_time']:.1f}s")
        
        # Final statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        topology["discovery_completed"] = end_time.isoformat()
        topology["discovery_duration"] = duration
        topology["total_stats"]["processing_stats"]["networks_processed"] = total_networks_processed
        topology["total_stats"]["processing_stats"]["api_calls_made"] = total_api_calls
        
        print(f"\n🎉 FULL-SCALE DISCOVERY COMPLETED!")
        print("=" * 50)
        print(f"🏢 Organizations: {topology['total_stats']['organizations']}")
        print(f"🌐 Networks Discovered: {topology['total_stats']['networks']:,}")
        print(f"🌐 Networks Processed: {total_networks_processed:,}")
        print(f"📱 Total Devices: {topology['total_stats']['devices']:,}")
        print(f"🔄 API Calls Made: {total_api_calls:,}")
        print(f"⏱️  Total Time: {duration:.2f} seconds")
        print(f"📈 Discovery Rate: {topology['total_stats']['devices'] / duration:.1f} devices/second")
        
        return topology
    
    def save_full_topology(self, topology: Dict[str, Any]) -> str:
        """Save complete topology data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/meraki_full_topology_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(topology, f, indent=2, default=str)
            
            file_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"💾 Complete topology saved:")
            print(f"   📂 File: {filename}")
            print(f"   📊 Size: {file_size:.1f} MB")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save topology: {e}")
            return None
    
    def analyze_full_scale_data(self, topology: Dict[str, Any]):
        """Analyze the full-scale discovery results"""
        print(f"\n🔍 FULL-SCALE DATA ANALYSIS")
        print("=" * 40)
        
        # Device distribution by organization
        print(f"📊 DEVICE DISTRIBUTION:")
        org_device_counts = []
        for org in topology["organizations"]:
            org_device_counts.append((org["name"], org["device_count"]))
        
        # Sort by device count
        org_device_counts.sort(key=lambda x: x[1], reverse=True)
        
        for org_name, device_count in org_device_counts:
            print(f"   🏢 {org_name}: {device_count:,} devices")
        
        # Model distribution analysis
        print(f"\n🔧 DEVICE MODEL ANALYSIS:")
        all_models = {}
        all_product_types = {}
        
        for org in topology["organizations"]:
            for network in org["networks"]:
                for device in network["devices"]:
                    # Count models
                    model = device.get("model", "Unknown")
                    all_models[model] = all_models.get(model, 0) + 1
                    
                    # Count product types
                    ptype = device.get("product_type", "Unknown")
                    all_product_types[ptype] = all_product_types.get(ptype, 0) + 1
        
        # Show top models
        top_models = sorted(all_models.items(), key=lambda x: x[1], reverse=True)[:15]
        for model, count in top_models:
            if model and model != "Unknown":
                print(f"   📱 {model}: {count:,} devices")
        
        # Show product types
        print(f"\n🏭 DEVICE TYPE DISTRIBUTION:")
        for ptype, count in sorted(all_product_types.items(), key=lambda x: x[1], reverse=True):
            if ptype and ptype != "Unknown":
                print(f"   🔧 {ptype}: {count:,} devices")
        
        # Performance statistics
        stats = topology["total_stats"]["processing_stats"]
        duration = topology["discovery_duration"]
        
        print(f"\n⚡ DISCOVERY PERFORMANCE:")
        print(f"   🔄 API Calls: {stats['api_calls_made']:,}")
        print(f"   📊 Networks/sec: {stats['networks_processed'] / duration:.1f}")
        print(f"   📱 Devices/sec: {topology['total_stats']['devices'] / duration:.1f}")
        print(f"   🎯 Success Rate: {(stats['networks_processed'] / topology['total_stats']['networks'] * 100):.1f}%")

async def main():
    """Main full-scale discovery function"""
    print("🚀 FULL-SCALE MERAKI INFRASTRUCTURE DISCOVERY")
    print("Discovering tens of thousands of devices across restaurant chains...")
    print("=" * 70)
    
    discovery = FullScaleMerakiDiscovery()
    
    try:
        await discovery.initialize_session()
        
        # Run complete infrastructure discovery
        topology = await discovery.discover_complete_infrastructure()
        
        if topology["total_stats"]["devices"] > 0:
            # Analyze the data
            discovery.analyze_full_scale_data(topology)
            
            # Save the complete data
            filename = discovery.save_full_topology(topology)
            
            print(f"\n🌟 FULL-SCALE DISCOVERY SUCCESS!")
            print("=" * 40)
            print(f"✅ Organizations: {topology['total_stats']['organizations']}")
            print(f"✅ Networks: {topology['total_stats']['networks']:,}")
            print(f"✅ Devices: {topology['total_stats']['devices']:,}")
            print(f"✅ Duration: {topology['discovery_duration']:.1f} seconds")
            
            if filename:
                print(f"💾 Data saved to: {filename}")
            
            print(f"\n🚀 READY FOR PRODUCTION SCALE:")
            print("1. Load complete data into Neo4j with batch optimization")
            print("2. Scale network management system for full infrastructure")
            print("3. Deploy executive dashboards with complete data")
            print("4. Enable AI-powered insights across all restaurant chains")
            
            return topology
        else:
            print("⚠️ No devices found - check API permissions")
            return None
            
    except Exception as e:
        print(f"❌ Full-scale discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        await discovery.close_session()

if __name__ == "__main__":
    asyncio.run(main())