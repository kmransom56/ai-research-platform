#!/usr/bin/env python3
"""
Multi-Agent Network Management System Test
Tests the integration of NetworkDiscoveryAgent, DeviceHealthMonitoringAgent,
AlertManagementAgent, and NetworkCoordinator
"""

import asyncio
import sys
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'/tmp/network-agent-test-{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger("NetworkAgentTest")

async def test_individual_agents():
    """Test each agent individually"""
    logger.info("🧪 Testing individual agents")
    
    try:
        # Test Network Discovery Agent
        logger.info("📡 Testing NetworkDiscoveryAgent")
        from network_discovery_agent import NetworkDiscoveryAgent
        
        discovery_agent = NetworkDiscoveryAgent()
        discovery_results = await discovery_agent.discover_all_networks()
        
        print(f"✅ Discovery Agent Results:")
        print(f"   Organizations: {discovery_results['summary']['total_organizations']}")
        print(f"   Networks: {discovery_results['summary']['total_networks']}")
        print(f"   Devices: {discovery_results['summary']['total_devices_discovered']}")
        print(f"   Duration: {discovery_results['summary']['discovery_duration_seconds']:.1f}s")
        
    except Exception as e:
        logger.error(f"❌ NetworkDiscoveryAgent test failed: {e}")
        return False
    
    try:
        # Test Device Health Agent
        logger.info("🏥 Testing DeviceHealthMonitoringAgent")
        from device_health_monitoring_agent import DeviceHealthMonitoringAgent
        
        health_agent = DeviceHealthMonitoringAgent()
        devices = discovery_results.get("devices", [])
        
        if devices:
            health_metrics = await health_agent.monitor_device_health(devices[:10])  # Test with first 10 devices
            health_summary = health_agent.generate_health_summary()
            
            print(f"✅ Health Agent Results:")
            print(f"   Devices monitored: {health_summary['overall_health']['total_devices']}")
            print(f"   Health percentage: {health_summary['overall_health']['health_percentage']:.1f}%")
            print(f"   Critical devices: {health_summary['overall_health']['critical']}")
            print(f"   Warning devices: {health_summary['overall_health']['warning']}")
        else:
            logger.warning("⚠️  No devices found for health monitoring test")
            health_metrics = []
            
    except Exception as e:
        logger.error(f"❌ DeviceHealthMonitoringAgent test failed: {e}")
        return False
    
    try:
        # Test Alert Management Agent
        logger.info("🔔 Testing AlertManagementAgent")
        from alert_management_agent import AlertManagementAgent
        
        alert_agent = AlertManagementAgent()
        
        if 'health_metrics' in locals() and health_metrics:
            new_alerts = await alert_agent.process_device_health_data(health_metrics)
            alert_summary = alert_agent.get_alert_summary()
            
            print(f"✅ Alert Agent Results:")
            print(f"   New alerts generated: {len(new_alerts)}")
            print(f"   Active alerts: {alert_summary['active_alerts']['total']}")
            print(f"   Critical alerts: {alert_summary['active_alerts']['by_severity']['critical']}")
        else:
            logger.warning("⚠️  No health metrics available for alert testing")
            
    except Exception as e:
        logger.error(f"❌ AlertManagementAgent test failed: {e}")
        return False
    
    return True

async def test_coordinator():
    """Test the NetworkCoordinator orchestration"""
    logger.info("🎯 Testing NetworkCoordinator")
    
    try:
        from autogen_network_coordinator import NetworkCoordinator
        
        coordinator = NetworkCoordinator()
        assessment = await coordinator.run_comprehensive_network_assessment()
        
        print(f"✅ Coordinator Assessment Results:")
        print(f"   Execution time: {assessment['execution_metadata']['duration_seconds']:.1f}s")
        print(f"   Organizations: {assessment['network_overview']['total_organizations']}")
        print(f"   Networks: {assessment['network_overview']['total_networks']}")
        print(f"   Devices: {assessment['network_overview']['total_devices']}")
        print(f"   Overall health: {assessment['health_summary']['overall_health_score']:.1f}%")
        print(f"   New alerts: {assessment['alert_summary']['new_alerts_generated']}")
        print(f"   Recommendations: {len(assessment['recommendations'])}")
        
        # Show top issues if any
        if assessment['top_issues']:
            print(f"\n🚨 Top Issues:")
            for i, issue in enumerate(assessment['top_issues'][:3], 1):
                print(f"   {i}. {issue['serial']} in {issue['location']}")
                print(f"      Issues: {', '.join(issue['issues'])}")
        
        # Show recommendations
        if assessment['recommendations']:
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(assessment['recommendations'][:3], 1):
                print(f"   {i}. [{rec['priority'].upper()}] {rec['title']}")
                print(f"      {rec['description']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NetworkCoordinator test failed: {e}")
        return False

