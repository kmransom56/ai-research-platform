#!/usr/bin/env python3
"""
Automated Network Health Assessment System
Multi-agent AI system for comprehensive network analysis and reporting

Architecture:
├── Discovery Agent → Polls Meraki/Fortinet APIs
├── Performance Agent → Analyzes metrics in Qdrant  
├── Security Agent → Updates Neo4j threat graph
└── Chat Copilot → Generates summary report
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from neo4j import GraphDatabase
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    """Health assessment metric"""
    metric_name: str
    value: float
    threshold: float
    status: str  # 'healthy', 'warning', 'critical'
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    business_impact: str
    timestamp: datetime

@dataclass
class NetworkIncident:
    """Network incident data structure"""
    incident_id: str
    severity: str
    category: str
    affected_devices: List[str]
    business_impact: str
    recommended_actions: List[str]
    timestamp: datetime

class DiscoveryAgent:
    """Agent responsible for polling network APIs and collecting data"""
    
    def __init__(self, meraki_api_key: str):
        self.meraki_api_key = meraki_api_key
        self.base_url = "https://api.meraki.com/api/v1"
        self.headers = {
            'X-Cisco-Meraki-API-Key': meraki_api_key,
            'Content-Type': 'application/json'
        }
    
    async def discover_network_health(self) -> Dict[str, Any]:
        """Discover current network health across all organizations"""
        logger.info("🔍 Discovery Agent: Starting network health assessment")
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Get organizations
            async with session.get(f"{self.base_url}/organizations") as response:
                orgs = await response.json()
            
            health_data = {
                "discovery_timestamp": datetime.now().isoformat(),
                "organizations": [],
                "global_metrics": {
                    "total_devices": 0,
                    "healthy_devices": 0,
                    "warning_devices": 0,
                    "critical_devices": 0,
                    "offline_devices": 0
                }
            }
            
            for org in orgs:
                org_health = await self.assess_organization_health(session, org)
                health_data["organizations"].append(org_health)
                
                # Update global metrics
                health_data["global_metrics"]["total_devices"] += org_health.get("device_count", 0)
                health_data["global_metrics"]["healthy_devices"] += org_health.get("healthy_count", 0)
                health_data["global_metrics"]["warning_devices"] += org_health.get("warning_count", 0)
                health_data["global_metrics"]["critical_devices"] += org_health.get("critical_count", 0)
                health_data["global_metrics"]["offline_devices"] += org_health.get("offline_count", 0)
        
        logger.info(f"✅ Discovery Agent: Assessed {health_data['global_metrics']['total_devices']} devices")
        return health_data
    
    async def assess_organization_health(self, session: aiohttp.ClientSession, org: Dict) -> Dict[str, Any]:
        """Assess health for a single organization"""
        org_id = org["id"]
        org_name = org["name"]
        
        try:
            # Get organization device statuses
            async with session.get(f"{self.base_url}/organizations/{org_id}/devices/statuses") as response:
                if response.status == 200:
                    device_statuses = await response.json()
                else:
                    logger.warning(f"Failed to get device statuses for {org_name}")
                    device_statuses = []
            
            # Analyze device health
            healthy_count = sum(1 for d in device_statuses if d.get('status') == 'online')
            offline_count = sum(1 for d in device_statuses if d.get('status') == 'offline')
            warning_count = sum(1 for d in device_statuses if d.get('status') in ['alerting', 'dormant'])
            critical_count = sum(1 for d in device_statuses if self.is_critical_device(d))
            
            # Calculate health score
            total_devices = len(device_statuses)
            if total_devices > 0:
                health_score = (healthy_count / total_devices) * 100
            else:
                health_score = 0
            
            return {
                "organization_id": org_id,
                "organization_name": org_name,
                "device_count": total_devices,
                "healthy_count": healthy_count,
                "warning_count": warning_count,
                "critical_count": critical_count,
                "offline_count": offline_count,
                "health_score": health_score,
                "health_status": self.get_health_status(health_score),
                "business_impact": self.assess_business_impact(org_name, critical_count, offline_count),
                "assessment_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing {org_name}: {e}")
            return {
                "organization_id": org_id,
                "organization_name": org_name,
                "device_count": 0,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "offline_count": 0,
                "health_score": 0,
                "health_status": "unknown",
                "business_impact": "unknown",
                "error": str(e)
            }
    
    def is_critical_device(self, device: Dict) -> bool:
        """Determine if a device is in critical state"""
        return (
            device.get('status') == 'offline' and
            device.get('model', '').startswith(('MX', 'MS', 'MR')) and
            device.get('productType') in ['appliance', 'switch', 'wireless']
        )
    
    def get_health_status(self, health_score: float) -> str:
        """Convert health score to status"""
        if health_score >= 95:
            return "excellent"
        elif health_score >= 90:
            return "good"
        elif health_score >= 80:
            return "warning"
        else:
            return "critical"
    
    def assess_business_impact(self, org_name: str, critical_count: int, offline_count: int) -> str:
        """Assess business impact for restaurant organizations"""
        restaurant_orgs = ["inspire brands", "buffalo", "arby", "baskin", "dunkin"]
        
        is_restaurant = any(term in org_name.lower() for term in restaurant_orgs)
        
        if not is_restaurant:
            return "low" if (critical_count + offline_count) < 5 else "medium"
        
        # Restaurant-specific business impact
        total_issues = critical_count + offline_count
        
        if total_issues == 0:
            return "none"
        elif total_issues <= 2:
            return "low - Limited store impact"
        elif total_issues <= 10:
            return "medium - Multiple store locations affected"
        else:
            return "high - Significant restaurant operations impact"

class ChatCopilotAgent:
    """Agent for generating AI-powered summary reports"""
    
    def __init__(self):
        self.system_prompt = """
        You are an AI network operations expert specializing in restaurant chain network management.
        Generate concise, actionable network health reports that focus on business impact.
        """
    
    def generate_health_report(self, health_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive health assessment report"""
        logger.info("🤖 Chat Copilot Agent: Generating network health summary report")
        
        # Calculate summary statistics
        total_devices = health_data["global_metrics"]["total_devices"]
        healthy_devices = health_data["global_metrics"]["healthy_devices"]
        availability = (healthy_devices / total_devices * 100) if total_devices > 0 else 0
        
        # Generate executive summary
        executive_summary = self.generate_executive_summary(health_data, availability)
        
        # Generate restaurant-specific insights
        restaurant_insights = self.generate_restaurant_insights(health_data)
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "report_type": "automated_health_assessment",
            "executive_summary": executive_summary,
            "network_overview": {
                "total_devices": total_devices,
                "network_availability": round(availability, 2),
                "organizations_monitored": len(health_data["organizations"]),
                "health_status": self.get_overall_health_status(availability)
            },
            "restaurant_insights": restaurant_insights,
            "organization_details": [
                {
                    "name": org["organization_name"],
                    "device_count": org.get("device_count", 0),
                    "health_score": org.get("health_score", 0),
                    "health_status": org.get("health_status", "unknown"),
                    "business_impact": org.get("business_impact", "unknown")
                } for org in health_data["organizations"]
            ],
            "recommendations": self.generate_recommendations(health_data),
            "next_assessment": (datetime.now() + timedelta(hours=4)).isoformat()
        }
        
        logger.info("✅ Chat Copilot Agent: Generated comprehensive health report")
        return report
    
    def generate_executive_summary(self, health_data: Dict, availability: float) -> str:
        """Generate executive summary"""
        total_devices = health_data["global_metrics"]["total_devices"]
        
        if availability >= 98:
            status_desc = "excellent condition"
        elif availability >= 95:
            status_desc = "good condition with minor issues"
        elif availability >= 90:
            status_desc = "experiencing some challenges"
        else:
            status_desc = "requiring immediate attention"
        
        summary = f"""
Network Health Assessment Summary:

Your restaurant network infrastructure ({total_devices:,} devices across {len(health_data['organizations'])} organizations) 
is in {status_desc} with {availability:.1f}% availability.

Key restaurant chains monitored: {', '.join([org['organization_name'] for org in health_data['organizations'][:3]])}
        """.strip()
        
        return summary
    
    def generate_recommendations(self, health_data: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Global metrics analysis
        global_metrics = health_data["global_metrics"]
        total_devices = global_metrics["total_devices"]
        
        if total_devices > 0:
            offline_ratio = (global_metrics["offline_devices"] / total_devices) * 100
            critical_ratio = (global_metrics["critical_devices"] / total_devices) * 100
            
            if critical_ratio > 5:
                recommendations.append("URGENT: Address critical infrastructure devices affecting business operations")
            
            if offline_ratio > 2:
                recommendations.append("Investigate root cause of device outages across multiple locations")
        
        # Organization-specific recommendations
        poor_health_orgs = [
            org for org in health_data["organizations"] 
            if org.get("health_score", 0) < 85
        ]
        
        if poor_health_orgs:
            recommendations.append(
                f"Focus on {len(poor_health_orgs)} organizations with health scores below 85%"
            )
        
        # General recommendations
        recommendations.extend([
            "Schedule proactive maintenance for devices showing early warning signs",
            "Review backup and redundancy for critical restaurant locations",
            "Consider implementing automated remediation for common issues"
        ])
        
        return recommendations
    
    def generate_restaurant_insights(self, health_data: Dict) -> Dict[str, Any]:
        """Generate restaurant-specific operational insights"""
        restaurant_orgs = []
        
        for org in health_data["organizations"]:
            org_name = org["organization_name"].lower()
            if any(term in org_name for term in ["inspire", "buffalo", "arby", "baskin", "dunkin"]):
                restaurant_orgs.append(org)
        
        if not restaurant_orgs:
            return {"message": "No restaurant organizations detected"}
        
        # Calculate restaurant-specific metrics
        total_restaurant_devices = sum(org.get("device_count", 0) for org in restaurant_orgs)
        avg_restaurant_health = sum(org.get("health_score", 0) for org in restaurant_orgs) / len(restaurant_orgs)
        
        return {
            "restaurant_chains_monitored": len(restaurant_orgs),
            "total_restaurant_devices": total_restaurant_devices,
            "average_restaurant_health": round(avg_restaurant_health, 1),
            "top_performing_chain": max(restaurant_orgs, key=lambda x: x.get("health_score", 0))["organization_name"],
            "chains_needing_attention": [
                org["organization_name"] for org in restaurant_orgs 
                if org.get("health_score", 0) < 90
            ]
        }
    
    def get_overall_health_status(self, availability: float) -> str:
        """Get overall health status description"""
        if availability >= 98:
            return "Excellent"
        elif availability >= 95:
            return "Good"
        elif availability >= 90:
            return "Fair"
        else:
            return "Poor"

class AutomatedHealthAssessment:
    """Main orchestrator for automated network health assessment"""
    
    def __init__(self, meraki_api_key: str):
        self.meraki_api_key = meraki_api_key
        
        # Initialize agents
        self.discovery_agent = DiscoveryAgent(meraki_api_key)
        self.copilot_agent = ChatCopilotAgent()
    
    async def run_health_assessment(self) -> Dict[str, Any]:
        """Run complete automated health assessment"""
        logger.info("🚀 Starting Automated Network Health Assessment")
        start_time = datetime.now()
        
        try:
            # Step 1: Discovery Agent - Collect network data
            health_data = await self.discovery_agent.discover_network_health()
            
            # Step 2: Chat Copilot Agent - Generate summary report
            report = self.copilot_agent.generate_health_report(health_data)
            
            # Save assessment results
            assessment_file = self.save_assessment_report(report)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Automated Health Assessment completed in {duration:.2f} seconds")
            logger.info(f"📄 Report saved to: {assessment_file}")
            
            return {
                "status": "completed",
                "duration_seconds": duration,
                "report": report,
                "report_file": assessment_file
            }
            
        except Exception as e:
            logger.error(f"❌ Health Assessment failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def save_assessment_report(self, report: Dict[str, Any]) -> str:
        """Save assessment report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/health_assessment_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return filename
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return None

async def main():
    """Main function for running automated health assessment"""
    print("🤖 AUTOMATED NETWORK HEALTH ASSESSMENT SYSTEM")
    print("Multi-Agent AI for Enterprise Restaurant Networks")
    print("=" * 60)
    
    # Initialize system
    meraki_api_key = "fd3b9969d25792d90f0789a7e28cc661c81e2150"
    assessment_system = AutomatedHealthAssessment(meraki_api_key)
    
    # Run health assessment
    result = await assessment_system.run_health_assessment()
    
    if result["status"] == "completed":
        report = result["report"]
        
        print(f"\n📊 HEALTH ASSESSMENT COMPLETED")
        print(f"⏱️ Duration: {result['duration_seconds']:.2f} seconds")
        print(f"📄 Report: {result['report_file']}")
        print("\n" + "=" * 60)
        
        # Display key findings
        print(f"🎯 EXECUTIVE SUMMARY:")
        print(report["executive_summary"])
        
        print(f"\n📈 NETWORK OVERVIEW:")
        overview = report["network_overview"]
        print(f"   Total Devices: {overview['total_devices']:,}")
        print(f"   Availability: {overview['network_availability']}%")
        print(f"   Health Status: {overview['health_status']}")
        
        print(f"\n🍴 RESTAURANT INSIGHTS:")
        insights = report["restaurant_insights"]
        print(f"   Chains Monitored: {insights.get('restaurant_chains_monitored', 0)}")
        print(f"   Restaurant Devices: {insights.get('total_restaurant_devices', 0):,}")
        print(f"   Avg Restaurant Health: {insights.get('average_restaurant_health', 0)}%")
        
        print(f"\n💡 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"][:3], 1):
            print(f"   {i}. {rec}")
        
    else:
        print(f"❌ Assessment failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())