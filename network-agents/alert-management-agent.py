"""
Alert Management Agent
Manages network alerts, notifications, and escalation workflows
Integrates with AutoGen Studio for intelligent alert processing
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import hashlib

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class NetworkAlert:
    """Network alert data structure"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    status: AlertStatus
    source: str  # 'device', 'network', 'organization'
    source_id: str  # serial, network_id, org_id
    source_name: str
    alert_type: str  # 'device_offline', 'performance_degraded', 'configuration_changed', etc.
    title: str
    description: str
    location: str  # network name or organization
    affected_users: int = 0
    escalation_level: int = 0
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_time: Optional[datetime] = None
    metadata: Dict[str, Any] = None

class AlertManagementAgent:
    """Agent for managing network alerts and notifications"""
    
    def __init__(self, meraki_api_base: str = "http://localhost:11030"):
        self.meraki_api = meraki_api_base
        self.logger = logging.getLogger("AlertManagement")
        self.active_alerts: Dict[str, NetworkAlert] = {}
        self.alert_history: List[NetworkAlert] = []
        self.notification_handlers: List[Callable] = []
        
        # Alert thresholds and rules
        self.alert_rules = {
            "device_offline": {
                "threshold_minutes": 5,
                "severity": AlertSeverity.HIGH,
                "auto_escalate_minutes": 30
            },
            "performance_degraded": {
                "threshold_percentage": 70,
                "severity": AlertSeverity.MEDIUM,
                "auto_escalate_minutes": 60
            },
            "multiple_devices_down": {
                "threshold_count": 3,
                "severity": AlertSeverity.CRITICAL,
                "auto_escalate_minutes": 15
            },
            "network_unreachable": {
                "threshold_percentage": 50,  # 50% of devices offline
                "severity": AlertSeverity.CRITICAL,
                "auto_escalate_minutes": 10
            }
        }

    def generate_alert_id(self, source: str, source_id: str, alert_type: str) -> str:
        """Generate unique alert ID"""
        content = f"{source}-{source_id}-{alert_type}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    async def process_device_health_data(self, health_metrics: List[Any]) -> List[NetworkAlert]:
        """Process device health data and generate alerts"""
        self.logger.info(f"🔔 Processing alerts from {len(health_metrics)} device health metrics")
        
        new_alerts = []
        
        # Track devices by location for network-level alerts
        location_status = {}
        
        for device_health in health_metrics:
            device_alerts = await self._generate_device_alerts(device_health)
            new_alerts.extend(device_alerts)
            
            # Track location status for network-level alerts
            location = device_health.network_name
            if location not in location_status:
                location_status[location] = {"total": 0, "offline": 0}
            location_status[location]["total"] += 1
            if device_health.alert_level == "red":
                location_status[location]["offline"] += 1
        
        # Generate network-level alerts
        network_alerts = await self._generate_network_alerts(location_status)
        new_alerts.extend(network_alerts)
        
        # Process and store new alerts
        for alert in new_alerts:
            await self._process_new_alert(alert)
        
        return new_alerts

    async def _generate_device_alerts(self, device_health) -> List[NetworkAlert]:
        """Generate alerts for individual device issues"""
        alerts = []
        
        if device_health.alert_level == "red":
            # Generate critical device alert
            alert_id = self.generate_alert_id("device", device_health.serial, "device_offline")
            
            # Check if this alert already exists
            if alert_id in self.active_alerts:
                # Update existing alert
                existing_alert = self.active_alerts[alert_id]
                existing_alert.timestamp = datetime.now()
                existing_alert.metadata = {
                    "uptime_score": device_health.uptime_score,
                    "performance_score": device_health.performance_score,
                    "issues": device_health.issues,
                    "last_seen": device_health.last_seen.isoformat()
                }
            else:
                # Create new alert
                alert = NetworkAlert(
                    alert_id=alert_id,
                    timestamp=datetime.now(),
                    severity=AlertSeverity.CRITICAL,
                    status=AlertStatus.ACTIVE,
                    source="device",
                    source_id=device_health.serial,
                    source_name=f"{device_health.model} ({device_health.serial})",
                    alert_type="device_offline",
                    title=f"Device Offline: {device_health.serial}",
                    description=f"Device {device_health.serial} ({device_health.model}) in {device_health.network_name} is offline. Issues: {', '.join(device_health.issues)}",
                    location=f"{device_health.organization_name} / {device_health.network_name}",
                    metadata={
                        "uptime_score": device_health.uptime_score,
                        "performance_score": device_health.performance_score,
                        "issues": device_health.issues,
                        "last_seen": device_health.last_seen.isoformat(),
                        "organization": device_health.organization_name,
                        "network": device_health.network_name
                    }
                )
                alerts.append(alert)
        
        elif device_health.alert_level == "yellow":
            # Generate warning-level alert
            alert_id = self.generate_alert_id("device", device_health.serial, "performance_degraded")
            
            if alert_id not in self.active_alerts:
                alert = NetworkAlert(
                    alert_id=alert_id,
                    timestamp=datetime.now(),
                    severity=AlertSeverity.MEDIUM,
                    status=AlertStatus.ACTIVE,
                    source="device",
                    source_id=device_health.serial,
                    source_name=f"{device_health.model} ({device_health.serial})",
                    alert_type="performance_degraded",
                    title=f"Performance Issue: {device_health.serial}",
                    description=f"Device {device_health.serial} in {device_health.network_name} has performance issues. {', '.join(device_health.issues)}",
                    location=f"{device_health.organization_name} / {device_health.network_name}",
                    metadata={
                        "uptime_score": device_health.uptime_score,
                        "performance_score": device_health.performance_score,
                        "issues": device_health.issues,
                        "organization": device_health.organization_name,
                        "network": device_health.network_name
                    }
                )
                alerts.append(alert)
        
        return alerts

    async def _generate_network_alerts(self, location_status: Dict[str, Dict[str, int]]) -> List[NetworkAlert]:
        """Generate network-level alerts based on device status aggregation"""
        alerts = []
        
        for location, status in location_status.items():
            total = status["total"]
            offline = status["offline"]
            
            if total > 0:
                offline_percentage = (offline / total) * 100
                
                # Network unreachable alert (>50% devices offline)
                if offline_percentage >= self.alert_rules["network_unreachable"]["threshold_percentage"]:
                    alert_id = self.generate_alert_id("network", location, "network_unreachable")
                    
                    if alert_id not in self.active_alerts:
                        alert = NetworkAlert(
                            alert_id=alert_id,
                            timestamp=datetime.now(),
                            severity=AlertSeverity.CRITICAL,
                            status=AlertStatus.ACTIVE,
                            source="network",
                            source_id=location,
                            source_name=location,
                            alert_type="network_unreachable",
                            title=f"Network Unreachable: {location}",
                            description=f"Network {location} has {offline}/{total} devices offline ({offline_percentage:.1f}%)",
                            location=location,
                            affected_users=offline * 10,  # Estimate 10 users per device
                            metadata={
                                "total_devices": total,
                                "offline_devices": offline,
                                "offline_percentage": offline_percentage
                            }
                        )
                        alerts.append(alert)
                
                # Multiple devices down alert (3+ devices offline but <50%)
                elif offline >= self.alert_rules["multiple_devices_down"]["threshold_count"] and offline_percentage < 50:
                    alert_id = self.generate_alert_id("network", location, "multiple_devices_down")
                    
                    if alert_id not in self.active_alerts:
                        alert = NetworkAlert(
                            alert_id=alert_id,
                            timestamp=datetime.now(),
                            severity=AlertSeverity.HIGH,
                            status=AlertStatus.ACTIVE,
                            source="network",
                            source_id=location,
                            source_name=location,
                            alert_type="multiple_devices_down",
                            title=f"Multiple Devices Down: {location}",
                            description=f"Network {location} has {offline} devices offline out of {total} total",
                            location=location,
                            affected_users=offline * 10,
                            metadata={
                                "total_devices": total,
                                "offline_devices": offline,
                                "offline_percentage": offline_percentage
                            }
                        )
                        alerts.append(alert)
        
        return alerts

    async def _process_new_alert(self, alert: NetworkAlert):
        """Process and store new alert"""
        # Store in active alerts
        self.active_alerts[alert.alert_id] = alert
        
        # Add to history
        self.alert_history.append(alert)
        
        # Send notifications
        await self._send_notifications(alert)
        
        self.logger.info(f"📢 New {alert.severity.value} alert: {alert.title}")

    async def _send_notifications(self, alert: NetworkAlert):
        """Send notifications for alert"""
        # In a real implementation, this would integrate with:
        # - Email notifications
        # - Slack/Teams webhooks  
        # - SMS for critical alerts
        # - SNMP traps
        # - PagerDuty/Opsgenie
        
        notification_data = {
            "alert_id": alert.alert_id,
            "severity": alert.severity.value,
            "title": alert.title,
            "description": alert.description,
            "location": alert.location,
            "timestamp": alert.timestamp.isoformat(),
            "source": alert.source,
            "source_id": alert.source_id
        }
        
        # Execute registered notification handlers
        for handler in self.notification_handlers:
            try:
                await handler(notification_data)
            except Exception as e:
                self.logger.error(f"Notification handler failed: {e}")

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            self.logger.info(f"✅ Alert acknowledged: {alert.title} by {acknowledged_by}")
            return True
        return False

    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_note: str = "") -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by = resolved_by
            alert.resolution_time = datetime.now()
            if resolution_note:
                if not alert.metadata:
                    alert.metadata = {}
                alert.metadata["resolution_note"] = resolution_note
            
            # Move from active to history
            del self.active_alerts[alert_id]
            
            self.logger.info(f"✅ Alert resolved: {alert.title} by {resolved_by}")
            return True
        return False

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None, source: Optional[str] = None) -> List[NetworkAlert]:
        """Get active alerts with optional filtering"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if source:
            alerts = [a for a in alerts if a.source == source]
        
        # Sort by severity and timestamp
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.HIGH: 1, AlertSeverity.MEDIUM: 2, AlertSeverity.LOW: 3}
        alerts.sort(key=lambda x: (severity_order[x.severity], x.timestamp), reverse=True)
        
        return alerts

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary dashboard"""
        active_alerts = list(self.active_alerts.values())
        
        # Count by severity
        severity_counts = {
            "critical": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            "high": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
            "medium": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
            "low": len([a for a in active_alerts if a.severity == AlertSeverity.LOW])
        }
        
        # Count by source
        source_counts = {}
        for alert in active_alerts:
            source = alert.source
            if source not in source_counts:
                source_counts[source] = 0
            source_counts[source] += 1
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_alerts = [a for a in self.alert_history if a.timestamp >= recent_cutoff]
        
        # Top affected locations
        location_impact = {}
        for alert in active_alerts:
            loc = alert.location
            if loc not in location_impact:
                location_impact[loc] = 0
            location_impact[loc] += 1
        
        top_locations = sorted(location_impact.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_alerts": {
                "total": len(active_alerts),
                "by_severity": severity_counts,
                "by_source": source_counts
            },
            "recent_activity": {
                "alerts_last_24h": len(recent_alerts),
                "resolved_last_24h": len([a for a in recent_alerts if a.status == AlertStatus.RESOLVED])
            },
            "top_affected_locations": [{"location": loc, "alert_count": count} for loc, count in top_locations],
            "critical_alerts": [
                {
                    "alert_id": a.alert_id,
                    "title": a.title,
                    "location": a.location,
                    "age_minutes": int((datetime.now() - a.timestamp).total_seconds() / 60),
                    "status": a.status.value
                }
                for a in active_alerts if a.severity == AlertSeverity.CRITICAL
            ][:10]  # Top 10 critical alerts
        }

    async def run_alert_escalation(self):
        """Background task to handle alert escalation"""
        self.logger.info("🔄 Starting alert escalation monitoring")
        
        while True:
            try:
                current_time = datetime.now()
                escalated_count = 0
                
                for alert in self.active_alerts.values():
                    # Skip already acknowledged alerts
                    if alert.status == AlertStatus.ACKNOWLEDGED:
                        continue
                    
                    # Calculate alert age
                    age_minutes = (current_time - alert.timestamp).total_seconds() / 60
                    
                    # Check escalation rules
                    rule = self.alert_rules.get(alert.alert_type, {})
                    escalation_threshold = rule.get("auto_escalate_minutes", 60)
                    
                    if age_minutes >= escalation_threshold and alert.escalation_level == 0:
                        # Escalate the alert
                        alert.escalation_level += 1
                        escalated_count += 1
                        
                        # Send escalation notification
                        escalation_notification = {
                            "alert_id": alert.alert_id,
                            "title": f"ESCALATED: {alert.title}",
                            "description": f"Alert has been active for {age_minutes:.0f} minutes without acknowledgment",
                            "severity": "escalated",
                            "original_severity": alert.severity.value,
                            "location": alert.location,
                            "age_minutes": age_minutes
                        }
                        
                        # Send to all notification handlers with escalation flag
                        for handler in self.notification_handlers:
                            try:
                                await handler(escalation_notification)
                            except Exception as e:
                                self.logger.error(f"Escalation notification failed: {e}")
                
                if escalated_count > 0:
                    self.logger.warning(f"📈 Escalated {escalated_count} alerts due to timeout")
                
                # Sleep for 5 minutes before next check
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Alert escalation cycle failed: {e}")
                await asyncio.sleep(60)

    def register_notification_handler(self, handler: Callable):
        """Register a notification handler function"""
        self.notification_handlers.append(handler)

