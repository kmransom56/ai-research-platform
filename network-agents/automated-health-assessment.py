"""
Automated Network Health Assessment Workflow
Scheduled every 15 minutes with multi-agent coordination
Integrates Discovery, Performance Analysis, Security Monitoring, and Reporting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import requests
from dataclasses import dataclass, asdict

# Import our network management components
from network_discovery_agent import NetworkDiscoveryAgent
from device_health_monitoring_agent import DeviceHealthMonitoringAgent
from alert_management_agent import AlertManagementAgent
from unified_network_manager import UnifiedNetworkManager
from neo4j_network_schema import NetworkKnowledgeGraph
from genai_network_query_agent import NetworkQueryAgent

@dataclass
class HealthAssessmentResult:
    """Structured health assessment result"""
    timestamp: datetime
    assessment_id: str
    overall_health_score: float
    critical_issues_count: int
    security_threats_detected: int
    performance_degradations: int
    devices_discovered: int
    networks_monitored: int
    recommendations: List[Dict[str, str]]
    executive_summary: str
    detailed_findings: Dict[str, Any]

class AutomatedHealthAssessment:
    """
    Automated Network Health Assessment System
    Orchestrates multi-agent workflows for comprehensive network analysis
    """
    
    def __init__(self,
                 meraki_api: str = "http://localhost:11030",
                 fortinet_api: str = "http://localhost:11031",
                 neo4j_uri: str = "neo4j://localhost:7687",
                 qdrant_url: str = "http://localhost:6333",
                 genai_api: str = "http://localhost:8504",
                 chat_copilot_api: str = "http://localhost:11000"):
        
        self.logger = logging.getLogger("AutomatedHealthAssessment")
        
        # Initialize all agents
        self.discovery_agent = NetworkDiscoveryAgent(meraki_api)
        self.health_agent = DeviceHealthMonitoringAgent(meraki_api)
        self.alert_agent = AlertManagementAgent(meraki_api)
        self.network_manager = UnifiedNetworkManager(meraki_api, fortinet_api)
        self.knowledge_graph = NetworkKnowledgeGraph(neo4j_uri)
        self.query_agent = NetworkQueryAgent(neo4j_uri, genai_api)
        
        # API endpoints
        self.qdrant_url = qdrant_url
        self.chat_copilot_api = chat_copilot_api
        
        # Assessment history
        self.assessment_history = []
        self.last_assessment = None
        
        # Performance tracking
        self.workflow_metrics = {
            "total_assessments": 0,
            "average_duration": 0.0,
            "success_rate": 100.0,
            "last_successful_run": None
        }

    async def run_scheduled_assessment(self) -> HealthAssessmentResult:
        """
        Main scheduled health assessment workflow
        Coordinates all agents for comprehensive network analysis
        """
        assessment_start = datetime.now()
        assessment_id = f"health_{assessment_start.strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"🔄 Starting scheduled health assessment: {assessment_id}")
        
        try:
            # Step 1: Discovery Agent - Poll Meraki/Fortinet APIs
            self.logger.info("📡 Step 1: Network Discovery")
            discovery_results = await self._run_discovery_phase()
            
            # Step 2: Performance Agent - Analyze metrics in Qdrant
            self.logger.info("📊 Step 2: Performance Analysis")
            performance_results = await self._run_performance_analysis(discovery_results)
            
            # Step 3: Security Agent - Update Neo4j threat graph
            self.logger.info("🔒 Step 3: Security Analysis")
            security_results = await self._run_security_analysis(discovery_results)
            
            # Step 4: Chat Copilot - Generate summary report
            self.logger.info("🤖 Step 4: AI Summary Generation")
            ai_summary = await self._generate_ai_summary(discovery_results, performance_results, security_results)
            
            # Compile comprehensive assessment
            assessment_result = await self._compile_assessment_result(
                assessment_id, assessment_start, discovery_results, 
                performance_results, security_results, ai_summary
            )
            
            # Store results
            await self._store_assessment_results(assessment_result)
            
            # Update metrics
            duration = (datetime.now() - assessment_start).total_seconds()
            await self._update_workflow_metrics(True, duration)
            
            self.logger.info(f"✅ Health assessment completed: {assessment_id} ({duration:.2f}s)")
            return assessment_result
            
        except Exception as e:
            self.logger.error(f"❌ Health assessment failed: {assessment_id} - {e}")
            await self._update_workflow_metrics(False, 0)
            raise

    async def _run_discovery_phase(self) -> Dict[str, Any]:
        """Discovery Agent - Polls Meraki/Fortinet APIs"""
        try:
            # Initialize network manager
            await self.network_manager.initialize()
            
            # Discover unified topology
            topology = await self.network_manager.discover_unified_topology()
            
            # Run Meraki-specific discovery for detailed data
            meraki_discovery = await self.discovery_agent.discover_all_networks()
            
            return {
                "unified_topology": topology,
                "meraki_discovery": meraki_discovery,
                "timestamp": datetime.now().isoformat(),
                "platforms_available": {
                    "meraki": self.network_manager.meraki_available,
                    "fortinet": self.network_manager.fortinet_available
                }
            }
            
        except Exception as e:
            self.logger.error(f"Discovery phase failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _run_performance_analysis(self, discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Performance Agent - Analyzes metrics in Qdrant"""
        try:
            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "device_health_analysis": {},
                "performance_trends": {},
                "qdrant_analysis": {},
                "degradation_alerts": []
            }
            
            # Extract devices from discovery
            devices = []
            if "unified_topology" in discovery_results:
                devices = discovery_results["unified_topology"].get("unified_devices", [])
            elif "meraki_discovery" in discovery_results:
                devices = discovery_results["meraki_discovery"].get("devices", [])
            
            if devices:
                # Convert to format expected by health agent
                device_list = []
                for device in devices:
                    if hasattr(device, '__dict__'):
                        device_dict = device.__dict__
                    else:
                        device_dict = device
                    device_list.append(device_dict)
                
                # Run health monitoring
                health_metrics = await self.health_agent.monitor_device_health(device_list)
                health_summary = self.health_agent.generate_health_summary()
                
                performance_data["device_health_analysis"] = health_summary
                
                # Identify performance degradations
                critical_devices = self.health_agent.get_critical_devices()
                warning_devices = self.health_agent.get_warning_devices()
                
                performance_data["degradation_alerts"] = [
                    {
                        "device": d.serial,
                        "location": f"{d.organization_name}/{d.network_name}",
                        "issues": d.issues,
                        "severity": "critical" if d.alert_level == "red" else "warning"
                    }
                    for d in critical_devices + warning_devices
                ]
            
            # Store performance vectors in Qdrant (if available)
            await self._store_performance_vectors(performance_data)
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _store_performance_vectors(self, performance_data: Dict[str, Any]):
        """Store performance metrics as vectors in Qdrant"""
        try:
            if not performance_data.get("device_health_analysis"):
                return
            
            # Prepare vector data for Qdrant
            health_summary = performance_data["device_health_analysis"]
            
            # Create performance vector (simplified representation)
            performance_vector = [
                health_summary["overall_health"]["health_percentage"],
                health_summary["overall_health"]["total_devices"],
                health_summary["overall_health"]["critical"],
                health_summary["overall_health"]["warning"],
                health_summary["performance_metrics"]["average_uptime_score"],
                health_summary["performance_metrics"]["average_performance_score"]
            ]
            
            # Pad vector to standard size (128 dimensions)
            while len(performance_vector) < 128:
                performance_vector.append(0.0)
            
            # Store in Qdrant collection
            vector_data = {
                "points": [
                    {
                        "id": int(datetime.now().timestamp()),
                        "vector": performance_vector,
                        "payload": {
                            "timestamp": performance_data["timestamp"],
                            "health_percentage": health_summary["overall_health"]["health_percentage"],
                            "total_devices": health_summary["overall_health"]["total_devices"],
                            "assessment_type": "automated_health"
                        }
                    }
                ]
            }
            
            # Send to Qdrant (create collection if needed)
            await self._ensure_qdrant_collection()
            
            response = requests.put(
                f"{self.qdrant_url}/collections/network_health/points",
                json=vector_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.debug("Performance vectors stored in Qdrant")
            else:
                self.logger.warning(f"Qdrant storage failed: {response.status_code}")
                
        except Exception as e:
            self.logger.warning(f"Qdrant vector storage failed: {e}")

    async def _ensure_qdrant_collection(self):
        """Ensure Qdrant collection exists for network health data"""
        try:
            collection_config = {
                "vectors": {
                    "size": 128,
                    "distance": "Cosine"
                }
            }
            
            response = requests.put(
                f"{self.qdrant_url}/collections/network_health",
                json=collection_config,
                timeout=10
            )
            
            # 200 = created, 409 = already exists
            if response.status_code in [200, 409]:
                self.logger.debug("Qdrant collection ready")
                
        except Exception as e:
            self.logger.debug(f"Qdrant collection setup skipped: {e}")

    async def _run_security_analysis(self, discovery_results: Dict[str, Any]) -> Dict[str, Any]:
        """Security Agent - Updates Neo4j threat graph"""
        try:
            security_data = {
                "timestamp": datetime.now().isoformat(),
                "threat_correlations": [],
                "security_posture": {},
                "neo4j_updates": 0,
                "fortinet_events": []
            }
            
            # Perform security correlation analysis
            if self.network_manager.fortinet_available:
                correlations = await self.network_manager.perform_security_correlation()
                security_data["threat_correlations"] = [asdict(c) for c in correlations]
                
                # Get Fortinet security events
                try:
                    response = requests.get(f"{self.network_manager.fortinet_api}/security/events?count=50", timeout=10)
                    if response.status_code == 200:
                        security_data["fortinet_events"] = response.json()
                except Exception as e:
                    self.logger.warning(f"Failed to get Fortinet events: {e}")
            
            # Update Neo4j threat graph
            await self._update_threat_graph(security_data)
            
            # Assess overall security posture
            security_data["security_posture"] = await self._assess_security_posture(discovery_results, security_data)
            
            return security_data
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _update_threat_graph(self, security_data: Dict[str, Any]):
        """Update Neo4j with security threat information"""
        try:
            with self.knowledge_graph.driver.session() as session:
                # Create threat events
                for correlation in security_data.get("threat_correlations", []):
                    query = """
                    CREATE (t:ThreatEvent {
                        correlation_id: $correlation_id,
                        timestamp: datetime($timestamp),
                        severity: $severity,
                        event_type: $event_type,
                        source_platform: $source_platform,
                        description: $description,
                        recommended_action: $recommended_action
                    })
                    """
                    
                    session.run(query, {
                        "correlation_id": correlation.get("correlation_id"),
                        "timestamp": correlation.get("timestamp"),
                        "severity": correlation.get("severity"),
                        "event_type": correlation.get("event_type"),
                        "source_platform": correlation.get("source_platform"),
                        "description": correlation.get("description"),
                        "recommended_action": correlation.get("recommended_action")
                    })
                    
                    security_data["neo4j_updates"] += 1
                
                # Link threats to affected devices
                for correlation in security_data.get("threat_correlations", []):
                    if correlation.get("target_device"):
                        query = """
                        MATCH (t:ThreatEvent {correlation_id: $correlation_id})
                        MATCH (d:Device {serial: $device_serial})
                        MERGE (t)-[:THREATENS]->(d)
                        """
                        
                        try:
                            session.run(query, {
                                "correlation_id": correlation.get("correlation_id"),
                                "device_serial": correlation.get("target_device")
                            })
                        except Exception as e:
                            self.logger.debug(f"Device linking failed: {e}")
                
        except Exception as e:
            self.logger.warning(f"Threat graph update failed: {e}")

    async def _assess_security_posture(self, discovery_results: Dict[str, Any], security_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall security posture"""
        posture = {
            "overall_score": 100.0,
            "threat_level": "low",
            "vulnerabilities": [],
            "recommendations": []
        }
        
        # Analyze threat correlations
        correlations = security_data.get("threat_correlations", [])
        critical_threats = len([c for c in correlations if c.get("severity") == "critical"])
        high_threats = len([c for c in correlations if c.get("severity") == "high"])
        
        # Calculate security score
        posture["overall_score"] -= (critical_threats * 20) + (high_threats * 10)
        posture["overall_score"] = max(0.0, posture["overall_score"])
        
        # Determine threat level
        if critical_threats > 0:
            posture["threat_level"] = "critical"
        elif high_threats > 0:
            posture["threat_level"] = "high"
        elif len(correlations) > 0:
            posture["threat_level"] = "medium"
        
        # Generate recommendations
        if critical_threats > 0:
            posture["recommendations"].append({
                "priority": "critical",
                "action": "Immediately investigate and remediate critical security threats",
                "details": f"{critical_threats} critical threats detected requiring urgent attention"
            })
        
        if not self.network_manager.fortinet_available:
            posture["vulnerabilities"].append("No centralized security platform detected")
            posture["recommendations"].append({
                "priority": "medium",
                "action": "Deploy centralized security management (FortiGate)",
                "details": "Consider implementing unified threat management for better security visibility"
            })
        
        return posture

    async def _generate_ai_summary(self, discovery_results: Dict[str, Any], 
                                  performance_results: Dict[str, Any], 
                                  security_results: Dict[str, Any]) -> Dict[str, Any]:
        """Chat Copilot - Generate AI summary report"""
        try:
            # Prepare data for AI analysis
            summary_data = {
                "discovery": discovery_results,
                "performance": performance_results,
                "security": security_results
            }
            
            # Generate natural language summary using our GenAI query agent
            executive_question = "Generate an executive summary of the current network health assessment results"
            
            ai_response = await self.query_agent.process_natural_language_query(
                executive_question, 
                context=summary_data
            )
            
            # Create comprehensive AI summary
            ai_summary = {
                "timestamp": datetime.now().isoformat(),
                "executive_summary": ai_response.get("natural_language_response", "Assessment completed successfully"),
                "key_findings": self._extract_key_findings(summary_data),
                "recommendations": self._generate_ai_recommendations(summary_data),
                "risk_assessment": self._assess_business_risk(summary_data),
                "next_actions": self._suggest_next_actions(summary_data)
            }
            
            # Send to Chat Copilot if available
            await self._send_to_chat_copilot(ai_summary)
            
            return ai_summary
            
        except Exception as e:
            self.logger.error(f"AI summary generation failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "executive_summary": "Automated assessment completed with AI summary unavailable"
            }

    def _extract_key_findings(self, summary_data: Dict[str, Any]) -> List[str]:
        """Extract key findings from assessment data"""
        findings = []
        
        # Performance findings
        perf_data = summary_data.get("performance", {})
        if "device_health_analysis" in perf_data:
            health = perf_data["device_health_analysis"]
            health_pct = health.get("overall_health", {}).get("health_percentage", 0)
            findings.append(f"Network health score: {health_pct:.1f}%")
            
            critical_count = health.get("overall_health", {}).get("critical", 0)
            if critical_count > 0:
                findings.append(f"{critical_count} devices require immediate attention")
        
        # Security findings
        security_data = summary_data.get("security", {})
        threat_count = len(security_data.get("threat_correlations", []))
        if threat_count > 0:
            findings.append(f"{threat_count} security correlations detected")
        
        # Discovery findings
        discovery_data = summary_data.get("discovery", {})
        if "unified_topology" in discovery_data:
            topology = discovery_data["unified_topology"]
            device_count = topology.get("summary", {}).get("total_devices", 0)
            findings.append(f"{device_count} devices monitored across platforms")
        
        return findings

    def _generate_ai_recommendations(self, summary_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate AI-powered recommendations"""
        recommendations = []
        
        # Analyze performance issues
        perf_data = summary_data.get("performance", {})
        degradations = perf_data.get("degradation_alerts", [])
        
        if degradations:
            critical_degradations = [d for d in degradations if d["severity"] == "critical"]
            if critical_degradations:
                recommendations.append({
                    "priority": "high",
                    "category": "performance",
                    "action": f"Address {len(critical_degradations)} critical device issues",
                    "impact": "Service availability at risk"
                })
        
        # Analyze security posture
        security_data = summary_data.get("security", {})
        posture = security_data.get("security_posture", {})
        
        if posture.get("threat_level") in ["critical", "high"]:
            recommendations.append({
                "priority": "critical",
                "category": "security",
                "action": "Investigate and remediate security threats immediately",
                "impact": "Network security compromise possible"
            })
        
        return recommendations

    def _assess_business_risk(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business risk from network issues"""
        risk_assessment = {
            "overall_risk": "low",
            "financial_impact": "minimal",
            "operational_impact": "minimal",
            "reputation_impact": "minimal"
        }
        
        # Analyze performance impact
        perf_data = summary_data.get("performance", {})
        if "degradation_alerts" in perf_data:
            critical_count = len([a for a in perf_data["degradation_alerts"] if a["severity"] == "critical"])
            
            if critical_count > 10:
                risk_assessment["overall_risk"] = "high"
                risk_assessment["operational_impact"] = "significant"
            elif critical_count > 5:
                risk_assessment["overall_risk"] = "medium"
                risk_assessment["operational_impact"] = "moderate"
        
        # Analyze security impact
        security_data = summary_data.get("security", {})
        threat_level = security_data.get("security_posture", {}).get("threat_level", "low")
        
        if threat_level == "critical":
            risk_assessment["overall_risk"] = "critical"
            risk_assessment["reputation_impact"] = "high"
        
        return risk_assessment

    def _suggest_next_actions(self, summary_data: Dict[str, Any]) -> List[str]:
        """Suggest next actions based on assessment"""
        actions = []
        
        # Performance-based actions
        perf_data = summary_data.get("performance", {})
        degradations = perf_data.get("degradation_alerts", [])
        
        if degradations:
            actions.append("Investigate and resolve device performance issues")
            actions.append("Review network capacity and optimization opportunities")
        
        # Security-based actions
        security_data = summary_data.get("security", {})
        if security_data.get("threat_correlations"):
            actions.append("Review security event correlations")
            actions.append("Validate security policies and configurations")
        
        # Always include monitoring actions
        actions.append("Continue automated monitoring every 15 minutes")
        actions.append("Review trends and patterns in next assessment cycle")
        
        return actions

    async def _send_to_chat_copilot(self, ai_summary: Dict[str, Any]):
        """Send summary to Chat Copilot for integration"""
        try:
            # Prepare Chat Copilot message
            message_data = {
                "type": "network_health_assessment",
                "timestamp": ai_summary["timestamp"],
                "summary": ai_summary["executive_summary"],
                "findings": ai_summary["key_findings"],
                "recommendations": ai_summary["recommendations"],
                "risk_level": ai_summary["risk_assessment"]["overall_risk"]
            }
            
            # Send to Chat Copilot API (if available)
            response = requests.post(
                f"{self.chat_copilot_api}/api/network-report",
                json=message_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Summary sent to Chat Copilot")
            else:
                self.logger.debug(f"Chat Copilot integration skipped: {response.status_code}")
                
        except Exception as e:
            self.logger.debug(f"Chat Copilot integration failed: {e}")

    async def _compile_assessment_result(self, assessment_id: str, start_time: datetime,
                                        discovery_results: Dict[str, Any],
                                        performance_results: Dict[str, Any], 
                                        security_results: Dict[str, Any],
                                        ai_summary: Dict[str, Any]) -> HealthAssessmentResult:
        """Compile comprehensive assessment result"""
        
        # Calculate overall health score
        perf_health = performance_results.get("device_health_analysis", {}).get("overall_health", {}).get("health_percentage", 100)
        security_score = security_results.get("security_posture", {}).get("overall_score", 100)
        overall_health = (perf_health + security_score) / 2
        
        # Count issues
        critical_issues = performance_results.get("device_health_analysis", {}).get("overall_health", {}).get("critical", 0)
        security_threats = len(security_results.get("threat_correlations", []))
        degradations = len(performance_results.get("degradation_alerts", []))
        
        # Device/network counts
        devices_discovered = discovery_results.get("unified_topology", {}).get("summary", {}).get("total_devices", 0)
        networks_monitored = discovery_results.get("unified_topology", {}).get("summary", {}).get("platform_distribution", {})
        
        return HealthAssessmentResult(
            timestamp=start_time,
            assessment_id=assessment_id,
            overall_health_score=round(overall_health, 2),
            critical_issues_count=critical_issues,
            security_threats_detected=security_threats,
            performance_degradations=degradations,
            devices_discovered=devices_discovered,
            networks_monitored=sum(networks_monitored.values()) if networks_monitored else 0,
            recommendations=ai_summary.get("recommendations", []),
            executive_summary=ai_summary.get("executive_summary", "Assessment completed"),
            detailed_findings={
                "discovery": discovery_results,
                "performance": performance_results,
                "security": security_results,
                "ai_analysis": ai_summary
            }
        )

    async def _store_assessment_results(self, result: HealthAssessmentResult):
        """Store assessment results for historical analysis"""
        self.assessment_history.append(result)
        self.last_assessment = result
        
        # Keep only last 100 assessments in memory
        if len(self.assessment_history) > 100:
            self.assessment_history = self.assessment_history[-100:]
        
        # Store in Neo4j for long-term analysis
        try:
            with self.knowledge_graph.driver.session() as session:
                query = """
                CREATE (a:HealthAssessment {
                    assessment_id: $assessment_id,
                    timestamp: datetime($timestamp),
                    overall_health_score: $health_score,
                    critical_issues_count: $critical_issues,
                    security_threats_detected: $security_threats,
                    devices_discovered: $devices_discovered,
                    executive_summary: $summary
                })
                """
                
                session.run(query, {
                    "assessment_id": result.assessment_id,
                    "timestamp": result.timestamp.isoformat(),
                    "health_score": result.overall_health_score,
                    "critical_issues": result.critical_issues_count,
                    "security_threats": result.security_threats_detected,
                    "devices_discovered": result.devices_discovered,
                    "summary": result.executive_summary
                })
                
        except Exception as e:
            self.logger.warning(f"Failed to store assessment in Neo4j: {e}")

    async def _update_workflow_metrics(self, success: bool, duration: float):
        """Update workflow performance metrics"""
        self.workflow_metrics["total_assessments"] += 1
        
        if success:
            self.workflow_metrics["last_successful_run"] = datetime.now().isoformat()
            
            # Update average duration
            total = self.workflow_metrics["total_assessments"]
            current_avg = self.workflow_metrics["average_duration"]
            self.workflow_metrics["average_duration"] = ((current_avg * (total - 1)) + duration) / total
        
        # Update success rate
        successful_runs = self.workflow_metrics["total_assessments"] - (0 if success else 1)
        self.workflow_metrics["success_rate"] = (successful_runs / self.workflow_metrics["total_assessments"]) * 100

    async def start_scheduled_workflow(self, interval_minutes: int = 15):
        """Start the scheduled assessment workflow"""
        self.logger.info(f"🔄 Starting automated health assessment workflow (every {interval_minutes} minutes)")
        
        while True:
            try:
                # Run assessment
                result = await self.run_scheduled_assessment()
                
                # Log key metrics
                self.logger.info(f"📊 Assessment {result.assessment_id}: "
                               f"Health {result.overall_health_score:.1f}%, "
                               f"Critical Issues {result.critical_issues_count}, "
                               f"Security Threats {result.security_threats_detected}")
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"❌ Scheduled assessment failed: {e}")
                # Wait 5 minutes before retry on failure
                await asyncio.sleep(300)

    def get_assessment_history(self) -> List[HealthAssessmentResult]:
        """Get historical assessment results"""
        return self.assessment_history.copy()

    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        return self.workflow_metrics.copy()

# Example usage and testing
if __name__ == "__main__":
    async def test_automated_assessment():
        assessment_system = AutomatedHealthAssessment()
        
        print("=== AUTOMATED HEALTH ASSESSMENT TEST ===")
        
        try:
            # Run single assessment
            result = await assessment_system.run_scheduled_assessment()
            
            print(f"\n✅ Assessment Results:")
            print(f"   Assessment ID: {result.assessment_id}")
            print(f"   Overall Health: {result.overall_health_score:.1f}%")
            print(f"   Critical Issues: {result.critical_issues_count}")
            print(f"   Security Threats: {result.security_threats_detected}")
            print(f"   Devices Discovered: {result.devices_discovered}")
            print(f"   Recommendations: {len(result.recommendations)}")
            
            print(f"\n🤖 Executive Summary:")
            print(f"   {result.executive_summary}")
            
            if result.recommendations:
                print(f"\n💡 Top Recommendations:")
                for rec in result.recommendations[:3]:
                    print(f"   [{rec.get('priority', 'medium').upper()}] {rec.get('action', 'Action recommended')}")
            
            print(f"\n📈 Workflow Metrics:")
            metrics = assessment_system.get_workflow_metrics()
            print(f"   Success Rate: {metrics['success_rate']:.1f}%")
            print(f"   Average Duration: {metrics['average_duration']:.2f}s")
            
        except Exception as e:
            print(f"❌ Assessment test failed: {e}")

    # Run test
    asyncio.run(test_automated_assessment())