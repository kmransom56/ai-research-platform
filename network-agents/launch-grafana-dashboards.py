#!/usr/bin/env python3
"""
Grafana Dashboard Launcher for Network Topology and Device Management
Provides direct access to all network visualization dashboards
"""

import webbrowser
import time
import requests
from datetime import datetime

def print_banner():
    """Print dashboard access banner"""
    print("=" * 80)
    print("📊 GRAFANA NETWORK DASHBOARDS - TOPOLOGY & DEVICE MANAGEMENT")
    print("=" * 80)
    print(f"🕐 Dashboard Access Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_grafana_availability():
    """Check if Grafana is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return response.status_code in [200, 302]  # 302 is redirect to login
    except:
        return False

def show_dashboard_access():
    """Display all available dashboard URLs"""
    print("🌐 AVAILABLE NETWORK DASHBOARDS:")
    print("-" * 50)
    
    base_url = "http://localhost:3000"
    
    dashboards = {
        "Network Topology Overview": f"{base_url}/d/network-topology",
        "Device Inventory": f"{base_url}/d/device-inventory", 
        "Performance Metrics": f"{base_url}/d/performance-metrics",
        "Security Posture": f"{base_url}/d/security-posture",
        "Configuration State": f"{base_url}/d/config-state",
        "Executive Summary": f"{base_url}/d/executive-summary",
        "Real-time Monitoring": f"{base_url}/d/realtime-monitoring",
        "Historical Trends": f"{base_url}/d/historical-trends",
        "Alert Dashboard": f"{base_url}/d/alerts",
        "Capacity Planning": f"{base_url}/d/capacity-planning"
    }
    
    for name, url in dashboards.items():
        print(f"   📊 {name:<25}: {url}")
    
    print()
    print("🔧 GRAFANA MANAGEMENT:")
    print(f"   ⚙️  Admin Interface        : {base_url}")
    print(f"   📈 Data Sources           : {base_url}/datasources")
    print(f"   🎛️  Dashboard Management   : {base_url}/dashboards")
    print()

def show_prometheus_metrics():
    """Show Prometheus metrics endpoints"""
    print("📈 PROMETHEUS METRICS ENDPOINTS:")
    print("-" * 50)
    
    metrics_base = "http://localhost:9090"
    
    endpoints = {
        "Network Device Health": f"{metrics_base}/graph?g0.expr=network_device_health_score",
        "Device Uptime": f"{metrics_base}/graph?g0.expr=network_device_uptime_score", 
        "Active Alerts": f"{metrics_base}/graph?g0.expr=network_alert_active",
        "Platform Availability": f"{metrics_base}/graph?g0.expr=network_platform_availability",
        "Security Events": f"{metrics_base}/graph?g0.expr=fortinet_security_events_total",
        "All Metrics": f"{metrics_base}/metrics",
        "Targets Status": f"{metrics_base}/targets",
        "Prometheus Config": f"{metrics_base}/config"
    }
    
    for name, url in endpoints.items():
        print(f"   📊 {name:<25}: {url}")
    
    print()

def launch_topology_viewer():
    """Launch Neo4j topology viewer"""
    print("🗺️ NETWORK TOPOLOGY VIEWER:")
    print("-" * 50)
    
    neo4j_url = "http://localhost:7474"
    print(f"   🌐 Neo4j Browser          : {neo4j_url}")
    print(f"   🔍 Topology Queries       : Copy from topology-queries.cypher")
    print()
    
    # Try to open Neo4j browser
    try:
        webbrowser.open(neo4j_url)
        print("   ✅ Neo4j Browser opened in your default browser")
    except:
        print("   ⚠️  Could not auto-open browser. Please visit URL manually.")
    
    print()

def show_api_endpoints():
    """Show network management API endpoints"""
    print("🔌 NETWORK MANAGEMENT APIs:")
    print("-" * 50)
    
    apis = {
        "Unified Network Manager": "http://localhost:11000/api/network",
        "Meraki Connector": "http://localhost:11030/api/devices",
        "Fortinet Connector": "http://localhost:11031/api/security",
        "Health Assessment": "http://localhost:11000/api/health-assessment",
        "Incident Response": "http://localhost:11000/api/incidents", 
        "Predictive Maintenance": "http://localhost:11000/api/maintenance",
        "Remediation System": "http://localhost:11000/api/remediation",
        "Network Metrics": "http://localhost:9090/api/v1/query"
    }
    
    for name, url in apis.items():
        print(f"   🔌 {name:<25}: {url}")
    
    print()

def show_executive_access():
    """Show executive-level access points"""
    print("👔 EXECUTIVE-LEVEL ACCESS:")
    print("-" * 50)
    
    print("   🤖 Natural Language Interface:")
    print("      Chat Copilot           : http://localhost:11000")
    print("      Try: 'Generate executive network report'")
    print()
    
    print("   📊 Executive Dashboards:")
    print("      Network Health Summary : http://localhost:3000/d/executive-summary")
    print("      Business Impact View   : http://localhost:3000/d/business-impact")
    print("      KPI Dashboard         : http://localhost:3000/d/network-kpis")
    print()
    
    print("   📋 Automated Reports:")
    print("      Run Health Assessment : python3 automated-health-assessment.py")
    print("      Generate Full Report  : python3 generate-executive-report.py")
    print()

def main():
    """Main dashboard launcher"""
    print_banner()
    
    # Check services
    grafana_available = check_grafana_availability()
    
    if not grafana_available:
        print("⚠️ WARNING: Grafana may not be running on port 3000")
        print("   To start Grafana: docker run -d -p 3000:3000 grafana/grafana")
        print()
    
    # Show all access points
    show_dashboard_access()
    show_prometheus_metrics()
    launch_topology_viewer()
    show_api_endpoints()
    show_executive_access()
    
    print("🎯 QUICK ACCESS SUMMARY:")
    print("=" * 80)
    
    print("📊 TOPOLOGY & INVENTORY:")
    print("   • Neo4j Browser: http://localhost:7474 (Interactive topology)")
    print("   • Grafana Dashboards: http://localhost:3000 (Visual monitoring)")
    print("   • Chat Copilot: http://localhost:11000 (Natural language)")
    print()
    
    print("🔍 DEVICE MANAGEMENT:")
    print("   • Complete inventory queries in Neo4j")
    print("   • Real-time performance in Grafana")
    print("   • Configuration state tracking")
    print("   • Historical trend analysis")
    print()
    
    print("🏢 EXECUTIVE REPORTING:")
    print("   • Natural language: 'Show me network health summary'")
    print("   • Automated assessments: python3 automated-health-assessment.py")
    print("   • Business impact analysis and recommendations")
    print()
    
    print("💡 NEXT STEPS:")
    print("   1. Open Neo4j Browser and run topology queries")
    print("   2. Access Chat Copilot for natural language queries")
    print("   3. Run: python3 automated-health-assessment.py")
    print("   4. View executive summaries and recommendations")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()