async def test_autogen_integration():
    """Test AutoGen Studio integration function"""
    logger.info("🤖 Testing AutoGen Studio integration")
    
    try:
        from autogen_network_coordinator import autogen_network_assessment
        
        result = await autogen_network_assessment()
        
        if result['success']:
            print(f"✅ AutoGen Integration Results:")
            print(f"   Total devices: {result['summary']['total_devices']}")
            print(f"   Health score: {result['summary']['health_score']:.1f}%") 
            print(f"   Critical issues: {result['summary']['critical_issues']}")
            print(f"   Recommendations: {result['summary']['recommendations']}")
            return True
        else:
            logger.error(f"❌ AutoGen integration failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ AutoGen integration test failed: {e}")
        return False

async def test_api_connectivity():
    """Test connectivity to required APIs"""
    logger.info("🌐 Testing API connectivity")
    
    import requests
    
    apis_to_test = [
        {"name": "Meraki Connector", "url": "http://localhost:11030/health", "required": True},
        {"name": "Neo4j", "url": "http://localhost:7474", "required": False},
        {"name": "AutoGen Studio", "url": "http://localhost:11001/health", "required": False}
    ]
    
    all_required_available = True
    
    for api in apis_to_test:
        try:
            response = requests.get(api["url"], timeout=5)
            if response.status_code == 200:
                print(f"✅ {api['name']}: Available")
            else:
                print(f"⚠️  {api['name']}: HTTP {response.status_code}")
                if api["required"]:
                    all_required_available = False
        except Exception as e:
            print(f"❌ {api['name']}: Not available ({e})")
            if api["required"]:
                all_required_available = False
    
    return all_required_available

