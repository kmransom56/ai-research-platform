#!/usr/bin/env python3
"""
Predictive Maintenance with GenAI Stack
Advanced AI system for predicting network and restaurant equipment failures

Architecture:
Device Metrics → GenAI Stack Analysis → Risk Assessment → Maintenance Scheduling
├── Neo4j Graph Analysis → Pattern Recognition  
├── Historical Trend Analysis → Failure Prediction
├── Restaurant Business Impact → Priority Scoring
└── Automated Maintenance Tickets → Proactive Resolution
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from neo4j import GraphDatabase
import requests
import logging
import random
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DeviceMetrics:
    """Device performance and health metrics"""
    device_serial: str
    device_type: str
    organization_name: str
    network_name: str
    
    # Performance metrics
    cpu_utilization: float
    memory_utilization: float  
    interface_utilization: float
    temperature: float
    uptime_hours: float
    
    # Health indicators
    health_score: float
    error_rate: float
    packet_loss: float
    latency_ms: float
    
    # Business context
    business_criticality: str  # 'critical', 'high', 'medium', 'low'
    restaurant_function: str   # 'pos', 'kitchen', 'customer_facing', 'infrastructure'
    last_maintenance: Optional[datetime]
    
    timestamp: datetime

@dataclass
class MaintenancePrediction:
    """Predictive maintenance recommendation"""
    device_serial: str
    device_type: str
    organization_name: str
    predicted_failure_date: datetime
    confidence_score: float
    risk_level: str  # 'critical', 'high', 'medium', 'low'
    failure_indicators: List[str]
    recommended_actions: List[str]
    business_impact: str
    estimated_downtime_hours: float
    maintenance_window: str
    cost_estimate: float

class DeviceMetricsCollector:
    """Collect device metrics from various sources"""
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        
    async def collect_device_metrics(self, organization_filter: str = None) -> List[DeviceMetrics]:
        """Collect current metrics for all devices"""
        logger.info("📊 Collecting device metrics for predictive analysis...")
        
        devices = await self.get_devices_from_neo4j(organization_filter)
        metrics = []
        
        for device in devices:
            try:
                device_metrics = await self.simulate_device_metrics(device)
                metrics.append(device_metrics)
            except Exception as e:
                logger.error(f"Failed to collect metrics for {device['serial']}: {e}")
                continue
        
        logger.info(f"✅ Collected metrics for {len(metrics)} devices")
        return metrics
    
    async def get_devices_from_neo4j(self, organization_filter: str = None) -> List[Dict[str, Any]]:
        """Get device list from Neo4j"""
        with self.driver.session() as session:
            query = """
                MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)-[:CONTAINS]->(d:Device)
                WHERE ($org_filter IS NULL OR o.name = $org_filter)
                RETURN d.serial as serial, d.model as model, d.product_type as product_type,
                       o.name as organization_name, n.name as network_name,
                       d.health_score as current_health_score
                LIMIT 100
            """
            
            result = session.run(query, {"org_filter": organization_filter})
            return [dict(record) for record in result]
    
    async def simulate_device_metrics(self, device: Dict[str, Any]) -> DeviceMetrics:
        """Simulate realistic device metrics (would be real API calls in production)"""
        base_health = device.get("current_health_score", 95.0)
        
        # Simulate metrics with some correlation to health score
        health_factor = base_health / 100.0
        
        # Simulate restaurant business context
        device_type = device.get("product_type", "").lower()
        restaurant_function = self.determine_restaurant_function(device_type)
        business_criticality = self.determine_business_criticality(restaurant_function)
        
        return DeviceMetrics(
            device_serial=device["serial"],
            device_type=device.get("model", "Unknown"),
            organization_name=device["organization_name"],
            network_name=device["network_name"],
            
            # Performance metrics (correlated with health)
            cpu_utilization=random.uniform(10, 90) * (2 - health_factor),
            memory_utilization=random.uniform(20, 80) * (2 - health_factor),
            interface_utilization=random.uniform(5, 95) * (1.5 - health_factor/2),
            temperature=random.uniform(25, 75) + (10 * (1 - health_factor)),
            uptime_hours=random.uniform(24, 8760),  # 1 day to 1 year
            
            # Health indicators
            health_score=base_health,
            error_rate=random.uniform(0, 5) * (2 - health_factor),
            packet_loss=random.uniform(0, 2) * (2 - health_factor),
            latency_ms=random.uniform(1, 100) * (2 - health_factor),
            
            # Business context
            business_criticality=business_criticality,
            restaurant_function=restaurant_function,
            last_maintenance=datetime.now() - timedelta(days=random.randint(30, 365)),
            
            timestamp=datetime.now()
        )
    
    def determine_restaurant_function(self, device_type: str) -> str:
        """Determine restaurant function based on device type"""
        if "mx" in device_type.lower() or "appliance" in device_type.lower():
            return "infrastructure"
        elif "ms" in device_type.lower() and "switch" in device_type.lower():
            return "pos"  # Switches often serve POS systems
        elif "mr" in device_type.lower() or "wireless" in device_type.lower():
            return "customer_facing"  # WiFi for customers
        elif "mc" in device_type.lower() or "camera" in device_type.lower():
            return "kitchen"  # Kitchen surveillance
        else:
            return "infrastructure"
    
    def determine_business_criticality(self, restaurant_function: str) -> str:
        """Determine business criticality based on restaurant function"""
        criticality_map = {
            "pos": "critical",           # POS systems are critical
            "kitchen": "high",           # Kitchen equipment is high priority  
            "customer_facing": "medium", # Customer WiFi is medium
            "infrastructure": "high"     # Infrastructure is generally high
        }
        return criticality_map.get(restaurant_function, "medium")

class GenAIStackAnalyzer:
    """GenAI Stack integration for advanced predictive analysis"""
    
    def __init__(self):
        self.genai_api_url = "http://localhost:8504"  # GenAI Stack API
        self.analysis_models = {
            "failure_prediction": "restaurant_failure_model",
            "pattern_recognition": "network_pattern_model", 
            "business_impact": "restaurant_impact_model"
        }
    
    async def analyze_failure_patterns(self, metrics: List[DeviceMetrics]) -> Dict[str, Any]:
        """Use GenAI Stack to analyze failure patterns"""
        logger.info("🤖 GenAI Stack: Analyzing failure patterns...")
        
        # Prepare data for GenAI analysis
        analysis_data = self.prepare_metrics_for_analysis(metrics)
        
        try:
            # In production, this would call the actual GenAI Stack API
            analysis_results = await self.simulate_genai_analysis(analysis_data)
            
            logger.info("✅ GenAI Stack: Pattern analysis complete")
            return analysis_results
            
        except Exception as e:
            logger.error(f"GenAI Stack analysis failed: {e}")
            # Fallback to rule-based analysis
            return await self.fallback_rule_based_analysis(metrics)
    
    def prepare_metrics_for_analysis(self, metrics: List[DeviceMetrics]) -> Dict[str, Any]:
        """Prepare metrics data for GenAI Stack analysis"""
        return {
            "device_count": len(metrics),
            "organizations": list(set(m.organization_name for m in metrics)),
            "device_types": list(set(m.device_type for m in metrics)),
            "avg_health_score": np.mean([m.health_score for m in metrics]),
            "metrics_summary": {
                "cpu_utilization": {
                    "avg": np.mean([m.cpu_utilization for m in metrics]),
                    "max": np.max([m.cpu_utilization for m in metrics]),
                    "std": np.std([m.cpu_utilization for m in metrics])
                },
                "temperature": {
                    "avg": np.mean([m.temperature for m in metrics]),
                    "max": np.max([m.temperature for m in metrics]),
                    "std": np.std([m.temperature for m in metrics])
                },
                "error_rate": {
                    "avg": np.mean([m.error_rate for m in metrics]),
                    "max": np.max([m.error_rate for m in metrics]),
                    "std": np.std([m.error_rate for m in metrics])
                }
            },
            "business_context": {
                "critical_devices": len([m for m in metrics if m.business_criticality == "critical"]),
                "pos_devices": len([m for m in metrics if m.restaurant_function == "pos"]),
                "kitchen_devices": len([m for m in metrics if m.restaurant_function == "kitchen"])
            }
        }
    
    async def simulate_genai_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate GenAI Stack analysis (would be real API call in production)"""
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Simulate intelligent analysis results
        return {
            "failure_risk_patterns": [
                {
                    "pattern": "high_temperature_correlation",
                    "description": "Devices with temperature > 60°C show 3x higher failure rate",
                    "confidence": 0.87,
                    "affected_devices": analysis_data["business_context"]["critical_devices"]
                },
                {
                    "pattern": "cpu_memory_combined_stress", 
                    "description": "CPU > 70% AND Memory > 60% indicates imminent failure",
                    "confidence": 0.92,
                    "affected_devices": random.randint(1, 10)
                },
                {
                    "pattern": "restaurant_pos_failure_cascade",
                    "description": "POS system failures often cascade to kitchen displays",
                    "confidence": 0.78,
                    "affected_devices": analysis_data["business_context"]["pos_devices"]
                }
            ],
            "predictive_insights": {
                "devices_at_risk": random.randint(5, 25),
                "predicted_failures_7d": random.randint(2, 8),
                "predicted_failures_30d": random.randint(8, 30),
                "business_impact_estimate": "$" + str(random.randint(1000, 25000)),
                "maintenance_urgency": "high" if analysis_data["avg_health_score"] < 85 else "medium"
            },
            "recommendations": [
                "Schedule proactive maintenance for devices with temperature > 60°C",
                "Implement redundancy for critical POS infrastructure", 
                "Upgrade firmware on devices showing memory pressure",
                "Plan maintenance windows during low-business hours (2-6 AM)"
            ]
        }
    
    async def fallback_rule_based_analysis(self, metrics: List[DeviceMetrics]) -> Dict[str, Any]:
        """Fallback rule-based analysis when GenAI Stack is unavailable"""
        logger.info("📊 Using rule-based analysis fallback...")
        
        high_risk_devices = []
        for metric in metrics:
            risk_score = 0
            if metric.temperature > 60: risk_score += 30
            if metric.cpu_utilization > 80: risk_score += 25
            if metric.error_rate > 2: risk_score += 20
            if metric.health_score < 80: risk_score += 25
            
            if risk_score > 50:
                high_risk_devices.append(metric.device_serial)
        
        return {
            "failure_risk_patterns": [
                {
                    "pattern": "rule_based_high_risk",
                    "description": f"Rule-based analysis identified {len(high_risk_devices)} high-risk devices",
                    "confidence": 0.75,
                    "affected_devices": len(high_risk_devices)
                }
            ],
            "predictive_insights": {
                "devices_at_risk": len(high_risk_devices),
                "predicted_failures_7d": max(1, len(high_risk_devices) // 4),
                "predicted_failures_30d": len(high_risk_devices),
                "business_impact_estimate": "$" + str(len(high_risk_devices) * 500),
                "maintenance_urgency": "high" if len(high_risk_devices) > 10 else "medium"
            },
            "recommendations": [
                "Review devices with multiple risk factors",
                "Plan proactive maintenance for high-risk devices",
                "Monitor temperature and utilization closely"
            ]
        }

class PredictiveMaintenanceEngine:
    """Main predictive maintenance engine"""
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        self.metrics_collector = DeviceMetricsCollector(neo4j_driver)
        self.genai_analyzer = GenAIStackAnalyzer()
    
    async def generate_maintenance_predictions(self, organization_filter: str = None) -> List[MaintenancePrediction]:
        """Generate predictive maintenance recommendations"""
        logger.info("🔮 PREDICTIVE MAINTENANCE ENGINE")
        logger.info("=" * 60)
        
        # Step 1: Collect device metrics
        metrics = await self.metrics_collector.collect_device_metrics(organization_filter)
        
        if not metrics:
            logger.warning("No device metrics available for analysis")
            return []
        
        # Step 2: GenAI Stack analysis
        genai_analysis = await self.genai_analyzer.analyze_failure_patterns(metrics)
        
        # Step 3: Generate predictions
        predictions = await self.create_maintenance_predictions(metrics, genai_analysis)
        
        # Step 4: Save predictions to Neo4j
        await self.save_predictions_to_neo4j(predictions)
        
        logger.info(f"✅ Generated {len(predictions)} maintenance predictions")
        return predictions
    
    async def create_maintenance_predictions(self, metrics: List[DeviceMetrics], 
                                           genai_analysis: Dict[str, Any]) -> List[MaintenancePrediction]:
        """Create maintenance predictions based on analysis"""
        predictions = []
        
        high_risk_threshold = 80  # Health score threshold for high risk
        insights = genai_analysis.get("predictive_insights", {})
        
        for metric in metrics:
            risk_factors = self.calculate_risk_factors(metric)
            risk_level = self.determine_risk_level(risk_factors)
            
            if risk_level in ["high", "critical"]:
                prediction = MaintenancePrediction(
                    device_serial=metric.device_serial,
                    device_type=metric.device_type,
                    organization_name=metric.organization_name,
                    predicted_failure_date=self.predict_failure_date(metric, risk_factors),
                    confidence_score=self.calculate_confidence_score(risk_factors),
                    risk_level=risk_level,
                    failure_indicators=self.identify_failure_indicators(metric, risk_factors),
                    recommended_actions=self.generate_maintenance_actions(metric, risk_factors),
                    business_impact=self.assess_business_impact(metric),
                    estimated_downtime_hours=self.estimate_downtime(metric),
                    maintenance_window=self.suggest_maintenance_window(metric),
                    cost_estimate=self.estimate_maintenance_cost(metric, risk_factors)
                )
                predictions.append(prediction)
        
        # Sort by risk level and predicted failure date
        predictions.sort(key=lambda p: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[p.risk_level],
            p.predicted_failure_date
        ))
        
        return predictions
    
    def calculate_risk_factors(self, metric: DeviceMetrics) -> Dict[str, float]:
        """Calculate various risk factors for a device"""
        risk_factors = {}
        
        # Health score risk (0-100, higher is worse)
        risk_factors["health_risk"] = max(0, 100 - metric.health_score)
        
        # Temperature risk
        if metric.temperature > 70:
            risk_factors["temperature_risk"] = 90
        elif metric.temperature > 60:
            risk_factors["temperature_risk"] = 60
        else:
            risk_factors["temperature_risk"] = 0
        
        # CPU utilization risk  
        if metric.cpu_utilization > 90:
            risk_factors["cpu_risk"] = 80
        elif metric.cpu_utilization > 70:
            risk_factors["cpu_risk"] = 50
        else:
            risk_factors["cpu_risk"] = 0
        
        # Error rate risk
        risk_factors["error_risk"] = min(100, metric.error_rate * 20)
        
        # Maintenance overdue risk
        if metric.last_maintenance:
            days_since_maintenance = (datetime.now() - metric.last_maintenance).days
            if days_since_maintenance > 365:
                risk_factors["maintenance_risk"] = 70
            elif days_since_maintenance > 180:
                risk_factors["maintenance_risk"] = 40
            else:
                risk_factors["maintenance_risk"] = 0
        else:
            risk_factors["maintenance_risk"] = 60  # No maintenance history
        
        return risk_factors
    
    def determine_risk_level(self, risk_factors: Dict[str, float]) -> str:
        """Determine overall risk level"""
        max_risk = max(risk_factors.values()) if risk_factors else 0
        avg_risk = sum(risk_factors.values()) / len(risk_factors) if risk_factors else 0
        
        if max_risk >= 90 or avg_risk >= 70:
            return "critical"
        elif max_risk >= 70 or avg_risk >= 50:
            return "high"
        elif max_risk >= 40 or avg_risk >= 30:
            return "medium"
        else:
            return "low"
    
    def predict_failure_date(self, metric: DeviceMetrics, risk_factors: Dict[str, float]) -> datetime:
        """Predict when device might fail"""
        base_days = 90  # Default 90 days
        max_risk = max(risk_factors.values()) if risk_factors else 0
        
        # Higher risk = sooner failure
        if max_risk >= 90:
            days_to_failure = random.randint(1, 14)  # 1-14 days
        elif max_risk >= 70:
            days_to_failure = random.randint(7, 30)  # 1-4 weeks
        elif max_risk >= 40:
            days_to_failure = random.randint(30, 90)  # 1-3 months
        else:
            days_to_failure = random.randint(90, 365)  # 3-12 months
        
        return datetime.now() + timedelta(days=days_to_failure)
    
    def calculate_confidence_score(self, risk_factors: Dict[str, float]) -> float:
        """Calculate confidence in the prediction"""
        if not risk_factors:
            return 0.5
        
        # More risk factors with high values = higher confidence
        high_risk_factors = [v for v in risk_factors.values() if v > 60]
        confidence = 0.5 + (len(high_risk_factors) * 0.15)
        
        return min(0.95, confidence)
    
    def identify_failure_indicators(self, metric: DeviceMetrics, risk_factors: Dict[str, float]) -> List[str]:
        """Identify specific failure indicators"""
        indicators = []
        
        if risk_factors.get("health_risk", 0) > 50:
            indicators.append(f"Low health score: {metric.health_score:.1f}%")
        
        if risk_factors.get("temperature_risk", 0) > 50:
            indicators.append(f"High temperature: {metric.temperature:.1f}°C")
        
        if risk_factors.get("cpu_risk", 0) > 50:
            indicators.append(f"High CPU utilization: {metric.cpu_utilization:.1f}%")
        
        if risk_factors.get("error_risk", 0) > 30:
            indicators.append(f"Elevated error rate: {metric.error_rate:.2f}%")
        
        if risk_factors.get("maintenance_risk", 0) > 50:
            indicators.append("Overdue for maintenance")
        
        return indicators
    
    def generate_maintenance_actions(self, metric: DeviceMetrics, risk_factors: Dict[str, float]) -> List[str]:
        """Generate recommended maintenance actions"""
        actions = []
        
        if risk_factors.get("temperature_risk", 0) > 50:
            actions.append("Clean device ventilation and check cooling systems")
        
        if risk_factors.get("cpu_risk", 0) > 50:
            actions.append("Review device configuration and optimize performance")
        
        if risk_factors.get("maintenance_risk", 0) > 50:
            actions.append("Schedule preventive maintenance inspection")
        
        if risk_factors.get("error_risk", 0) > 30:
            actions.append("Investigate and resolve recurring errors")
        
        if metric.business_criticality == "critical":
            actions.append("Prepare backup/replacement device for critical system")
        
        if not actions:
            actions.append("General health check and maintenance review")
        
        return actions
    
    def assess_business_impact(self, metric: DeviceMetrics) -> str:
        """Assess business impact of potential failure"""
        if metric.business_criticality == "critical":
            if metric.restaurant_function == "pos":
                return "Critical - POS system failure would stop all transactions"
            else:
                return "High - Critical infrastructure failure would impact operations"
        elif metric.business_criticality == "high":
            if metric.restaurant_function == "kitchen":
                return "High - Kitchen system failure would impact food service"
            else:
                return "Medium - Important system but operations could continue"
        else:
            return "Low - Minimal impact on restaurant operations"
    
    def estimate_downtime(self, metric: DeviceMetrics) -> float:
        """Estimate downtime in hours if device fails"""
        if metric.business_criticality == "critical":
            return random.uniform(2, 8)  # 2-8 hours for critical systems
        elif metric.business_criticality == "high":
            return random.uniform(1, 4)  # 1-4 hours for high priority
        else:
            return random.uniform(0.5, 2)  # 30 minutes to 2 hours
    
    def suggest_maintenance_window(self, metric: DeviceMetrics) -> str:
        """Suggest optimal maintenance window"""
        if metric.restaurant_function in ["pos", "kitchen"]:
            return "2:00 AM - 6:00 AM (Low business hours)"
        else:
            return "1:00 AM - 5:00 AM (Minimal customer impact)"
    
    def estimate_maintenance_cost(self, metric: DeviceMetrics, risk_factors: Dict[str, float]) -> float:
        """Estimate maintenance cost"""
        base_cost = 200  # Base maintenance cost
        
        # Add cost for complexity
        max_risk = max(risk_factors.values()) if risk_factors else 0
        if max_risk >= 80:
            base_cost *= 2  # High complexity
        elif max_risk >= 60:
            base_cost *= 1.5  # Medium complexity
        
        # Add cost for business criticality
        if metric.business_criticality == "critical":
            base_cost *= 1.5  # Higher cost for critical systems
        
        return base_cost + random.uniform(-50, 100)  # Add some variance
    
    async def save_predictions_to_neo4j(self, predictions: List[MaintenancePrediction]):
        """Save predictions to Neo4j for tracking"""
        logger.info(f"💾 Saving {len(predictions)} predictions to Neo4j...")
        
        with self.driver.session() as session:
            for pred in predictions:
                session.run("""
                    MERGE (p:MaintenancePrediction {device_serial: $device_serial, created_date: date()})
                    SET p.predicted_failure_date = datetime($predicted_failure_date),
                        p.confidence_score = $confidence_score,
                        p.risk_level = $risk_level,
                        p.business_impact = $business_impact,
                        p.estimated_downtime_hours = $estimated_downtime_hours,
                        p.cost_estimate = $cost_estimate,
                        p.failure_indicators = $failure_indicators,
                        p.recommended_actions = $recommended_actions,
                        p.maintenance_window = $maintenance_window,
                        p.organization_name = $organization_name,
                        p.created_timestamp = datetime()
                """, {
                    "device_serial": pred.device_serial,
                    "predicted_failure_date": pred.predicted_failure_date.isoformat(),
                    "confidence_score": pred.confidence_score,
                    "risk_level": pred.risk_level,
                    "business_impact": pred.business_impact,
                    "estimated_downtime_hours": pred.estimated_downtime_hours,
                    "cost_estimate": pred.cost_estimate,
                    "failure_indicators": pred.failure_indicators,
                    "recommended_actions": pred.recommended_actions,
                    "maintenance_window": pred.maintenance_window,
                    "organization_name": pred.organization_name
                })
        
        logger.info("✅ Predictions saved to Neo4j")

