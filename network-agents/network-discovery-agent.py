"""
Network Discovery Agent
Discovers and catalogs network infrastructure across Meraki organizations
"""

import requests
import json
from datetime import datetime
import time
from typing import Dict, List, Any
import logging

class NetworkDiscoveryAgent:
    def __init__(self, meraki_api_base: str = "http://localhost:11030"):
        self.meraki_api = meraki_api_base
        self.logger = logging.getLogger("NetworkDiscovery")
        self.discovery_data = {
            "timestamp": None,
            "organizations": [],
            "networks": [],
            "devices": [],
            "summary": {}
        }

    async def discover_all_networks(self) -> Dict[str, Any]:
        """
        Complete network discovery across all accessible organizations
        """
        self.logger.info("🔍 Starting comprehensive network discovery")
        start_time = datetime.now()
        
        try:
            # Get all organizations
            orgs_response = requests.get(f"{self.meraki_api}/organizations")
            organizations = orgs_response.json()
            
            total_networks = 0
            total_devices = 0
            org_summary = []
            
            for org in organizations:
                org_id = org['id']
                org_name = org['name']
                
                self.logger.info(f"📡 Discovering networks in {org_name}")
                
                # Get networks for this organization
                networks_response = requests.get(f"{self.meraki_api}/organizations/{org_id}/networks")
                networks = networks_response.json()
                
                org_networks = len(networks)
                org_devices = 0
                
                # For each network, get devices (limit to first 10 for demo)
                for network in networks[:10]:  # Limit for demo purposes
                    network_id = network['id']
                    
                    try:
                        devices_response = requests.get(f"{self.meraki_api}/networks/{network_id}/devices")
                        devices = devices_response.json()
                        org_devices += len(devices)
                        
                        # Store device data
                        for device in devices:
                            device['organization_name'] = org_name
                            device['network_name'] = network['name']
                            self.discovery_data["devices"].append(device)
                        
                        # Rate limiting
                        time.sleep(0.2)
                        
                    except Exception as e:
                        self.logger.warning(f"Could not get devices for network {network['name']}: {e}")
                
                total_networks += org_networks
                total_devices += org_devices
                
                org_summary.append({
                    "name": org_name,
                    "id": org_id,
                    "networks": org_networks,
                    "devices_sampled": org_devices,
                    "regions": org.get('cloud_region_name', 'Unknown')
                })
                
                # Store organization and network data
                self.discovery_data["organizations"].append(org)
                self.discovery_data["networks"].extend(networks)
            
            # Create summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.discovery_data["timestamp"] = start_time.isoformat()
            self.discovery_data["summary"] = {
                "total_organizations": len(organizations),
                "total_networks": total_networks,
                "total_devices_discovered": total_devices,
                "discovery_duration_seconds": duration,
                "organizations": org_summary
            }
            
            self.logger.info(f"✅ Discovery complete: {len(organizations)} orgs, {total_networks} networks, {total_devices} devices")
            return self.discovery_data
            
        except Exception as e:
            self.logger.error(f"❌ Discovery failed: {e}")
            raise

    def get_organization_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all discovered organizations"""
        return self.discovery_data["summary"].get("organizations", [])

    def get_devices_by_status(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group devices by their status"""
        devices_by_status = {
            "online": [],
            "offline": [],
            "unknown": [],
            "alerting": []
        }
        
        for device in self.discovery_data["devices"]:
            status = device.get("status", "unknown").lower()
            if status in devices_by_status:
                devices_by_status[status].append(device)
            else:
                devices_by_status["unknown"].append(device)
                
        return devices_by_status

    def get_devices_by_location(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group devices by their network/location"""
        devices_by_location = {}
        
        for device in self.discovery_data["devices"]:
            location = device.get("network_name", "Unknown Location")
            if location not in devices_by_location:
                devices_by_location[location] = []
            devices_by_location[location].append(device)
            
        return devices_by_location

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate network health report"""
        devices_by_status = self.get_devices_by_status()
        devices_by_location = self.get_devices_by_location()
        
        # Calculate health metrics
        total_devices = len(self.discovery_data["devices"])
        online_devices = len(devices_by_status["online"])
        offline_devices = len(devices_by_status["offline"])
        unknown_devices = len(devices_by_status["unknown"])
        
        health_percentage = (online_devices / total_devices * 100) if total_devices > 0 else 0
        
        # Identify problem locations
        problem_locations = []
        for location, devices in devices_by_location.items():
            offline_count = sum(1 for d in devices if d.get("status", "").lower() in ["offline", "alerting"])
            if offline_count > 0:
                problem_locations.append({
                    "location": location,
                    "total_devices": len(devices),
                    "offline_devices": offline_count,
                    "health_percentage": ((len(devices) - offline_count) / len(devices) * 100)
                })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": {
                "total_devices": total_devices,
                "online": online_devices,
                "offline": offline_devices,
                "unknown": unknown_devices,
                "health_percentage": round(health_percentage, 2)
            },
            "status_distribution": {k: len(v) for k, v in devices_by_status.items()},
            "problem_locations": sorted(problem_locations, key=lambda x: x["health_percentage"]),
            "organizations_summary": self.get_organization_summary()
        }

# Example usage for AutoGen Studio
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = NetworkDiscoveryAgent()
        
        # Run discovery
        discovery_results = await agent.discover_all_networks()
        
        # Generate health report
        health_report = agent.generate_health_report()
        
        print("=== NETWORK DISCOVERY COMPLETE ===")
        print(f"Organizations: {discovery_results['summary']['total_organizations']}")
        print(f"Networks: {discovery_results['summary']['total_networks']}")
        print(f"Devices: {discovery_results['summary']['total_devices_discovered']}")
        print(f"Overall Health: {health_report['overall_health']['health_percentage']:.1f}%")
        
        # Print problem locations
        if health_report['problem_locations']:
            print(f"\n⚠️  LOCATIONS NEEDING ATTENTION:")
            for location in health_report['problem_locations'][:5]:  # Top 5 problem locations
                print(f"  - {location['location']}: {location['offline_devices']}/{location['total_devices']} offline ({location['health_percentage']:.1f}% healthy)")
    
    asyncio.run(main())