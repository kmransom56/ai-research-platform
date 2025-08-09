#!/usr/bin/env python3
"""
Neo4j Connection Fix and Test Script
Helps resolve Neo4j password issues and test connectivity
"""

import sys
import subprocess
import requests
from neo4j import GraphDatabase
import json

def print_banner():
    """Print fix banner"""
    print("=" * 80)
    print("🔧 NEO4J CONNECTION TROUBLESHOOTING")
    print("=" * 80)
    print()

def check_neo4j_status():
    """Check Neo4j service status"""
    print("🔍 CHECKING NEO4J STATUS...")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:7474", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Neo4j is running")
            print(f"   📊 Version: {data.get('neo4j_version', 'Unknown')}")
            print(f"   🎯 Edition: {data.get('neo4j_edition', 'Unknown')}")
            print(f"   🔌 Bolt: {data.get('bolt_direct', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Neo4j responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Neo4j connection failed: {e}")
        return False

def show_common_passwords():
    """Show common Neo4j default passwords"""
    print("\n🔑 COMMON NEO4J DEFAULT CREDENTIALS:")
    print("-" * 40)
    
    common_creds = [
        ("neo4j", "neo4j"),
        ("neo4j", "password"),
        ("neo4j", "admin"),
        ("neo4j", ""),
        ("admin", "admin"),
        ("admin", "password")
    ]
    
    print("   Try these username/password combinations:")
    for i, (user, pwd) in enumerate(common_creds, 1):
        pwd_display = '(empty)' if pwd == '' else pwd
        print(f"   {i}. Username: {user} | Password: {pwd_display}")
    
    print()
    print("   💡 Note: First-time Neo4j setup often requires:")
    print("      Username: neo4j")
    print("      Password: neo4j (then you'll be prompted to change it)")

def test_neo4j_connection(uri="neo4j://localhost:7687", username="neo4j", password="neo4j"):
    """Test Neo4j connection with provided credentials"""
    print(f"\n🧪 TESTING CONNECTION...")
    print(f"   URI: {uri}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful!' as message")
            record = result.single()
            
            if record:
                print(f"   ✅ Connection successful!")
                print(f"   📊 Message: {record['message']}")
                
                # Test database info
                result = session.run("CALL dbms.components()")
                components = list(result)
                if components:
                    print(f"   🎯 Database components: {len(components)}")
                
                driver.close()
                return True
                
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Connection failed: {error_msg}")
        
        # Provide specific help based on error type
        if "authentication failed" in error_msg.lower():
            print("   💡 This is an authentication error. Try these solutions:")
            print("      1. Use default credentials: neo4j/neo4j")
            print("      2. Check if password was changed during setup")
            print("      3. Reset Neo4j password (see instructions below)")
        elif "service unavailable" in error_msg.lower():
            print("   💡 Neo4j service seems unavailable. Try:")
            print("      1. Restart Neo4j service")
            print("      2. Check if Neo4j is running on port 7687")
        
        return False

def provide_reset_instructions():
    """Provide Neo4j password reset instructions"""
    print("\n🔄 NEO4J PASSWORD RESET INSTRUCTIONS:")
    print("-" * 40)
    
    print("   If you need to reset Neo4j password, try these methods:")
    print()
    
    print("   📝 Method 1: Browser Reset")
    print("   1. Open http://localhost:7474 in your browser")
    print("   2. Try username: neo4j, password: neo4j")
    print("   3. If prompted, set a new password")
    print("   4. Remember the new password!")
    print()
    
    print("   🔧 Method 2: Command Line (if Neo4j is installed locally)")
    print("   1. Stop Neo4j service")
    print("   2. Delete auth file: rm $NEO4J_HOME/data/dbms/auth")
    print("   3. Start Neo4j service") 
    print("   4. Use default neo4j/neo4j credentials")
    print()
    
    print("   🐳 Method 3: Docker Reset (if running in Docker)")
    print("   1. docker stop neo4j-container")
    print("   2. docker rm neo4j-container")
    print("   3. docker run --name neo4j-container \\")
    print("      -p 7474:7474 -p 7687:7687 \\")
    print("      -e NEO4J_AUTH=neo4j/password \\")
    print("      -d neo4j:latest")
    print()

