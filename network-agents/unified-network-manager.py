"""
Unified Network Management System
Combines Meraki and Fortinet platforms for comprehensive network oversight
Provides correlated security analysis and unified monitoring
"""

import asyncio
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from dataclasses import dataclass, asdict

# Import our existing agents
from network_discovery_agent import NetworkDiscoveryAgent
from device_health_monitoring_agent import DeviceHealthMonitoringAgent
from alert_management_agent import AlertManagementAgent, NetworkAlert, AlertSeverity

@dataclass
class UnifiedDevice:
    """Unified device representation across platforms"""
    id: str
    name: str
    model: str
    platform: str  # 'meraki' or 'fortinet'
    device_type: str  # 'switch', 'firewall', 'access_point', etc.
    status: str
    health_score: float
    location: str
    management_ip: str
    firmware_version: str
    last_seen: datetime
    security_status: str = "unknown"
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}

@dataclass
class SecurityCorrelation:
    """Security event correlation between platforms"""
    correlation_id: str
    timestamp: datetime
    severity: str
    event_type: str
    source_platform: str
    source_device: str
    target_device: Optional[str]
    description: str
    recommended_action: str

class UnifiedNetworkManager:
    """
    Unified management system for Meraki and Fortinet platforms
    Provides comprehensive network oversight and security correlation
    """
    
    def __init__(self, 
                 meraki_api_base: str = "http://localhost:11030",
                 fortinet_api_base: str = "http://localhost:11031"):
        self.meraki_api = meraki_api_base
        self.fortinet_api = fortinet_api_base
        self.logger = logging.getLogger("UnifiedNetworkManager")
        
        # Initialize platform agents
        self.discovery_agent = NetworkDiscoveryAgent(meraki_api_base)
        self.health_agent = DeviceHealthMonitoringAgent(meraki_api_base)
        self.alert_agent = AlertManagementAgent(meraki_api_base)
        
        # Unified device inventory
        self.unified_inventory = []
        self.security_correlations = []
        
        # Platform availability
        self.meraki_available = True
        self.fortinet_available = True

    async def initialize(self):
        """Initialize unified network manager"""
        self.logger.info("🔄 Initializing unified network manager")
        
        # Test platform connectivity
        await self._test_platform_connectivity()
        
        self.logger.info(f"✅ Unified manager initialized - Meraki: {'✅' if self.meraki_available else '❌'}, Fortinet: {'✅' if self.fortinet_available else '❌'}")

    async def _test_platform_connectivity(self):
        """Test connectivity to both platforms"""
        # Test Meraki
        try:
            response = requests.get(f"{self.meraki_api}/health", timeout=5)
            self.meraki_available = response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Meraki platform not available: {e}")
            self.meraki_available = False
        
        # Test Fortinet
        try:
            response = requests.get(f"{self.fortinet_api}/health", timeout=5)
            self.fortinet_available = response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Fortinet platform not available: {e}")
            self.fortinet_available = False

    async def discover_unified_topology(self) -> Dict[str, Any]:
        """Discover network topology across both platforms"""
        self.logger.info("🌐 Discovering unified network topology")
        
        unified_topology = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {
                "meraki": {"available": self.meraki_available, "devices": []},
                "fortinet": {"available": self.fortinet_available, "devices": []}
            },
            "unified_devices": [],
            "security_analysis": {},
            "summary": {}
        }
        
        # Discover Meraki infrastructure
        if self.meraki_available:
            try:
                meraki_data = await self.discovery_agent.discover_all_networks()
                unified_topology["platforms"]["meraki"] = {
                    "available": True,
                    "organizations": meraki_data["summary"]["total_organizations"],
                    "networks": meraki_data["summary"]["total_networks"],
                    "devices": meraki_data["summary"]["total_devices_discovered"],
                    "discovery_time": meraki_data["summary"]["discovery_duration_seconds"]
                }
                
                # Convert Meraki devices to unified format
                for device in meraki_data.get("devices", []):
                    unified_device = self._convert_meraki_device(device)
                    unified_topology["unified_devices"].append(unified_device)
                    
            except Exception as e:
                self.logger.error(f"Meraki discovery failed: {e}")
                unified_topology["platforms"]["meraki"]["error"] = str(e)
        
        # Discover Fortinet infrastructure
        if self.fortinet_available:
            try:
                fortinet_data = await self._discover_fortinet_infrastructure()
                unified_topology["platforms"]["fortinet"] = fortinet_data
                
                # Convert Fortinet devices to unified format
                for device in fortinet_data.get("devices", []):
                    unified_device = self._convert_fortinet_device(device)
                    unified_topology["unified_devices"].append(unified_device)
                    
            except Exception as e:
                self.logger.error(f"Fortinet discovery failed: {e}")
                unified_topology["platforms"]["fortinet"]["error"] = str(e)
        
        # Store unified inventory
        self.unified_inventory = unified_topology["unified_devices"]
        
        # Generate topology summary
        unified_topology["summary"] = self._generate_topology_summary(unified_topology)
        
        return unified_topology

    async def _discover_fortinet_infrastructure(self) -> Dict[str, Any]:
        """Discover Fortinet infrastructure"""
        try:
            # Get unified overview from Fortinet API
            response = requests.get(f"{self.fortinet_api}/unified/overview", timeout=30)
            if response.status_code == 200:
                fortinet_overview = response.json()
                
                # Extract device information
                devices = []
                
                # Add FortiGate itself
                system_info = fortinet_overview.get("system", {})
                if system_info:
                    devices.append({
                        "serial": system_info.get("serial", "unknown"),
                        "model": system_info.get("version", "FortiGate"),
                        "type": "security_appliance",
                        "status": "online" if system_info.get("status") == "success" else "offline",
                        "version": system_info.get("version", "unknown"),
                        "interfaces": fortinet_overview.get("interfaces", [])
                    })
                
                # Add managed switches
                for switch in fortinet_overview.get("switches", []):
                    devices.append({
                        "serial": switch.get("serial", "unknown"),
                        "model": switch.get("model", "FortiSwitch"),
                        "type": "switch",
                        "status": switch.get("status", "unknown"),
                        "version": switch.get("version", "unknown")
                    })
                
                # Add managed access points
                for ap in fortinet_overview.get("access_points", []):
                    devices.append({
                        "serial": ap.get("serial", "unknown"),
                        "model": ap.get("model", "FortiAP"),
                        "type": "access_point", 
                        "status": ap.get("status", "unknown"),
                        "version": ap.get("version", "unknown")
                    })
                
                return {
                    "available": True,
                    "devices": devices,
                    "summary": fortinet_overview.get("summary", {}),
                    "health_score": fortinet_overview.get("health", {}).get("health_score", 100)
                }
            else:
                return {"available": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _convert_meraki_device(self, meraki_device: Dict[str, Any]) -> UnifiedDevice:
        """Convert Meraki device to unified format"""
        device_type = self._determine_meraki_device_type(meraki_device.get("model", ""))
        
        return UnifiedDevice(
            id=f"meraki_{meraki_device.get('serial', '')}",
            name=meraki_device.get('name', meraki_device.get('serial', 'Unknown')),
            model=meraki_device.get('model', 'Unknown'),
            platform='meraki',
            device_type=device_type,
            status=meraki_device.get('status', 'unknown'),
            health_score=85.0,  # Default, would be updated by health monitoring
            location=f"{meraki_device.get('organization_name', 'Unknown')} / {meraki_device.get('network_name', 'Unknown')}",
            management_ip=meraki_device.get('lanIp', 'unknown'),
            firmware_version=meraki_device.get('firmware', 'unknown'),
            last_seen=datetime.fromisoformat(meraki_device.get('lastReportedAt', datetime.now().isoformat()).replace('Z', '+00:00')) if meraki_device.get('lastReportedAt') else datetime.now(),
            security_status="managed"
        )

    def _convert_fortinet_device(self, fortinet_device: Dict[str, Any]) -> UnifiedDevice:
        """Convert Fortinet device to unified format"""
        return UnifiedDevice(
            id=f"fortinet_{fortinet_device.get('serial', '')}",
            name=fortinet_device.get('name', fortinet_device.get('serial', 'Unknown')),
            model=fortinet_device.get('model', 'Unknown'),
            platform='fortinet',
            device_type=fortinet_device.get('type', 'unknown'),
            status=fortinet_device.get('status', 'unknown'),
            health_score=90.0,  # Default, would be updated by health monitoring
            location="Fortinet Managed",
            management_ip=fortinet_device.get('ip', 'unknown'),
            firmware_version=fortinet_device.get('version', 'unknown'),
            last_seen=datetime.now(),
            security_status="secure"
        )

    def _determine_meraki_device_type(self, model: str) -> str:
        """Determine device type from Meraki model"""
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

    def _generate_topology_summary(self, topology: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for unified topology"""
        devices = topology["unified_devices"]
        
        # Platform distribution
        platform_counts = {}
        device_type_counts = {}
        status_counts = {}
        
        for device in devices:
            # Platform counts
            platform = device.platform
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Device type counts
            device_type = device.device_type
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
            
            # Status counts
            status = device.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate health metrics
        if devices:
            avg_health = sum(d.health_score for d in devices) / len(devices)
            online_devices = len([d for d in devices if d.status == 'online'])
            health_percentage = (online_devices / len(devices)) * 100
        else:
            avg_health = 0
            health_percentage = 0
        
        return {
            "total_devices": len(devices),
            "platform_distribution": platform_counts,
            "device_type_distribution": device_type_counts,
            "status_distribution": status_counts,
            "health_metrics": {
                "average_health_score": round(avg_health, 2),
                "devices_online": status_counts.get('online', 0),
                "devices_offline": status_counts.get('offline', 0),
                "health_percentage": round(health_percentage, 2)
            }
        }

    async def perform_security_correlation(self) -> List[SecurityCorrelation]:
        """Perform security correlation analysis between platforms"""
        self.logger.info("🔒 Performing security correlation analysis")
        
        correlations = []
        
        if not (self.meraki_available and self.fortinet_available):
            self.logger.warning("Security correlation requires both platforms to be available")
            return correlations
        
        try:
            # Get Fortinet security events
            fortinet_events = await self._get_fortinet_security_events()
            
            # Get Meraki network activity (through existing health monitoring)
            meraki_devices = [d for d in self.unified_inventory if d.platform == 'meraki']
            
            # Correlate security events
            correlations.extend(await self._correlate_security_events(fortinet_events, meraki_devices))
            
            # Check for configuration discrepancies
            correlations.extend(await self._check_security_posture())
            
            self.security_correlations = correlations
            return correlations
            
        except Exception as e:
            self.logger.error(f"Security correlation failed: {e}")
            return []

    async def _get_fortinet_security_events(self) -> List[Dict[str, Any]]:
        """Get recent security events from Fortinet"""
        try:
            response = requests.get(f"{self.fortinet_api}/security/events?count=50", timeout=30)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            self.logger.warning(f"Failed to get Fortinet security events: {e}")
            return []

    async def _correlate_security_events(self, fortinet_events: List[Dict[str, Any]], 
                                       meraki_devices: List[UnifiedDevice]) -> List[SecurityCorrelation]:
        """Correlate security events between platforms"""
        correlations = []
        
        for event in fortinet_events:
            # Look for events that might affect Meraki devices
            source_ip = event.get('srcip', '')
            dest_ip = event.get('dstip', '')
            
            # Find related Meraki devices
            related_devices = [
                d for d in meraki_devices 
                if d.management_ip in [source_ip, dest_ip]
            ]
            
            if related_devices:
                correlation = SecurityCorrelation(
                    correlation_id=f"sec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    timestamp=datetime.now(),
                    severity=self._map_fortinet_severity(event.get('level', 'info')),
                    event_type=event.get('subtype', 'unknown'),
                    source_platform='fortinet',
                    source_device=event.get('devname', 'FortiGate'),
                    target_device=related_devices[0].name,
                    description=f"Fortinet detected {event.get('subtype', 'security event')} involving Meraki device",
                    recommended_action="Review Meraki device logs and consider policy adjustment"
                )
                correlations.append(correlation)
        
        return correlations

    async def _check_security_posture(self) -> List[SecurityCorrelation]:
        """Check for security posture discrepancies"""
        correlations = []
        
        # Check for devices that should be behind Fortinet security but aren't
        meraki_devices = [d for d in self.unified_inventory if d.platform == 'meraki']
        fortinet_devices = [d for d in self.unified_inventory if d.platform == 'fortinet']
        
        if not fortinet_devices and meraki_devices:
            correlation = SecurityCorrelation(
                correlation_id=f"posture_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.now(),
                severity="medium",
                event_type="security_posture",
                source_platform="unified",
                source_device="security_analyzer",
                target_device=None,
                description=f"Found {len(meraki_devices)} Meraki devices without Fortinet security protection",
                recommended_action="Consider deploying FortiGate for centralized security management"
            )
            correlations.append(correlation)
        
        return correlations

    def _map_fortinet_severity(self, fortinet_level: str) -> str:
        """Map Fortinet log levels to unified severity"""
        mapping = {
            'emergency': 'critical',
            'alert': 'critical', 
            'critical': 'critical',
            'error': 'high',
            'warning': 'medium',
            'notice': 'low',
            'info': 'low',
            'debug': 'low'
        }
        return mapping.get(fortinet_level.lower(), 'medium')

    async def generate_unified_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report across both platforms"""
        self.logger.info("📊 Generating unified health report")
        
        # Get unified topology
        topology = await self.discover_unified_topology()
        
        # Perform security correlation
        security_correlations = await self.perform_security_correlation()
        
        # Analyze health across platforms
        health_analysis = await self._analyze_unified_health()
        
        # Generate recommendations
        recommendations = self._generate_unified_recommendations(topology, security_correlations, health_analysis)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "report_type": "unified_network_health",
            "platform_status": {
                "meraki": {
                    "available": self.meraki_available,
                    "device_count": len([d for d in self.unified_inventory if d.platform == 'meraki']),
                    "health_score": self._calculate_platform_health('meraki')
                },
                "fortinet": {
                    "available": self.fortinet_available,
                    "device_count": len([d for d in self.unified_inventory if d.platform == 'fortinet']),
                    "health_score": self._calculate_platform_health('fortinet')
                }
            },
            "unified_summary": topology["summary"],
            "security_analysis": {
                "correlations_found": len(security_correlations),
                "critical_security_issues": len([c for c in security_correlations if c.severity == 'critical']),
                "security_score": self._calculate_security_score(security_correlations)
            },
            "health_analysis": health_analysis,
            "recommendations": recommendations,
            "detailed_correlations": [asdict(c) for c in security_correlations]
        }
        
        return report

    def _calculate_platform_health(self, platform: str) -> float:
        """Calculate health score for specific platform"""
        platform_devices = [d for d in self.unified_inventory if d.platform == platform]
        
        if not platform_devices:
            return 0.0
        
        avg_health = sum(d.health_score for d in platform_devices) / len(platform_devices)
        online_percentage = (len([d for d in platform_devices if d.status == 'online']) / len(platform_devices)) * 100
        
        return (avg_health + online_percentage) / 2

    def _calculate_security_score(self, correlations: List[SecurityCorrelation]) -> float:
        """Calculate overall security score"""
        if not correlations:
            return 100.0  # No issues found
        
        base_score = 100.0
        
        for correlation in correlations:
            if correlation.severity == 'critical':
                base_score -= 20
            elif correlation.severity == 'high':
                base_score -= 10
            elif correlation.severity == 'medium':
                base_score -= 5
        
        return max(0.0, base_score)

    async def _analyze_unified_health(self) -> Dict[str, Any]:
        """Analyze health across unified infrastructure"""
        analysis = {
            "overall_health_score": 0.0,
            "platform_comparison": {},
            "critical_issues": [],
            "performance_trends": {},
            "availability_metrics": {}
        }
        
        if not self.unified_inventory:
            return analysis
        
        # Overall health calculation
        total_health = sum(d.health_score for d in self.unified_inventory)
        analysis["overall_health_score"] = total_health / len(self.unified_inventory)
        
        # Platform comparison
        meraki_devices = [d for d in self.unified_inventory if d.platform == 'meraki']
        fortinet_devices = [d for d in self.unified_inventory if d.platform == 'fortinet']
        
        if meraki_devices:
            meraki_avg_health = sum(d.health_score for d in meraki_devices) / len(meraki_devices)
            analysis["platform_comparison"]["meraki"] = {
                "device_count": len(meraki_devices),
                "average_health": meraki_avg_health,
                "online_percentage": (len([d for d in meraki_devices if d.status == 'online']) / len(meraki_devices)) * 100
            }
        
        if fortinet_devices:
            fortinet_avg_health = sum(d.health_score for d in fortinet_devices) / len(fortinet_devices)
            analysis["platform_comparison"]["fortinet"] = {
                "device_count": len(fortinet_devices),
                "average_health": fortinet_avg_health,
                "online_percentage": (len([d for d in fortinet_devices if d.status == 'online']) / len(fortinet_devices)) * 100
            }
        
        # Identify critical issues
        critical_devices = [d for d in self.unified_inventory if d.health_score < 50 or d.status == 'offline']
        analysis["critical_issues"] = [
            {
                "device_id": d.id,
                "device_name": d.name,
                "platform": d.platform,
                "issue": "Low health score" if d.health_score < 50 else "Device offline",
                "health_score": d.health_score,
                "location": d.location
            }
            for d in critical_devices
        ]
        
        return analysis

    def _generate_unified_recommendations(self, topology: Dict[str, Any], 
                                        correlations: List[SecurityCorrelation],
                                        health_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on unified analysis"""
        recommendations = []
        
        # Platform availability recommendations
        if not self.meraki_available:
            recommendations.append({
                "priority": "high",
                "category": "platform_connectivity",
                "title": "Meraki Platform Unavailable",
                "description": "Unable to connect to Meraki platform for monitoring and management",
                "action": "Check Meraki API connectivity, API key validity, and network connectivity"
            })
        
        if not self.fortinet_available:
            recommendations.append({
                "priority": "medium",
                "category": "platform_connectivity", 
                "title": "Fortinet Platform Unavailable",
                "description": "Unable to connect to Fortinet platform for security monitoring",
                "action": "Check Fortinet API connectivity, credentials, and firewall rules"
            })
        
        # Security recommendations
        critical_security = len([c for c in correlations if c.severity == 'critical'])
        if critical_security > 0:
            recommendations.append({
                "priority": "critical",
                "category": "security",
                "title": f"Critical Security Correlations Detected",
                "description": f"Found {critical_security} critical security correlations requiring immediate attention",
                "action": "Review security correlations and implement recommended security policies"
            })
        
        # Health recommendations
        critical_issues = len(health_analysis.get("critical_issues", []))
        if critical_issues > 0:
            recommendations.append({
                "priority": "high",
                "category": "device_health",
                "title": f"Critical Device Issues Detected",
                "description": f"{critical_issues} devices require immediate attention due to health issues",
                "action": "Investigate and resolve critical device issues to restore service"
            })
        
        # Platform balance recommendations
        meraki_count = len([d for d in self.unified_inventory if d.platform == 'meraki'])
        fortinet_count = len([d for d in self.unified_inventory if d.platform == 'fortinet'])
        
        if meraki_count > 0 and fortinet_count == 0:
            recommendations.append({
                "priority": "medium",
                "category": "architecture",
                "title": "Consider Fortinet Integration",
                "description": "Network relies solely on Meraki platform without centralized security",
                "action": "Consider deploying FortiGate for enhanced security and centralized management"
            })
        
        return recommendations

# Example usage and integration
if __name__ == "__main__":
    async def test_unified_management():
        manager = UnifiedNetworkManager()
        
        print("=== UNIFIED NETWORK MANAGEMENT TEST ===")
        
        try:
            # Initialize
            await manager.initialize()
            
            # Discover unified topology
            topology = await manager.discover_unified_topology()
            print(f"\n🌐 Unified Topology Discovery:")
            print(f"   Total Devices: {topology['summary']['total_devices']}")
            print(f"   Meraki Devices: {topology['summary']['platform_distribution'].get('meraki', 0)}")
            print(f"   Fortinet Devices: {topology['summary']['platform_distribution'].get('fortinet', 0)}")
            print(f"   Health: {topology['summary']['health_metrics']['health_percentage']:.1f}%")
            
            # Generate unified health report
            report = await manager.generate_unified_health_report()
            print(f"\n📊 Unified Health Report:")
            print(f"   Overall Health: {report['health_analysis']['overall_health_score']:.1f}%")
            print(f"   Security Score: {report['security_analysis']['security_score']:.1f}%")
            print(f"   Critical Issues: {len(report['health_analysis']['critical_issues'])}")
            print(f"   Security Correlations: {report['security_analysis']['correlations_found']}")
            print(f"   Recommendations: {len(report['recommendations'])}")
            
            if report['recommendations']:
                print(f"\n💡 Top Recommendations:")
                for rec in report['recommendations'][:3]:
                    print(f"   [{rec['priority'].upper()}] {rec['title']}")
            
            print("\n✅ Unified network management test completed successfully!")
            
        except Exception as e:
            print(f"❌ Unified management test failed: {e}")

    asyncio.run(test_unified_management())