async def performance_test():
    """Run performance test of the multi-agent system"""
    logger.info("⚡ Running performance test")
    
    try:
        from autogen_network_coordinator import NetworkCoordinator
        
        coordinator = NetworkCoordinator()
        
        # Time multiple assessments
        times = []
        for i in range(3):
            start_time = datetime.now()
            await coordinator.run_comprehensive_network_assessment()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            times.append(duration)
            logger.info(f"   Assessment {i+1}: {duration:.1f}s")
        
        avg_time = sum(times) / len(times)
        print(f"✅ Performance Test Results:")
        print(f"   Average assessment time: {avg_time:.1f}s")
        print(f"   Min time: {min(times):.1f}s")
        print(f"   Max time: {max(times):.1f}s")
        
        # Performance thresholds
        if avg_time < 30:
            print(f"   🚀 Excellent performance!")
        elif avg_time < 60:
            print(f"   ✅ Good performance")
        else:
            print(f"   ⚠️  Consider optimization (>{avg_time:.1f}s)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return False

async def integration_test():
    """Full integration test of multi-agent system"""
    logger.info("🔄 Running full integration test")
    
    test_results = {
        "api_connectivity": False,
        "individual_agents": False,
        "coordinator": False,
        "autogen_integration": False,
        "performance": False
    }
    
    print("=" * 60)
    print("🧪 MULTI-AGENT NETWORK MANAGEMENT SYSTEM TEST")
    print("=" * 60)
    
    # Test API connectivity first
    print("\n1️⃣  Testing API Connectivity...")
    test_results["api_connectivity"] = await test_api_connectivity()
    
    if not test_results["api_connectivity"]:
        logger.error("❌ Required APIs not available. Cannot proceed with integration test.")
        return False
    
    # Test individual agents
    print("\n2️⃣  Testing Individual Agents...")
    test_results["individual_agents"] = await test_individual_agents()
    
    # Test coordinator
    print("\n3️⃣  Testing Network Coordinator...")
    test_results["coordinator"] = await test_coordinator()
    
    # Test AutoGen integration
    print("\n4️⃣  Testing AutoGen Studio Integration...")
    test_results["autogen_integration"] = await test_autogen_integration()
    
    # Performance test
    print("\n5️⃣  Running Performance Test...")
    test_results["performance"] = await performance_test()
    
    # Results summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, passed_flag in test_results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL" 
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Multi-agent system is ready for deployment.")
    elif passed >= total * 0.8:
        print("✅ System is mostly functional. Address failing tests before production use.")
    else:
        print("⚠️  System has significant issues. Review and fix failing components.")
    
    return passed == total

def print_deployment_info():
    """Print deployment and usage information"""
    print("\n" + "=" * 60)  
    print("🚀 DEPLOYMENT INFORMATION")
    print("=" * 60)
    
    print("""
📁 Files Created:
   - network-discovery-agent.py          (Network discovery and topology mapping)
   - device-health-monitoring-agent.py   (Device health and performance monitoring)
   - alert-management-agent.py           (Alert generation and management) 
   - autogen-network-coordinator.py      (Multi-agent coordination)
   - autogen-studio-config.json          (AutoGen Studio configuration)
   - test-multi-agent-system.py          (This test script)

🔌 Integration Points:
   - Meraki API Connector: http://localhost:11030
   - AutoGen Studio: http://localhost:11001
   - Neo4j Knowledge Graph: http://localhost:7474
   - Chat Copilot Platform: http://localhost:11000

⚙️  Usage Examples:
   
   # Run individual discovery
   python3 network-discovery-agent.py
   
   # Run health monitoring 
   python3 device-health-monitoring-agent.py
   
   # Run full coordinator assessment
   python3 autogen-network-coordinator.py
   
   # Test entire system
   python3 test-multi-agent-system.py

🤖 AutoGen Studio Integration:
   1. Import autogen-studio-config.json into AutoGen Studio
   2. Configure agents and workflows
   3. Use autogen_network_assessment() function for programmatic access
   4. Set up scheduled workflows for continuous monitoring

📈 Monitoring Features:
   - Real-time device health scoring
   - Automated alert generation and escalation
   - Business impact assessment
   - Comprehensive network topology discovery
   - Multi-organization support
   - Performance trending and analysis

🔔 Alert Capabilities:
   - Device offline detection
   - Performance degradation alerts
   - Network-wide outage detection
   - Automated escalation workflows
   - Multiple notification channels (console, Slack, email)
   
🎯 Next Steps:
   1. Configure notification handlers in alert-management-agent.py
   2. Set up Neo4j knowledge graph schema (Option B)
   3. Add Fortinet API integration (Option C)
   4. Create Grafana dashboards (Option D) 
   5. Integrate with Chat Copilot (Option E)
    """)

if __name__ == "__main__":
    async def main():
        try:
            success = await integration_test()
            print_deployment_info()
            
            if success:
                logger.info("🎉 Multi-agent network management system test completed successfully!")
                sys.exit(0)
            else:
                logger.error("❌ Multi-agent system test completed with failures.")
                sys.exit(1)
                
        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            sys.exit(1)
    
    # Check if the Meraki connector service is running
    import requests
    try:
        response = requests.get("http://localhost:11030/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: Meraki connector service may not be running properly")
            print("   Start the service with: docker-compose -f configs/docker-compose/docker-compose-full-stack.yml up meraki-connector")
    except:
        print("❌ Error: Meraki connector service is not running")
        print("   Start the service with: docker-compose -f configs/docker-compose/docker-compose-full-stack.yml up meraki-connector")
        print("   Or run: cd python/meraki-connector && python main.py")
    
    asyncio.run(main())