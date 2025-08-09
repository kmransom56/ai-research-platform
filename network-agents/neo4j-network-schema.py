"""
Neo4j Network Knowledge Graph Schema
Creates comprehensive network topology and relationship mapping
Integrates with GenAI Stack for natural language queries
"""

from neo4j import GraphDatabase
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
import os

class NetworkKnowledgeGraph:
    """
    Neo4j Knowledge Graph for Network Management
    Stores network topology, device relationships, and operational data
    """
    
    def __init__(self, uri: str = "neo4j://localhost:7687", 
                 username: str = "neo4j", 
                 password: str = "password"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.logger = logging.getLogger("NetworkKnowledgeGraph")
        
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

    def create_network_schema(self):
        """Create the complete network knowledge graph schema"""
        self.logger.info("🏗️ Creating network knowledge graph schema")
        
        with self.driver.session() as session:
            # Create constraints for unique identifiers
            constraints = [
                "CREATE CONSTRAINT organization_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE",
                "CREATE CONSTRAINT network_id IF NOT EXISTS FOR (n:Network) REQUIRE n.id IS UNIQUE", 
                "CREATE CONSTRAINT device_serial IF NOT EXISTS FOR (d:Device) REQUIRE d.serial IS UNIQUE",
                "CREATE CONSTRAINT client_mac IF NOT EXISTS FOR (c:Client) REQUIRE c.mac IS UNIQUE",
                "CREATE CONSTRAINT alert_id IF NOT EXISTS FOR (a:Alert) REQUIRE a.id IS UNIQUE",
                "CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    self.logger.debug(f"Created constraint: {constraint.split()[2]}")
                except Exception as e:
                    self.logger.debug(f"Constraint may already exist: {e}")
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX device_status IF NOT EXISTS FOR (d:Device) ON (d.status)",
                "CREATE INDEX device_model IF NOT EXISTS FOR (d:Device) ON (d.model)",
                "CREATE INDEX network_name IF NOT EXISTS FOR (n:Network) ON (n.name)",
                "CREATE INDEX alert_severity IF NOT EXISTS FOR (a:Alert) ON (a.severity)",
                "CREATE INDEX timestamp_index IF NOT EXISTS FOR (e:Event) ON (e.timestamp)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    self.logger.debug(f"Created index: {index.split()[2]}")
                except Exception as e:
                    self.logger.debug(f"Index may already exist: {e}")
            
            self.logger.info("✅ Network schema created successfully")

    def import_meraki_topology(self, discovery_data: Dict[str, Any]):
        """Import Meraki network topology into knowledge graph"""
        self.logger.info("📊 Importing Meraki topology into knowledge graph")
        
        with self.driver.session() as session:
            # Import organizations
            for org in discovery_data.get("organizations", []):
                self._create_organization(session, org)
            
            # Import networks
            for network in discovery_data.get("networks", []):
                self._create_network(session, network)
            
            # Import devices and create relationships
            for device in discovery_data.get("devices", []):
                self._create_device_with_relationships(session, device)
            
            # Create network topology relationships
            self._create_topology_relationships(session, discovery_data)
            
        self.logger.info("✅ Meraki topology imported successfully")

    def _create_organization(self, session, org_data: Dict[str, Any]):
        """Create organization node"""
        query = """
        MERGE (o:Organization {id: $id})
        SET o.name = $name,
            o.url = $url,
            o.api_enabled = $api_enabled,
            o.licensing_model = $licensing_model,
            o.cloud_region = $cloud_region,
            o.last_updated = datetime()
        RETURN o
        """
        session.run(query, {
            "id": org_data.get("id", ""),
            "name": org_data.get("name", ""),
            "url": org_data.get("url", ""),
            "api_enabled": org_data.get("api", {}).get("enabled", False),
            "licensing_model": org_data.get("licensing", {}).get("model", ""),
            "cloud_region": org_data.get("cloud", {}).get("region", {}).get("name", "")
        })

    def _create_network(self, session, network_data: Dict[str, Any]):
        """Create network node and link to organization"""
        query = """
        MATCH (o:Organization {id: $org_id})
        MERGE (n:Network {id: $id})
        SET n.name = $name,
            n.product_types = $product_types,
            n.timezone = $timezone,
            n.tags = $tags,
            n.last_updated = datetime()
        MERGE (o)-[:MANAGES]->(n)
        RETURN n
        """
        session.run(query, {
            "id": network_data.get("id", ""),
            "org_id": network_data.get("organizationId", ""),
            "name": network_data.get("name", ""),
            "product_types": network_data.get("productTypes", []),
            "timezone": network_data.get("timeZone", "UTC"),
            "tags": network_data.get("tags", [])
        })

    def _create_device_with_relationships(self, session, device_data: Dict[str, Any]):
        """Create device node and establish all relationships"""
        # Create device node
        device_query = """
        MATCH (n:Network {id: $network_id})
        MERGE (d:Device {serial: $serial})
        SET d.model = $model,
            d.name = $name,
            d.mac = $mac,
            d.lan_ip = $lan_ip,
            d.firmware = $firmware,
            d.status = $status,
            d.last_reported_at = $last_reported_at,
            d.organization_name = $organization_name,
            d.network_name = $network_name,
            d.device_type = $device_type,
            d.last_updated = datetime()
        MERGE (d)-[:LOCATED_IN]->(n)
        RETURN d
        """
        
        # Determine device type from model
        device_type = self._get_device_type(device_data.get("model", ""))
        
        session.run(device_query, {
            "serial": device_data.get("serial", ""),
            "network_id": device_data.get("networkId", ""),
            "model": device_data.get("model", ""),
            "name": device_data.get("name", ""),
            "mac": device_data.get("mac", ""),
            "lan_ip": device_data.get("lanIp", ""),
            "firmware": device_data.get("firmware", ""),
            "status": device_data.get("status", ""),
            "last_reported_at": device_data.get("lastReportedAt", ""),
            "organization_name": device_data.get("organization_name", ""),
            "network_name": device_data.get("network_name", ""),
            "device_type": device_type
        })

    def _get_device_type(self, model: str) -> str:
        """Determine device type from model name"""
        model_lower = model.lower()
        if any(prefix in model_lower for prefix in ["mr", "wifi", "access"]):
            return "access_point"
        elif any(prefix in model_lower for prefix in ["ms", "switch"]):
            return "switch"
        elif any(prefix in model_lower for prefix in ["mx", "security", "firewall"]):
            return "security_appliance"
        elif any(prefix in model_lower for prefix in ["mg", "cellular"]):
            return "cellular_gateway"
        elif any(prefix in model_lower for prefix in ["mv", "camera"]):
            return "camera"
        else:
            return "unknown"

    def _create_topology_relationships(self, session, discovery_data: Dict[str, Any]):
        """Create network topology relationships between devices"""
        # This would be enhanced with actual topology data from Meraki
        # For now, create basic hierarchical relationships
        
        query = """
        MATCH (d1:Device)-[:LOCATED_IN]->(n:Network)<-[:LOCATED_IN]-(d2:Device)
        WHERE d1.device_type = 'security_appliance' AND d2.device_type = 'switch'
        AND d1.serial <> d2.serial
        MERGE (d1)-[:ROUTES_TO]->(d2)
        """
        session.run(query)
        
        # Connect switches to access points
        query = """
        MATCH (d1:Device)-[:LOCATED_IN]->(n:Network)<-[:LOCATED_IN]-(d2:Device)
        WHERE d1.device_type = 'switch' AND d2.device_type = 'access_point'
        AND d1.serial <> d2.serial
        MERGE (d1)-[:PROVIDES_POWER_TO]->(d2)
        """
        session.run(query)

    def store_health_metrics(self, health_metrics: List[Any]):
        """Store device health metrics as time-series data"""
        self.logger.info(f"💾 Storing health metrics for {len(health_metrics)} devices")
        
        with self.driver.session() as session:
            for metric in health_metrics:
                query = """
                MATCH (d:Device {serial: $serial})
                CREATE (h:HealthMetric {
                    timestamp: datetime(),
                    uptime_score: $uptime_score,
                    performance_score: $performance_score,
                    alert_level: $alert_level,
                    issues: $issues
                })
                MERGE (d)-[:HAS_HEALTH_METRIC]->(h)
                
                // Keep only last 30 days of health metrics
                WITH d
                MATCH (d)-[:HAS_HEALTH_METRIC]->(old:HealthMetric)
                WHERE old.timestamp < datetime() - duration('P30D')
                DETACH DELETE old
                """
                
                session.run(query, {
                    "serial": metric.serial,
                    "uptime_score": metric.uptime_score,
                    "performance_score": metric.performance_score,
                    "alert_level": metric.alert_level,
                    "issues": metric.issues
                })

    def store_alerts(self, alerts: List[Any]):
        """Store network alerts in knowledge graph"""
        self.logger.info(f"🚨 Storing {len(alerts)} alerts in knowledge graph")
        
        with self.driver.session() as session:
            for alert in alerts:
                # Create alert node
                alert_query = """
                MERGE (a:Alert {id: $alert_id})
                SET a.timestamp = datetime($timestamp),
                    a.severity = $severity,
                    a.status = $status,
                    a.source = $source,
                    a.source_id = $source_id,
                    a.alert_type = $alert_type,
                    a.title = $title,
                    a.description = $description,
                    a.location = $location,
                    a.affected_users = $affected_users
                """
                
                session.run(alert_query, {
                    "alert_id": alert.alert_id,
                    "timestamp": alert.timestamp.isoformat(),
                    "severity": alert.severity.value,
                    "status": alert.status.value,
                    "source": alert.source,
                    "source_id": alert.source_id,
                    "alert_type": alert.alert_type,
                    "title": alert.title,
                    "description": alert.description,
                    "location": alert.location,
                    "affected_users": alert.affected_users
                })
                
                # Link alert to affected device/network
                if alert.source == "device":
                    relationship_query = """
                    MATCH (a:Alert {id: $alert_id})
                    MATCH (d:Device {serial: $source_id})
                    MERGE (a)-[:AFFECTS]->(d)
                    """
                    session.run(relationship_query, {
                        "alert_id": alert.alert_id,
                        "source_id": alert.source_id
                    })

    def query_network_insights(self, query_type: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute predefined network insight queries"""
        
        queries = {
            "critical_devices": """
                MATCH (d:Device)-[:HAS_HEALTH_METRIC]->(h:HealthMetric)
                WHERE h.alert_level = 'red'
                AND h.timestamp > datetime() - duration('PT1H')
                RETURN d.serial, d.name, d.model, d.network_name, d.organization_name, h.issues
                ORDER BY h.timestamp DESC
                LIMIT 10
            """,
            
            "network_health_summary": """
                MATCH (n:Network)<-[:LOCATED_IN]-(d:Device)-[:HAS_HEALTH_METRIC]->(h:HealthMetric)
                WHERE h.timestamp > datetime() - duration('PT1H')
                WITH n, 
                     count(d) as total_devices,
                     sum(CASE WHEN h.alert_level = 'green' THEN 1 ELSE 0 END) as healthy,
                     sum(CASE WHEN h.alert_level = 'yellow' THEN 1 ELSE 0 END) as warning,
                     sum(CASE WHEN h.alert_level = 'red' THEN 1 ELSE 0 END) as critical
                RETURN n.name as network_name, 
                       total_devices, healthy, warning, critical,
                       round(100.0 * healthy / total_devices, 1) as health_percentage
                ORDER BY health_percentage ASC
            """,
            
            "device_topology": """
                MATCH path = (d1:Device)-[r]->(d2:Device)
                WHERE $network_name IS NULL OR 
                      (d1.network_name = $network_name AND d2.network_name = $network_name)
                RETURN d1.serial as source_device, 
                       d1.model as source_model,
                       type(r) as relationship_type,
                       d2.serial as target_device,
                       d2.model as target_model
                LIMIT 50
            """,
            
            "alert_patterns": """
                MATCH (a:Alert)-[:AFFECTS]->(d:Device)
                WHERE a.timestamp > datetime() - duration('P7D')
                RETURN d.model as device_model,
                       a.alert_type as alert_type,
                       count(*) as occurrence_count,
                       collect(DISTINCT d.network_name)[0..5] as affected_networks
                ORDER BY occurrence_count DESC
                LIMIT 20
            """,
            
            "organization_overview": """
                MATCH (o:Organization)-[:MANAGES]->(n:Network)<-[:LOCATED_IN]-(d:Device)
                OPTIONAL MATCH (d)-[:HAS_HEALTH_METRIC]->(h:HealthMetric)
                WHERE h.timestamp IS NULL OR h.timestamp > datetime() - duration('PT1H')
                WITH o, 
                     count(DISTINCT n) as networks,
                     count(DISTINCT d) as devices,
                     avg(h.uptime_score) as avg_uptime,
                     avg(h.performance_score) as avg_performance
                RETURN o.name as organization,
                       networks, devices,
                       round(avg_uptime, 1) as avg_uptime_score,
                       round(avg_performance, 1) as avg_performance_score,
                       round((avg_uptime + avg_performance) / 2, 1) as overall_health
                ORDER BY overall_health DESC
            """
        }
        
        if query_type not in queries:
            raise ValueError(f"Unknown query type: {query_type}")
        
        with self.driver.session() as session:
            result = session.run(queries[query_type], parameters or {})
            return [record.data() for record in result]

    def natural_language_query_helper(self, question: str) -> Dict[str, Any]:
        """
        Helper function for natural language queries
        Maps common questions to appropriate Cypher queries
        """
        question_lower = question.lower()
        
        # Pattern matching for common network questions
        if any(phrase in question_lower for phrase in ["offline", "down", "critical"]):
            results = self.query_network_insights("critical_devices")
            return {
                "query_type": "critical_devices",
                "question": question,
                "results": results,
                "summary": f"Found {len(results)} critical devices requiring attention"
            }
        
        elif any(phrase in question_lower for phrase in ["health", "status", "overview"]):
            results = self.query_network_insights("network_health_summary")
            return {
                "query_type": "network_health",
                "question": question,
                "results": results,
                "summary": f"Health summary for {len(results)} networks"
            }
        
        elif any(phrase in question_lower for phrase in ["topology", "connected", "relationship"]):
            results = self.query_network_insights("device_topology")
            return {
                "query_type": "topology",
                "question": question,
                "results": results,
                "summary": f"Network topology showing {len(results)} device relationships"
            }
        
        elif any(phrase in question_lower for phrase in ["alert", "problem", "issue"]):
            results = self.query_network_insights("alert_patterns")
            return {
                "query_type": "alerts",
                "question": question,
                "results": results,
                "summary": f"Alert patterns showing {len(results)} common issues"
            }
        
        else:
            # Default to organization overview
            results = self.query_network_insights("organization_overview")
            return {
                "query_type": "overview",
                "question": question,
                "results": results,
                "summary": f"Organization overview for {len(results)} organizations"
            }

    def export_graph_for_genai(self) -> Dict[str, Any]:
        """Export graph data for GenAI Stack integration"""
        self.logger.info("📤 Exporting graph data for GenAI Stack")
        
        with self.driver.session() as session:
            # Export key network information
            export_data = {
                "organizations": [],
                "networks": [],
                "devices": [],
                "relationships": [],
                "health_summary": [],
                "recent_alerts": []
            }
            
            # Organizations
            org_result = session.run("MATCH (o:Organization) RETURN o")
            export_data["organizations"] = [record["o"] for record in org_result]
            
            # Networks with device counts
            net_result = session.run("""
                MATCH (n:Network)<-[:LOCATED_IN]-(d:Device)
                RETURN n, count(d) as device_count
            """)
            for record in net_result:
                network = dict(record["n"])
                network["device_count"] = record["device_count"]
                export_data["networks"].append(network)
            
            # Devices with latest health
            dev_result = session.run("""
                MATCH (d:Device)
                OPTIONAL MATCH (d)-[:HAS_HEALTH_METRIC]->(h:HealthMetric)
                WHERE h.timestamp > datetime() - duration('PT1H')
                RETURN d, h
                ORDER BY h.timestamp DESC
            """)
            for record in dev_result:
                device = dict(record["d"])
                if record["h"]:
                    device["current_health"] = dict(record["h"])
                export_data["devices"].append(device)
            
            return export_data

# Integration functions for the multi-agent system

def integrate_with_network_agents(kg: NetworkKnowledgeGraph):
    """Integration function for network agents"""
    
    # Import existing discovery data
    try:
        from network_discovery_agent import NetworkDiscoveryAgent
        discovery_agent = NetworkDiscoveryAgent()
        # Would run discovery and import results
        # discovery_data = await discovery_agent.discover_all_networks()
        # kg.import_meraki_topology(discovery_data)
    except ImportError:
        logging.warning("Network discovery agent not available for integration")
    
    # Import health metrics
    try:
        from device_health_monitoring_agent import DeviceHealthMonitoringAgent
        # Would integrate health monitoring results
        # health_agent = DeviceHealthMonitoringAgent()
        # health_metrics = await health_agent.monitor_device_health(devices)
        # kg.store_health_metrics(health_metrics)
    except ImportError:
        logging.warning("Health monitoring agent not available for integration")

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Test the knowledge graph
    kg = NetworkKnowledgeGraph()
    
    try:
        print("=== NEO4J NETWORK KNOWLEDGE GRAPH TEST ===")
        
        # Create schema
        kg.create_network_schema()
        print("✅ Schema created successfully")
        
        # Test queries
        print("\n📊 Testing predefined queries:")
        
        queries_to_test = [
            ("organization_overview", "Organization Overview"),
            ("network_health_summary", "Network Health Summary"),
            ("device_topology", "Device Topology")
        ]
        
        for query_type, description in queries_to_test:
            try:
                results = kg.query_network_insights(query_type)
                print(f"   {description}: {len(results)} results")
            except Exception as e:
                print(f"   {description}: Error - {e}")
        
        # Test natural language queries
        print("\n🗣️ Testing natural language queries:")
        test_questions = [
            "What devices are offline?",
            "Show me network health status",
            "What are the current alerts?"
        ]
        
        for question in test_questions:
            try:
                result = kg.natural_language_query_helper(question)
                print(f"   Q: {question}")
                print(f"   A: {result['summary']}")
            except Exception as e:
                print(f"   Q: {question} - Error: {e}")
        
        print("\n✅ Knowledge graph test completed successfully!")
        
    except Exception as e:
        print(f"❌ Knowledge graph test failed: {e}")
    
    finally:
        kg.close()