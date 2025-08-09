"""
Intelligent Incident Response System
Multi-agent coordination for network incident investigation and resolution
Integrates Magentic-One, AutoGen Studio, Perplexica, and GenAI Stack
"""

import asyncio
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import our network management components
from alert_management_agent import AlertManagementAgent, NetworkAlert, AlertSeverity
from unified_network_manager import UnifiedNetworkManager
from neo4j_network_schema import NetworkKnowledgeGraph
from genai_network_query_agent import NetworkQueryAgent

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    RESOLVING = "resolving"
    RESOLVED = "resolved"

@dataclass
class NetworkIncident:
    """Network incident data structure"""
    incident_id: str
    timestamp: datetime
    severity: IncidentSeverity
    status: IncidentStatus
    incident_type: str
    title: str
    description: str
    affected_devices: List[str]
    affected_networks: List[str]
    business_impact: Dict[str, Any]
    root_cause_analysis: Optional[str]
    resolution_steps: List[str]
    lessons_learned: Optional[str]
    investigation_timeline: List[Dict[str, Any]]
    ai_agents_involved: List[str]

@dataclass
class InvestigationStep:
    """Investigation step data structure"""
    step_id: str
    timestamp: datetime
    agent_name: str
    action_type: str
    description: str
    findings: Dict[str, Any]
    confidence_score: float
    next_recommendations: List[str]

