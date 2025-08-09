"""
Network Metrics Exporter for Prometheus/Grafana
Exports network monitoring data in Prometheus format
Integrates with unified network management system
"""

from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest, start_http_server
import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import json

# Import our network management components
from unified_network_manager import UnifiedNetworkManager
from neo4j_network_schema import NetworkKnowledgeGraph

class NetworkMetricsExporter:
    """
    Exports network metrics for Prometheus/Grafana monitoring
    Provides real-time metrics from both Meraki and Fortinet platforms
    """
    
    def __init__(self, 
                 meraki_api: str = "http://localhost:11030",
                 fortinet_api: str = "http://localhost:11031",
                 export_port: int = 9090):
        self.meraki_api = meraki_api
        self.fortinet_api = fortinet_api
        self.export_port = export_port
        self.logger = logging.getLogger("NetworkMetricsExporter")
        
        # Initialize network manager
        self.network_manager = UnifiedNetworkManager(meraki_api, fortinet_api)
        
        # Create Prometheus registry
        self.registry = CollectorRegistry()
        
        # Define metrics
        self._define_metrics()
        
        # Metrics collection state
        self.last_collection_time = None
        self.collection_duration = 0

    def _define_metrics(self):
        """Define Prometheus metrics"""
        
        # Device Information
        self.device_info = Gauge(
            'network_device_info',
            'Network device information',
            ['device_id', 'device_name', 'model', 'platform', 'device_type', 'status', 'location', 'organization'],
            registry=self.registry
        )
        
        # Health Metrics
        self.device_health_score = Gauge(
            'network_device_health_score',
            'Device health score (0-100)',
            ['device_id', 'device_name', 'platform', 'organization'],
            registry=self.registry
        )
        
        self.device_uptime_score = Gauge(
            'network_device_uptime_score',
            'Device uptime score (0-100)',
            ['device_id', 'device_name', 'platform', 'organization'],
            registry=self.registry
        )
        
        self.device_performance_score = Gauge(
            'network_device_performance_score', 
            'Device performance score (0-100)',
            ['device_id', 'device_name', 'platform', 'organization'],
            registry=self.registry
        )
        
        # Alert Metrics
        self.alert_active = Gauge(
            'network_alert_active',
            'Active network alerts',
            ['alert_id', 'device_name', 'alert_type', 'severity', 'location', 'organization'],
            registry=self.registry
        )
        
        self.alert_count = Counter(
            'network_alert_count',
            'Total network alerts generated',
            ['device_name', 'alert_type', 'severity', 'platform', 'organization'],
            registry=self.registry
        )
        
        # Network Traffic (if available)
        self.interface_bytes_total = Counter(
            'network_interface_bytes_total',
            'Network interface bytes transferred',
            ['device_id', 'interface', 'direction', 'organization'],
            registry=self.registry
        )
        
        # Platform Metrics
        self.platform_availability = Gauge(
            'network_platform_availability',
            'Platform availability status (1=available, 0=unavailable)',
            ['platform'],
            registry=self.registry
        )
        
        self.platform_health_score = Gauge(
            'network_platform_health_score',
            'Overall platform health score',
            ['platform'],
            registry=self.registry
        )
        
        # Fortinet Security Metrics
        self.fortinet_security_events = Counter(
            'fortinet_security_events_total',
            'Total Fortinet security events',
            ['event_type', 'severity'],
            registry=self.registry
        )
        
        self.fortinet_blocked_threats = Counter(
            'fortinet_blocked_threats_total',
            'Total blocked security threats',
            ['threat_type'],
            registry=self.registry
        )
        
        self.fortinet_vpn_sessions = Gauge(
            'fortinet_vpn_sessions_active',
            'Active VPN sessions',
            ['vpn_type'],
            registry=self.registry
        )
        
        # System Metrics
        self.metrics_collection_duration = Histogram(
            'network_metrics_collection_duration_seconds',
            'Time spent collecting network metrics',
            registry=self.registry
        )
        
        self.metrics_collection_timestamp = Gauge(
            'network_metrics_collection_timestamp',
            'Timestamp of last metrics collection',
            registry=self.registry
        )

    async def collect_metrics(self):
        """Collect metrics from all network platforms"""
        start_time = time.time()
        self.logger.info("📊 Collecting network metrics")
        
        try:
            # Initialize network manager
            await self.network_manager.initialize()
            
            # Collect unified network data
            unified_report = await self.network_manager.generate_unified_health_report()
            
            # Update device metrics
            await self._update_device_metrics(unified_report)
            
            # Update alert metrics
            await self._update_alert_metrics(unified_report)
            
            # Update platform metrics
            await self._update_platform_metrics(unified_report)
            
            # Update Fortinet security metrics
            if self.network_manager.fortinet_available:
                await self._update_fortinet_metrics()
            
            # Update collection metadata
            collection_duration = time.time() - start_time
            self.metrics_collection_duration.observe(collection_duration)
            self.metrics_collection_timestamp.set_to_current_time()
            
            self.last_collection_time = datetime.now()
            self.collection_duration = collection_duration
            
            self.logger.info(f"✅ Metrics collection completed in {collection_duration:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Metrics collection failed: {e}")
            raise

    async def _update_device_metrics(self, unified_report: Dict[str, Any]):
        """Update device-related metrics"""
        
        # Clear existing device metrics
        self.device_info.clear()
        self.device_health_score.clear()
        self.device_uptime_score.clear()
        self.device_performance_score.clear()
        
        # Get unified device inventory
        devices = self.network_manager.unified_inventory
        
        for device in devices:
            labels = {
                'device_id': device.id,
                'device_name': device.name,
                'model': device.model,
                'platform': device.platform,
                'device_type': device.device_type,
                'status': device.status,
                'location': device.location,
                'organization': device.location.split(' / ')[0] if ' / ' in device.location else 'Unknown'
            }
            
            # Device info (always set to 1 for active devices)
            self.device_info.labels(**labels).set(1)
            
            # Health scores
            health_labels = {
                'device_id': device.id,
                'device_name': device.name,
                'platform': device.platform,
                'organization': labels['organization']
            }
            
            self.device_health_score.labels(**health_labels).set(device.health_score)
            
            # For Meraki devices, try to get detailed health metrics
            if device.platform == 'meraki':
                # These would come from actual health monitoring
                uptime_score = device.performance_metrics.get('uptime_score', device.health_score)
                performance_score = device.performance_metrics.get('performance_score', device.health_score)
                
                self.device_uptime_score.labels(**health_labels).set(uptime_score)
                self.device_performance_score.labels(**health_labels).set(performance_score)

    async def _update_alert_metrics(self, unified_report: Dict[str, Any]):
        """Update alert-related metrics"""
        
        # Clear existing alert metrics
        self.alert_active.clear()
        
        # Get active alerts from alert management agent
        try:
            active_alerts = self.network_manager.alert_agent.get_active_alerts()
            
            for alert in active_alerts:
                alert_labels = {
                    'alert_id': alert.alert_id,
                    'device_name': alert.source_name,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity.value,
                    'location': alert.location,
                    'organization': alert.location.split(' / ')[0] if ' / ' in alert.location else 'Unknown'
                }
                
                # Set active alert (1 = active)
                self.alert_active.labels(**alert_labels).set(1)
                
                # Increment alert counter
                counter_labels = {
                    'device_name': alert.source_name,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity.value,
                    'platform': 'meraki',  # Most alerts come from Meraki currently
                    'organization': alert_labels['organization']
                }
                
                # This would normally be incremented when alert is created
                # For demo purposes, we'll set a base count
                self.alert_count.labels(**counter_labels)._value.set(1)
                
        except Exception as e:
            self.logger.warning(f"Failed to update alert metrics: {e}")

    async def _update_platform_metrics(self, unified_report: Dict[str, Any]):
        """Update platform-level metrics"""
        
        platform_status = unified_report.get("platform_status", {})
        
        # Meraki platform metrics
        meraki_status = platform_status.get("meraki", {})
        self.platform_availability.labels(platform='meraki').set(1 if meraki_status.get("available", False) else 0)
        self.platform_health_score.labels(platform='meraki').set(meraki_status.get("health_score", 0))
        
        # Fortinet platform metrics
        fortinet_status = platform_status.get("fortinet", {})
        self.platform_availability.labels(platform='fortinet').set(1 if fortinet_status.get("available", False) else 0)
        self.platform_health_score.labels(platform='fortinet').set(fortinet_status.get("health_score", 0))

    async def _update_fortinet_metrics(self):
        """Update Fortinet-specific security metrics"""
        
        try:
            # Get Fortinet security events
            response = requests.get(f"{self.fortinet_api}/security/events?count=100", timeout=10)
            if response.status_code == 200:
                events = response.json()
                
                # Count events by type and severity
                event_counts = {}
                for event in events:
                    event_type = event.get('subtype', 'unknown')
                    severity = self._map_fortinet_severity(event.get('level', 'info'))
                    
                    key = (event_type, severity)
                    event_counts[key] = event_counts.get(key, 0) + 1
                
                # Update security event metrics
                for (event_type, severity), count in event_counts.items():
                    self.fortinet_security_events.labels(
                        event_type=event_type, 
                        severity=severity
                    )._value.set(count)
            
            # Get VPN session info
            response = requests.get(f"{self.fortinet_api}/vpn/ssl-users", timeout=10)
            if response.status_code == 200:
                ssl_users = response.json()
                self.fortinet_vpn_sessions.labels(vpn_type='ssl').set(len(ssl_users))
            
            response = requests.get(f"{self.fortinet_api}/vpn/tunnels", timeout=10)
            if response.status_code == 200:
                tunnels = response.json()
                active_tunnels = len([t for t in tunnels if t.get('status') == 'up'])
                self.fortinet_vpn_sessions.labels(vpn_type='ipsec').set(active_tunnels)
                
        except Exception as e:
            self.logger.warning(f"Failed to update Fortinet metrics: {e}")

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

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')

    async def start_metrics_server(self):
        """Start HTTP server for metrics endpoint"""
        try:
            # Custom metrics handler
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
            
            class MetricsHandler(BaseHTTPRequestHandler):
                def __init__(self, exporter, *args, **kwargs):
                    self.exporter = exporter
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    if self.path == '/metrics':
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
                        self.end_headers()
                        metrics_data = self.exporter.get_metrics()
                        self.wfile.write(metrics_data.encode('utf-8'))
                    elif self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        health_data = {
                            "status": "healthy",
                            "last_collection": self.exporter.last_collection_time.isoformat() if self.exporter.last_collection_time else None,
                            "collection_duration": self.exporter.collection_duration
                        }
                        self.wfile.write(json.dumps(health_data).encode('utf-8'))
                    else:
                        self.send_error(404)
                
                def log_message(self, format, *args):
                    # Suppress default HTTP logging
                    pass
            
            # Create handler with exporter reference
            handler = lambda *args, **kwargs: MetricsHandler(self, *args, **kwargs)
            
            # Start HTTP server in thread
            httpd = HTTPServer(('0.0.0.0', self.export_port), handler)
            server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            server_thread.start()
            
            self.logger.info(f"📊 Metrics server started on port {self.export_port}")
            self.logger.info(f"   Metrics endpoint: http://localhost:{self.export_port}/metrics")
            self.logger.info(f"   Health endpoint: http://localhost:{self.export_port}/health")
            
            return httpd
            
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
            raise

    async def run_continuous_collection(self, interval_seconds: int = 30):
        """Run continuous metrics collection"""
        self.logger.info(f"🔄 Starting continuous metrics collection (interval: {interval_seconds}s)")
        
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"❌ Metrics collection cycle failed: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

