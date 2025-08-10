"""
FortiManager API Module - Restaurant Network Integration
Enhanced version of the proven FortiManager API for restaurant network management
Based on: https://github.com/kmransom56/meraki_management_application
"""

import json
import requests
import logging
from typing import Dict, List, Optional, Any
import os

# Apply SSL fixes for corporate environments with self-signed certificates
try:
    from ssl_universal_fix import apply_all_ssl_fixes
    apply_all_ssl_fixes(verbose=False)
    print("[FortiManager API] SSL fixes applied successfully")
except ImportError:
    print("[FortiManager API] SSL fix module not found, using manual SSL bypass")
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning
    urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class FortiManagerAPI:
    """FortiManager JSON-RPC API client for centralized device management"""
    
    def __init__(self, host, username, password, port=443, timeout=30, site=None):
        """
        Initialize FortiManager API client
        
        Args:
            host (str): FortiManager IP address or hostname
            username (str): FortiManager username
            password (str): FortiManager password
            port (int): HTTPS port (default: 443)
            timeout (int): Request timeout (default: 30)
            site (str): Site name for Redis session management (default: 'default')
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.site = site or 'default'
        self.base_url = f"https://{host}:{port}/jsonrpc"
        self.session_id = None
        
        # Create session with SSL verification disabled
        self.session = requests.Session()
        self.session.verify = False
        
        # Initialize session managers if available
        self.redis_session_manager = None
        self.fm_session_manager = None
        self._initialize_session_managers()
        
    def _initialize_session_managers(self):
        """Initialize Redis and FortiManager session managers if available"""
        try:
            from redis_session_manager import get_session_managers
            self.redis_session_manager, self.fm_session_manager = get_session_managers()
            if self.redis_session_manager:
                logger.info(f"Redis session management enabled for {self.site}")
        except ImportError:
            logger.info("Redis session management not available - using direct connections")
        except Exception as e:
            logger.warning(f"Session manager initialization failed: {str(e)}")
    
    def login(self):
        """
        Login to FortiManager and establish session with Redis token reuse
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # First, try to get cached session token from Redis
            if self.fm_session_manager:
                cached_session = self.fm_session_manager.get_fortimanager_session(
                    self.site, self.host, self.username
                )
                if cached_session:
                    self.session_id = cached_session
                    logger.info(f"Using cached FortiManager session for {self.site}: {self.host}")
                    return True
            
            logger.info(f"Attempting new login to FortiManager: {self.host}:{self.port}")
            logger.info(f"Using username: {self.username}")
            logger.info(f"JSON-RPC URL: {self.base_url}")
            
            payload = {
                "method": "exec",
                "params": [{
                    "url": "/sys/login/user",
                    "data": {
                        "user": self.username,
                        "passwd": self.password
                    }
                }],
                "id": 1
            }
            
            logger.debug(f"Login payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            logger.info(f"Login response status: {response.status_code}")
            logger.debug(f"Login response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.debug(f"Login response JSON: {json.dumps(result, indent=2)}")
                    
                    if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                        self.session_id = result.get('session')
                        logger.info(f"Successfully logged into FortiManager: {self.host}")
                        logger.info(f"Session ID: {self.session_id}")
                        
                        # Store session token in Redis for reuse
                        if self.fm_session_manager and self.session_id:
                            self.fm_session_manager.store_fortimanager_session(
                                self.site, self.host, self.username, self.session_id
                            )
                            logger.info(f"Stored FortiManager session token in Redis for {self.site}")
                        
                        return True
                    else:
                        error_code = result.get('result', [{}])[0].get('status', {}).get('code', 'Unknown')
                        error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                        logger.error(f"FortiManager login failed - Code: {error_code}, Message: {error_msg}")
                        return False
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {str(e)}")
                    logger.error(f"Raw response: {response.text[:500]}")
                    return False
            else:
                logger.error(f"FortiManager login HTTP error: {response.status_code}")
                logger.error(f"Response text: {response.text[:500]}")
                return False
                
        except requests.exceptions.ConnectTimeout as e:
            logger.error(f"FortiManager connection timeout: {str(e)}")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"FortiManager connection error: {str(e)}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"FortiManager request error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"FortiManager login unexpected error: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return False
    
    def logout(self):
        """Logout from FortiManager"""
        try:
            if self.session_id:
                payload = {
                    "method": "exec",
                    "params": [{
                        "url": "/sys/logout"
                    }],
                    "session": self.session_id,
                    "id": 1
                }
                
                self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                self.session_id = None
                logger.info("Logged out from FortiManager")
                
        except Exception as e:
            logger.error(f"FortiManager logout error: {str(e)}")
    
    def get_managed_devices(self):
        """
        Get list of managed devices from FortiManager
        Enhanced for restaurant network classification
        
        Returns:
            list: List of managed devices with details
        """
        try:
            if not self.session_id:
                logger.error("Not logged into FortiManager")
                return []
            
            payload = {
                "method": "get",
                "params": [{
                    "url": "/dvmdb/device"
                }],
                "session": self.session_id,
                "id": 1
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    devices = result.get('result', [{}])[0].get('data', [])
                    
                    # Process device information with restaurant enhancements
                    processed_devices = []
                    for device in devices:
                        # Determine restaurant organization from device metadata
                        organization = self._determine_restaurant_organization(device)
                        device_type = self._determine_device_type(device.get('platform_str', ''))
                        
                        processed_device = {
                            'name': device.get('name', 'Unknown'),
                            'serial': device.get('sn', 'N/A'),
                            'model': device.get('platform_str', 'N/A'),
                            'os_ver': device.get('os_ver', 'N/A'),
                            'status': 'online' if device.get('conn_status') == 1 else 'offline',
                            'ip': device.get('ip', 'N/A'),
                            'site': device.get('meta fields', {}).get('Company/Organization', self.site),
                            'device_type': device_type,
                            'vendor': 'Fortinet',
                            'organization': organization,
                            'restaurant_role': self._determine_restaurant_role(device.get('name', ''), device_type),
                            'last_seen': device.get('last_resync', 'N/A'),
                            'uptime': device.get('uptime', 'N/A'),
                            'fortimanager_host': self.host
                        }
                        processed_devices.append(processed_device)
                    
                    logger.info(f"Retrieved {len(processed_devices)} managed devices from {self.host}")
                    return processed_devices
                else:
                    error_msg = result.get('result', [{}])[0].get('status', {}).get('message', 'Unknown error')
                    logger.error(f"Failed to get managed devices: {error_msg}")
                    return []
            else:
                logger.error(f"Get managed devices HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting managed devices: {str(e)}")
            return []
    
    def _determine_restaurant_organization(self, device):
        """Determine restaurant organization from device metadata"""
        device_name = device.get('name', '').lower()
        site = device.get('meta fields', {}).get('Company/Organization', '').lower()
        
        # Check device name patterns
        if any(x in device_name for x in ['arby', 'arbys']):
            return "Arby's"
        elif any(x in device_name for x in ['bww', 'buffalo', 'wild', 'wings']):
            return "Buffalo Wild Wings"
        elif 'sonic' in device_name:
            return "Sonic"
        
        # Check site/organization metadata
        if any(x in site for x in ['arby', 'arbys']):
            return "Arby's"
        elif any(x in site for x in ['bww', 'buffalo', 'wild', 'wings']):
            return "Buffalo Wild Wings"
        elif 'sonic' in site:
            return "Sonic"
        
        # Fallback to site name
        return self.site.title()
    
    def _determine_device_type(self, platform_str):
        """Determine device type from platform string"""
        if not platform_str:
            return 'Unknown'
            
        platform_lower = platform_str.lower()
        
        # FortiGate models
        if any(x in platform_lower for x in ['fortigate', 'fgt']):
            return 'FortiGate'
        
        # FortiAP models
        elif any(x in platform_lower for x in ['fortiap', 'fap']):
            return 'FortiAP'
        
        # FortiSwitch models
        elif any(x in platform_lower for x in ['fortiswitch', 'fs']):
            return 'FortiSwitch'
        
        # Generic detection by model number patterns
        elif platform_str.startswith('FGT'):
            return 'FortiGate'
        elif platform_str.startswith('FAP'):
            return 'FortiAP'
        elif platform_str.startswith('FS'):
            return 'FortiSwitch'
        else:
            return 'Fortinet Device'
    
    def _determine_restaurant_role(self, device_name, device_type):
        """Determine restaurant-specific role from device name and type"""
        name_lower = device_name.lower()
        
        if device_type == 'FortiGate':
            if any(x in name_lower for x in ['store', 'branch', 'location']):
                return 'Store Firewall'
            elif any(x in name_lower for x in ['corporate', 'hq', 'datacenter']):
                return 'Corporate Firewall'
            else:
                return 'Network Security'
        
        elif device_type == 'FortiAP':
            if any(x in name_lower for x in ['customer', 'guest', 'public']):
                return 'Customer WiFi'
            elif any(x in name_lower for x in ['staff', 'employee', 'pos']):
                return 'Staff WiFi'
            elif any(x in name_lower for x in ['kitchen', 'back']):
                return 'Kitchen Operations'
            else:
                return 'WiFi Access'
        
        elif device_type == 'FortiSwitch':
            if any(x in name_lower for x in ['pos', 'register']):
                return 'POS Network'
            elif any(x in name_lower for x in ['kitchen', 'kds']):
                return 'Kitchen Network'
            else:
                return 'Network Switching'
        
        else:
            return 'Network Equipment'
    
    def get_device_interfaces(self, device_name):
        """
        Get interfaces for a specific device
        
        Args:
            device_name (str): Name of the device
            
        Returns:
            list: List of device interfaces
        """
        try:
            if not self.session_id:
                logger.error("Not logged into FortiManager")
                return []
            
            payload = {
                "method": "get",
                "params": [{
                    "url": f"/pm/config/device/{device_name}/global/system/interface"
                }],
                "session": self.session_id,
                "id": 1
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    interfaces = result.get('result', [{}])[0].get('data', [])
                    
                    # Process interface information
                    processed_interfaces = []
                    for interface in interfaces:
                        processed_interface = {
                            'name': interface.get('name', 'Unknown'),
                            'ip': interface.get('ip', ['0.0.0.0', '0.0.0.0'])[0] if isinstance(interface.get('ip'), list) else interface.get('ip', '0.0.0.0'),
                            'status': interface.get('status', 'down'),
                            'type': interface.get('type', 'unknown'),
                            'vdom': interface.get('vdom', 'root')
                        }
                        processed_interfaces.append(processed_interface)
                    
                    return processed_interfaces
                else:
                    logger.warning(f"Failed to get interfaces for {device_name}")
                    return []
            else:
                logger.error(f"Get interfaces HTTP error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Error getting interfaces for {device_name}: {str(e)}")
            return []
    
    def get_device_inventory(self):
        """
        Get comprehensive device inventory with restaurant-specific enhancements
        
        Returns:
            dict: Device inventory data with nodes and connections
        """
        try:
            devices = self.get_managed_devices()
            
            inventory_data = {
                'nodes': [],
                'edges': [],
                'vlans': {},
                'stats': {
                    'total_devices': len(devices),
                    'online_devices': len([d for d in devices if d['status'] == 'online']),
                    'offline_devices': len([d for d in devices if d['status'] == 'offline']),
                    'fortigates': len([d for d in devices if d['device_type'] == 'FortiGate']),
                    'fortiaps': len([d for d in devices if d['device_type'] == 'FortiAP']),
                    'fortiswitches': len([d for d in devices if d['device_type'] == 'FortiSwitch']),
                    'organizations': {}
                }
            }
            
            # Process devices into nodes with restaurant enhancements
            for device in devices:
                # Count by organization
                org = device.get('organization', 'Unknown')
                inventory_data['stats']['organizations'][org] = inventory_data['stats']['organizations'].get(org, 0) + 1
                
                # Determine icon and color based on device type and status
                icon, color = self._get_device_icon_color(device['device_type'], device['status'])
                
                node = {
                    'id': f"fortinet_{device['serial']}",
                    'name': device['name'],
                    'type': device['device_type'].lower().replace(' ', '_'),
                    'vendor': 'Fortinet',
                    'model': device['model'],
                    'serial': device['serial'],
                    'status': device['status'],
                    'ip': device['ip'],
                    'site': device['site'],
                    'organization': device['organization'],
                    'restaurant_role': device['restaurant_role'],
                    'os_version': device['os_ver'],
                    'size': 40,  # Enhanced size for Fortinet devices
                    'icon': icon,
                    'color': color,
                    'last_seen': device['last_seen'],
                    'uptime': device['uptime'],
                    'fortimanager_host': self.host
                }
                inventory_data['nodes'].append(node)
                
                # Get interfaces for connection mapping
                interfaces = self.get_device_interfaces(device['name'])
                for interface in interfaces:
                    if interface['status'] == 'up' and interface['ip'] != '0.0.0.0':
                        # Create VLAN/network information
                        vlan_key = f"fortinet_{device['name']}_{interface['name']}"
                        inventory_data['vlans'][vlan_key] = {
                            'name': interface['name'],
                            'ip': interface['ip'],
                            'device': device['name'],
                            'type': interface['type'],
                            'vdom': interface['vdom'],
                            'vendor': 'Fortinet',
                            'organization': device['organization']
                        }
            
            logger.info(f"Generated Fortinet inventory: {len(inventory_data['nodes'])} devices, {len(inventory_data['vlans'])} interfaces")
            logger.info(f"Restaurant breakdown: {inventory_data['stats']['organizations']}")
            return inventory_data
            
        except Exception as e:
            logger.error(f"Error getting Fortinet device inventory: {str(e)}")
            return {'nodes': [], 'edges': [], 'vlans': {}, 'stats': {}}
    
    def _get_device_icon_color(self, device_type, status):
        """Get appropriate icon and color for device type and status"""
        # Base colors - Fortinet red theme
        online_color = '#d43527'  # Fortinet red
        offline_color = '#6c757d'  # Gray
        
        color = online_color if status == 'online' else offline_color
        
        # Icons based on device type
        if device_type == 'FortiGate':
            icon = 'fas fa-shield-alt'  # Security/firewall icon
        elif device_type == 'FortiAP':
            icon = 'fas fa-wifi'  # WiFi icon
        elif device_type == 'FortiSwitch':
            icon = 'fas fa-network-wired'  # Network switch icon
        else:
            icon = 'fas fa-server'  # Generic device icon
        
        return icon, color
    
    def get_device_status(self, device_name):
        """
        Get detailed status for a specific device
        
        Args:
            device_name (str): Name of the device
            
        Returns:
            dict: Device status information
        """
        try:
            if not self.session_id:
                logger.error("Not logged into FortiManager")
                return {}
            
            payload = {
                "method": "get",
                "params": [{
                    "url": f"/dvmdb/device/{device_name}"
                }],
                "session": self.session_id,
                "id": 1
            }
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result', [{}])[0].get('status', {}).get('code') == 0:
                    device_data = result.get('result', [{}])[0].get('data', {})
                    
                    status = {
                        'name': device_data.get('name', 'Unknown'),
                        'status': 'online' if device_data.get('conn_status') == 1 else 'offline',
                        'last_seen': device_data.get('last_resync', 'N/A'),
                        'uptime': device_data.get('uptime', 'N/A'),
                        'cpu_usage': device_data.get('cpu', 'N/A'),
                        'memory_usage': device_data.get('mem', 'N/A'),
                        'version': device_data.get('os_ver', 'N/A'),
                        'model': device_data.get('platform_str', 'N/A'),
                        'serial': device_data.get('sn', 'N/A')
                    }
                    
                    return status
                else:
                    logger.error(f"Failed to get status for {device_name}")
                    return {}
            else:
                logger.error(f"Get device status HTTP error: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting device status for {device_name}: {str(e)}")
            return {}

def load_env_file():
    """Load environment variables from .env file"""
    import os
    from pathlib import Path
    
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"⚠️  .env file not found at {env_path}")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
        
        print(f"✅ Loaded environment variables from {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading .env file: {str(e)}")
        return False

def test_fortimanager_connection():
    """Test FortiManager API connection with restaurant chain detection"""
    # Load environment variables
    load_env_file()
    
    # Test all three restaurant FortiManagers
    fortimanager_configs = [
        {
            'name': 'Arby\'s',
            'host': os.getenv('ARBYS_FORTIMANAGER_HOST'),
            'username': os.getenv('ARBYS_USERNAME'),
            'password': os.getenv('ARBYS_PASSWORD'),
            'site': 'arbys'
        },
        {
            'name': 'Buffalo Wild Wings',
            'host': os.getenv('BWW_FORTIMANAGER_HOST'),
            'username': os.getenv('BWW_USERNAME'),
            'password': os.getenv('BWW_PASSWORD'),
            'site': 'bww'
        },
        {
            'name': 'Sonic',
            'host': os.getenv('SONIC_FORTIMANAGER_HOST'),
            'username': os.getenv('SONIC_USERNAME'),
            'password': os.getenv('SONIC_PASSWORD'),
            'site': 'sonic'
        }
    ]
    
    total_devices = 0
    total_online = 0
    restaurant_summary = {}
    
    for config in fortimanager_configs:
        if not all([config['host'], config['username'], config['password']]):
            print(f"⚠️  {config['name']} FortiManager credentials incomplete - skipping")
            continue
            
        print(f"\n🔍 Testing {config['name']} FortiManager: {config['host']}")
        print("-" * 60)
        
        try:
            fm = FortiManagerAPI(config['host'], config['username'], config['password'], site=config['site'])
            
            if fm.login():
                print(f"✅ Successfully connected to {config['name']} FortiManager")
                
                devices = fm.get_managed_devices()
                print(f"📊 Found {len(devices)} managed devices")
                
                # Count devices and status
                site_devices = len(devices)
                site_online = len([d for d in devices if d['status'] == 'online'])
                
                total_devices += site_devices
                total_online += site_online
                
                # Track by restaurant
                restaurant_summary[config['name']] = {
                    'total': site_devices,
                    'online': site_online,
                    'host': config['host']
                }
                
                # Show device breakdown by type
                device_types = {}
                restaurant_roles = {}
                
                for device in devices:
                    device_type = device.get('device_type', 'Unknown')
                    device_types[device_type] = device_types.get(device_type, 0) + 1
                    
                    role = device.get('restaurant_role', 'Unknown')
                    restaurant_roles[role] = restaurant_roles.get(role, 0) + 1
                
                print(f"🛡️  Device Types: {dict(device_types)}")
                print(f"🍽️  Restaurant Roles: {dict(restaurant_roles)}")
                print(f"📈 Health: {site_online}/{site_devices} online ({(site_online/site_devices)*100:.1f}%)")
                
                # Show first few devices
                print("📋 Sample Devices:")
                for device in devices[:3]:
                    print(f"  - {device['name']} ({device['model']}) - {device['status']} - {device.get('restaurant_role', 'N/A')}")
                
                fm.logout()
                
            else:
                print(f"❌ Failed to login to {config['name']} FortiManager")
                restaurant_summary[config['name']] = {
                    'total': 0,
                    'online': 0,
                    'host': config['host'],
                    'error': 'Login failed'
                }
                
        except Exception as e:
            print(f"❌ {config['name']} FortiManager test failed: {str(e)}")
            restaurant_summary[config['name']] = {
                'total': 0,
                'online': 0, 
                'host': config['host'],
                'error': str(e)
            }
    
    # Overall summary
    print(f"\n🎯 OVERALL RESTAURANT NETWORK SUMMARY")
    print("=" * 60)
    print(f"📊 Total Fortinet Devices: {total_devices}")
    print(f"📊 Total Online: {total_online}")
    if total_devices > 0:
        print(f"📊 Overall Health: {(total_online/total_devices)*100:.1f}%")
    
    print(f"\n🏪 Restaurant Chain Breakdown:")
    for restaurant, stats in restaurant_summary.items():
        if 'error' in stats:
            print(f"  - {restaurant}: ❌ {stats['error']} ({stats['host']})")
        else:
            health = (stats['online']/stats['total'])*100 if stats['total'] > 0 else 0
            print(f"  - {restaurant}: {stats['online']}/{stats['total']} online ({health:.1f}%) - {stats['host']}")
    
    return total_devices > 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    test_fortimanager_connection()