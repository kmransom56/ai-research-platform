#!/usr/bin/env python3
"""
Scaled Network Queries for Large-Scale Meraki Infrastructure
Optimized for tens of thousands of devices across restaurant chains
"""

from neo4j import GraphDatabase
from typing import Dict, List, Any
import time
from datetime import datetime
# import pandas as pd  # Not needed for this analysis

class ScaledNetworkQueries:
    """
    High-performance queries optimized for large-scale restaurant chain networks
    """
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
    def get_executive_network_summary(self) -> Dict[str, Any]:
        """Executive dashboard summary optimized for large datasets"""
        print("📊 EXECUTIVE NETWORK SUMMARY")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Organization overview with device counts
            result = session.run("""
                MATCH (o:Organization)
                OPTIONAL MATCH (o)-[:HAS_NETWORK]->(n:Network)
                OPTIONAL MATCH (n)-[:CONTAINS]->(d:Device)
                WITH o, count(DISTINCT n) as network_count, count(d) as device_count
                RETURN o.name as organization,
                       network_count,
                       device_count,
                       o.network_count as total_networks
                ORDER BY device_count DESC
            """)
            
            organizations = []
            total_devices = 0
            total_networks = 0
            
            for record in result:
                org_data = {
                    "name": record["organization"],
                    "networks_loaded": record["network_count"],
                    "total_networks": record["total_networks"],
                    "devices": record["device_count"]
                }
                organizations.append(org_data)
                total_devices += record["device_count"]
                total_networks += record["total_networks"]
                
                print(f"🏢 {record['organization']}:")
                print(f"   📱 Devices: {record['device_count']:,}")
                print(f"   🌐 Networks Loaded: {record['network_count']:,}")  
                print(f"   🌐 Total Networks: {record['total_networks']:,}")
            
            print(f"\n🎯 INFRASTRUCTURE SCALE:")
            print(f"   Total Devices Loaded: {total_devices:,}")
            print(f"   Total Networks: {total_networks:,}")
            print(f"   Organizations: {len(organizations)}")
            
            return {
                "organizations": organizations,
                "total_devices": total_devices,
                "total_networks": total_networks,
                "summary_timestamp": datetime.now().isoformat()
            }
    
    def get_device_health_by_organization(self) -> List[Dict[str, Any]]:
        """Health analysis across all restaurant chains"""
        print("\n💊 DEVICE HEALTH BY ORGANIZATION")
        print("=" * 40)
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WITH d.organization_name as org,
                     count(d) as total_devices,
                     count(CASE WHEN d.status = 'critical' THEN 1 END) as critical,
                     count(CASE WHEN d.status = 'warning' THEN 1 END) as warning,
                     count(CASE WHEN d.status = 'online' THEN 1 END) as healthy,
                     avg(d.health_score) as avg_health,
                     avg(d.cpu_usage) as avg_cpu,
                     avg(d.memory_usage) as avg_memory
                RETURN org, total_devices, critical, warning, healthy, 
                       round(avg_health, 1) as avg_health,
                       round(avg_cpu, 1) as avg_cpu,
                       round(avg_memory, 1) as avg_memory
                ORDER BY total_devices DESC
            """)
            
            health_data = []
            for record in result:
                org_health = {
                    "organization": record["org"],
                    "total_devices": record["total_devices"],
                    "critical": record["critical"],
                    "warning": record["warning"], 
                    "healthy": record["healthy"],
                    "avg_health_score": record["avg_health"],
                    "avg_cpu_usage": record["avg_cpu"],
                    "avg_memory_usage": record["avg_memory"]
                }
                health_data.append(org_health)
                
                # Calculate percentages
                total = record["total_devices"]
                healthy_pct = (record["healthy"] / total * 100) if total > 0 else 0
                warning_pct = (record["warning"] / total * 100) if total > 0 else 0
                critical_pct = (record["critical"] / total * 100) if total > 0 else 0
                
                print(f"🏢 {record['org']}:")
                print(f"   📊 Total Devices: {total:,}")
                print(f"   ✅ Healthy: {record['healthy']:,} ({healthy_pct:.1f}%)")
                print(f"   ⚠️  Warning: {record['warning']:,} ({warning_pct:.1f}%)")
                print(f"   🚨 Critical: {record['critical']:,} ({critical_pct:.1f}%)")
                print(f"   📈 Health Score: {record['avg_health']}")
                print()
                
            return health_data
    
    def get_device_inventory_by_type(self) -> Dict[str, Any]:
        """Complete device inventory across all locations"""
        print("📋 DEVICE INVENTORY BY TYPE & LOCATION")
        print("=" * 45)
        
        with self.driver.session() as session:
            # Device types by organization
            result = session.run("""
                MATCH (d:Device)
                WITH d.organization_name as org,
                     d.product_type as type,
                     d.model as model,
                     count(d) as device_count
                WHERE type IS NOT NULL AND type <> ''
                RETURN org, type, collect({model: model, count: device_count}) as models,
                       sum(device_count) as total_for_type
                ORDER BY org, total_for_type DESC
            """)
            
            inventory = {}
            for record in result:
                org = record["org"]
                device_type = record["type"]
                
                if org not in inventory:
                    inventory[org] = {}
                    
                inventory[org][device_type] = {
                    "total": record["total_for_type"],
                    "models": record["models"]
                }
                
                print(f"🏢 {org} - {device_type.upper()}:")
                print(f"   Total: {record['total_for_type']:,} devices")
                
                # Show top models for this type
                sorted_models = sorted(record["models"], key=lambda x: x["count"], reverse=True)[:3]
                for model_info in sorted_models:
                    if model_info["model"]:
                        print(f"   • {model_info['model']}: {model_info['count']:,}")
                print()
            
            return inventory
    
    def get_critical_devices_requiring_attention(self) -> List[Dict[str, Any]]:
        """Find devices needing immediate attention"""
        print("🚨 CRITICAL DEVICES REQUIRING ATTENTION")
        print("=" * 42)
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WHERE d.status IN ['critical', 'warning'] 
                   OR d.health_score < 80 
                   OR d.cpu_usage > 80 
                   OR d.memory_usage > 85
                RETURN d.name as device_name,
                       d.model as model,
                       d.organization_name as organization,
                       d.network_name as network,
                       d.status as status,
                       d.health_score as health_score,
                       d.cpu_usage as cpu_usage,
                       d.memory_usage as memory_usage,
                       d.issues as issues
                ORDER BY 
                    CASE d.status 
                        WHEN 'critical' THEN 1 
                        WHEN 'warning' THEN 2 
                        ELSE 3 
                    END,
                    d.health_score ASC
                LIMIT 50
            """)
            
            critical_devices = []
            critical_count = 0
            warning_count = 0
            
            for record in result:
                device_info = {
                    "device_name": record["device_name"],
                    "model": record["model"],
                    "organization": record["organization"],
                    "network": record["network"],
                    "status": record["status"],
                    "health_score": record["health_score"],
                    "cpu_usage": record["cpu_usage"],
                    "memory_usage": record["memory_usage"],
                    "issues": record["issues"]
                }
                critical_devices.append(device_info)
                
                if record["status"] == "critical":
                    critical_count += 1
                elif record["status"] == "warning":
                    warning_count += 1
                
                # Format issues list
                issues_str = ", ".join(record["issues"]) if record["issues"] else "Performance degradation"
                
                status_icon = "🚨" if record["status"] == "critical" else "⚠️"
                print(f"{status_icon} {record['device_name']} ({record['model']})")
                print(f"   🏢 {record['organization']} → {record['network']}")
                print(f"   📊 Health: {record['health_score']:.1f} | CPU: {record['cpu_usage']:.1f}% | Memory: {record['memory_usage']:.1f}%")
                print(f"   🔧 Issues: {issues_str}")
                print()
            
            print(f"📈 ATTENTION SUMMARY:")
            print(f"   🚨 Critical: {critical_count} devices")
            print(f"   ⚠️  Warning: {warning_count} devices")
            print(f"   📱 Total: {len(critical_devices)} devices need attention")
            
            return critical_devices
    
    def get_network_topology_summary(self) -> Dict[str, Any]:
        """Network topology overview for executives"""
        print("\n🗺️  NETWORK TOPOLOGY SUMMARY")
        print("=" * 35)
        
        with self.driver.session() as session:
            # Get network distribution
            result = session.run("""
                MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)
                OPTIONAL MATCH (n)-[:CONTAINS]->(d:Device)
                WITH o.name as org, 
                     count(DISTINCT n) as networks_loaded,
                     o.network_count as total_networks,
                     count(d) as devices,
                     collect(DISTINCT d.product_type) as device_types
                RETURN org, networks_loaded, total_networks, devices, device_types
                ORDER BY devices DESC
            """)
            
            topology_summary = {
                "organizations": [],
                "total_loaded_networks": 0,
                "total_networks": 0,
                "total_devices": 0
            }
            
            for record in result:
                # Filter out empty device types
                device_types = [dt for dt in record["device_types"] if dt and dt != ""]
                
                org_topology = {
                    "organization": record["org"],
                    "networks_loaded": record["networks_loaded"],
                    "total_networks": record["total_networks"],
                    "devices": record["devices"],
                    "device_types": device_types,
                    "coverage_percentage": (record["networks_loaded"] / record["total_networks"] * 100) if record["total_networks"] > 0 else 0
                }
                topology_summary["organizations"].append(org_topology)
                topology_summary["total_loaded_networks"] += record["networks_loaded"]
                topology_summary["total_networks"] += record["total_networks"]
                topology_summary["total_devices"] += record["devices"]
                
                print(f"🏢 {record['org']}:")
                print(f"   🌐 Networks: {record['networks_loaded']:,} loaded / {record['total_networks']:,} total ({org_topology['coverage_percentage']:.1f}%)")
                print(f"   📱 Devices: {record['devices']:,}")
                print(f"   🔧 Types: {', '.join(device_types)}")
                print()
            
            # Overall coverage
            overall_coverage = (topology_summary["total_loaded_networks"] / topology_summary["total_networks"] * 100) if topology_summary["total_networks"] > 0 else 0
            
            print(f"🎯 TOPOLOGY COVERAGE:")
            print(f"   Loaded: {topology_summary['total_loaded_networks']:,} / {topology_summary['total_networks']:,} networks ({overall_coverage:.1f}%)")
            print(f"   Devices: {topology_summary['total_devices']:,}")
            
            return topology_summary
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete network analysis for executives"""
        print("🚀 COMPLETE NETWORK ANALYSIS FOR RESTAURANT CHAINS")
        print("=" * 60)
        
        start_time = time.time()
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "executive_summary": self.get_executive_network_summary(),
            "device_health": self.get_device_health_by_organization(), 
            "device_inventory": self.get_device_inventory_by_type(),
            "critical_devices": self.get_critical_devices_requiring_attention(),
            "topology_summary": self.get_network_topology_summary()
        }
        
        duration = time.time() - start_time
        analysis["analysis_duration"] = duration
        
        print(f"\n✅ ANALYSIS COMPLETED IN {duration:.2f} SECONDS")
        print("=" * 50)
        print("📊 Ready for executive presentation")
        print("🗺️  Topology maps available in Neo4j Browser")
        print("🤖 Natural language queries available in Chat Copilot")
        
        return analysis
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()

if __name__ == "__main__":
    # Run scaled analysis
    analyzer = ScaledNetworkQueries()
    
    try:
        analysis = analyzer.run_complete_analysis()
        
        # Save analysis results
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"network_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"\n💾 Analysis saved to: {filename}")
        
    finally:
        analyzer.close()