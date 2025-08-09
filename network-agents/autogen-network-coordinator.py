"""
AutoGen Network Coordinator
Coordinates multiple network agents using AutoGen Studio multi-agent framework
Orchestrates NetworkDiscoveryAgent, DeviceHealthMonitoringAgent, and AlertManagementAgent
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from dataclasses import asdict

# Import our network agents
from network_discovery_agent import NetworkDiscoveryAgent
from device_health_monitoring_agent import DeviceHealthMonitoringAgent, DeviceHealthMetrics
from alert_management_agent import AlertManagementAgent, NetworkAlert, AlertSeverity

class NetworkCoordinator:
    """
    Main coordinator for multi-agent network management system
    Integrates with AutoGen Studio for collaborative AI workflows
    """
    
    def __init__(self, meraki_api_base: str = "http://localhost:11030"):
        self.meraki_api = meraki_api_base
        self.logger = logging.getLogger("NetworkCoordinator")
        
        # Initialize all network agents
        self.discovery_agent = NetworkDiscoveryAgent(meraki_api_base)
        self.health_agent = DeviceHealthMonitoringAgent(meraki_api_base)  
        self.alert_agent = AlertManagementAgent(meraki_api_base)
        
        # Coordinator state
        self.last_discovery_time = None
        self.last_health_check_time = None
        self.coordination_data = {
            "total_organizations": 0,
            "total_networks": 0,
            "total_devices": 0,
            "overall_health_score": 0.0,
            "active_alerts": 0,
            "critical_alerts": 0
        }
        
        # Setup notification handlers for alerts
        self.alert_agent.register_notification_handler(self._network_alert_handler)

    async def run_comprehensive_network_assessment(self) -> Dict[str, Any]:
        """
        Run complete network assessment using all agents
        This is the main workflow for AutoGen Studio integration
        """
        self.logger.info("🔄 Starting comprehensive network assessment")
        start_time = datetime.now()
        
        try:
            # Step 1: Network Discovery
            self.logger.info("📡 Phase 1: Network Discovery")
            discovery_results = await self.discovery_agent.discover_all_networks()
            self.last_discovery_time = datetime.now()
            
            # Step 2: Device Health Monitoring
            self.logger.info("🏥 Phase 2: Device Health Analysis")
            devices = discovery_results.get("devices", [])
            health_metrics = await self.health_agent.monitor_device_health(devices)
            self.last_health_check_time = datetime.now()
            
            # Step 3: Alert Processing
            self.logger.info("🔔 Phase 3: Alert Generation and Processing")
            new_alerts = await self.alert_agent.process_device_health_data(health_metrics)
            
            # Step 4: Generate Comprehensive Report
            self.logger.info("📊 Phase 4: Comprehensive Analysis")
            assessment_report = await self._generate_assessment_report(
                discovery_results, health_metrics, new_alerts
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            assessment_report["execution_metadata"] = {
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "agents_used": ["NetworkDiscoveryAgent", "DeviceHealthMonitoringAgent", "AlertManagementAgent"]
            }
            
            self.logger.info(f"✅ Network assessment complete in {duration:.1f} seconds")
            return assessment_report
            
        except Exception as e:
            self.logger.error(f"❌ Network assessment failed: {e}")
            raise

    async def _generate_assessment_report(self, discovery_results: Dict[str, Any], 
                                        health_metrics: List[DeviceHealthMetrics],
                                        new_alerts: List[NetworkAlert]) -> Dict[str, Any]:
        """Generate comprehensive assessment report"""
        
        # Basic statistics
        total_orgs = discovery_results["summary"]["total_organizations"]
        total_networks = discovery_results["summary"]["total_networks"]
        total_devices = discovery_results["summary"]["total_devices_discovered"]
        
        # Health analysis
        if health_metrics:
            avg_uptime = sum(m.uptime_score for m in health_metrics) / len(health_metrics)
            avg_performance = sum(m.performance_score for m in health_metrics) / len(health_metrics)
            critical_devices = [m for m in health_metrics if m.alert_level == "red"]
            warning_devices = [m for m in health_metrics if m.alert_level == "yellow"]
            healthy_devices = [m for m in health_metrics if m.alert_level == "green"]
        else:
            avg_uptime = avg_performance = 0
            critical_devices = warning_devices = healthy_devices = []
        
        # Alert analysis
        alert_summary = self.alert_agent.get_alert_summary()
        
        # Business impact assessment
        business_impact = self._calculate_business_impact(health_metrics, new_alerts)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(health_metrics, new_alerts, discovery_results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "assessment_type": "comprehensive_network_assessment",
            "network_overview": {
                "total_organizations": total_orgs,
                "total_networks": total_networks,
                "total_devices": total_devices,
                "discovery_duration": discovery_results["summary"]["discovery_duration_seconds"]
            },
            "health_summary": {
                "overall_health_score": round((avg_uptime + avg_performance) / 2, 2),
                "average_uptime_score": round(avg_uptime, 2),
                "average_performance_score": round(avg_performance, 2),
                "device_status": {
                    "healthy": len(healthy_devices),
                    "warning": len(warning_devices),
                    "critical": len(critical_devices),
                    "total": len(health_metrics)
                }
            },
            "alert_summary": {
                "new_alerts_generated": len(new_alerts),
                "total_active_alerts": alert_summary["active_alerts"]["total"],
                "critical_alerts": alert_summary["active_alerts"]["by_severity"]["critical"],
                "high_alerts": alert_summary["active_alerts"]["by_severity"]["high"]
            },
            "business_impact": business_impact,
            "top_issues": [
                {
                    "serial": device.serial,
                    "location": f"{device.organization_name} / {device.network_name}",
                    "model": device.model,
                    "issues": device.issues,
                    "uptime_score": device.uptime_score,
                    "performance_score": device.performance_score
                }
                for device in critical_devices[:10]  # Top 10 critical issues
            ],
            "recommendations": recommendations,
            "organization_breakdown": self._get_organization_breakdown(discovery_results, health_metrics),
            "trending_data": await self._get_trending_analysis()
        }

    def _calculate_business_impact(self, health_metrics: List[DeviceHealthMetrics], 
                                 alerts: List[NetworkAlert]) -> Dict[str, Any]:
        """Calculate estimated business impact"""
        
        if not health_metrics:
            return {"estimated_affected_users": 0, "estimated_revenue_impact": 0, "risk_level": "unknown"}
        
        # Estimate affected users (rough calculation)
        critical_devices = [m for m in health_metrics if m.alert_level == "red"]
        warning_devices = [m for m in health_metrics if m.alert_level == "yellow"]
        
        # Assume each critical device affects 15 users, warning devices affect 5 users
        affected_users = len(critical_devices) * 15 + len(warning_devices) * 5
        
        # Estimate revenue impact (very rough - $10/user/hour for critical, $2/user/hour for warnings)
        hourly_revenue_impact = len(critical_devices) * 15 * 10 + len(warning_devices) * 5 * 2
        
        # Risk level assessment
        total_devices = len(health_metrics)
        critical_percentage = (len(critical_devices) / total_devices * 100) if total_devices > 0 else 0
        
        if critical_percentage > 20:
            risk_level = "critical"
        elif critical_percentage > 10:
            risk_level = "high"
        elif critical_percentage > 5:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "estimated_affected_users": affected_users,
            "estimated_hourly_revenue_impact": hourly_revenue_impact,
            "risk_level": risk_level,
            "critical_device_percentage": round(critical_percentage, 1),
            "business_continuity_score": max(0, 100 - critical_percentage * 2)  # Simple scoring
        }

    def _generate_recommendations(self, health_metrics: List[DeviceHealthMetrics], 
                                alerts: List[NetworkAlert], 
                                discovery_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on assessment"""
        recommendations = []
        
        if not health_metrics:
            recommendations.append({
                "priority": "high",
                "category": "monitoring",
                "title": "No Health Data Available",
                "description": "Unable to retrieve device health metrics. Check Meraki API connectivity.",
                "action": "Verify API keys and network connectivity to Meraki Dashboard."
            })
            return recommendations
        
        critical_devices = [m for m in health_metrics if m.alert_level == "red"]
        warning_devices = [m for m in health_metrics if m.alert_level == "yellow"]
        
        # Critical device recommendations
        if critical_devices:
            recommendations.append({
                "priority": "critical",
                "category": "immediate_action",
                "title": f"Address {len(critical_devices)} Critical Device Issues",
                "description": f"Multiple devices are offline or experiencing critical issues requiring immediate attention.",
                "action": f"Investigate and restore service for devices: {', '.join([d.serial for d in critical_devices[:5]])}{'...' if len(critical_devices) > 5 else ''}"
            })
        
        # Network-wide issues
        networks_with_issues = {}
        for device in critical_devices + warning_devices:
            network = device.network_name
            if network not in networks_with_issues:
                networks_with_issues[network] = []
            networks_with_issues[network].append(device)
        
        for network, devices in networks_with_issues.items():
            if len(devices) > 3:  # Multiple devices in same network
                recommendations.append({
                    "priority": "high",
                    "category": "network_infrastructure", 
                    "title": f"Network-Wide Issues in {network}",
                    "description": f"Multiple devices ({len(devices)}) in {network} are experiencing issues, suggesting possible infrastructure problems.",
                    "action": f"Check network infrastructure, ISP connectivity, and power systems for {network}."
                })
        
        # Performance recommendations
        low_performance_devices = [m for m in health_metrics if m.performance_score < 80]
        if len(low_performance_devices) > len(health_metrics) * 0.2:  # More than 20% have performance issues
            recommendations.append({
                "priority": "medium",
                "category": "performance_optimization",
                "title": "Network Performance Optimization Needed", 
                "description": f"{len(low_performance_devices)} devices showing performance degradation across the network.",
                "action": "Review network configuration, bandwidth allocation, and consider firmware updates."
            })
        
        # Monitoring improvements
        if self.last_discovery_time and (datetime.now() - self.last_discovery_time).total_seconds() > 3600:
            recommendations.append({
                "priority": "low",
                "category": "monitoring",
                "title": "Increase Monitoring Frequency",
                "description": "Network discovery is running infrequently. Consider more frequent monitoring for better visibility.",
                "action": "Configure automated monitoring to run every 15-30 minutes during business hours."
            })
        
        return recommendations

    def _get_organization_breakdown(self, discovery_results: Dict[str, Any], 
                                   health_metrics: List[DeviceHealthMetrics]) -> List[Dict[str, Any]]:
        """Get per-organization health breakdown"""
        org_breakdown = []
        
        # Group health metrics by organization
        org_health = {}
        for device in health_metrics:
            org_name = device.organization_name
            if org_name not in org_health:
                org_health[org_name] = {"total": 0, "critical": 0, "warning": 0, "healthy": 0}
            
            org_health[org_name]["total"] += 1
            if device.alert_level == "red":
                org_health[org_name]["critical"] += 1
            elif device.alert_level == "yellow":
                org_health[org_name]["warning"] += 1
            else:
                org_health[org_name]["healthy"] += 1
        
        # Combine with discovery data
        for org_data in discovery_results.get("summary", {}).get("organizations", []):
            org_name = org_data["name"]
            health_data = org_health.get(org_name, {"total": 0, "critical": 0, "warning": 0, "healthy": 0})
            
            health_percentage = 0
            if health_data["total"] > 0:
                health_percentage = (health_data["healthy"] / health_data["total"]) * 100
            
            org_breakdown.append({
                "organization": org_name,
                "networks": org_data["networks"],
                "devices_discovered": org_data["devices_sampled"],
                "health_score": round(health_percentage, 1),
                "device_health": health_data,
                "region": org_data.get("regions", "Unknown")
            })
        
        # Sort by health score (worst first)
        org_breakdown.sort(key=lambda x: x["health_score"])
        return org_breakdown

    async def _get_trending_analysis(self) -> Dict[str, Any]:
        """Get trending analysis (placeholder for historical data)"""
        # In a real implementation, this would analyze historical data
        # For now, return basic trending structure
        return {
            "trend_period": "24_hours",
            "device_count_trend": "stable",  # "increasing", "decreasing", "stable"
            "health_score_trend": "improving",  # "improving", "declining", "stable"  
            "alert_volume_trend": "stable",
            "top_failing_models": [],  # Would be populated from historical data
            "recurring_issues": []     # Would identify patterns
        }

    async def _network_alert_handler(self, notification_data: Dict[str, Any]):
        """Custom alert handler for network coordinator"""
        alert_level = notification_data.get("severity", "unknown")
        title = notification_data.get("title", "Unknown Alert")
        
        # Log important alerts
        if alert_level in ["critical", "escalated"]:
            self.logger.warning(f"🚨 NETWORK ALERT: {title}")
        else:
            self.logger.info(f"🔔 Network Alert: {title}")
        
        # Update coordination data
        self.coordination_data["active_alerts"] = len(self.alert_agent.active_alerts)
        self.coordination_data["critical_alerts"] = len([
            a for a in self.alert_agent.active_alerts.values() 
            if a.severity == AlertSeverity.CRITICAL
        ])

    async def run_continuous_monitoring(self, assessment_interval_minutes: int = 15):
        """Run continuous network monitoring and assessment"""
        self.logger.info(f"🔄 Starting continuous network monitoring (interval: {assessment_interval_minutes} min)")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._monitoring_loop(assessment_interval_minutes)),
            asyncio.create_task(self.alert_agent.run_alert_escalation()),
            asyncio.create_task(self._coordination_status_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"❌ Continuous monitoring failed: {e}")
            raise

    async def _monitoring_loop(self, interval_minutes: int):
        """Main monitoring loop"""
        while True:
            try:
                self.logger.info("🔍 Running scheduled network assessment")
                assessment = await self.run_comprehensive_network_assessment()
                
                # Update coordination data
                self.coordination_data.update({
                    "total_organizations": assessment["network_overview"]["total_organizations"],
                    "total_networks": assessment["network_overview"]["total_networks"],  
                    "total_devices": assessment["network_overview"]["total_devices"],
                    "overall_health_score": assessment["health_summary"]["overall_health_score"]
                })
                
                # Log key metrics
                health_score = assessment["health_summary"]["overall_health_score"]
                critical_alerts = assessment["alert_summary"]["critical_alerts"]
                
                self.logger.info(f"📊 Network Health: {health_score:.1f}%, Critical Alerts: {critical_alerts}")
                
                if critical_alerts > 0:
                    self.logger.warning(f"⚠️  {critical_alerts} critical alerts require attention!")
                
                # Sleep until next assessment
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def _coordination_status_loop(self):
        """Status reporting loop"""
        while True:
            try:
                # Log coordination status every 5 minutes
                self.logger.info("📈 Network Coordinator Status", extra=self.coordination_data)
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.logger.error(f"Status reporting failed: {e}")
                await asyncio.sleep(60)

    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get current coordinator status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "last_discovery": self.last_discovery_time.isoformat() if self.last_discovery_time else None,
            "last_health_check": self.last_health_check_time.isoformat() if self.last_health_check_time else None,
            "coordination_data": self.coordination_data,
            "active_agents": {
                "discovery_agent": "active",
                "health_agent": "active", 
                "alert_agent": "active"
            }
        }

