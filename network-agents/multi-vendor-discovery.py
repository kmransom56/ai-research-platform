#!/usr/bin/env python3
"""
Multi-Vendor Network Discovery
Combines Meraki and FortiManager devices for comprehensive restaurant network management
"""

import json
import logging
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase

# Import vendor-specific modules
try:
    from fortimanager_api import FortiManagerAPI
    FORTINET_AVAILABLE = True
except ImportError:
    print("⚠️  FortiManager API not available - Fortinet devices will be skipped")
    FORTINET_AVAILABLE = False

try:
    import meraki
    MERAKI_AVAILABLE = True
except ImportError:
    print("⚠️  Meraki SDK not available - Meraki devices will be skipped")
    MERAKI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiVendorDiscovery:
    """Multi-vendor network discovery for restaurant chains"""
    
    def __init__(self):
        self.discovered_devices = []
        self.discovered_networks = []
        self.discovered_organizations = []
        self.neo4j_driver = None
        
        # Initialize vendor APIs
        self.meraki_api = None
        self.fortimanager_apis = []
        
        self._initialize_apis()
        
    def _initialize_apis(self):
        """Initialize all available vendor APIs"""
        try:
            # Initialize Meraki API
            if MERAKI_AVAILABLE:
                meraki_key = os.getenv('MERAKI_API_KEY')
                if meraki_key:
                    self.meraki_api = meraki.DashboardAPI(
                        api_key=meraki_key,
                        print_console=False,
                        suppress_logging=True
                    )
                    logger.info("✅ Meraki API initialized")
                else:
                    logger.warning("⚠️  MERAKI_API_KEY not found in environment")
            
            # Initialize FortiManager APIs (can have multiple)
            if FORTINET_AVAILABLE:
                fm_configs = self._get_fortimanager_configs()
                for config in fm_configs:
                    try:
                        fm_api = FortiManagerAPI(
                            host=config['host'],
                            username=config['username'],
                            password=config['password'],
                            site=config.get('site', 'default')
                        )
                        self.fortimanager_apis.append({
                            'api': fm_api,
                            'site': config.get('site', 'default'),
                            'host': config['host']
                        })
                        logger.info(f"✅ FortiManager API initialized for {config['host']}")
                    except Exception as e:
                        logger.error(f"❌ Failed to initialize FortiManager {config['host']}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error initializing vendor APIs: {str(e)}")
    
    def _get_fortimanager_configs(self):
        """Get FortiManager configurations from environment"""
        configs = []
        
        # Single FortiManager configuration
        fm_host = os.getenv('FORTIMANAGER_HOST')
        fm_username = os.getenv('FORTIMANAGER_USERNAME') 
        fm_password = os.getenv('FORTIMANAGER_PASSWORD')
        
        if all([fm_host, fm_username, fm_password]):
            configs.append({
                'host': fm_host,
                'username': fm_username,
                'password': fm_password,
                'site': os.getenv('FORTIMANAGER_SITE', 'default')
            })
        
        # Multiple FortiManager configurations (FM1_, FM2_, etc.)
        for i in range(1, 10):  # Support up to 10 FortiManager instances
            fm_host = os.getenv(f'FORTIMANAGER{i}_HOST')
            fm_username = os.getenv(f'FORTIMANAGER{i}_USERNAME')
            fm_password = os.getenv(f'FORTIMANAGER{i}_PASSWORD')
            
            if all([fm_host, fm_username, fm_password]):
                configs.append({
                    'host': fm_host,
                    'username': fm_username,
                    'password': fm_password,
                    'site': os.getenv(f'FORTIMANAGER{i}_SITE', f'site{i}')
                })
        
        return configs
    
    def discover_all_devices(self):
        """Discover devices from all vendor platforms"""
        logger.info("🔍 Starting multi-vendor network discovery...")
        
        all_devices = []
        all_networks = []
        all_organizations = []
        
        # Discover Meraki devices
        if self.meraki_api:
            try:
                meraki_data = self._discover_meraki_devices()
                all_devices.extend(meraki_data.get('devices', []))
                all_networks.extend(meraki_data.get('networks', []))
                all_organizations.extend(meraki_data.get('organizations', []))
                logger.info(f"✅ Meraki discovery: {len(meraki_data.get('devices', []))} devices")
            except Exception as e:
                logger.error(f"❌ Meraki discovery failed: {str(e)}")
        
        # Discover Fortinet devices
        for fm_config in self.fortimanager_apis:
            try:
                fortinet_data = self._discover_fortinet_devices(fm_config)
                all_devices.extend(fortinet_data.get('devices', []))
                all_networks.extend(fortinet_data.get('networks', []))
                all_organizations.extend(fortinet_data.get('organizations', []))
                logger.info(f"✅ Fortinet discovery ({fm_config['site']}): {len(fortinet_data.get('devices', []))} devices")
            except Exception as e:
                logger.error(f"❌ Fortinet discovery failed for {fm_config['host']}: {str(e)}")
        
        # Store discovered data
        self.discovered_devices = all_devices
        self.discovered_networks = all_networks
        self.discovered_organizations = all_organizations
        
        # Generate summary
        summary = self._generate_discovery_summary()
        logger.info("🎯 Multi-vendor discovery completed!")
        logger.info(f"📊 Summary: {summary}")
        
        return {
            'devices': all_devices,
            'networks': all_networks,
            'organizations': all_organizations,
            'summary': summary
        }
    
    def _discover_meraki_devices(self):
        """Discover Meraki devices and networks"""
        devices = []
        networks = []
        organizations = []
        
        try:
            # Get organizations
            meraki_orgs = self.meraki_api.organizations.getOrganizations()
            
            for org in meraki_orgs:
                org_data = {
                    'id': org['id'],
                    'name': org['name'],
                    'vendor': 'Meraki',
                    'type': 'organization'
                }
                organizations.append(org_data)
                
                # Get networks for organization
                try:
                    org_networks = self.meraki_api.organizations.getOrganizationNetworks(org['id'])
                    
                    for network in org_networks:
                        network_data = {
                            'id': network['id'],
                            'name': network['name'],
                            'organization_id': org['id'],
                            'organization_name': org['name'],
                            'vendor': 'Meraki',
                            'type': 'network',
                            'product_types': network.get('productTypes', [])
                        }
                        networks.append(network_data)
                        
                        # Get devices for network
                        try:
                            network_devices = self.meraki_api.networks.getNetworkDevices(network['id'])
                            
                            for device in network_devices:
                                device_data = {
                                    'id': device.get('serial', 'unknown'),
                                    'name': device.get('name', device.get('serial', 'Unknown')),
                                    'serial': device.get('serial', 'N/A'),
                                    'model': device.get('model', 'Unknown'),
                                    'vendor': 'Meraki',
                                    'device_type': self._get_meraki_device_type(device.get('model', '')),
                                    'status': 'online' if device.get('status') == 'online' else 'offline',
                                    'network_id': network['id'],
                                    'network_name': network['name'],
                                    'organization_id': org['id'],
                                    'organization_name': org['name'],
                                    'mac_address': device.get('mac', 'N/A'),
                                    'lan_ip': device.get('lanIp', 'N/A'),
                                    'wan1_ip': device.get('wan1Ip', 'N/A'),
                                    'public_ip': device.get('publicIp', 'N/A'),
                                    'firmware': device.get('firmware', 'N/A'),
                                    'notes': device.get('notes', ''),
                                    'tags': device.get('tags', [])
                                }
                                devices.append(device_data)
                                
                        except Exception as e:
                            logger.warning(f"Failed to get devices for network {network['name']}: {str(e)}")
                            
                except Exception as e:
                    logger.warning(f"Failed to get networks for org {org['name']}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Meraki discovery error: {str(e)}")
        
        return {
            'devices': devices,
            'networks': networks,
            'organizations': organizations
        }
    
    def _discover_fortinet_devices(self, fm_config):
        """Discover Fortinet devices from FortiManager"""
        devices = []
        networks = []
        organizations = []
        
        try:
            fm_api = fm_config['api']
            site = fm_config['site']
            
            if fm_api.login():
                # Get managed devices
                managed_devices = fm_api.get_managed_devices()
                
                # Create organization for this FortiManager
                org_data = {
                    'id': f"fortinet_{site}",
                    'name': f"Fortinet {site}",
                    'vendor': 'Fortinet',
                    'type': 'organization',
                    'fortimanager_host': fm_config['host']
                }
                organizations.append(org_data)
                
                # Process devices
                for device in managed_devices:
                    device_data = {
                        'id': f"fortinet_{device['serial']}",
                        'name': device['name'],
                        'serial': device['serial'],
                        'model': device['model'],
                        'vendor': 'Fortinet',
                        'device_type': device['device_type'],
                        'status': device['status'],
                        'network_id': f"fortinet_{site}_network",
                        'network_name': f"{site} Network",
                        'organization_id': f"fortinet_{site}",
                        'organization_name': f"Fortinet {site}",
                        'ip_address': device['ip'],
                        'os_version': device['os_ver'],
                        'last_seen': device.get('last_seen', 'N/A'),
                        'uptime': device.get('uptime', 'N/A'),
                        'fortimanager_host': fm_config['host']
                    }
                    devices.append(device_data)
                
                # Create network for this site
                network_data = {
                    'id': f"fortinet_{site}_network",
                    'name': f"{site} Network",
                    'organization_id': f"fortinet_{site}",
                    'organization_name': f"Fortinet {site}",
                    'vendor': 'Fortinet',
                    'type': 'network',
                    'device_count': len(managed_devices)
                }
                networks.append(network_data)
                
                fm_api.logout()
                
        except Exception as e:
            logger.error(f"FortiManager discovery error for {fm_config['host']}: {str(e)}")
        
        return {
            'devices': devices,
            'networks': networks,
            'organizations': organizations
        }
    
    def _get_meraki_device_type(self, model):
        """Determine Meraki device type from model"""
        model_lower = model.lower()
        if model_lower.startswith('mr'):
            return 'Access Point'
        elif model_lower.startswith('ms'):
            return 'Switch'
        elif model_lower.startswith('mx'):
            return 'Security Appliance'
        elif model_lower.startswith('mv'):
            return 'Camera'
        elif model_lower.startswith('mt'):
            return 'Sensor'
        else:
            return 'Unknown'
    
    def _generate_discovery_summary(self):
        """Generate discovery summary statistics"""
        summary = {
            'total_devices': len(self.discovered_devices),
            'total_networks': len(self.discovered_networks),
            'total_organizations': len(self.discovered_organizations),
            'vendors': {},
            'device_types': {},
            'status_count': {'online': 0, 'offline': 0}
        }
        
        # Count by vendor
        for device in self.discovered_devices:
            vendor = device.get('vendor', 'Unknown')
            summary['vendors'][vendor] = summary['vendors'].get(vendor, 0) + 1
            
            device_type = device.get('device_type', 'Unknown')
            summary['device_types'][device_type] = summary['device_types'].get(device_type, 0) + 1
            
            status = device.get('status', 'unknown')
            if status in summary['status_count']:
                summary['status_count'][status] += 1
        
        return summary
    
    def load_to_neo4j(self):
        """Load discovered devices into Neo4j database"""
        try:
            # Connect to Neo4j
            self.neo4j_driver = GraphDatabase.driver(
                "neo4j://localhost:7687",
                auth=("neo4j", "password")
            )
            
            with self.neo4j_driver.session() as session:
                # Load organizations
                for org in self.discovered_organizations:
                    session.run("""
                        MERGE (o:Organization {id: $id})
                        SET o.name = $name,
                            o.vendor = $vendor,
                            o.type = $type,
                            o.updated_timestamp = datetime()
                    """, org)
                
                # Load networks
                for network in self.discovered_networks:
                    session.run("""
                        MERGE (n:Network {id: $id})
                        SET n.name = $name,
                            n.vendor = $vendor,
                            n.type = $type,
                            n.updated_timestamp = datetime()
                        
                        WITH n
                        MATCH (o:Organization {id: $organization_id})
                        MERGE (o)-[:CONTAINS]->(n)
                    """, network)
                
                # Load devices
                device_count = 0
                for device in self.discovered_devices:
                    session.run("""
                        MERGE (d:Device {id: $id})
                        SET d.name = $name,
                            d.serial = $serial,
                            d.model = $model,
                            d.vendor = $vendor,
                            d.device_type = $device_type,
                            d.status = $status,
                            d.updated_timestamp = datetime()
                        
                        WITH d
                        MATCH (n:Network {id: $network_id})
                        MERGE (n)-[:CONTAINS]->(d)
                    """, device)
                    
                    device_count += 1
                    if device_count % 100 == 0:
                        logger.info(f"Loaded {device_count} devices to Neo4j...")
                
                logger.info(f"✅ Successfully loaded {device_count} devices to Neo4j")
            
            self.neo4j_driver.close()
            
        except Exception as e:
            logger.error(f"Neo4j loading error: {str(e)}")
    
    def save_discovery_results(self):
        """Save discovery results to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save comprehensive results
        results = {
            'timestamp': timestamp,
            'devices': self.discovered_devices,
            'networks': self.discovered_networks,
            'organizations': self.discovered_organizations,
            'summary': self._generate_discovery_summary()
        }
        
        filename = f"multi_vendor_discovery_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📁 Discovery results saved to {filename}")
        return filename

def main():
    """Main discovery function"""
    discovery = MultiVendorDiscovery()
    
    # Perform discovery
    results = discovery.discover_all_devices()
    
    # Save results
    filename = discovery.save_discovery_results()
    
    # Load to Neo4j
    discovery.load_to_neo4j()
    
    # Print summary
    print("\n🎯 Multi-Vendor Network Discovery Complete!")
    print("=" * 60)
    print(f"📊 Total Devices: {results['summary']['total_devices']}")
    print(f"📊 Total Networks: {results['summary']['total_networks']}")
    print(f"📊 Total Organizations: {results['summary']['total_organizations']}")
    print("\nVendor Breakdown:")
    for vendor, count in results['summary']['vendors'].items():
        print(f"  - {vendor}: {count} devices")
    print("\nDevice Type Breakdown:")
    for device_type, count in results['summary']['device_types'].items():
        print(f"  - {device_type}: {count} devices")
    print(f"\n📁 Results saved to: {filename}")
    print("🔗 Data loaded to Neo4j database")

if __name__ == "__main__":
    main()