def create_network_test_data(driver):
    """Create sample network data for testing"""
    print("\n📊 CREATING SAMPLE NETWORK DATA...")
    
    try:
        with driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create sample network topology
            session.run("""
                // Create Organizations
                CREATE (org1:Organization {name: 'Restaurant Chain HQ', id: 'org_001'})
                CREATE (org2:Organization {name: 'Restaurant Chain West', id: 'org_002'})
                
                // Create Networks
                CREATE (net1:Network {name: 'HQ Main Network', id: 'net_001'})
                CREATE (net2:Network {name: 'West Coast Branch', id: 'net_002'})
                
                // Create Devices
                CREATE (dev1:Device {
                    name: 'Core-Switch-01', 
                    model: 'MS425-32', 
                    platform: 'meraki',
                    device_type: 'switch',
                    status: 'online',
                    location: 'Restaurant Chain HQ / Main Data Center',
                    serial: 'Q2HP-ABCD-EFGH',
                    health_score: 85.5,
                    firmware_version: '16.16'
                })
                
                CREATE (dev2:Device {
                    name: 'FW-Branch-05', 
                    model: 'FortiGate-100F', 
                    platform: 'fortinet',
                    device_type: 'firewall',
                    status: 'online',
                    location: 'Restaurant Chain West / Los Angeles Branch',
                    serial: 'FGT100F-123456',
                    health_score: 92.1,
                    firmware_version: '7.4.1'
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
                    firmware_version: '28.7'
                })
                
                // Create relationships
                CREATE (org1)-[:HAS_NETWORK]->(net1)
                CREATE (org2)-[:HAS_NETWORK]->(net2)
                CREATE (net1)-[:CONTAINS]->(dev1)
                CREATE (net2)-[:CONTAINS]->(dev2)
                CREATE (net1)-[:CONTAINS]->(dev3)
                CREATE (dev1)-[:CONNECTED_TO]->(dev3)
                
                // Create performance metrics
                CREATE (perf1:PerformanceMetric {
                    metric_type: 'cpu_usage',
                    value: 45.2,
                    timestamp: datetime()
                })
                CREATE (perf2:PerformanceMetric {
                    metric_type: 'memory_usage', 
                    value: 67.8,
                    timestamp: datetime()
                })
                CREATE (dev1)-[:HAS_METRIC]->(perf1)
                CREATE (dev1)-[:HAS_METRIC]->(perf2)
                
                RETURN 'Sample network data created successfully!' as result
            """)
            
            print("   ✅ Sample network topology created!")
            print("   📊 Created: 2 Organizations, 2 Networks, 3 Devices")
            print("   🔗 Added: Device connections and performance metrics")
            return True
            
    except Exception as e:
        print(f"   ❌ Failed to create test data: {e}")
        return False

def test_network_queries(driver):
    """Test some basic network queries"""
    print("\n🔍 TESTING NETWORK QUERIES...")
    
    try:
        with driver.session() as session:
            # Test device inventory
            result = session.run("""
                MATCH (d:Device)
                RETURN d.name as DeviceName, 
                       d.platform as Platform,
                       d.status as Status,
                       d.health_score as HealthScore
                ORDER BY d.name
            """)
            
            devices = list(result)
            print(f"   📊 Device Inventory Query: Found {len(devices)} devices")
            
            for device in devices:
                print(f"      - {device['DeviceName']} ({device['Platform']}) - {device['Status']} - Health: {device['HealthScore']}%")
            
            # Test topology query
            result = session.run("""
                MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device)
                RETURN o.name as Organization, n.name as Network, count(d) as DeviceCount
            """)
            
            topology = list(result)
            print(f"\n   🗺️ Network Topology Query: Found {len(topology)} network segments")
            
            for topo in topology:
                print(f"      - {topo['Organization']} / {topo['Network']}: {topo['DeviceCount']} devices")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
        return False

def main():
    """Main troubleshooting function"""
    print_banner()
    
    # Check if Neo4j is running
    if not check_neo4j_status():
        print("\n❌ Neo4j is not running or not accessible.")
        print("   Please start Neo4j service first.")
        return
    
    # Show common passwords
    show_common_passwords()
    
    # Interactive password testing
    print("\n🔑 INTERACTIVE CONNECTION TESTING:")
    print("-" * 40)
    
    # Try common passwords first
    common_passwords = ["neo4j", "password", "admin", ""]
    
    successful_connection = False
    working_credentials = None
    
    for password in common_passwords:
        print(f"\nTrying password: {'(empty)' if password == '' else password}")
        if test_neo4j_connection(password=password):
            successful_connection = True
            working_credentials = ("neo4j", password)
            break
    
    if not successful_connection:
        # Ask user for custom password
        print("\n🔧 CUSTOM PASSWORD TEST:")
        print("   The common passwords didn't work.")
        
        try:
            custom_password = input("   Please enter your Neo4j password (or press Enter to skip): ").strip()
            if custom_password:
                if test_neo4j_connection(password=custom_password):
                    successful_connection = True
                    working_credentials = ("neo4j", custom_password)
        except KeyboardInterrupt:
            print("\n   Skipped custom password test.")
    
    if successful_connection:
        print("\n🎉 SUCCESS! Neo4j connection is working!")
        username, password = working_credentials
        
        # Create test data and run queries
        driver = GraphDatabase.driver("neo4j://localhost:7687", auth=(username, password))
        
        print("\n📊 SETTING UP NETWORK TOPOLOGY DATA...")
        if create_network_test_data(driver):
            test_network_queries(driver)
        
        driver.close()
        
        # Show next steps
        print("\n🚀 NEXT STEPS:")
        print("=" * 40)
        print("✅ Neo4j is working! You can now:")
        print()
        print("1. 🌐 Open Neo4j Browser: http://localhost:7474")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print()
        print("2. 📊 Try these queries in Neo4j Browser:")
        print("   MATCH (d:Device) RETURN d")
        print("   MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device) RETURN o, n, d")
        print()
        print("3. 🔍 Use pre-built queries from topology-queries.cypher")
        print("4. 🤖 Try natural language queries in Chat Copilot: http://localhost:11000")
        print("5. 📈 Access Grafana dashboards: http://localhost:3000")
        
    else:
        print("\n❌ CONNECTION FAILED")
        provide_reset_instructions()
        
        print("\n🆘 ALTERNATIVE SOLUTIONS:")
        print("   If you continue having issues:")
        print("   1. The system will work in simulation mode without Neo4j")
        print("   2. Use Chat Copilot (http://localhost:11000) for natural language queries")
        print("   3. Generate executive reports: python3 generate-executive-report.py")
        print("   4. Run health assessments: python3 automated-health-assessment.py")

if __name__ == "__main__":
    main()