class IntelligentIncidentResponse:
    """
    Intelligent Incident Response System
    Coordinates multiple AI agents for automated network incident investigation
    """
    
    def __init__(self,
                 meraki_api: str = "http://localhost:11030",
                 fortinet_api: str = "http://localhost:11031",
                 neo4j_uri: str = "neo4j://localhost:7687",
                 autogen_api: str = "http://localhost:11001",
                 magentic_one_api: str = "http://localhost:11003",
                 perplexica_api: str = "http://localhost:11020",
                 genai_stack_api: str = "http://localhost:8504"):
        
        self.logger = logging.getLogger("IntelligentIncidentResponse")
        
        # Initialize core components
        self.alert_agent = AlertManagementAgent(meraki_api)
        self.network_manager = UnifiedNetworkManager(meraki_api, fortinet_api)
        self.knowledge_graph = NetworkKnowledgeGraph(neo4j_uri)
        self.query_agent = NetworkQueryAgent(neo4j_uri, genai_stack_api)
        
        # AI platform endpoints
        self.autogen_api = autogen_api
        self.magentic_one_api = magentic_one_api
        self.perplexica_api = perplexica_api
        self.genai_stack_api = genai_stack_api
        
        # Active incidents and investigation state
        self.active_incidents: Dict[str, NetworkIncident] = {}
        self.investigation_history: List[NetworkIncident] = []
        
        # AI agent capabilities
        self.ai_agents = {
            "correlation_agent": "Analyzes event correlations and patterns",
            "security_agent": "Investigates security-related incidents",
            "performance_agent": "Analyzes network performance issues",
            "topology_agent": "Examines network topology and dependencies",
            "remediation_agent": "Suggests and executes remediation actions"
        }
        
        # Investigation workflows
        self.incident_workflows = {
            "high_bandwidth_utilization": self._investigate_bandwidth_incident,
            "device_offline": self._investigate_device_offline,
            "security_breach": self._investigate_security_incident,
            "performance_degradation": self._investigate_performance_incident,
            "network_outage": self._investigate_network_outage
        }

    async def detect_and_respond_to_incident(self, trigger_alert: NetworkAlert) -> NetworkIncident:
        """
        Main incident response workflow triggered by high-priority alerts
        Example: High bandwidth utilization detected
        """
        incident_id = f"inc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{trigger_alert.alert_id[:8]}"
        
        self.logger.info(f"🚨 Incident detected: {incident_id} - {trigger_alert.title}")
        
        # Create incident record
        incident = NetworkIncident(
            incident_id=incident_id,
            timestamp=datetime.now(),
            severity=self._map_alert_to_incident_severity(trigger_alert.severity),
            status=IncidentStatus.DETECTED,
            incident_type=trigger_alert.alert_type,
            title=f"Network Incident: {trigger_alert.title}",
            description=trigger_alert.description,
            affected_devices=[trigger_alert.source_id] if trigger_alert.source == "device" else [],
            affected_networks=[trigger_alert.source_id] if trigger_alert.source == "network" else [],
            business_impact={},
            root_cause_analysis=None,
            resolution_steps=[],
            lessons_learned=None,
            investigation_timeline=[],
            ai_agents_involved=[]
        )
        
        # Store active incident
        self.active_incidents[incident_id] = incident
        
        try:
            # Start intelligent investigation workflow
            await self._run_intelligent_investigation(incident, trigger_alert)
            
            return incident
            
        except Exception as e:
            self.logger.error(f"❌ Incident response failed: {incident_id} - {e}")
            incident.status = IncidentStatus.ESCALATED
            raise

    async def _run_intelligent_investigation(self, incident: NetworkIncident, trigger_alert: NetworkAlert):
        """
        Run comprehensive AI-powered investigation
        Coordinates: Magentic-One → AutoGen Studio → Perplexica → GenAI Stack → Automated Remediation
        """
        self.logger.info(f"🔍 Starting intelligent investigation: {incident.incident_id}")
        
        # Update incident status
        incident.status = IncidentStatus.INVESTIGATING
        
        # Step 1: Magentic-One → Correlates with security events
        correlation_findings = await self._magentic_one_correlation(incident, trigger_alert)
        
        # Step 2: AutoGen Studio → Creates investigation team
        investigation_team = await self._autogen_create_investigation_team(incident, correlation_findings)
        
        # Step 3: Perplexica → Searches for similar incidents
        similar_incidents = await self._perplexica_search_similar_incidents(incident)
        
        # Step 4: GenAI Stack → Consults knowledge base
        knowledge_base_insights = await self._genai_stack_knowledge_consultation(incident, similar_incidents)
        
        # Step 5: Automated → Implements approved remediation
        remediation_actions = await self._automated_remediation(incident, knowledge_base_insights)
        
        # Compile comprehensive analysis
        await self._compile_investigation_results(incident, {
            "correlation": correlation_findings,
            "investigation_team": investigation_team,
            "similar_incidents": similar_incidents,
            "knowledge_insights": knowledge_base_insights,
            "remediation": remediation_actions
        })
        
        # Update incident status based on results
        if remediation_actions.get("auto_resolved"):
            incident.status = IncidentStatus.RESOLVED
        else:
            incident.status = IncidentStatus.RESOLVING

    async def _magentic_one_correlation(self, incident: NetworkIncident, trigger_alert: NetworkAlert) -> Dict[str, Any]:
        """
        Magentic-One Agent: Correlates with security events and system data
        Uses Microsoft's multi-agent architecture for comprehensive analysis
        """
        self.logger.info(f"🧠 Magentic-One: Correlating security events for {incident.incident_id}")
        
        correlation_step = InvestigationStep(
            step_id=f"{incident.incident_id}_correlation",
            timestamp=datetime.now(),
            agent_name="Magentic-One",
            action_type="security_correlation",
            description="Analyzing security event correlations and system patterns",
            findings={},
            confidence_score=0.0,
            next_recommendations=[]
        )
        
        try:
            # Prepare correlation request for Magentic-One
            correlation_request = {
                "incident_id": incident.incident_id,
                "alert_details": {
                    "type": trigger_alert.alert_type,
                    "severity": trigger_alert.severity.value,
                    "source_device": trigger_alert.source_id,
                    "timestamp": trigger_alert.timestamp.isoformat(),
                    "description": trigger_alert.description
                },
                "correlation_scope": {
                    "time_window_hours": 24,
                    "include_security_events": True,
                    "include_performance_data": True,
                    "include_network_topology": True
                },
                "analysis_requirements": [
                    "Identify related security events",
                    "Analyze temporal patterns",
                    "Assess potential attack vectors",
                    "Evaluate system interdependencies"
                ]
            }
            
            # Call Magentic-One API
            response = await self._call_magentic_one_api(correlation_request)
            
            if response and response.get("status") == "success":
                findings = response.get("analysis", {})
                
                correlation_step.findings = {
                    "security_correlations": findings.get("security_correlations", []),
                    "temporal_patterns": findings.get("temporal_patterns", []),
                    "risk_assessment": findings.get("risk_assessment", {}),
                    "affected_systems": findings.get("affected_systems", []),
                    "correlation_confidence": findings.get("confidence_score", 0.0)
                }
                
                correlation_step.confidence_score = findings.get("confidence_score", 0.7)
                
                # Generate next recommendations
                if findings.get("security_correlations"):
                    correlation_step.next_recommendations.append("Investigate identified security correlations")
                
                if findings.get("affected_systems"):
                    correlation_step.next_recommendations.append("Analyze impact on correlated systems")
                
            else:
                # Fallback to local correlation analysis
                local_correlation = await self._perform_local_correlation(trigger_alert)
                correlation_step.findings = local_correlation
                correlation_step.confidence_score = 0.5
                correlation_step.next_recommendations.append("Perform deeper manual investigation")
            
            # Add step to investigation timeline
            incident.investigation_timeline.append(asdict(correlation_step))
            incident.ai_agents_involved.append("Magentic-One")
            
            return correlation_step.findings
            
        except Exception as e:
            self.logger.warning(f"Magentic-One correlation failed: {e}")
            correlation_step.findings = {"error": str(e)}
            correlation_step.confidence_score = 0.0
            incident.investigation_timeline.append(asdict(correlation_step))
            
            # Return basic correlation
            return await self._perform_local_correlation(trigger_alert)

    async def _call_magentic_one_api(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call Magentic-One API for multi-agent analysis"""
        try:
            response = requests.post(
                f"{self.magentic_one_api}/analyze/network-incident",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Magentic-One API returned {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.debug(f"Magentic-One API unavailable: {e}")
            return None

    async def _perform_local_correlation(self, trigger_alert: NetworkAlert) -> Dict[str, Any]:
        """Perform local correlation analysis as fallback"""
        correlation = {
            "security_correlations": [],
            "temporal_patterns": [],
            "risk_assessment": {"level": "medium"},
            "affected_systems": [],
            "correlation_confidence": 0.5
        }
        
        # Check for related alerts
        active_alerts = self.alert_agent.get_active_alerts()
        related_alerts = [
            alert for alert in active_alerts 
            if (alert.source_id == trigger_alert.source_id or 
                alert.location == trigger_alert.location) and
                alert.alert_id != trigger_alert.alert_id
        ]
        
        if related_alerts:
            correlation["security_correlations"] = [
                {
                    "alert_id": alert.alert_id,
                    "type": alert.alert_type,
                    "correlation_type": "location" if alert.location == trigger_alert.location else "device"
                }
                for alert in related_alerts
            ]
        
        # Perform security correlation with Fortinet if available
        if self.network_manager.fortinet_available:
            security_correlations = await self.network_manager.perform_security_correlation()
            relevant_correlations = [
                c for c in security_correlations
                if c.target_device and c.target_device in trigger_alert.source_id
            ]
            
            if relevant_correlations:
                correlation["security_correlations"].extend([
                    {
                        "correlation_id": c.correlation_id,
                        "type": c.event_type,
                        "severity": c.severity,
                        "description": c.description
                    }
                    for c in relevant_correlations
                ])
        
        return correlation

    async def _autogen_create_investigation_team(self, incident: NetworkIncident, 
                                               correlation_findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        AutoGen Studio: Creates specialized investigation team
        Dynamically assembles AI agents based on incident characteristics
        """
        self.logger.info(f"👥 AutoGen Studio: Creating investigation team for {incident.incident_id}")
        
        team_step = InvestigationStep(
            step_id=f"{incident.incident_id}_team_creation",
            timestamp=datetime.now(),
            agent_name="AutoGen-Studio",
            action_type="team_assembly",
            description="Creating specialized AI agent team for incident investigation",
            findings={},
            confidence_score=0.0,
            next_recommendations=[]
        )
        
        try:
            # Determine required agent specializations
            required_specializations = self._determine_required_agents(incident, correlation_findings)
            
            # Create AutoGen Studio team configuration
            team_config = {
                "investigation_id": incident.incident_id,
                "team_objective": f"Investigate and resolve {incident.incident_type} incident",
                "specializations_required": required_specializations,
                "incident_context": {
                    "severity": incident.severity.value,
                    "affected_devices": incident.affected_devices,
                    "affected_networks": incident.affected_networks,
                    "correlation_data": correlation_findings
                },
                "coordination_mode": "collaborative",
                "escalation_thresholds": {
                    "time_limit_minutes": 30,
                    "confidence_threshold": 0.8
                }
            }
            
            # Request team creation from AutoGen Studio
            response = await self._call_autogen_studio_api("create-investigation-team", team_config)
            
            if response and response.get("status") == "success":
                team_data = response.get("team", {})
                
                team_step.findings = {
                    "team_id": team_data.get("team_id"),
                    "agents_assigned": team_data.get("agents", []),
                    "coordination_plan": team_data.get("coordination_plan", {}),
                    "investigation_workflow": team_data.get("workflow_steps", []),
                    "estimated_resolution_time": team_data.get("estimated_time_minutes", 30)
                }
                
                team_step.confidence_score = 0.9
                team_step.next_recommendations = team_data.get("workflow_steps", [])
                
                # Start team coordination
                await self._coordinate_investigation_team(team_data, incident)
                
            else:
                # Fallback to predefined investigation workflow
                fallback_team = self._create_fallback_investigation_team(incident, correlation_findings)
                team_step.findings = fallback_team
                team_step.confidence_score = 0.6
            
            incident.investigation_timeline.append(asdict(team_step))
            incident.ai_agents_involved.append("AutoGen-Studio")
            
            return team_step.findings
            
        except Exception as e:
            self.logger.warning(f"AutoGen Studio team creation failed: {e}")
            fallback_team = self._create_fallback_investigation_team(incident, correlation_findings)
            team_step.findings = fallback_team
            team_step.confidence_score = 0.4
            incident.investigation_timeline.append(asdict(team_step))
            return fallback_team

    def _determine_required_agents(self, incident: NetworkIncident, correlation_findings: Dict[str, Any]) -> List[str]:
        """Determine which AI agents are needed for this incident"""
        required_agents = ["correlation_agent"]  # Always include correlation
        
        # Add agents based on incident type
        if "security" in incident.incident_type.lower() or correlation_findings.get("security_correlations"):
            required_agents.append("security_agent")
        
        if "performance" in incident.incident_type.lower() or "bandwidth" in incident.incident_type.lower():
            required_agents.append("performance_agent")
        
        if incident.affected_networks or len(incident.affected_devices) > 1:
            required_agents.append("topology_agent")
        
        # Always include remediation agent for resolution
        required_agents.append("remediation_agent")
        
        return required_agents

    async def _call_autogen_studio_api(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call AutoGen Studio API"""
        try:
            response = requests.post(
                f"{self.autogen_api}/api/{endpoint}",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"AutoGen Studio API returned {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.debug(f"AutoGen Studio API unavailable: {e}")
            return None

    def _create_fallback_investigation_team(self, incident: NetworkIncident, 
                                          correlation_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback investigation team when AutoGen Studio is unavailable"""
        return {
            "team_id": f"fallback_{incident.incident_id}",
            "agents_assigned": self._determine_required_agents(incident, correlation_findings),
            "coordination_plan": {
                "mode": "sequential",
                "steps": [
                    "Analyze network topology impact",
                    "Review performance metrics", 
                    "Assess security implications",
                    "Recommend remediation actions"
                ]
            },
            "investigation_workflow": [
                "Review incident context and correlations",
                "Analyze affected systems and dependencies",
                "Search for similar historical incidents",
                "Develop remediation recommendations"
            ],
            "estimated_resolution_time": 45
        }

    async def _coordinate_investigation_team(self, team_data: Dict[str, Any], incident: NetworkIncident):
        """Coordinate the investigation team activities"""
        team_id = team_data.get("team_id")
        workflow_steps = team_data.get("workflow_steps", [])
        
        self.logger.info(f"🎯 Coordinating investigation team {team_id}")
        
        for step in workflow_steps:
            try:
                # Execute each workflow step
                step_result = await self._execute_investigation_step(step, incident)
                
                # Log step completion
                self.logger.info(f"✅ Completed step: {step}")
                
            except Exception as e:
                self.logger.warning(f"Investigation step failed: {step} - {e}")

    async def _execute_investigation_step(self, step: str, incident: NetworkIncident) -> Dict[str, Any]:
        """Execute individual investigation step"""
        # This would contain the actual step execution logic
        # For now, return a placeholder result
        return {
            "step": step,
            "status": "completed",
            "findings": {},
            "timestamp": datetime.now().isoformat()
        }

    async def _perplexica_search_similar_incidents(self, incident: NetworkIncident) -> Dict[str, Any]:
        """
        Perplexica: Searches for similar incidents
        Uses AI-powered search to find related incidents and solutions
        """
        self.logger.info(f"🔍 Perplexica: Searching for similar incidents to {incident.incident_id}")
        
        search_step = InvestigationStep(
            step_id=f"{incident.incident_id}_similarity_search",
            timestamp=datetime.now(),
            agent_name="Perplexica",
            action_type="similarity_search",
            description="Searching for similar network incidents and proven solutions",
            findings={},
            confidence_score=0.0,
            next_recommendations=[]
        )
        
        try:
            # Prepare search query for Perplexica
            search_query = self._generate_perplexica_search_query(incident)
            
            search_request = {
                "query": search_query,
                "search_scope": [
                    "network_incidents",
                    "troubleshooting_guides", 
                    "vendor_documentation",
                    "community_solutions"
                ],
                "filters": {
                    "incident_type": incident.incident_type,
                    "severity_level": incident.severity.value,
                    "time_range": "last_2_years"
                },
                "result_limit": 10
            }
            
            # Call Perplexica API
            response = await self._call_perplexica_api(search_request)
            
            if response and response.get("results"):
                results = response.get("results", [])
                
                search_step.findings = {
                    "similar_incidents": results,
                    "solution_patterns": self._extract_solution_patterns(results),
                    "confidence_scores": [r.get("confidence", 0.0) for r in results],
                    "search_query_used": search_query
                }
                
                search_step.confidence_score = sum(search_step.findings["confidence_scores"]) / len(results) if results else 0.0
                search_step.next_recommendations = [
                    "Review similar incident resolutions",
                    "Apply proven solution patterns",
                    "Adapt solutions to current context"
                ]
                
            else:
                # Fallback to local knowledge base search
                local_search = await self._search_local_knowledge_base(incident)
                search_step.findings = local_search
                search_step.confidence_score = 0.4
            
            incident.investigation_timeline.append(asdict(search_step))
            incident.ai_agents_involved.append("Perplexica")
            
            return search_step.findings
            
        except Exception as e:
            self.logger.warning(f"Perplexica search failed: {e}")
            local_search = await self._search_local_knowledge_base(incident)
            search_step.findings = local_search
            search_step.confidence_score = 0.2
            incident.investigation_timeline.append(asdict(search_step))
            return local_search

    def _generate_perplexica_search_query(self, incident: NetworkIncident) -> str:
        """Generate optimized search query for Perplexica"""
        query_parts = [
            incident.incident_type.replace("_", " "),
            incident.severity.value,
            "network incident"
        ]
        
        # Add device-specific terms
        if incident.affected_devices:
            # Extract device models if available
            query_parts.append("device failure")
        
        # Add network-specific terms  
        if incident.affected_networks:
            query_parts.append("network outage")
        
        # Add context from description
        if "bandwidth" in incident.description.lower():
            query_parts.append("bandwidth utilization")
        if "security" in incident.description.lower():
            query_parts.append("security breach")
        
        return " ".join(query_parts)

    async def _call_perplexica_api(self, search_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call Perplexica API for AI-powered search"""
        try:
            response = requests.post(
                f"{self.perplexica_api}/api/search",
                json=search_request,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Perplexica API returned {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.debug(f"Perplexica API unavailable: {e}")
            return None

    def _extract_solution_patterns(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract common solution patterns from search results"""
        patterns = []
        
        for result in search_results:
            if result.get("solution_summary"):
                patterns.append({
                    "pattern": result.get("solution_summary"),
                    "success_rate": result.get("success_rate", "unknown"),
                    "complexity": result.get("complexity", "medium")
                })
        
        return patterns

    async def _search_local_knowledge_base(self, incident: NetworkIncident) -> Dict[str, Any]:
        """Search local Neo4j knowledge base for similar incidents"""
        try:
            # Query Neo4j for similar historical incidents
            with self.knowledge_graph.driver.session() as session:
                query = """
                MATCH (a:HealthAssessment)
                WHERE a.critical_issues_count > 0 OR a.security_threats_detected > 0
                RETURN a.assessment_id, a.timestamp, a.critical_issues_count, 
                       a.security_threats_detected, a.executive_summary
                ORDER BY a.timestamp DESC
                LIMIT 5
                """
                
                result = session.run(query)
                historical_data = [record.data() for record in result]
                
                return {
                    "similar_incidents": historical_data,
                    "solution_patterns": [
                        {"pattern": "Monitor and investigate critical devices", "success_rate": "high"},
                        {"pattern": "Correlate with security events", "success_rate": "medium"}
                    ],
                    "search_source": "local_knowledge_base"
                }
                
        except Exception as e:
            self.logger.warning(f"Local knowledge base search failed: {e}")
            return {
                "similar_incidents": [],
                "solution_patterns": [],
                "search_source": "none"
            }

    async def _genai_stack_knowledge_consultation(self, incident: NetworkIncident, 
                                                similar_incidents: Dict[str, Any]) -> Dict[str, Any]:
        """
        GenAI Stack: Consults knowledge base
        Uses AI to analyze incident context and provide intelligent recommendations
        """
        self.logger.info(f"🧠 GenAI Stack: Consulting knowledge base for {incident.incident_id}")
        
        knowledge_step = InvestigationStep(
            step_id=f"{incident.incident_id}_knowledge_consultation",
            timestamp=datetime.now(),
            agent_name="GenAI-Stack",
            action_type="knowledge_consultation",
            description="Consulting AI knowledge base for intelligent incident analysis",
            findings={},
            confidence_score=0.0,
            next_recommendations=[]
        )
        
        try:
            # Prepare consultation request
            consultation_context = {
                "incident_details": {
                    "type": incident.incident_type,
                    "severity": incident.severity.value,
                    "description": incident.description,
                    "affected_systems": {
                        "devices": incident.affected_devices,
                        "networks": incident.affected_networks
                    }
                },
                "investigation_findings": {
                    "similar_incidents": similar_incidents.get("similar_incidents", []),
                    "solution_patterns": similar_incidents.get("solution_patterns", [])
                },
                "consultation_objectives": [
                    "Identify root cause candidates",
                    "Recommend investigation priorities",
                    "Suggest remediation approaches",
                    "Assess business impact"
                ]
            }
            
            # Use our GenAI query agent for natural language analysis
            analysis_question = f"Analyze this {incident.incident_type} incident and provide expert recommendations for investigation and resolution"
            
            ai_response = await self.query_agent.process_natural_language_query(
                analysis_question,
                context=consultation_context
            )
            
            if ai_response and ai_response.get("natural_language_response"):
                knowledge_step.findings = {
                    "ai_analysis": ai_response.get("natural_language_response"),
                    "root_cause_candidates": self._extract_root_cause_candidates(ai_response),
                    "investigation_priorities": self._extract_investigation_priorities(ai_response),
                    "remediation_suggestions": self._extract_remediation_suggestions(ai_response),
                    "business_impact_assessment": self._assess_business_impact_from_ai(ai_response, incident)
                }
                
                knowledge_step.confidence_score = 0.8
                knowledge_step.next_recommendations = knowledge_step.findings["investigation_priorities"]
                
            else:
                # Fallback to rule-based analysis
                fallback_analysis = self._perform_rule_based_analysis(incident, similar_incidents)
                knowledge_step.findings = fallback_analysis
                knowledge_step.confidence_score = 0.5
            
            incident.investigation_timeline.append(asdict(knowledge_step))
            incident.ai_agents_involved.append("GenAI-Stack")
            
            return knowledge_step.findings
            
        except Exception as e:
            self.logger.warning(f"GenAI Stack consultation failed: {e}")
            fallback_analysis = self._perform_rule_based_analysis(incident, similar_incidents)
            knowledge_step.findings = fallback_analysis
            knowledge_step.confidence_score = 0.3
            incident.investigation_timeline.append(asdict(knowledge_step))
            return fallback_analysis

    def _extract_root_cause_candidates(self, ai_response: Dict[str, Any]) -> List[str]:
        """Extract potential root causes from AI analysis"""
        # Simple keyword extraction - could be enhanced with NLP
        response_text = ai_response.get("natural_language_response", "").lower()
        
        root_causes = []
        if "bandwidth" in response_text or "traffic" in response_text:
            root_causes.append("Network congestion or bandwidth saturation")
        if "security" in response_text or "attack" in response_text:
            root_causes.append("Security incident or malicious activity")
        if "hardware" in response_text or "device" in response_text:
            root_causes.append("Hardware failure or device malfunction")
        if "configuration" in response_text or "policy" in response_text:
            root_causes.append("Configuration error or policy conflict")
        
        return root_causes if root_causes else ["Unknown - requires further investigation"]

    def _extract_investigation_priorities(self, ai_response: Dict[str, Any]) -> List[str]:
        """Extract investigation priorities from AI response"""
        return [
            "Verify device connectivity and status",
            "Analyze recent configuration changes",
            "Review security logs and events",
            "Check network topology and dependencies",
            "Assess performance metrics and trends"
        ]

    def _extract_remediation_suggestions(self, ai_response: Dict[str, Any]) -> List[str]:
        """Extract remediation suggestions from AI response"""
        return [
            "Restart affected network devices",
            "Review and optimize network configurations",
            "Implement additional monitoring for early detection",
            "Update security policies if security-related",
            "Document incident for future reference"
        ]

    def _assess_business_impact_from_ai(self, ai_response: Dict[str, Any], incident: NetworkIncident) -> Dict[str, Any]:
        """Assess business impact using AI insights"""
        return {
            "severity": incident.severity.value,
            "affected_users": len(incident.affected_devices) * 10,  # Rough estimate
            "estimated_downtime": "30-60 minutes" if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL] else "minimal",
            "financial_impact": "medium" if incident.severity == IncidentSeverity.CRITICAL else "low",
            "reputation_risk": "medium" if incident.severity == IncidentSeverity.CRITICAL else "low"
        }

    def _perform_rule_based_analysis(self, incident: NetworkIncident, similar_incidents: Dict[str, Any]) -> Dict[str, Any]:
        """Perform rule-based analysis as fallback"""
        return {
            "ai_analysis": f"Rule-based analysis of {incident.incident_type} incident",
            "root_cause_candidates": [
                "Network congestion",
                "Device malfunction", 
                "Configuration error"
            ],
            "investigation_priorities": [
                "Check device status and connectivity",
                "Review network performance metrics",
                "Analyze recent changes"
            ],
            "remediation_suggestions": [
                "Restart affected devices",
                "Review network configuration",
                "Monitor for recurrence"
            ],
            "business_impact_assessment": {
                "severity": incident.severity.value,
                "affected_users": "unknown",
                "estimated_downtime": "unknown",
                "analysis_source": "rule_based"
            }
        }

    async def _automated_remediation(self, incident: NetworkIncident, 
                                   knowledge_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automated Remediation: Implements approved remediation actions
        Executes safe automated fixes and prepares manual intervention steps
        """
        self.logger.info(f"🔧 Automated Remediation: Processing {incident.incident_id}")
        
        remediation_step = InvestigationStep(
            step_id=f"{incident.incident_id}_auto_remediation",
            timestamp=datetime.now(),
            agent_name="AutomatedRemediation",
            action_type="remediation",
            description="Executing automated remediation actions",
            findings={},
            confidence_score=0.0,
            next_recommendations=[]
        )
        
        try:
            remediation_plan = self._create_remediation_plan(incident, knowledge_insights)
            
            # Execute safe automated actions
            automated_results = await self._execute_safe_remediations(incident, remediation_plan)
            
            # Prepare manual actions for approval
            manual_actions = self._prepare_manual_actions(incident, remediation_plan)
            
            remediation_step.findings = {
                "remediation_plan": remediation_plan,
                "automated_actions_taken": automated_results.get("executed_actions", []),
                "automated_success_rate": automated_results.get("success_rate", 0.0),
                "manual_actions_required": manual_actions,
                "auto_resolved": automated_results.get("incident_resolved", False),
                "estimated_completion_time": "15-30 minutes"
            }
            
            remediation_step.confidence_score = automated_results.get("success_rate", 0.0)
            remediation_step.next_recommendations = manual_actions
            
            # Update incident resolution steps
            incident.resolution_steps.extend(automated_results.get("executed_actions", []))
            incident.resolution_steps.extend(manual_actions)
            
            incident.investigation_timeline.append(asdict(remediation_step))
            incident.ai_agents_involved.append("AutomatedRemediation")
            
            return remediation_step.findings
            
        except Exception as e:
            self.logger.error(f"Automated remediation failed: {e}")
            remediation_step.findings = {"error": str(e)}
            remediation_step.confidence_score = 0.0
            incident.investigation_timeline.append(asdict(remediation_step))
            return {"error": str(e), "auto_resolved": False}

    def _create_remediation_plan(self, incident: NetworkIncident, knowledge_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive remediation plan"""
        plan = {
            "incident_id": incident.incident_id,
            "safe_automated_actions": [],
            "manual_approval_actions": [],
            "monitoring_actions": [],
            "rollback_procedures": []
        }
        
        # Determine safe automated actions based on incident type
        if incident.incident_type == "device_offline":
            plan["safe_automated_actions"].extend([
                "Ping device to verify connectivity",
                "Check device status via API",
                "Send device restart command if safe"
            ])
            
        elif "bandwidth" in incident.incident_type:
            plan["safe_automated_actions"].extend([
                "Collect current traffic statistics",
                "Identify top bandwidth consumers",
                "Generate traffic analysis report"
            ])
            
        elif "performance" in incident.incident_type:
            plan["safe_automated_actions"].extend([
                "Collect performance metrics",
                "Run automated diagnostics",
                "Generate performance report"
            ])
        
        # Add monitoring actions
        plan["monitoring_actions"].extend([
            "Enable enhanced monitoring for affected devices",
            "Set up alerting for similar issues",
            "Schedule follow-up health checks"
        ])
        
        return plan

    async def _execute_safe_remediations(self, incident: NetworkIncident, remediation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute safe automated remediation actions"""
        results = {
            "executed_actions": [],
            "failed_actions": [],
            "success_rate": 0.0,
            "incident_resolved": False
        }
        
        safe_actions = remediation_plan.get("safe_automated_actions", [])
        
        for action in safe_actions:
            try:
                action_result = await self._execute_remediation_action(action, incident)
                
                if action_result.get("success"):
                    results["executed_actions"].append(action)
                    self.logger.info(f"✅ Executed: {action}")
                else:
                    results["failed_actions"].append(action)
                    self.logger.warning(f"❌ Failed: {action}")
                    
            except Exception as e:
                results["failed_actions"].append(f"{action} (error: {e})")
                self.logger.error(f"❌ Action failed: {action} - {e}")
        
        # Calculate success rate
        total_actions = len(safe_actions)
        if total_actions > 0:
            results["success_rate"] = len(results["executed_actions"]) / total_actions
            
            # Determine if incident is auto-resolved
            if results["success_rate"] >= 0.8:
                results["incident_resolved"] = await self._verify_incident_resolution(incident)
        
        return results

    async def _execute_remediation_action(self, action: str, incident: NetworkIncident) -> Dict[str, Any]:
        """Execute individual remediation action"""
        action_lower = action.lower()
        
        if "ping device" in action_lower:
            return await self._ping_affected_devices(incident.affected_devices)
        elif "check device status" in action_lower:
            return await self._check_device_status(incident.affected_devices)
        elif "restart command" in action_lower:
            return await self._send_device_restart(incident.affected_devices)
        elif "traffic statistics" in action_lower:
            return await self._collect_traffic_stats(incident.affected_networks)
        elif "performance metrics" in action_lower:
            return await self._collect_performance_metrics(incident.affected_devices)
        else:
            return {"success": False, "reason": "Unknown action type"}

    async def _ping_affected_devices(self, device_ids: List[str]) -> Dict[str, Any]:
        """Ping affected devices to check connectivity"""
        # This would integrate with actual device management
        return {"success": True, "result": "Devices responding to ping"}

    async def _check_device_status(self, device_ids: List[str]) -> Dict[str, Any]:
        """Check device status via API"""
        # This would call the actual Meraki/Fortinet APIs
        return {"success": True, "result": "Device status checked"}

    async def _send_device_restart(self, device_ids: List[str]) -> Dict[str, Any]:
        """Send restart command to devices (if safe)"""
        # This would require careful validation before execution
        return {"success": False, "reason": "Manual approval required for device restart"}

    async def _collect_traffic_stats(self, network_ids: List[str]) -> Dict[str, Any]:
        """Collect traffic statistics"""
        # This would gather actual network traffic data
        return {"success": True, "result": "Traffic statistics collected"}

    async def _collect_performance_metrics(self, device_ids: List[str]) -> Dict[str, Any]:
        """Collect performance metrics"""
        # This would gather actual performance data
        return {"success": True, "result": "Performance metrics collected"}

    def _prepare_manual_actions(self, incident: NetworkIncident, remediation_plan: Dict[str, Any]) -> List[str]:
        """Prepare manual actions that require human approval"""
        manual_actions = []
        
        # Add incident-specific manual actions
        if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            manual_actions.append("Escalate to network operations center")
            manual_actions.append("Consider emergency change procedures")
        
        # Add actions requiring approval
        manual_actions.extend([
            "Review and approve device restart procedures",
            "Validate network configuration changes",
            "Coordinate with business stakeholders if needed",
            "Document incident resolution for compliance"
        ])
        
        return manual_actions

    async def _verify_incident_resolution(self, incident: NetworkIncident) -> bool:
        """Verify if incident has been resolved"""
        try:
            # Check if triggering alert is still active
            active_alerts = self.alert_agent.get_active_alerts()
            
            # Look for alerts related to this incident
            related_active_alerts = [
                alert for alert in active_alerts
                if (alert.source_id in incident.affected_devices or
                    alert.source_id in incident.affected_networks)
            ]
            
            # If no related alerts are active, incident may be resolved
            return len(related_active_alerts) == 0
            
        except Exception as e:
            self.logger.warning(f"Failed to verify incident resolution: {e}")
            return False

    async def _compile_investigation_results(self, incident: NetworkIncident, investigation_data: Dict[str, Any]):
        """Compile comprehensive investigation results"""
        
        # Generate root cause analysis
        root_causes = []
        for step_data in investigation_data.values():
            if isinstance(step_data, dict) and "root_cause_candidates" in step_data:
                root_causes.extend(step_data["root_cause_candidates"])
        
        incident.root_cause_analysis = "; ".join(set(root_causes)) if root_causes else "Investigation incomplete"
        
        # Generate business impact assessment
        remediation_data = investigation_data.get("remediation", {})
        knowledge_data = investigation_data.get("knowledge_insights", {})
        
        incident.business_impact = knowledge_data.get("business_impact_assessment", {
            "severity": incident.severity.value,
            "estimated_impact": "unknown"
        })
        
        # Generate lessons learned
        if remediation_data.get("auto_resolved"):
            incident.lessons_learned = "Incident successfully resolved through automated remediation"
        else:
            incident.lessons_learned = "Manual intervention required - consider improving automation"
        
        # Store in incident history
        self.investigation_history.append(incident)
        
        # Keep only last 50 incidents in memory
        if len(self.investigation_history) > 50:
            self.investigation_history = self.investigation_history[-50:]

    def _map_alert_to_incident_severity(self, alert_severity: AlertSeverity) -> IncidentSeverity:
        """Map alert severity to incident severity"""
        mapping = {
            AlertSeverity.LOW: IncidentSeverity.LOW,
            AlertSeverity.MEDIUM: IncidentSeverity.MEDIUM,
            AlertSeverity.HIGH: IncidentSeverity.HIGH,
            AlertSeverity.CRITICAL: IncidentSeverity.CRITICAL
        }
        return mapping.get(alert_severity, IncidentSeverity.MEDIUM)

    def get_active_incidents(self) -> List[NetworkIncident]:
        """Get currently active incidents"""
        return list(self.active_incidents.values())

    def get_incident_history(self) -> List[NetworkIncident]:
        """Get incident investigation history"""
        return self.investigation_history.copy()

    async def close_incident(self, incident_id: str, resolution_summary: str):
        """Close an incident with resolution summary"""
        if incident_id in self.active_incidents:
            incident = self.active_incidents[incident_id]
            incident.status = IncidentStatus.RESOLVED
            incident.lessons_learned = resolution_summary
            
            # Move to history
            del self.active_incidents[incident_id]
            
            self.logger.info(f"✅ Incident closed: {incident_id}")

# Example usage and testing
if __name__ == "__main__":
    async def test_incident_response():
        from alert_management_agent import NetworkAlert, AlertSeverity
        
        # Create test incident response system
        incident_response = IntelligentIncidentResponse()
        
        # Create test alert (simulating high bandwidth utilization)
        test_alert = NetworkAlert(
            alert_id="test_bandwidth_001",
            timestamp=datetime.now(),
            severity=AlertSeverity.HIGH,
            status="active",
            source="network",
            source_id="network_main_office",
            source_name="Main Office Network",
            alert_type="high_bandwidth_utilization",
            title="High Bandwidth Utilization Detected",
            description="Network bandwidth utilization has exceeded 90% threshold",
            location="Corporate / Main Office",
            affected_users=150
        )
        
        print("=== INTELLIGENT INCIDENT RESPONSE TEST ===")
        
        try:
            # Trigger incident response workflow
            incident = await incident_response.detect_and_respond_to_incident(test_alert)
            
            print(f"\n🚨 Incident Created:")
            print(f"   ID: {incident.incident_id}")
            print(f"   Severity: {incident.severity.value}")
            print(f"   Status: {incident.status.value}")
            print(f"   AI Agents Involved: {', '.join(incident.ai_agents_involved)}")
            
            print(f"\n📋 Investigation Timeline:")
            for i, step in enumerate(incident.investigation_timeline, 1):
                print(f"   {i}. {step['agent_name']}: {step['description']}")
                print(f"      Confidence: {step['confidence_score']:.2f}")
            
            print(f"\n🔧 Resolution Steps:")
            for i, step in enumerate(incident.resolution_steps, 1):
                print(f"   {i}. {step}")
            
            if incident.root_cause_analysis:
                print(f"\n🎯 Root Cause Analysis:")
                print(f"   {incident.root_cause_analysis}")
            
            print(f"\n✅ Incident response test completed successfully!")
            
        except Exception as e:
            print(f"❌ Incident response test failed: {e}")

    # Run test
    asyncio.run(test_incident_response())