# Example notification handlers
async def console_notification_handler(notification_data: Dict[str, Any]):
    """Simple console notification handler"""
    severity = notification_data.get("severity", "unknown")
    title = notification_data.get("title", "Unknown Alert")
    print(f"🔔 [{severity.upper()}] {title}")

async def slack_webhook_handler(webhook_url: str):
    """Slack webhook notification handler factory"""
    async def handler(notification_data: Dict[str, Any]):
        # In real implementation, would send to Slack webhook
        severity = notification_data.get("severity", "unknown")
        title = notification_data.get("title", "Unknown Alert")
        description = notification_data.get("description", "")
        
        payload = {
            "text": f"Network Alert: {title}",
            "attachments": [{
                "color": "danger" if severity in ["critical", "escalated"] else "warning",
                "fields": [
                    {"title": "Severity", "value": severity, "short": True},
                    {"title": "Location", "value": notification_data.get("location", "Unknown"), "short": True},
                    {"title": "Description", "value": description, "short": False}
                ]
            }]
        }
        
        # Would use aiohttp to POST to webhook_url
        print(f"📤 Would send to Slack: {payload}")
    
    return handler

# Example usage for AutoGen Studio integration  
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = AlertManagementAgent()
        
        # Register notification handlers
        agent.register_notification_handler(console_notification_handler)
        # agent.register_notification_handler(await slack_webhook_handler("https://hooks.slack.com/..."))
        
        # Example: Create some test alerts
        test_alert = NetworkAlert(
            alert_id="test-001",
            timestamp=datetime.now(),
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.ACTIVE,
            source="device",
            source_id="Q2XX-XXXX-XXXX",
            source_name="MR33 (Q2XX-XXXX-XXXX)",
            alert_type="device_offline",
            title="Device Offline: Q2XX-XXXX-XXXX",
            description="Device Q2XX-XXXX-XXXX in Main Office is offline for 15 minutes",
            location="Acme Corp / Main Office",
            affected_users=25
        )
        
        await agent._process_new_alert(test_alert)
        
        # Get alert summary
        summary = agent.get_alert_summary()
        
        print("=== ALERT MANAGEMENT DASHBOARD ===")
        print(f"Active Alerts: {summary['active_alerts']['total']}")
        print(f"Critical: {summary['active_alerts']['by_severity']['critical']}")
        print(f"High: {summary['active_alerts']['by_severity']['high']}")
        print(f"Medium: {summary['active_alerts']['by_severity']['medium']}")
        
        if summary['critical_alerts']:
            print(f"\n🚨 CRITICAL ALERTS:")
            for alert in summary['critical_alerts']:
                print(f"  - {alert['title']} (Age: {alert['age_minutes']} min)")
    
    asyncio.run(main())