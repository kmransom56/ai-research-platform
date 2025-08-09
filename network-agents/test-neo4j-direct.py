#!/usr/bin/env python3
"""
Direct Neo4j Connection Test
Tests connection with the password from container configuration
"""

import sys
import os
from neo4j import GraphDatabase
import json
from datetime import datetime

def test_direct_connection():
    """Test Neo4j connection with container password"""
    print("🔧 DIRECT NEO4J CONNECTION TEST")
    print("=" * 50)
    
    # Use the password from container inspection: neo4j/password
    uri = "neo4j://localhost:7687"
    username = "neo4j"
    password = "password"
    
    print(f"URI: {uri}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print()
    
    try:
        print("🔌 Connecting to Neo4j...")
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            print("✅ Connection successful!")
            
            # Test basic query
            result = session.run("RETURN 'Hello Neo4j!' as message, datetime() as timestamp")
            record = result.single()
            
            if record:
                print(f"📊 Test message: {record['message']}")
                print(f"🕐 Server time: {record['timestamp']}")
            
            # Get database info
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            components = list(result)
            
            if components:
                comp = components[0]
                print(f"🏷️ Database: {comp['name']}")
                print(f"📈 Version: {comp['versions'][0]}")
                print(f"🎯 Edition: {comp['edition']}")
            
            print("\n✅ Neo4j connection is working perfectly!")
            return driver
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def setup_network_topology(driver):
    """Set up sample network topology data"""
    print("\n📊 SETTING UP NETWORK TOPOLOGY DATA")
    print("=" * 50)
    
    try:
        with driver.session() as session:
            # Clear existing data
            print("🧹 Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create comprehensive network topology
            print("🏗️ Creating network topology...")
            result = session.run("""
                // Create Organizations
                CREATE (org1:Organization {
                    name: 'Restaurant Chain HQ', 
                    id: 'org_001',
                    type: 'headquarters',
                    location: 'New York, NY'
                })
                CREATE (org2:Organization {
                    name: 'Restaurant Chain West', 
                    id: 'org_002',
                    type: 'regional',
                    location: 'Los Angeles, CA'
                })
                CREATE (org3:Organization {
                    name: 'Restaurant Chain East', 
                    id: 'org_003',
                    type: 'regional',
                    location: 'Miami, FL'
                })
                
                // Create Networks
                CREATE (net1:Network {
                    name: 'HQ Main Network', 
                    id: 'net_001',
                    vlan_id: 100,
                    subnet: '10.1.0.0/24'
                })
                CREATE (net2:Network {
                    name: 'West Coast Branch', 
                    id: 'net_002',
                    vlan_id: 200,
                    subnet: '10.2.0.0/24'
                })
                CREATE (net3:Network {
                    name: 'East Coast Branch', 
                    id: 'net_003',
                    vlan_id: 300,
                    subnet: '10.3.0.0/24'
                })
                
                // Create Devices - Meraki
                CREATE (dev1:Device {
                    name: 'Core-Switch-01', 
                    model: 'MS425-32', 
                    platform: 'meraki',
                    device_type: 'switch',
                    status: 'online',
                    location: 'Restaurant Chain HQ / Main Data Center',
                    serial: 'Q2HP-ABCD-EFGH',
                    health_score: 85.5,
                    firmware_version: '16.16',
                    ip_address: '10.1.0.10',
                    mac_address: '00:1B:44:11:3A:B7',
                    uptime_percentage: 99.8,
                    cpu_usage: 35.2,
                    memory_usage: 67.8,
                    last_seen: datetime()
                })
                
                CREATE (dev2:Device {
                    name: 'Access-Switch-02', 
                    model: 'MS210-24', 
                    platform: 'meraki',
                    device_type: 'switch',
                    status: 'online',
                    location: 'Restaurant Chain HQ / Floor 2',
                    serial: 'Q2HP-WXYZ-1234',
                    health_score: 92.3,
                    firmware_version: '16.16',
                    ip_address: '10.1.0.11',
                    mac_address: '00:1B:44:22:4B:C8',
                    uptime_percentage: 99.9,
                    cpu_usage: 22.1,
                    memory_usage: 45.6,
                    last_seen: datetime()
                })
                
                CREATE (dev3:Device {
                    name: 'AP-Floor2-08', 
                    model: 'MR46', 
                    platform: 'meraki',
                    device_type: 'access_point',
                    status: 'warning',
                    location: 'Restaurant Chain HQ / Floor 2',
                    serial: 'Q2GD-WXYZ-MNOP',
                    health_score: 73.8,
                    firmware_version: '28.7',
                    ip_address: '10.1.0.50',
                    mac_address: '00:1B:44:33:5C:D9',
                    uptime_percentage: 97.2,
                    cpu_usage: 18.5,
                    memory_usage: 38.9,
                    last_seen: datetime(),
                    issues: ['intermittent_connectivity', 'signal_strength_low']
                })
                
                // Create Devices - Fortinet
                CREATE (dev4:Device {
                    name: 'FW-Branch-05', 
                    model: 'FortiGate-100F', 
                    platform: 'fortinet',
                    device_type: 'firewall',
                    status: 'online',
                    location: 'Restaurant Chain West / Los Angeles Branch',
                    serial: 'FGT100F-123456',
                    health_score: 92.1,
                    firmware_version: '7.4.1',
                    ip_address: '10.2.0.1',
                    mac_address: '00:09:0F:09:00:01',
                    uptime_percentage: 99.5,
                    cpu_usage: 28.7,
                    memory_usage: 52.3,
                    last_seen: datetime()
                })
                
                CREATE (dev5:Device {
                    name: 'FW-East-03', 
                    model: 'FortiGate-60F', 
                    platform: 'fortinet',
                    device_type: 'firewall',
                    status: 'critical',
                    location: 'Restaurant Chain East / Miami Branch',
                    serial: 'FGT60F-789012',
                    health_score: 45.2,
                    firmware_version: '7.2.8',
                    ip_address: '10.3.0.1',
                    mac_address: '00:09:0F:09:00:02',
                    uptime_percentage: 87.3,
                    cpu_usage: 89.4,
                    memory_usage: 94.7,
                    last_seen: datetime(),
                    issues: ['high_cpu_usage', 'memory_exhaustion', 'firmware_outdated']
                })
                
                // Create relationships
                CREATE (org1)-[:HAS_NETWORK]->(net1)
                CREATE (org2)-[:HAS_NETWORK]->(net2)
                CREATE (org3)-[:HAS_NETWORK]->(net3)
                
                CREATE (net1)-[:CONTAINS]->(dev1)
                CREATE (net1)-[:CONTAINS]->(dev2)
                CREATE (net1)-[:CONTAINS]->(dev3)
                CREATE (net2)-[:CONTAINS]->(dev4)
                CREATE (net3)-[:CONTAINS]->(dev5)
                
                // Device connections
                CREATE (dev1)-[:CONNECTED_TO {connection_type: 'ethernet', port: 'gi1/0/24'}]->(dev2)
                CREATE (dev2)-[:CONNECTED_TO {connection_type: 'poe', port: 'gi1/0/12'}]->(dev3)
                CREATE (dev1)-[:UPLINKS_TO {connection_type: 'fiber', bandwidth: '10Gbps'}]->(dev4)
                CREATE (dev1)-[:UPLINKS_TO {connection_type: 'fiber', bandwidth: '10Gbps'}]->(dev5)
                
                // Create performance metrics
                CREATE (perf1:PerformanceMetric {
                    metric_type: 'throughput',
                    value: 2.34,
                    unit: 'Gbps',
                    timestamp: datetime()
                })
                CREATE (perf2:PerformanceMetric {
                    metric_type: 'latency', 
                    value: 12.8,
                    unit: 'ms',
                    timestamp: datetime()
                })
                CREATE (perf3:PerformanceMetric {
                    metric_type: 'packet_loss', 
                    value: 0.02,
                    unit: '%',
                    timestamp: datetime()
                })
                
                CREATE (dev1)-[:HAS_METRIC]->(perf1)
                CREATE (dev1)-[:HAS_METRIC]->(perf2)
                CREATE (dev4)-[:HAS_METRIC]->(perf3)
                
                // Create security events
                CREATE (threat1:ThreatEvent {
                    correlation_id: 'THR_001',
                    timestamp: datetime(),
                    severity: 'medium',
                    event_type: 'suspicious_traffic',
                    source_platform: 'fortinet',
                    description: 'Unusual traffic pattern detected from external IP',
                    recommended_action: 'Monitor and analyze traffic patterns'
                })
                
                CREATE (vuln1:Vulnerability {
                    cve_id: 'CVE-2024-1234',
                    severity: 'high',
                    description: 'Firmware vulnerability in FortiGate devices',
                    affected_versions: ['7.2.8', '7.2.9'],
                    remediation: 'Upgrade to firmware version 7.4.1 or later'
                })
                
                CREATE (threat1)-[:THREATENS]->(dev5)
                CREATE (dev5)-[:HAS_VULNERABILITY]->(vuln1)
                
                RETURN 'Comprehensive network topology created!' as result
            """)
            
            record = result.single()
            print(f"✅ {record['result']}")
            
            # Create change records
            print("📝 Creating change history records...")
            session.run("""
                MATCH (d:Device {name: 'FW-Branch-05'})
                CREATE (d)-[:HAS_CHANGE_RECORD]->(ch1:ChangeRecord {
                    change_id: 'CHG_001',
                    change_type: 'firmware_update',
                    timestamp: datetime() - duration('P2D'),
                    change_description: 'Updated FortiGate firmware from 7.2.8 to 7.4.1',
                    impact_assessment: 'Low risk - routine security update',
                    success_status: 'completed',
                    performed_by: 'automated_system'
                })
                
                MATCH (d:Device {name: 'Core-Switch-01'})
                CREATE (d)-[:HAS_CHANGE_RECORD]->(ch2:ChangeRecord {
                    change_id: 'CHG_002',
                    change_type: 'configuration_update',
                    timestamp: datetime() - duration('PT6H'),
                    change_description: 'Updated VLAN configuration and port security settings',
                    impact_assessment: 'Medium risk - network configuration change',
                    success_status: 'completed',
                    performed_by: 'network_admin'
                })
                
                RETURN count(*) as change_records_created
            """)
            
            print("✅ Network topology setup completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to setup topology: {e}")
        return False

def test_network_queries(driver):
    """Test network topology queries"""
    print("\n🔍 TESTING NETWORK TOPOLOGY QUERIES")
    print("=" * 50)
    
    try:
        with driver.session() as session:
            
            # Test 1: Device inventory
            print("📋 1. Device Inventory:")
            result = session.run("""
                MATCH (d:Device)
                RETURN d.name as DeviceName, 
                       d.platform as Platform,
                       d.device_type as Type,
                       d.status as Status,
                       d.health_score as HealthScore,
                       d.location as Location
                ORDER BY d.platform, d.health_score DESC
            """)
            
            devices = list(result)
            print(f"   Found {len(devices)} devices:")
            for device in devices:
                status_icon = "🟢" if device['Status'] == 'online' else "🟡" if device['Status'] == 'warning' else "🔴"
                print(f"   {status_icon} {device['DeviceName']} ({device['Platform']}) - {device['HealthScore']}% - {device['Type']}")
                print(f"      📍 {device['Location']}")
            
            print()
            
            # Test 2: Network topology
            print("🗺️ 2. Network Topology:")
            result = session.run("""
                MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device)
                RETURN o.name as Organization, 
                       n.name as Network,
                       n.subnet as Subnet,
                       count(d) as DeviceCount,
                       collect(d.name) as Devices
                ORDER BY o.name, n.name
            """)
            
            networks = list(result)
            print(f"   Found {len(networks)} network segments:")
            for net in networks:
                print(f"   🏢 {net['Organization']} / {net['Network']} ({net['Subnet']})")
                print(f"      📊 {net['DeviceCount']} devices: {', '.join(net['Devices'][:3])}")
                if len(net['Devices']) > 3:
                    print(f"      ... and {len(net['Devices']) - 3} more")
            
            print()
            
            # Test 3: Critical issues
            print("🚨 3. Critical Issues:")
            result = session.run("""
                MATCH (d:Device)
                WHERE d.health_score < 80 OR d.status <> 'online'
                OPTIONAL MATCH (d)<-[:THREATENS]-(t:ThreatEvent)
                OPTIONAL MATCH (d)-[:HAS_VULNERABILITY]->(v:Vulnerability)
                RETURN d.name as Device,
                       d.status as Status,
                       d.health_score as HealthScore,
                       d.issues as Issues,
                       count(t) as SecurityThreats,
                       count(v) as Vulnerabilities
                ORDER BY d.health_score ASC
            """)
            
            issues = list(result)
            print(f"   Found {len(issues)} devices requiring attention:")
            for issue in issues:
                print(f"   ⚠️ {issue['Device']} - Health: {issue['HealthScore']}% - Status: {issue['Status']}")
                if issue['Issues']:
                    print(f"      🔧 Issues: {', '.join(issue['Issues'])}")
                if issue['SecurityThreats'] > 0:
                    print(f"      🛡️ Security threats: {issue['SecurityThreats']}")
                if issue['Vulnerabilities'] > 0:
                    print(f"      🚨 Vulnerabilities: {issue['Vulnerabilities']}")
            
            print()
            
            # Test 4: Performance metrics
            print("📈 4. Performance Metrics:")
            result = session.run("""
                MATCH (d:Device)-[:HAS_METRIC]->(m:PerformanceMetric)
                RETURN d.name as Device,
                       collect(m.metric_type + ': ' + toString(m.value) + ' ' + m.unit) as Metrics
                ORDER BY d.name
            """)
            
            metrics = list(result)
            print(f"   Performance data for {len(metrics)} devices:")
            for metric in metrics:
                print(f"   📊 {metric['Device']}: {', '.join(metric['Metrics'])}")
            
            return True
            
    except Exception as e:
        print(f"❌ Query testing failed: {e}")
        return False

def provide_next_steps():
    """Show next steps for using Neo4j"""
    print("\n🚀 NEXT STEPS - NEO4J IS READY!")
    print("=" * 50)
    
    print("✅ Neo4j connection is working perfectly!")
    print()
    print("🌐 Access Neo4j Browser:")
    print("   1. Open: http://localhost:7474")
    print("   2. Username: neo4j")
    print("   3. Password: password")
    print()
    print("🔍 Try these queries in Neo4j Browser:")
    print("   // All devices with health scores")
    print("   MATCH (d:Device) RETURN d")
    print()
    print("   // Network topology visualization")
    print("   MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device)")
    print("   OPTIONAL MATCH (d)-[r:CONNECTED_TO]->(d2:Device)")
    print("   RETURN o, n, d, d2, r")
    print()
    print("   // Critical devices requiring attention")
    print("   MATCH (d:Device)")
    print("   WHERE d.health_score < 80 OR d.status <> 'online'")
    print("   RETURN d.name, d.health_score, d.status, d.issues")
    print()
    print("🤖 Natural Language Queries:")
    print("   Open Chat Copilot: http://localhost:11000")
    print("   Ask: 'Show me all network devices and their health status'")
    print("   Ask: 'What devices need immediate attention?'")
    print("   Ask: 'Show me the network topology for all locations'")
    print()
    print("📊 Additional Tools:")
    print("   • Grafana Dashboards: http://localhost:3000")
    print("   • Generate Executive Report: python3 generate-executive-report.py")
    print("   • Run Health Assessment: python3 automated-health-assessment.py")

def main():
    """Main function"""
    driver = test_direct_connection()
    
    if driver:
        if setup_network_topology(driver):
            test_network_queries(driver)
        
        driver.close()
        provide_next_steps()
    else:
        print("\n❌ Could not establish Neo4j connection")
        print("   Check that Neo4j container is running with correct credentials")

if __name__ == "__main__":
    main()