async def main():
    """Main function for predictive maintenance"""
    # Initialize Neo4j connection
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    
    try:
        # Initialize predictive maintenance engine
        engine = PredictiveMaintenanceEngine(driver)
        
        # Generate predictions for all organizations
        print("🔮 PREDICTIVE MAINTENANCE WITH GENAI STACK")
        print("=" * 70)
        
        predictions = await engine.generate_maintenance_predictions()
        
        if predictions:
            print(f"\n⚠️  CRITICAL MAINTENANCE PREDICTIONS:")
            critical_predictions = [p for p in predictions if p.risk_level == "critical"]
            
            for pred in critical_predictions[:5]:  # Show top 5 critical
                print(f"\n🚨 {pred.device_serial} ({pred.organization_name})")
                print(f"   Risk Level: {pred.risk_level}")
                print(f"   Predicted Failure: {pred.predicted_failure_date.strftime('%Y-%m-%d')}")
                print(f"   Confidence: {pred.confidence_score:.2f}")
                print(f"   Business Impact: {pred.business_impact}")
                print(f"   Estimated Cost: ${pred.cost_estimate:.0f}")
                print(f"   Indicators: {', '.join(pred.failure_indicators[:2])}")
            
            print(f"\n📊 PREDICTION SUMMARY:")
            risk_counts = defaultdict(int)
            for pred in predictions:
                risk_counts[pred.risk_level] += 1
            
            print(f"   Critical Risk: {risk_counts['critical']}")
            print(f"   High Risk: {risk_counts['high']}")  
            print(f"   Medium Risk: {risk_counts['medium']}")
            print(f"   Low Risk: {risk_counts['low']}")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"predictive_maintenance_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump({
                    "predictions": [asdict(p) for p in predictions],
                    "summary": {
                        "total_predictions": len(predictions),
                        "risk_distribution": dict(risk_counts),
                        "critical_devices": critical_predictions
                    },
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, default=str)
            
            print(f"\n📄 Results saved to: {results_file}")
        
        else:
            print("No maintenance predictions generated")
    
    finally:
        driver.close()

if __name__ == "__main__":
    asyncio.run(main())