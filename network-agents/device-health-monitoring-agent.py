"""
Device Health Monitoring Agent
Monitors device performance, connectivity, and health metrics
Integrates with AutoGen Studio for multi-agent network management
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import asyncio

@dataclass
class DeviceHealthMetrics:
    """Device health metrics data structure"""
    serial: str
    network_name: str
    organization_name: str
    model: str
    status: str
    last_seen: datetime
    firmware_version: str
    uptime_score: float
    performance_score: float
    alert_level: str  # 'green', 'yellow', 'red'
    issues: List[str]

class DeviceHealthMonitoringAgent:
    """Agent for monitoring device health and performance"""
    
    def __init__(self, meraki_api_base: str = "http://localhost:11030"):
        self.meraki_api = meraki_api_base
        self.logger = logging.getLogger("DeviceHealthMonitoring")
        self.health_data = []
        self.alert_thresholds = {
            "offline_minutes": 10,
            "firmware_age_days": 180,
            "performance_threshold": 70.0,
            "uptime_threshold": 95.0
        }

    async def monitor_device_health(self, devices: List[Dict[str, Any]]) -> List[DeviceHealthMetrics]:
        """
        Monitor health for a list of devices
        """
        self.logger.info(f"🏥 Monitoring health for {len(devices)} devices")
        health_metrics = []
        
        for device in devices:
            try:
                # Get detailed device status
                serial = device.get('serial')
                status_response = requests.get(f"{self.meraki_api}/devices/{serial}/status")
                device_status = status_response.json() if status_response.status_code == 200 else {}
                
                # Calculate health metrics
                health_metric = await self._calculate_device_health(device, device_status)
                health_metrics.append(health_metric)
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.warning(f"Failed to get health for device {device.get('serial', 'unknown')}: {e}")
                
        self.health_data = health_metrics
        return health_metrics

    async def _calculate_device_health(self, device: Dict[str, Any], status: Dict[str, Any]) -> DeviceHealthMetrics:
        """Calculate comprehensive health metrics for a device"""
        
        # Basic device info
        serial = device.get('serial', '')
        network_name = device.get('network_name', 'Unknown')
        organization_name = device.get('organization_name', 'Unknown')
        model = device.get('model', 'Unknown')
        current_status = device.get('status', 'unknown').lower()
        
        # Parse last seen time
        last_seen_str = device.get('lastReportedAt') or device.get('last_reported_at')
        if last_seen_str:
            try:
                last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
            except:
                last_seen = datetime.now() - timedelta(hours=24)
        else:
            last_seen = datetime.now() - timedelta(hours=24)
        
        # Calculate metrics
        firmware_version = device.get('firmware', 'Unknown')
        uptime_score = self._calculate_uptime_score(current_status, last_seen)
        performance_score = self._calculate_performance_score(status)
        
        # Determine alert level and issues
        issues = []
        alert_level = "green"
        
        # Check offline status
        minutes_since_seen = (datetime.now() - last_seen.replace(tzinfo=None)).total_seconds() / 60
        if current_status == 'offline' or minutes_since_seen > self.alert_thresholds["offline_minutes"]:
            issues.append(f"Device offline for {minutes_since_seen:.0f} minutes")
            alert_level = "red"
        elif current_status == 'alerting':
            issues.append("Device is in alerting state")
            alert_level = "yellow"
        
        # Check performance
        if performance_score < self.alert_thresholds["performance_threshold"]:
            issues.append(f"Performance score low: {performance_score:.1f}%")
            if alert_level == "green":
                alert_level = "yellow"
        
        # Check uptime
        if uptime_score < self.alert_thresholds["uptime_threshold"]:
            issues.append(f"Uptime score low: {uptime_score:.1f}%")
            if alert_level == "green":
                alert_level = "yellow"
        
        # Check firmware age (simplified)
        if firmware_version == 'Unknown' or not firmware_version:
            issues.append("Firmware version unknown")
            if alert_level == "green":
                alert_level = "yellow"
        
        return DeviceHealthMetrics(
            serial=serial,
            network_name=network_name,
            organization_name=organization_name,
            model=model,
            status=current_status,
            last_seen=last_seen,
            firmware_version=firmware_version,
            uptime_score=uptime_score,
            performance_score=performance_score,
            alert_level=alert_level,
            issues=issues
        )

    def _calculate_uptime_score(self, status: str, last_seen: datetime) -> float:
        """Calculate uptime score based on status and last seen time"""
        if status.lower() == 'online':
            # Device is currently online
            minutes_since_seen = (datetime.now() - last_seen.replace(tzinfo=None)).total_seconds() / 60
            if minutes_since_seen < 5:
                return 100.0  # Recently seen and online
            elif minutes_since_seen < 30:
                return 95.0   # Online but not recently seen
            else:
                return 85.0   # Online but stale data
        elif status.lower() == 'offline':
            return 0.0        # Offline
        else:
            return 50.0       # Unknown/alerting status

    def _calculate_performance_score(self, device_status: Dict[str, Any]) -> float:
        """Calculate performance score from device status data"""
        # This is simplified - in real implementation would use actual performance metrics
        # from the device status response (CPU, memory, network utilization, etc.)
        
        if not device_status:
            return 75.0  # Default score when no status data available
        
        # Look for performance indicators in the status
        score = 85.0  # Base score
        
        # Check for any performance-related fields in the status
        if 'performance' in device_status:
            perf_data = device_status['performance']
            if isinstance(perf_data, dict) and 'score' in perf_data:
                score = float(perf_data['score'])
        
        # Check for warnings or errors that might indicate performance issues
        if 'warnings' in device_status and device_status['warnings']:
            score -= 10.0
        
        if 'errors' in device_status and device_status['errors']:
            score -= 20.0
        
        return max(0.0, min(100.0, score))

    def get_critical_devices(self) -> List[DeviceHealthMetrics]:
        """Get devices with critical health issues"""
        return [device for device in self.health_data if device.alert_level == "red"]

    def get_warning_devices(self) -> List[DeviceHealthMetrics]:
        """Get devices with warning-level issues"""
        return [device for device in self.health_data if device.alert_level == "yellow"]

    def get_healthy_devices(self) -> List[DeviceHealthMetrics]:
        """Get healthy devices"""
        return [device for device in self.health_data if device.alert_level == "green"]

    def generate_health_summary(self) -> Dict[str, Any]:
        """Generate comprehensive health summary"""
        if not self.health_data:
            return {"error": "No health data available"}
        
        total_devices = len(self.health_data)
        critical_devices = self.get_critical_devices()
        warning_devices = self.get_warning_devices()
        healthy_devices = self.get_healthy_devices()
        
        # Calculate averages
        avg_uptime = sum(d.uptime_score for d in self.health_data) / total_devices
        avg_performance = sum(d.performance_score for d in self.health_data) / total_devices
        
        # Group by organization
        orgs = {}
        for device in self.health_data:
            org_name = device.organization_name
            if org_name not in orgs:
                orgs[org_name] = {"total": 0, "critical": 0, "warning": 0, "healthy": 0}
            orgs[org_name]["total"] += 1
            orgs[org_name][device.alert_level] += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": {
                "total_devices": total_devices,
                "healthy": len(healthy_devices),
                "warning": len(warning_devices),
                "critical": len(critical_devices),
                "health_percentage": (len(healthy_devices) / total_devices * 100) if total_devices > 0 else 0
            },
            "performance_metrics": {
                "average_uptime_score": round(avg_uptime, 2),
                "average_performance_score": round(avg_performance, 2)
            },
            "critical_devices": [
                {
                    "serial": d.serial,
                    "network": d.network_name,
                    "organization": d.organization_name,
                    "model": d.model,
                    "issues": d.issues,
                    "uptime_score": d.uptime_score,
                    "performance_score": d.performance_score
                }
                for d in critical_devices[:10]  # Top 10 critical devices
            ],
            "organization_health": orgs
        }

    async def run_continuous_monitoring(self, interval_minutes: int = 5):
        """Run continuous health monitoring"""
        self.logger.info(f"🔄 Starting continuous health monitoring (interval: {interval_minutes} min)")
        
        while True:
            try:
                # Get all devices from discovery agent
                discovery_response = requests.get(f"{self.meraki_api}/ai/discovery")
                # In real implementation, this would get devices from the discovery agent
                # For now, we'll get organizations and iterate through them
                
                orgs_response = requests.get(f"{self.meraki_api}/organizations")
                organizations = orgs_response.json()
                
                all_devices = []
                for org in organizations[:3]:  # Limit for performance
                    org_id = org['id']
                    networks_response = requests.get(f"{self.meraki_api}/organizations/{org_id}/networks")
                    networks = networks_response.json()
                    
                    for network in networks[:5]:  # Limit networks per org
                        network_id = network['id']
                        devices_response = requests.get(f"{self.meraki_api}/networks/{network_id}/devices")
                        devices = devices_response.json()
                        
                        # Add organization and network info to devices
                        for device in devices:
                            device['organization_name'] = org['name']
                            device['network_name'] = network['name']
                            all_devices.append(device)
                
                # Monitor health for all devices
                health_metrics = await self.monitor_device_health(all_devices)
                
                # Generate and log summary
                summary = self.generate_health_summary()
                self.logger.info("📊 Health monitoring complete", 
                               total_devices=summary["overall_health"]["total_devices"],
                               critical=summary["overall_health"]["critical"],
                               warning=summary["overall_health"]["warning"],
                               health_percentage=f"{summary['overall_health']['health_percentage']:.1f}%")
                
                # If critical devices found, alert should be sent
                if summary["overall_health"]["critical"] > 0:
                    self.logger.warning(f"🚨 {summary['overall_health']['critical']} critical devices need attention!")
                
                # Wait for next interval
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"❌ Health monitoring cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

# Example usage for AutoGen Studio integration
if __name__ == "__main__":
    import asyncio
    
    async def main():
        agent = DeviceHealthMonitoringAgent()
        
        # Example: Get devices and monitor their health
        try:
            orgs_response = requests.get("http://localhost:11030/organizations")
            organizations = orgs_response.json()
            
            if organizations:
                org = organizations[0]  # Use first organization
                networks_response = requests.get(f"http://localhost:11030/organizations/{org['id']}/networks")
                networks = networks_response.json()
                
                if networks:
                    network = networks[0]  # Use first network
                    devices_response = requests.get(f"http://localhost:11030/networks/{network['id']}/devices")
                    devices = devices_response.json()
                    
                    # Add context to devices
                    for device in devices:
                        device['organization_name'] = org['name']
                        device['network_name'] = network['name']
                    
                    # Monitor health
                    health_metrics = await agent.monitor_device_health(devices)
                    summary = agent.generate_health_summary()
                    
                    print("=== DEVICE HEALTH MONITORING COMPLETE ===")
                    print(f"Total Devices: {summary['overall_health']['total_devices']}")
                    print(f"Health Score: {summary['overall_health']['health_percentage']:.1f}%")
                    print(f"Critical: {summary['overall_health']['critical']}")
                    print(f"Warning: {summary['overall_health']['warning']}")
                    print(f"Healthy: {summary['overall_health']['healthy']}")
                    
                    if summary['critical_devices']:
                        print(f"\n🚨 CRITICAL DEVICES NEEDING ATTENTION:")
                        for device in summary['critical_devices'][:5]:
                            print(f"  - {device['serial']} ({device['model']}) in {device['network']}")
                            for issue in device['issues']:
                                print(f"    • {issue}")
        
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(main())