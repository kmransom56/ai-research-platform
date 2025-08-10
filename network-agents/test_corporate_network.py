#!/usr/bin/env python3
"""
Corporate Network Testing Tool
Tests FortiManager connectivity through Zscaler and corporate proxies
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ssl_universal_fix import (
    apply_all_ssl_fixes, 
    configure_zscaler_environment,
    patch_requests_for_fortimanager,
    test_ssl_connectivity,
    print_ssl_diagnostics,
    create_fortimanager_session
)
from fortimanager_api import FortiManagerAPI, load_env_file
import logging

def test_corporate_connectivity():
    """
    Comprehensive test for corporate network connectivity
    """
    
    print("🏢 Corporate Network Connectivity Test")
    print("=" * 60)
    
    # Step 1: Apply all SSL fixes
    print("1️⃣ Applying SSL fixes for corporate environment...")
    if apply_all_ssl_fixes(verbose=True):
        print("✅ SSL fixes applied successfully")
    else:
        print("❌ SSL fixes failed")
        return False
    
    # Step 2: Configure Zscaler environment  
    print("\n2️⃣ Configuring Zscaler environment...")
    zscaler_configs = configure_zscaler_environment()
    for config in zscaler_configs:
        print(f"  ✅ {config}")
    
    # Step 3: Apply FortiManager patches
    print("\n3️⃣ Applying FortiManager-specific patches...")
    fm_patch = patch_requests_for_fortimanager()
    print(f"  ✅ {fm_patch}")
    
    # Step 4: Load environment variables
    print("\n4️⃣ Loading FortiManager credentials...")
    if load_env_file():
        print("  ✅ Environment file loaded")
    else:
        print("  ❌ Failed to load environment file")
        return False
    
    # Step 5: Test FortiManager connectivity
    print("\n5️⃣ Testing FortiManager connectivity...")
    fortimanagers = [
        ('Arby\'s', os.getenv('ARBYS_FORTIMANAGER_HOST')),
        ('Buffalo Wild Wings', os.getenv('BWW_FORTIMANAGER_HOST')),
        ('Sonic', os.getenv('SONIC_FORTIMANAGER_HOST'))
    ]
    
    connectivity_results = {}
    
    for name, host in fortimanagers:
        if not host:
            print(f"  ⚠️  {name}: No host configured")
            continue
            
        print(f"\n  🔍 Testing {name} FortiManager ({host})...")
        results = test_ssl_connectivity(host, 443)
        connectivity_results[name] = results
        
        for test_name, result in results['tests'].items():
            print(f"    {result}")
    
    return connectivity_results

def test_fortimanager_login():
    """
    Test actual FortiManager login with SSL fixes
    """
    
    print("\n6️⃣ Testing FortiManager Authentication...")
    print("-" * 50)
    
    # Load credentials
    load_env_file()
    
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
    
    login_results = {}
    
    for config in fortimanager_configs:
        if not all([config['host'], config['username'], config['password']]):
            print(f"  ⚠️  {config['name']}: Incomplete credentials")
            continue
        
        print(f"\n  🔐 Testing {config['name']} login...")
        
        try:
            # Create FortiManager instance with SSL fixes
            fm = FortiManagerAPI(
                host=config['host'],
                username=config['username'],
                password=config['password'],
                site=config['site'],
                timeout=60  # Longer timeout for corporate networks
            )
            
            # Attempt login
            if fm.login():
                print(f"    ✅ Successfully logged into {config['name']} FortiManager")
                
                # Test device discovery
                devices = fm.get_managed_devices()
                device_count = len(devices)
                online_count = len([d for d in devices if d['status'] == 'online'])
                
                print(f"    📊 Found {device_count} devices ({online_count} online)")
                
                # Show device types
                device_types = {}
                for device in devices:
                    dtype = device.get('device_type', 'Unknown')
                    device_types[dtype] = device_types.get(dtype, 0) + 1
                
                print(f"    🛡️  Device types: {dict(device_types)}")
                
                login_results[config['name']] = {
                    'success': True,
                    'device_count': device_count,
                    'online_count': online_count,
                    'device_types': device_types
                }
                
                fm.logout()
                
            else:
                print(f"    ❌ Failed to login to {config['name']} FortiManager")
                login_results[config['name']] = {
                    'success': False,
                    'error': 'Login failed'
                }
                
        except Exception as e:
            print(f"    ❌ {config['name']} test failed: {str(e)}")
            login_results[config['name']] = {
                'success': False,
                'error': str(e)
            }
    
    return login_results

def generate_corporate_network_report(connectivity_results, login_results):
    """
    Generate comprehensive report for corporate network testing
    """
    
    print(f"\n🎯 CORPORATE NETWORK TEST REPORT")
    print("=" * 60)
    
    # Connectivity summary
    print(f"\n📡 Connectivity Test Results:")
    for restaurant, results in connectivity_results.items():
        print(f"\n  🏪 {restaurant} ({results['host']}):")
        for test_name, result in results['tests'].items():
            print(f"    {result}")
    
    # Authentication summary
    print(f"\n🔐 Authentication Test Results:")
    total_success = 0
    total_devices = 0
    
    for restaurant, results in login_results.items():
        if results.get('success'):
            device_count = results.get('device_count', 0)
            online_count = results.get('online_count', 0)
            health_pct = (online_count / device_count * 100) if device_count > 0 else 0
            
            print(f"  ✅ {restaurant}: {device_count} devices ({online_count} online, {health_pct:.1f}% health)")
            total_success += 1
            total_devices += device_count
        else:
            error = results.get('error', 'Unknown error')
            print(f"  ❌ {restaurant}: {error}")
    
    # Overall summary
    print(f"\n📊 Overall Summary:")
    print(f"  - FortiManagers tested: {len(login_results)}")
    print(f"  - Successful connections: {total_success}")
    print(f"  - Total Fortinet devices discovered: {total_devices}")
    print(f"  - Corporate network compatibility: {'✅ GOOD' if total_success > 0 else '❌ ISSUES'}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if total_success == 0:
        print(f"  - Verify you're connected to corporate network (not public internet)")
        print(f"  - Check VPN connection if working remotely")
        print(f"  - Verify Zscaler proxy allows FortiManager traffic")
        print(f"  - Contact IT if SSL certificate issues persist")
    elif total_success < len(login_results):
        print(f"  - Some FortiManagers may be offline or have different SSL requirements")
        print(f"  - Check individual FortiManager configurations")
    else:
        print(f"  - ✅ All systems operational - ready for production discovery")
        print(f"  - Run full multi-vendor discovery: python3 multi-vendor-discovery.py")

def main():
    """
    Main testing function
    """
    
    # Set logging level
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during testing
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run connectivity tests
        connectivity_results = test_corporate_connectivity()
        
        # Run authentication tests
        login_results = test_fortimanager_login()
        
        # Generate report
        generate_corporate_network_report(connectivity_results, login_results)
        
        # SSL diagnostics
        print(f"\n🔍 SSL Diagnostics:")
        print_ssl_diagnostics()
        
        print(f"\n✅ Corporate network testing complete!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()