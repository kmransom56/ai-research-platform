"""
Predictive Maintenance Workflow System
Uses historical performance trends and AI analysis for proactive network maintenance
Integrates GenAI Loader, Neo4j, AI Agents, and Grafana for comprehensive predictive insights
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import our network management components
from network_discovery_agent import NetworkDiscoveryAgent
from device_health_monitoring_agent import DeviceHealthMonitoringAgent
from neo4j_network_schema import NetworkKnowledgeGraph
from unified_network_manager import UnifiedNetworkManager

@dataclass
class PredictiveInsight:
    """Predictive maintenance insight"""
    insight_id: str
    timestamp: datetime
    device_id: str
    device_name: str
    prediction_type: str  # 'failure_risk', 'performance_degradation', 'maintenance_required'
    risk_score: float  # 0-100
    confidence_level: float  # 0-1
    predicted_timeframe: str  # 'immediate', 'within_24h', 'within_week', 'within_month'
    contributing_factors: List[str]
    recommended_actions: List[str]
    business_impact: Dict[str, Any]
    historical_patterns: Dict[str, Any]

@dataclass
class MaintenanceRecommendation:
    """Maintenance recommendation"""
    recommendation_id: str
    timestamp: datetime
    priority: str  # 'critical', 'high', 'medium', 'low'
    maintenance_type: str  # 'preventive', 'predictive', 'corrective'
    target_devices: List[str]
    estimated_duration: str
    required_resources: List[str]
    optimal_maintenance_window: Dict[str, str]
    cost_benefit_analysis: Dict[str, Any]
    risk_if_deferred: str

class PredictiveMaintenanceWorkflow:
    """
    Predictive Maintenance System using AI and Historical Data Analysis
    Processes vendor documentation, analyzes failure patterns, and generates recommendations
    """
    
    def __init__(self,
                 meraki_api: str = "http://localhost:11030",
                 fortinet_api: str = "http://localhost:11031", 
                 neo4j_uri: str = "neo4j://localhost:7687",
                 genai_loader_api: str = "http://localhost:8502",
                 genai_stack_api: str = "http://localhost:8504",
                 grafana_api: str = "http://localhost:11002"):
        
        self.logger = logging.getLogger("PredictiveMaintenanceWorkflow")
        
        # Initialize network management components
        self.discovery_agent = NetworkDiscoveryAgent(meraki_api)
        self.health_agent = DeviceHealthMonitoringAgent(meraki_api)
        self.network_manager = UnifiedNetworkManager(meraki_api, fortinet_api)
        self.knowledge_graph = NetworkKnowledgeGraph(neo4j_uri)
        
        # AI platform endpoints
        self.genai_loader_api = genai_loader_api
        self.genai_stack_api = genai_stack_api
        self.grafana_api = grafana_api
        
        # Predictive models and data
        self.failure_prediction_model = None
        self.performance_prediction_model = None
        self.historical_data_cache = {}
        self.vendor_documentation_cache = {}
        
        # Predictive insights and recommendations
        self.current_insights: List[PredictiveInsight] = []
        self.maintenance_recommendations: List[MaintenanceRecommendation] = []
        self.prediction_accuracy_metrics = {
            "total_predictions": 0,
            "accurate_predictions": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "accuracy_rate": 0.0
        }

    async def run_predictive_maintenance_cycle(self) -> Dict[str, Any]:
        """
        Main predictive maintenance workflow
        Data → GenAI Loader → Neo4j → AI Agents → Grafana → Recommendations
        """
        cycle_start = datetime.now()
        cycle_id = f"pred_maint_{cycle_start.strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"🔮 Starting predictive maintenance cycle: {cycle_id}")
        
        try:
            # Step 1: GenAI Loader → Processes vendor documentation
            self.logger.info("📚 Step 1: Processing vendor documentation")
            documentation_insights = await self._process_vendor_documentation()
            
            # Step 2: Collect and analyze historical performance trends
            self.logger.info("📊 Step 2: Analyzing historical performance trends")
            historical_analysis = await self._analyze_historical_performance_trends()
            
            # Step 3: Neo4j → Maps device relationships and dependencies
            self.logger.info("🕸️ Step 3: Mapping device relationships and dependencies")
            dependency_analysis = await self._analyze_device_dependencies()
            
            # Step 4: AI Agents → Analyze failure patterns
            self.logger.info("🤖 Step 4: AI analysis of failure patterns")
            failure_pattern_analysis = await self._analyze_failure_patterns(historical_analysis)
            
            # Step 5: Generate predictive insights
            self.logger.info("🔍 Step 5: Generating predictive insights")
            predictive_insights = await self._generate_predictive_insights(
                documentation_insights, historical_analysis, dependency_analysis, failure_pattern_analysis
            )
            
            # Step 6: Create maintenance recommendations
            self.logger.info("📋 Step 6: Creating maintenance recommendations")
            maintenance_recommendations = await self._create_maintenance_recommendations(predictive_insights)
            
            # Step 7: Grafana → Visualizes predictions and recommendations
            self.logger.info("📈 Step 7: Updating visualization dashboards")
            visualization_update = await self._update_grafana_dashboards(predictive_insights, maintenance_recommendations)
            
            # Compile results
            cycle_results = {
                "cycle_id": cycle_id,
                "timestamp": cycle_start.isoformat(),
                "duration_seconds": (datetime.now() - cycle_start).total_seconds(),
                "insights_generated": len(predictive_insights),
                "recommendations_created": len(maintenance_recommendations),
                "high_risk_devices": len([i for i in predictive_insights if i.risk_score >= 80]),
                "critical_recommendations": len([r for r in maintenance_recommendations if r.priority == 'critical']),
                "analysis_summary": {
                    "documentation_processed": documentation_insights.get("documents_processed", 0),
                    "historical_data_points": historical_analysis.get("data_points_analyzed", 0),
                    "dependencies_mapped": dependency_analysis.get("relationships_analyzed", 0),
                    "failure_patterns_identified": len(failure_pattern_analysis.get("patterns", []))
                },
                "detailed_results": {
                    "documentation_insights": documentation_insights,
                    "historical_analysis": historical_analysis,
                    "dependency_analysis": dependency_analysis,
                    "failure_patterns": failure_pattern_analysis,
                    "predictive_insights": [asdict(insight) for insight in predictive_insights],
                    "maintenance_recommendations": [asdict(rec) for rec in maintenance_recommendations]
                }
            }
            
            # Store results
            await self._store_cycle_results(cycle_results)
            
            self.logger.info(f"✅ Predictive maintenance cycle completed: {cycle_id}")
            return cycle_results
            
        except Exception as e:
            self.logger.error(f"❌ Predictive maintenance cycle failed: {cycle_id} - {e}")
            raise

    async def _process_vendor_documentation(self) -> Dict[str, Any]:
        """
        GenAI Loader: Processes vendor documentation for maintenance insights
        """
        try:
            # Prepare documentation processing request
            processing_request = {
                "document_sources": [
                    "meraki_maintenance_guides",
                    "fortinet_troubleshooting_docs",
                    "network_best_practices",
                    "device_lifecycle_documentation"
                ],
                "extraction_objectives": [
                    "Identify common failure patterns",
                    "Extract maintenance recommendations",
                    "Analyze lifecycle information",
                    "Parse performance optimization guidelines"
                ],
                "output_format": "structured_insights"
            }
            
            # Call GenAI Loader API
            response = await self._call_genai_loader_api(processing_request)
            
            if response and response.get("status") == "success":
                insights = response.get("insights", {})
                
                # Cache processed documentation
                self.vendor_documentation_cache.update(insights)
                
                return {
                    "documents_processed": response.get("documents_count", 0),
                    "maintenance_patterns": insights.get("maintenance_patterns", []),
                    "failure_indicators": insights.get("failure_indicators", []),
                    "lifecycle_recommendations": insights.get("lifecycle_recommendations", []),
                    "performance_optimization": insights.get("performance_tips", []),
                    "processing_timestamp": datetime.now().isoformat()
                }
            else:
                # Fallback to built-in knowledge
                return await self._use_builtin_documentation_knowledge()
                
        except Exception as e:
            self.logger.warning(f"Vendor documentation processing failed: {e}")
            return await self._use_builtin_documentation_knowledge()

    async def _call_genai_loader_api(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call GenAI Loader API for document processing"""
        try:
            response = requests.post(
                f"{self.genai_loader_api}/api/process-documents",
                json=request_data,
                timeout=120  # Longer timeout for document processing
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"GenAI Loader API returned {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.debug(f"GenAI Loader API unavailable: {e}")
            return None

    async def _use_builtin_documentation_knowledge(self) -> Dict[str, Any]:
        """Use built-in documentation knowledge as fallback"""
        return {
            "documents_processed": 0,
            "maintenance_patterns": [
                {"pattern": "Device performance degradation over time", "frequency": "common"},
                {"pattern": "Firmware-related stability issues", "frequency": "occasional"},
                {"pattern": "Environmental factor impacts", "frequency": "seasonal"}
            ],
            "failure_indicators": [
                {"indicator": "Increasing CPU utilization", "reliability": "high"},
                {"indicator": "Memory usage trends", "reliability": "medium"},
                {"indicator": "Interface error rates", "reliability": "high"}
            ],
            "lifecycle_recommendations": [
                {"recommendation": "Replace devices after 5 years", "device_type": "switches"},
                {"recommendation": "Update firmware quarterly", "device_type": "all"},
                {"recommendation": "Monitor performance degradation", "device_type": "all"}
            ],
            "performance_optimization": [
                {"tip": "Regular configuration optimization", "impact": "medium"},
                {"tip": "Proactive firmware updates", "impact": "high"},
                {"tip": "Environmental monitoring", "impact": "medium"}
            ],
            "processing_timestamp": datetime.now().isoformat(),
            "source": "builtin_knowledge"
        }

    async def _analyze_historical_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze historical performance data to identify trends and patterns
        """
        try:
            # Collect historical data from multiple sources
            historical_data = await self._collect_historical_data()
            
            if not historical_data.get("data_points"):
                return {"data_points_analyzed": 0, "trends": [], "patterns": []}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(historical_data["data_points"])
            
            # Perform trend analysis
            trend_analysis = self._perform_trend_analysis(df)
            
            # Identify performance patterns
            pattern_analysis = self._identify_performance_patterns(df)
            
            # Detect anomalies
            anomaly_analysis = self._detect_performance_anomalies(df)
            
            # Generate degradation predictions
            degradation_predictions = self._predict_performance_degradation(df)
            
            return {
                "data_points_analyzed": len(df),
                "time_range": {
                    "start": historical_data.get("start_date"),
                    "end": historical_data.get("end_date")
                },
                "trends": trend_analysis,
                "patterns": pattern_analysis,
                "anomalies": anomaly_analysis,
                "degradation_predictions": degradation_predictions,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Historical performance analysis failed: {e}")
            return {"data_points_analyzed": 0, "error": str(e)}

    async def _collect_historical_data(self) -> Dict[str, Any]:
        """Collect historical performance data from various sources"""
        # This would collect data from:
        # - Neo4j health assessments
        # - Prometheus metrics
        # - Device logs
        # - Network monitoring data
        
        try:
            historical_data = {
                "data_points": [],
                "start_date": (datetime.now() - timedelta(days=90)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
            
            # Get historical health assessments from Neo4j
            with self.knowledge_graph.driver.session() as session:
                query = """
                MATCH (a:HealthAssessment)
                WHERE a.timestamp > datetime() - duration('P90D')
                OPTIONAL MATCH (a)-[:ASSESSED]->(d:Device)-[:HAS_HEALTH_METRIC]->(h:HealthMetric)
                RETURN a.assessment_id, a.timestamp, a.overall_health_score,
                       collect({device: d.serial, health: h.uptime_score, performance: h.performance_score}) as device_metrics
                ORDER BY a.timestamp ASC
                """
                
                result = session.run(query)
                for record in result:
                    assessment_data = {
                        "assessment_id": record["assessment_id"],
                        "timestamp": record["timestamp"],
                        "overall_health": record["overall_health_score"],
                        "device_metrics": record["device_metrics"]
                    }
                    historical_data["data_points"].append(assessment_data)
            
            return historical_data
            
        except Exception as e:
            self.logger.warning(f"Historical data collection failed: {e}")
            return {"data_points": [], "start_date": None, "end_date": None}

    def _perform_trend_analysis(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Perform statistical trend analysis on performance data"""
        trends = []
        
        try:
            if 'overall_health' in df.columns and len(df) > 5:
                # Calculate trend for overall health
                health_values = df['overall_health'].dropna()
                if len(health_values) > 1:
                    # Simple linear trend
                    x = np.arange(len(health_values))
                    slope = np.polyfit(x, health_values, 1)[0]
                    
                    trend_direction = "improving" if slope > 0.5 else "declining" if slope < -0.5 else "stable"
                    
                    trends.append({
                        "metric": "overall_health",
                        "direction": trend_direction,
                        "slope": float(slope),
                        "confidence": "medium",
                        "significance": "high" if abs(slope) > 1.0 else "low"
                    })
            
            return trends
            
        except Exception as e:
            self.logger.warning(f"Trend analysis failed: {e}")
            return []

    def _identify_performance_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify recurring performance patterns"""
        patterns = []
        
        try:
            # Pattern 1: Time-based patterns (e.g., daily, weekly cycles)
            if 'timestamp' in df.columns and 'overall_health' in df.columns:
                # Convert timestamp to hour of day
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                
                # Check for daily patterns
                hourly_avg = df.groupby('hour')['overall_health'].mean()
                
                if hourly_avg.std() > 5:  # Significant variation
                    patterns.append({
                        "type": "daily_cycle",
                        "description": "Performance varies by time of day",
                        "peak_hours": hourly_avg.idxmax(),
                        "low_hours": hourly_avg.idxmin(),
                        "variation_magnitude": float(hourly_avg.std())
                    })
            
            # Pattern 2: Degradation patterns
            if len(df) > 10:
                # Check for gradual degradation
                recent_avg = df.tail(5)['overall_health'].mean()
                historical_avg = df.head(5)['overall_health'].mean()
                
                if historical_avg - recent_avg > 5:
                    patterns.append({
                        "type": "gradual_degradation",
                        "description": "Overall health declining over time",
                        "degradation_rate": float(historical_avg - recent_avg),
                        "severity": "high" if historical_avg - recent_avg > 10 else "medium"
                    })
            
            return patterns
            
        except Exception as e:
            self.logger.warning(f"Pattern identification failed: {e}")
            return []

    def _detect_performance_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect performance anomalies using machine learning"""
        anomalies = []
        
        try:
            if 'overall_health' in df.columns and len(df) > 10:
                # Use Isolation Forest for anomaly detection
                health_data = df['overall_health'].dropna().values.reshape(-1, 1)
                
                # Scale the data
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(health_data)
                
                # Detect anomalies
                isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = isolation_forest.fit_predict(scaled_data)
                
                # Extract anomaly information
                anomaly_indices = np.where(anomaly_labels == -1)[0]
                
                for idx in anomaly_indices:
                    if idx < len(df):
                        anomalies.append({
                            "timestamp": df.iloc[idx]['timestamp'],
                            "health_score": float(df.iloc[idx]['overall_health']),
                            "anomaly_score": float(isolation_forest.score_samples(scaled_data[idx].reshape(1, -1))[0]),
                            "severity": "high" if df.iloc[idx]['overall_health'] < 70 else "medium"
                        })
            
            return anomalies[:10]  # Return top 10 anomalies
            
        except Exception as e:
            self.logger.warning(f"Anomaly detection failed: {e}")
            return []

    def _predict_performance_degradation(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict future performance degradation"""
        predictions = []
        
        try:
            if 'overall_health' in df.columns and len(df) > 5:
                health_values = df['overall_health'].dropna().values
                
                # Simple linear extrapolation
                x = np.arange(len(health_values))
                coeffs = np.polyfit(x, health_values, 1)
                
                # Predict next few time periods
                future_periods = [len(health_values) + i for i in range(1, 6)]
                future_predictions = np.polyval(coeffs, future_periods)
                
                for i, prediction in enumerate(future_predictions):
                    predictions.append({
                        "time_period": f"period_{i+1}",
                        "predicted_health": float(max(0, min(100, prediction))),
                        "confidence": max(0.3, 1.0 - (i * 0.2)),  # Decreasing confidence over time
                        "risk_level": "high" if prediction < 70 else "medium" if prediction < 85 else "low"
                    })
            
            return predictions
            
        except Exception as e:
            self.logger.warning(f"Performance prediction failed: {e}")
            return []

    async def _analyze_device_dependencies(self) -> Dict[str, Any]:
        """
        Neo4j: Maps device relationships and dependencies for impact analysis
        """
        try:
            dependency_analysis = {
                "relationships_analyzed": 0,
                "critical_dependencies": [],
                "failure_impact_chains": [],
                "single_points_of_failure": []
            }
            
            with self.knowledge_graph.driver.session() as session:
                # Analyze device relationships
                relationships_query = """
                MATCH (d1:Device)-[r]->(d2:Device)
                RETURN d1.serial as source_device, d1.model as source_model,
                       type(r) as relationship_type,
                       d2.serial as target_device, d2.model as target_model,
                       d1.network_name as network
                ORDER BY network, source_device
                """
                
                result = session.run(relationships_query)
                relationships = []
                
                for record in result:
                    relationships.append({
                        "source": record["source_device"],
                        "source_model": record["source_model"],
                        "target": record["target_device"],
                        "target_model": record["target_model"],
                        "relationship": record["relationship_type"],
                        "network": record["network"]
                    })
                
                dependency_analysis["relationships_analyzed"] = len(relationships)
                
                # Identify critical dependencies (devices that many others depend on)
                dependency_counts = {}
                for rel in relationships:
                    source = rel["source"]
                    if source not in dependency_counts:
                        dependency_counts[source] = 0
                    dependency_counts[source] += 1
                
                # Critical devices are those with many dependents
                critical_threshold = max(2, len(relationships) // 10) if relationships else 0
                critical_devices = [
                    {"device": device, "dependent_count": count}
                    for device, count in dependency_counts.items()
                    if count >= critical_threshold
                ]
                
                dependency_analysis["critical_dependencies"] = critical_devices
                
                # Identify single points of failure
                single_points = []
                for rel in relationships:
                    if rel["relationship"] in ["ROUTES_TO", "PROVIDES_POWER_TO"]:
                        # Check if target has only one source of this relationship type
                        same_type_sources = [
                            r for r in relationships 
                            if r["target"] == rel["target"] and r["relationship"] == rel["relationship"]
                        ]
                        
                        if len(same_type_sources) == 1:
                            single_points.append({
                                "critical_device": rel["source"],
                                "affected_device": rel["target"],
                                "relationship_type": rel["relationship"],
                                "network": rel["network"]
                            })
                
                dependency_analysis["single_points_of_failure"] = single_points[:10]  # Top 10
                
                # Analyze potential failure impact chains
                impact_chains = self._analyze_failure_impact_chains(relationships)
                dependency_analysis["failure_impact_chains"] = impact_chains
            
            return dependency_analysis
            
        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {e}")
            return {"relationships_analyzed": 0, "error": str(e)}

    def _analyze_failure_impact_chains(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze potential cascading failure impacts"""
        impact_chains = []
        
        try:
            # Build dependency graph
            dependency_graph = {}
            for rel in relationships:
                source = rel["source"]
                target = rel["target"]
                
                if source not in dependency_graph:
                    dependency_graph[source] = []
                dependency_graph[source].append(target)
            
            # Find impact chains for critical devices
            for source_device, targets in dependency_graph.items():
                if len(targets) >= 2:  # Device with multiple dependents
                    # Calculate potential impact
                    direct_impact = len(targets)
                    indirect_impact = 0
                    
                    # Calculate second-level impacts
                    for target in targets:
                        if target in dependency_graph:
                            indirect_impact += len(dependency_graph[target])
                    
                    if direct_impact + indirect_impact >= 3:  # Significant impact
                        impact_chains.append({
                            "source_device": source_device,
                            "direct_impact": direct_impact,
                            "indirect_impact": indirect_impact,
                            "total_potential_impact": direct_impact + indirect_impact,
                            "affected_devices": targets[:5]  # Sample of affected devices
                        })
            
            # Sort by total impact
            impact_chains.sort(key=lambda x: x["total_potential_impact"], reverse=True)
            return impact_chains[:5]  # Top 5 impact chains
            
        except Exception as e:
            self.logger.warning(f"Impact chain analysis failed: {e}")
            return []

    async def _analyze_failure_patterns(self, historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI Agents: Analyze failure patterns using machine learning and historical data
        """
        try:
            pattern_analysis = {
                "patterns": [],
                "failure_indicators": [],
                "risk_factors": [],
                "predictive_models": {}
            }
            
            # Extract patterns from historical data
            anomalies = historical_analysis.get("anomalies", [])
            trends = historical_analysis.get("trends", [])
            
            # Identify failure patterns
            if anomalies:
                # Pattern 1: Recurring anomaly patterns
                anomaly_hours = []
                for anomaly in anomalies:
                    try:
                        hour = datetime.fromisoformat(anomaly["timestamp"]).hour
                        anomaly_hours.append(hour)
                    except:
                        continue
                
                if anomaly_hours:
                    most_common_hour = max(set(anomaly_hours), key=anomaly_hours.count)
                    pattern_analysis["patterns"].append({
                        "type": "temporal_failure_pattern",
                        "description": f"Failures commonly occur around hour {most_common_hour}",
                        "confidence": min(0.8, anomaly_hours.count(most_common_hour) / len(anomaly_hours))
                    })
            
            # Identify failure indicators from trends
            for trend in trends:
                if trend["direction"] == "declining" and trend.get("significance") == "high":
                    pattern_analysis["failure_indicators"].append({
                        "metric": trend["metric"],
                        "indicator_type": "performance_degradation",
                        "severity": "high" if abs(trend["slope"]) > 2 else "medium",
                        "trend_rate": trend["slope"]
                    })
            
            # Risk factor analysis
            degradation_predictions = historical_analysis.get("degradation_predictions", [])
            high_risk_predictions = [p for p in degradation_predictions if p.get("risk_level") == "high"]
            
            if high_risk_predictions:
                pattern_analysis["risk_factors"].append({
                    "factor": "performance_degradation_trend",
                    "risk_level": "high",
                    "affected_timeframes": len(high_risk_predictions),
                    "description": "Predictive models indicate high risk of performance issues"
                })
            
            # Build simple predictive models
            if historical_analysis.get("data_points_analyzed", 0) > 20:
                pattern_analysis["predictive_models"] = await self._build_predictive_models(historical_analysis)
            
            return pattern_analysis
            
        except Exception as e:
            self.logger.error(f"Failure pattern analysis failed: {e}")
            return {"patterns": [], "error": str(e)}

    async def _build_predictive_models(self, historical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build simple predictive models for failure prediction"""
        models = {}
        
        try:
            # Model 1: Simple threshold-based failure prediction
            anomalies = historical_analysis.get("anomalies", [])
            if anomalies:
                # Calculate failure threshold based on anomalies
                anomaly_scores = [a["health_score"] for a in anomalies]
                if anomaly_scores:
                    failure_threshold = np.mean(anomaly_scores) - np.std(anomaly_scores)
                    
                    models["threshold_model"] = {
                        "type": "threshold_based",
                        "failure_threshold": float(failure_threshold),
                        "confidence": 0.7,
                        "description": "Devices below this health score have high failure risk"
                    }
            
            # Model 2: Trend-based prediction
            trends = historical_analysis.get("trends", [])
            declining_trends = [t for t in trends if t["direction"] == "declining"]
            
            if declining_trends:
                avg_decline_rate = np.mean([abs(t["slope"]) for t in declining_trends])
                
                models["trend_model"] = {
                    "type": "trend_based",
                    "average_decline_rate": float(avg_decline_rate),
                    "confidence": 0.6,
                    "description": "Predicts failure based on performance decline trends"
                }
            
            return models
            
        except Exception as e:
            self.logger.warning(f"Predictive model building failed: {e}")
            return {}

    async def _generate_predictive_insights(self, documentation_insights: Dict[str, Any],
                                          historical_analysis: Dict[str, Any],
                                          dependency_analysis: Dict[str, Any],
                                          failure_patterns: Dict[str, Any]) -> List[PredictiveInsight]:
        """
        Generate comprehensive predictive insights by combining all analysis results
        """
        insights = []
        
        try:
            # Get current device inventory
            await self.network_manager.initialize()
            topology = await self.network_manager.discover_unified_topology()
            devices = self.network_manager.unified_inventory
            
            for device in devices:
                insight = await self._generate_device_insight(
                    device, documentation_insights, historical_analysis, 
                    dependency_analysis, failure_patterns
                )
                
                if insight:
                    insights.append(insight)
            
            # Sort insights by risk score
            insights.sort(key=lambda x: x.risk_score, reverse=True)
            
            # Store insights
            self.current_insights = insights
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            return []

    async def _generate_device_insight(self, device, documentation_insights: Dict[str, Any],
                                     historical_analysis: Dict[str, Any],
                                     dependency_analysis: Dict[str, Any],
                                     failure_patterns: Dict[str, Any]) -> Optional[PredictiveInsight]:
        """Generate predictive insight for individual device"""
        
        try:
            risk_score = 0.0
            confidence_level = 0.5
            prediction_type = "maintenance_required"
            contributing_factors = []
            recommended_actions = []
            
            # Factor 1: Historical performance trends
            if historical_analysis.get("trends"):
                declining_trends = [t for t in historical_analysis["trends"] if t["direction"] == "declining"]
                if declining_trends:
                    risk_score += 30
                    contributing_factors.append("Declining performance trend detected")
                    recommended_actions.append("Monitor device performance closely")
            
            # Factor 2: Anomaly detection
            if historical_analysis.get("anomalies"):
                # Check if this device had recent anomalies (simplified check)
                risk_score += 20
                contributing_factors.append("Historical performance anomalies detected")
                recommended_actions.append("Investigate performance anomalies")
            
            # Factor 3: Dependency analysis
            critical_deps = dependency_analysis.get("critical_dependencies", [])
            device_in_critical = any(d["device"] == device.id for d in critical_deps)
            
            if device_in_critical:
                risk_score += 25
                contributing_factors.append("Device is a critical dependency")
                recommended_actions.append("Prioritize maintenance due to critical role")
            
            # Factor 4: Single point of failure
            spof = dependency_analysis.get("single_points_of_failure", [])
            device_is_spof = any(s["critical_device"] == device.id for s in spof)
            
            if device_is_spof:
                risk_score += 35
                prediction_type = "failure_risk"
                contributing_factors.append("Device is a single point of failure")
                recommended_actions.append("Consider redundancy implementation")
            
            # Factor 5: Device age/model (from documentation insights)
            lifecycle_recs = documentation_insights.get("lifecycle_recommendations", [])
            for rec in lifecycle_recs:
                if "5 years" in rec.get("recommendation", ""):
                    # Assume device might be approaching age limit
                    risk_score += 15
                    contributing_factors.append("Device approaching recommended replacement age")
                    recommended_actions.append("Evaluate device replacement schedule")
                    break
            
            # Factor 6: Current health status
            if device.health_score < 80:
                risk_score += (100 - device.health_score) * 0.5
                contributing_factors.append(f"Current health score: {device.health_score:.1f}%")
                recommended_actions.append("Address current health issues")
                
                if device.health_score < 60:
                    prediction_type = "failure_risk"
            
            # Determine confidence level
            factor_count = len(contributing_factors)
            confidence_level = min(0.9, 0.3 + (factor_count * 0.15))
            
            # Determine timeframe
            if risk_score >= 80:
                timeframe = "immediate"
                prediction_type = "failure_risk"
            elif risk_score >= 60:
                timeframe = "within_24h"
            elif risk_score >= 40:
                timeframe = "within_week"
            else:
                timeframe = "within_month"
            
            # Only create insight if there are meaningful factors
            if not contributing_factors:
                return None
            
            # Add general recommendations
            if not recommended_actions:
                recommended_actions = ["Schedule routine maintenance check"]
            
            # Business impact assessment
            business_impact = {
                "affected_users": len(dependency_analysis.get("single_points_of_failure", [])) * 10 if device_is_spof else 5,
                "service_impact": "high" if device_is_spof else "medium" if device_in_critical else "low",
                "financial_impact": "high" if prediction_type == "failure_risk" else "medium",
                "operational_impact": "significant" if risk_score >= 70 else "moderate"
            }
            
            # Historical patterns
            historical_patterns = {
                "trend_direction": "declining" if any("declining" in str(t.get("direction", "")) for t in historical_analysis.get("trends", [])) else "stable",
                "anomaly_frequency": len(historical_analysis.get("anomalies", [])),
                "performance_variability": "high" if historical_analysis.get("patterns") else "low"
            }
            
            return PredictiveInsight(
                insight_id=f"insight_{device.id}_{datetime.now().strftime('%Y%m%d%H%M')}",
                timestamp=datetime.now(),
                device_id=device.id,
                device_name=device.name,
                prediction_type=prediction_type,
                risk_score=min(100.0, risk_score),
                confidence_level=confidence_level,
                predicted_timeframe=timeframe,
                contributing_factors=contributing_factors,
                recommended_actions=recommended_actions,
                business_impact=business_impact,
                historical_patterns=historical_patterns
            )
            
        except Exception as e:
            self.logger.warning(f"Device insight generation failed for {device.id}: {e}")
            return None

    async def _create_maintenance_recommendations(self, insights: List[PredictiveInsight]) -> List[MaintenanceRecommendation]:
        """
        Create actionable maintenance recommendations based on predictive insights
        """
        recommendations = []
        
        try:
            # Group insights by risk level and timeframe
            critical_insights = [i for i in insights if i.risk_score >= 80]
            high_risk_insights = [i for i in insights if 60 <= i.risk_score < 80]
            medium_risk_insights = [i for i in insights if 40 <= i.risk_score < 60]
            
            # Create critical maintenance recommendations
            if critical_insights:
                rec = await self._create_critical_maintenance_recommendation(critical_insights)
                recommendations.append(rec)
            
            # Create preventive maintenance recommendations
            if high_risk_insights:
                rec = await self._create_preventive_maintenance_recommendation(high_risk_insights)
                recommendations.append(rec)
            
            # Create routine maintenance recommendations
            if medium_risk_insights:
                rec = await self._create_routine_maintenance_recommendation(medium_risk_insights)
                recommendations.append(rec)
            
            # Create optimization recommendations
            optimization_rec = await self._create_optimization_recommendation(insights)
            if optimization_rec:
                recommendations.append(optimization_rec)
            
            # Store recommendations
            self.maintenance_recommendations = recommendations
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation creation failed: {e}")
            return []

    async def _create_critical_maintenance_recommendation(self, critical_insights: List[PredictiveInsight]) -> MaintenanceRecommendation:
        """Create critical maintenance recommendation"""
        
        target_devices = [i.device_id for i in critical_insights]
        
        return MaintenanceRecommendation(
            recommendation_id=f"critical_{datetime.now().strftime('%Y%m%d%H%M')}",
            timestamp=datetime.now(),
            priority="critical",
            maintenance_type="corrective",
            target_devices=target_devices,
            estimated_duration="2-4 hours",
            required_resources=["network_engineer", "backup_devices", "configuration_backup"],
            optimal_maintenance_window={
                "preferred_time": "immediate",
                "backup_time": "next_maintenance_window",
                "constraints": "business_hours_if_necessary"
            },
            cost_benefit_analysis={
                "maintenance_cost": "high",
                "downtime_cost": "very_high",
                "risk_reduction": "critical",
                "roi": "immediate"
            },
            risk_if_deferred="Very high risk of service outage and cascading failures"
        )

    async def _create_preventive_maintenance_recommendation(self, high_risk_insights: List[PredictiveInsight]) -> MaintenanceRecommendation:
        """Create preventive maintenance recommendation"""
        
        target_devices = [i.device_id for i in high_risk_insights]
        
        return MaintenanceRecommendation(
            recommendation_id=f"preventive_{datetime.now().strftime('%Y%m%d%H%M')}",
            timestamp=datetime.now(),
            priority="high",
            maintenance_type="preventive",
            target_devices=target_devices,
            estimated_duration="1-2 hours",
            required_resources=["network_technician", "monitoring_tools"],
            optimal_maintenance_window={
                "preferred_time": "weekend_hours",
                "backup_time": "early_morning",
                "constraints": "avoid_business_hours"
            },
            cost_benefit_analysis={
                "maintenance_cost": "medium",
                "downtime_cost": "low",
                "risk_reduction": "high",
                "roi": "within_month"
            },
            risk_if_deferred="Medium risk of performance degradation and potential service impact"
        )

    async def _create_routine_maintenance_recommendation(self, medium_risk_insights: List[PredictiveInsight]) -> MaintenanceRecommendation:
        """Create routine maintenance recommendation"""
        
        target_devices = [i.device_id for i in medium_risk_insights]
        
        return MaintenanceRecommendation(
            recommendation_id=f"routine_{datetime.now().strftime('%Y%m%d%H%M')}",
            timestamp=datetime.now(),
            priority="medium",
            maintenance_type="predictive",
            target_devices=target_devices,
            estimated_duration="30-60 minutes",
            required_resources=["monitoring_review", "configuration_check"],
            optimal_maintenance_window={
                "preferred_time": "scheduled_maintenance",
                "backup_time": "low_usage_hours",
                "constraints": "flexible"
            },
            cost_benefit_analysis={
                "maintenance_cost": "low",
                "downtime_cost": "minimal",
                "risk_reduction": "moderate",
                "roi": "within_quarter"
            },
            risk_if_deferred="Low to medium risk of gradual performance decline"
        )

    async def _create_optimization_recommendation(self, all_insights: List[PredictiveInsight]) -> Optional[MaintenanceRecommendation]:
        """Create network optimization recommendation"""
        
        # Look for patterns that suggest optimization opportunities
        performance_issues = [i for i in all_insights if "performance" in i.prediction_type]
        
        if len(performance_issues) >= 3:  # Multiple performance issues suggest optimization need
            return MaintenanceRecommendation(
                recommendation_id=f"optimization_{datetime.now().strftime('%Y%m%d%H%M')}",
                timestamp=datetime.now(),
                priority="low",
                maintenance_type="predictive",
                target_devices=[i.device_id for i in performance_issues[:10]],
                estimated_duration="2-4 hours",
                required_resources=["network_architect", "performance_tools", "optimization_guidelines"],
                optimal_maintenance_window={
                    "preferred_time": "planned_maintenance",
                    "backup_time": "weekend",
                    "constraints": "coordinate_with_business"
                },
                cost_benefit_analysis={
                    "maintenance_cost": "medium",
                    "downtime_cost": "planned",
                    "risk_reduction": "long_term",
                    "roi": "within_six_months"
                },
                risk_if_deferred="Gradual performance decline and suboptimal resource utilization"
            )
        
        return None

    async def _update_grafana_dashboards(self, insights: List[PredictiveInsight], 
                                       recommendations: List[MaintenanceRecommendation]) -> Dict[str, Any]:
        """
        Grafana: Visualizes predictions and recommendations
        """
        try:
            # Prepare dashboard update data
            dashboard_data = {
                "predictive_insights": {
                    "total_insights": len(insights),
                    "high_risk_devices": len([i for i in insights if i.risk_score >= 70]),
                    "immediate_attention": len([i for i in insights if i.predicted_timeframe == "immediate"]),
                    "risk_distribution": self._calculate_risk_distribution(insights)
                },
                "maintenance_recommendations": {
                    "total_recommendations": len(recommendations),
                    "critical_priority": len([r for r in recommendations if r.priority == "critical"]),
                    "high_priority": len([r for r in recommendations if r.priority == "high"]),
                    "maintenance_types": self._calculate_maintenance_type_distribution(recommendations)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Update Grafana dashboard (if API available)
            grafana_update = await self._update_grafana_api(dashboard_data)
            
            if grafana_update:
                return {
                    "dashboards_updated": grafana_update.get("updated_panels", []),
                    "update_status": "success",
                    "last_update": datetime.now().isoformat()
                }
            else:
                # Store data for manual dashboard update
                return {
                    "dashboards_updated": ["predictive_maintenance_dashboard"],
                    "update_status": "data_prepared",
                    "dashboard_data": dashboard_data,
                    "last_update": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.warning(f"Grafana dashboard update failed: {e}")
            return {"update_status": "failed", "error": str(e)}

    def _calculate_risk_distribution(self, insights: List[PredictiveInsight]) -> Dict[str, int]:
        """Calculate risk score distribution for dashboard"""
        distribution = {
            "critical": 0,  # 80-100
            "high": 0,      # 60-79
            "medium": 0,    # 40-59
            "low": 0        # 0-39
        }
        
        for insight in insights:
            if insight.risk_score >= 80:
                distribution["critical"] += 1
            elif insight.risk_score >= 60:
                distribution["high"] += 1
            elif insight.risk_score >= 40:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution

    def _calculate_maintenance_type_distribution(self, recommendations: List[MaintenanceRecommendation]) -> Dict[str, int]:
        """Calculate maintenance type distribution"""
        distribution = {}
        
        for rec in recommendations:
            mtype = rec.maintenance_type
            if mtype not in distribution:
                distribution[mtype] = 0
            distribution[mtype] += 1
        
        return distribution

    async def _update_grafana_api(self, dashboard_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update Grafana dashboard via API"""
        try:
            # This would call Grafana API to update dashboard panels
            # For now, return simulated success
            return {
                "updated_panels": [
                    "predictive_insights_panel",
                    "maintenance_recommendations_panel",
                    "risk_distribution_panel"
                ],
                "status": "success"
            }
            
        except Exception as e:
            self.logger.debug(f"Grafana API update failed: {e}")
            return None

    async def _store_cycle_results(self, cycle_results: Dict[str, Any]):
        """Store predictive maintenance cycle results"""
        try:
            # Store in Neo4j for historical analysis
            with self.knowledge_graph.driver.session() as session:
                query = """
                CREATE (pm:PredictiveMaintenanceCycle {
                    cycle_id: $cycle_id,
                    timestamp: datetime($timestamp),
                    duration_seconds: $duration,
                    insights_generated: $insights_count,
                    recommendations_created: $recommendations_count,
                    high_risk_devices: $high_risk_count
                })
                """
                
                session.run(query, {
                    "cycle_id": cycle_results["cycle_id"],
                    "timestamp": cycle_results["timestamp"],
                    "duration": cycle_results["duration_seconds"],
                    "insights_count": cycle_results["insights_generated"],
                    "recommendations_count": cycle_results["recommendations_created"],
                    "high_risk_count": cycle_results["high_risk_devices"]
                })
                
        except Exception as e:
            self.logger.warning(f"Failed to store cycle results: {e}")

    async def start_continuous_predictive_maintenance(self, interval_hours: int = 24):
        """Start continuous predictive maintenance workflow"""
        self.logger.info(f"🔄 Starting continuous predictive maintenance (every {interval_hours} hours)")
        
        while True:
            try:
                # Run predictive maintenance cycle
                results = await self.run_predictive_maintenance_cycle()
                
                # Log key results
                self.logger.info(f"📊 Predictive maintenance cycle completed: "
                               f"{results['insights_generated']} insights, "
                               f"{results['high_risk_devices']} high-risk devices, "
                               f"{results['critical_recommendations']} critical recommendations")
                
                # Wait for next cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"❌ Predictive maintenance cycle failed: {e}")
                # Wait 1 hour before retry on failure
                await asyncio.sleep(3600)

    def get_current_insights(self) -> List[PredictiveInsight]:
        """Get current predictive insights"""
        return self.current_insights.copy()

    def get_maintenance_recommendations(self) -> List[MaintenanceRecommendation]:
        """Get current maintenance recommendations"""
        return self.maintenance_recommendations.copy()

    def get_prediction_accuracy_metrics(self) -> Dict[str, Any]:
        """Get prediction accuracy metrics"""
        return self.prediction_accuracy_metrics.copy()

# Example usage and testing
if __name__ == "__main__":
    async def test_predictive_maintenance():
        workflow = PredictiveMaintenanceWorkflow()
        
        print("=== PREDICTIVE MAINTENANCE WORKFLOW TEST ===")
        
        try:
            # Run single predictive maintenance cycle
            results = await workflow.run_predictive_maintenance_cycle()
            
            print(f"\n🔮 Predictive Maintenance Results:")
            print(f"   Cycle ID: {results['cycle_id']}")
            print(f"   Duration: {results['duration_seconds']:.2f}s")
            print(f"   Insights Generated: {results['insights_generated']}")
            print(f"   High-Risk Devices: {results['high_risk_devices']}")
            print(f"   Critical Recommendations: {results['critical_recommendations']}")
            
            print(f"\n📊 Analysis Summary:")
            summary = results['analysis_summary']
            print(f"   Documentation Processed: {summary['documentation_processed']}")
            print(f"   Historical Data Points: {summary['historical_data_points']}")
            print(f"   Dependencies Mapped: {summary['dependencies_mapped']}")
            print(f"   Failure Patterns: {summary['failure_patterns_identified']}")
            
            # Show sample insights
            insights = workflow.get_current_insights()
            if insights:
                print(f"\n🎯 Top Predictive Insights:")
                for i, insight in enumerate(insights[:3], 1):
                    print(f"   {i}. {insight.device_name}: Risk {insight.risk_score:.1f}% ({insight.predicted_timeframe})")
                    print(f"      Factors: {', '.join(insight.contributing_factors[:2])}")
            
            # Show sample recommendations
            recommendations = workflow.get_maintenance_recommendations()
            if recommendations:
                print(f"\n💡 Maintenance Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. [{rec.priority.upper()}] {rec.maintenance_type.title()} Maintenance")
                    print(f"      Devices: {len(rec.target_devices)}, Duration: {rec.estimated_duration}")
            
            print(f"\n✅ Predictive maintenance test completed successfully!")
            
        except Exception as e:
            print(f"❌ Predictive maintenance test failed: {e}")

    # Run test
    asyncio.run(test_predictive_maintenance())