# AutoGen Studio integration function
async def autogen_network_assessment():
    """
    Main function for AutoGen Studio integration
    Call this function from AutoGen Studio workflows
    """
    coordinator = NetworkCoordinator()
    
    try:
        assessment = await coordinator.run_comprehensive_network_assessment()
        
        # Format for AutoGen Studio consumption
        return {
            "success": True,
            "assessment_data": assessment,
            "summary": {
                "total_devices": assessment["network_overview"]["total_devices"],
                "health_score": assessment["health_summary"]["overall_health_score"],
                "critical_issues": len(assessment["top_issues"]),
                "recommendations": len(assessment["recommendations"])
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Network assessment failed"
        }

# Example usage and testing
if __name__ == "__main__":
    async def main():
        coordinator = NetworkCoordinator()
        
        print("=== NETWORK COORDINATOR TEST ===")
        
        # Run single assessment
        try:
            assessment = await coordinator.run_comprehensive_network_assessment()
            
            print(f"Organizations: {assessment['network_overview']['total_organizations']}")
            print(f"Networks: {assessment['network_overview']['total_networks']}")
            print(f"Devices: {assessment['network_overview']['total_devices']}")
            print(f"Overall Health: {assessment['health_summary']['overall_health_score']:.1f}%")
            print(f"Critical Alerts: {assessment['alert_summary']['critical_alerts']}")
            print(f"New Alerts: {assessment['alert_summary']['new_alerts_generated']}")
            
            if assessment['top_issues']:
                print(f"\n🚨 TOP ISSUES:")
                for issue in assessment['top_issues'][:3]:
                    print(f"  - {issue['serial']} in {issue['location']}: {', '.join(issue['issues'])}")
            
            if assessment['recommendations']:
                print(f"\n💡 RECOMMENDATIONS:")
                for rec in assessment['recommendations'][:3]:
                    print(f"  - [{rec['priority'].upper()}] {rec['title']}")
                    
        except Exception as e:
            print(f"Assessment failed: {e}")
    
    asyncio.run(main())