# Grafana Dashboard Management
class GrafanaDashboardManager:
    """
    Manages Grafana dashboard provisioning and updates
    Automatically deploys network monitoring dashboards
    """
    
    def __init__(self, grafana_url: str = "http://localhost:3000", 
                 grafana_token: Optional[str] = None):
        self.grafana_url = grafana_url.rstrip('/')
        self.grafana_token = grafana_token or "admin"  # Default admin token
        self.logger = logging.getLogger("GrafanaDashboardManager")
        
        self.headers = {
            'Authorization': f'Bearer {self.grafana_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def deploy_network_dashboard(self):
        """Deploy the network monitoring dashboard to Grafana"""
        self.logger.info("🎨 Deploying network dashboard to Grafana")
        
        try:
            # Load dashboard configuration
            with open('/home/keith/chat-copilot/network-agents/grafana-dashboard-config.json', 'r') as f:
                dashboard_config = json.load(f)
            
            # Deploy dashboard
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                json=dashboard_config,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                dashboard_url = f"{self.grafana_url}/d/{result.get('uid', '')}"
                self.logger.info(f"✅ Dashboard deployed successfully: {dashboard_url}")
                return dashboard_url
            else:
                self.logger.error(f"❌ Dashboard deployment failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Dashboard deployment error: {e}")
            return None

    async def configure_prometheus_datasource(self, prometheus_url: str = "http://localhost:9090"):
        """Configure Prometheus as a Grafana data source"""
        self.logger.info("🔌 Configuring Prometheus data source")
        
        datasource_config = {
            "name": "Prometheus-Network",
            "type": "prometheus",
            "url": prometheus_url,
            "access": "proxy",
            "isDefault": True,
            "basicAuth": False
        }
        
        try:
            response = requests.post(
                f"{self.grafana_url}/api/datasources",
                json=datasource_config,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 409]:  # 409 = already exists
                self.logger.info("✅ Prometheus data source configured")
                return True
            else:
                self.logger.error(f"❌ Data source configuration failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Data source configuration error: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    async def test_metrics_exporter():
        exporter = NetworkMetricsExporter()
        
        print("=== NETWORK METRICS EXPORTER TEST ===")
        
        try:
            # Start metrics server
            await exporter.start_metrics_server()
            
            # Collect initial metrics
            await exporter.collect_metrics()
            
            # Show metrics sample
            metrics_data = exporter.get_metrics()
            print(f"\n📊 Sample metrics (first 1000 chars):")
            print(metrics_data[:1000])
            print("...")
            
            print(f"\n✅ Metrics exporter test completed successfully!")
            print(f"📈 Metrics available at: http://localhost:9090/metrics")
            print(f"🏥 Health check at: http://localhost:9090/health")
            
            # Keep server running for testing
            print("\n🔄 Server running... Press Ctrl+C to stop")
            while True:
                await asyncio.sleep(30)
                await exporter.collect_metrics()
                print(f"📊 Metrics updated at {datetime.now().strftime('%H:%M:%S')}")
                
        except KeyboardInterrupt:
            print("\n👋 Metrics exporter stopped")
        except Exception as e:
            print(f"❌ Metrics exporter test failed: {e}")

    # Run test
    asyncio.run(test_metrics_exporter())