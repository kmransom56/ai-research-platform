#!/usr/bin/env python3
"""
Complete Network Topology Setup for Neo4j
Sets up comprehensive network topology with proper Cypher syntax
"""

from neo4j import GraphDatabase

def setup_complete_topology():
    """Set up complete network topology in Neo4j"""
    print("📊 COMPLETE NETWORK TOPOLOGY SETUP")
    print("=" * 50)
    
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    
    try:
        with driver.session() as session:
            # Clear existing data
            print("🧹 Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create the main topology
            print("🏗️ Creating organizations, networks, and devices...")
            session.run("""
                // Create Organizations
                CREATE (org1:Organization {
                    name: 'Restaurant Chain HQ', 
                    id: 'org_001',
                    type: 'headquarters',
                    location: 'New York, NY'
                }),
                (org2:Organization {
                    name: 'Restaurant Chain West', 
                    id: 'org_002',
                    type: 'regional',
                    location: 'Los Angeles, CA'
                }),
                (org3:Organization {
                    name: 'Restaurant Chain East', 
                    id: 'org_003',
                    type: 'regional',
                    location: 'Miami, FL'
                }),
                
                // Create Networks
                (net1:Network {
                    name: 'HQ Main Network', 
                    id: 'net_001',
                    vlan_id: 100,
                    subnet: '10.1.0.0/24'
                }),
                (net2:Network {
                    name: 'West Coast Branch', 
                    id: 'net_002',
                    vlan_id: 200,
                    subnet: '10.2.0.0/24'
                }),
                (net3:Network {
                    name: 'East Coast Branch', 
                    id: 'net_003',
                    vlan_id: 300,
                    subnet: '10.3.0.0/24'
                }),
                
                // Create Devices - Meraki
                (dev1:Device {
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
                }),
                
                (dev2:Device {
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
                }),
                
                (dev3:Device {
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
                }),
                
                // Create Devices - Fortinet
                (dev4:Device {
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
                }),
                
                (dev5:Device {
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
                }),
                
                // Create relationships
                (org1)-[:HAS_NETWORK]->(net1),
                (org2)-[:HAS_NETWORK]->(net2),
                (org3)-[:HAS_NETWORK]->(net3),
                
                (net1)-[:CONTAINS]->(dev1),
                (net1)-[:CONTAINS]->(dev2),
                (net1)-[:CONTAINS]->(dev3),
                (net2)-[:CONTAINS]->(dev4),
                (net3)-[:CONTAINS]->(dev5),
                
                // Device connections
                (dev1)-[:CONNECTED_TO {connection_type: 'ethernet', port: 'gi1/0/24'}]->(dev2),
                (dev2)-[:CONNECTED_TO {connection_type: 'poe', port: 'gi1/0/12'}]->(dev3),
                (dev1)-[:UPLINKS_TO {connection_type: 'fiber', bandwidth: '10Gbps'}]->(dev4),
                (dev1)-[:UPLINKS_TO {connection_type: 'fiber', bandwidth: '10Gbps'}]->(dev5)
            """)
            
            print("✅ Main topology created!")
            
            # Add performance metrics
            print("📈 Adding performance metrics...")
            session.run("""
                MATCH (dev1:Device {name: 'Core-Switch-01'})
                MATCH (dev4:Device {name: 'FW-Branch-05'})
                
                CREATE (perf1:PerformanceMetric {
                    metric_type: 'throughput',
                    value: 2.34,
                    unit: 'Gbps',
                    timestamp: datetime()
                }),
                (perf2:PerformanceMetric {
                    metric_type: 'latency', 
                    value: 12.8,
                    unit: 'ms',
                    timestamp: datetime()
                }),
                (perf3:PerformanceMetric {
                    metric_type: 'packet_loss', 
                    value: 0.02,
                    unit: '%',
                    timestamp: datetime()
                }),
                
                (dev1)-[:HAS_METRIC]->(perf1),
                (dev1)-[:HAS_METRIC]->(perf2),
                (dev4)-[:HAS_METRIC]->(perf3)
            """)
            
            print("✅ Performance metrics added!")
            
            # Add security events
            print("🛡️ Adding security events...")
            session.run("""
                MATCH (dev5:Device {name: 'FW-East-03'})
                
                CREATE (threat1:ThreatEvent {
                    correlation_id: 'THR_001',
                    timestamp: datetime(),
                    severity: 'medium',
                    event_type: 'suspicious_traffic',
                    source_platform: 'fortinet',
                    description: 'Unusual traffic pattern detected from external IP',
                    recommended_action: 'Monitor and analyze traffic patterns'
                }),
                
                (vuln1:Vulnerability {
                    cve_id: 'CVE-2024-1234',
                    severity: 'high',
                    description: 'Firmware vulnerability in FortiGate devices',
                    affected_versions: ['7.2.8', '7.2.9'],
                    remediation: 'Upgrade to firmware version 7.4.1 or later'
                }),
                
                (threat1)-[:THREATENS]->(dev5),
                (dev5)-[:HAS_VULNERABILITY]->(vuln1)
            """)
            
            print("✅ Security events added!")
            
            # Add change records
            print("📝 Adding change history...")
            session.run("""
                MATCH (dev4:Device {name: 'FW-Branch-05'})
                MATCH (dev1:Device {name: 'Core-Switch-01'})
                
                CREATE (ch1:ChangeRecord {
                    change_id: 'CHG_001',
                    change_type: 'firmware_update',
                    timestamp: datetime() - duration('P2D'),
                    change_description: 'Updated FortiGate firmware from 7.2.8 to 7.4.1',
                    impact_assessment: 'Low risk - routine security update',
                    success_status: 'completed',
                    performed_by: 'automated_system'
                }),
                
                (ch2:ChangeRecord {
                    change_id: 'CHG_002',
                    change_type: 'configuration_update',
                    timestamp: datetime() - duration('PT6H'),
                    change_description: 'Updated VLAN configuration and port security settings',
                    impact_assessment: 'Medium risk - network configuration change',
                    success_status: 'completed',
                    performed_by: 'network_admin'
                }),
                
                (dev4)-[:HAS_CHANGE_RECORD]->(ch1),
                (dev1)-[:HAS_CHANGE_RECORD]->(ch2)
            """)
            
            print("✅ Change history added!")
            
            # Test queries
            print("\n🔍 TESTING NETWORK QUERIES:")
            print("-" * 40)
            
            # Device count
            result = session.run("MATCH (d:Device) RETURN count(d) as device_count")
            device_count = result.single()["device_count"]
            print(f"📊 Total devices created: {device_count}")
            
            # Network count
            result = session.run("MATCH (n:Network) RETURN count(n) as network_count")
            network_count = result.single()["network_count"]
            print(f"🌐 Total networks created: {network_count}")
            
            # Organization count
            result = session.run("MATCH (o:Organization) RETURN count(o) as org_count")
            org_count = result.single()["org_count"]
            print(f"🏢 Total organizations created: {org_count}")
            
            # Critical devices
            result = session.run("""
                MATCH (d:Device)
                WHERE d.health_score < 80 OR d.status <> 'online'
                RETURN count(d) as critical_count
            """)
            critical_count = result.single()["critical_count"]
            print(f"⚠️ Devices needing attention: {critical_count}")
            
            print(f"\n✅ Complete network topology setup successful!")
            return True
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    finally:
        driver.close()

def test_topology_queries():
    """Test the complete topology with queries"""
    print("\n🔍 TESTING COMPLETE TOPOLOGY QUERIES")
    print("=" * 50)
    
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    
    try:
        with driver.session() as session:
            
            # Query 1: Complete device inventory
            print("1. 📋 Complete Device Inventory:")
            result = session.run("""
                MATCH (d:Device)
                RETURN d.name as DeviceName, 
                       d.platform as Platform,
                       d.device_type as Type,
                       d.status as Status,
                       d.health_score as HealthScore,
                       d.location as Location,
                       d.cpu_usage as CPU,
                       d.memory_usage as Memory
                ORDER BY d.platform, d.health_score DESC
            """)
            
            for device in result:
                status_icon = "🟢" if device['Status'] == 'online' else "🟡" if device['Status'] == 'warning' else "🔴"
                print(f"   {status_icon} {device['DeviceName']} ({device['Platform']}) - Health: {device['HealthScore']}%")
                print(f"      📍 {device['Location']}")
                print(f"      💻 CPU: {device['CPU']}% | Memory: {device['Memory']}%")
            
            print()
            
            # Query 2: Network topology with connections
            print("2. 🗺️ Network Topology with Connections:")
            result = session.run("""
                MATCH (d1:Device)-[r:CONNECTED_TO|UPLINKS_TO]->(d2:Device)
                RETURN d1.name as Device1, 
                       type(r) as ConnectionType, 
                       r.connection_type as Medium,
                       d2.name as Device2,
                       d1.location as Location1,
                       d2.location as Location2
            """)
            
            connections = list(result)
            print(f"   Found {len(connections)} device connections:")
            for conn in connections:
                print(f"   🔗 {conn['Device1']} --[{conn['Medium']}]--> {conn['Device2']}")
                if conn['Location1'] != conn['Location2']:
                    print(f"      🌐 Cross-site: {conn['Location1']} → {conn['Location2']}")
            
            print()
            
            # Query 3: Security and vulnerability summary
            print("3. 🛡️ Security and Vulnerability Summary:")
            result = session.run("""
                MATCH (d:Device)
                OPTIONAL MATCH (d)<-[:THREATENS]-(t:ThreatEvent)
                OPTIONAL MATCH (d)-[:HAS_VULNERABILITY]->(v:Vulnerability)
                WHERE t IS NOT NULL OR v IS NOT NULL
                RETURN d.name as Device,
                       d.platform as Platform,
                       collect(t.event_type) as Threats,
                       collect(v.cve_id) as Vulnerabilities,
                       collect(v.severity) as VulnSeverity
            """)
            
            security_issues = list(result)
            print(f"   Found {len(security_issues)} devices with security concerns:")
            for issue in security_issues:
                print(f"   🚨 {issue['Device']} ({issue['Platform']})")
                if issue['Threats'] and issue['Threats'][0]:
                    print(f"      ⚠️ Active threats: {', '.join(filter(None, issue['Threats']))}")
                if issue['Vulnerabilities'] and issue['Vulnerabilities'][0]:
                    print(f"      🔍 Vulnerabilities: {', '.join(filter(None, issue['Vulnerabilities']))} ({', '.join(filter(None, issue['VulnSeverity']))})")
            
            return True
            
    except Exception as e:
        print(f"❌ Query testing failed: {e}")
        return False
    finally:
        driver.close()

def main():
    """Main setup function"""
    if setup_complete_topology():
        test_topology_queries()
        
        print("\n🎉 SUCCESS! Neo4j Network Topology is Ready!")
        print("=" * 50)
        print("✅ Neo4j connection: WORKING")
        print("✅ Network topology: COMPLETE")
        print("✅ Device inventory: LOADED")
        print("✅ Security data: CONFIGURED")
        print("✅ Performance metrics: ADDED")
        print("✅ Change history: TRACKED")
        print()
        print("🌐 Access Neo4j Browser:")
        print("   URL: http://localhost:7474")
        print("   Username: neo4j")
        print("   Password: password")
        print()
        print("🔍 Ready-to-use queries available in:")
        print("   • topology-queries.cypher")
        print("   • Neo4j Browser query examples")
        print("   • Chat Copilot natural language interface")
        print()
        print("🚀 Next: Try the network management features!")

if __name__ == "__main__":
    main()