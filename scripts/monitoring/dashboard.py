#!/usr/bin/env python3
"""
Simple monitoring dashboard for API usage
"""

import json
import glob
from pathlib import Path
import datetime

class MonitoringDashboard:
    def __init__(self):
        self.log_dir = Path("logs/monitoring")
    
    def generate_dashboard(self):
        """Generate text-based dashboard"""
        print("📊 API MONITORING DASHBOARD")
        print("=" * 50)
        print(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get latest report
        report_files = glob.glob(str(self.log_dir / "usage_report_*.json"))
        if not report_files:
            print("❌ No usage reports found")
            return
        
        latest_report_file = max(report_files)
        try:
            with open(latest_report_file) as f:
                latest_report = json.load(f)
        except Exception as e:
            print(f"❌ Error reading report: {e}")
            return
        
        # Display service status
        print("🔐 SERVICE STATUS:")
        services = latest_report.get('services', {})
        
        for service_name, service_data in services.items():
            status_icon = "✅" if service_data.get('status') == 'configured' else "📊"
            print(f"  {status_icon} {service_name.replace('_', ' ').title()}")
            
            if service_name == 'github' and 'used' in service_data:
                usage_pct = (service_data['used'] / service_data['limit']) * 100
                bar_length = 20
                filled_length = int(bar_length * usage_pct / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f"    Usage: {usage_pct:.1f}% [{bar}] {service_data['used']}/{service_data['limit']}")
                
                # Reset time
                reset_time = datetime.datetime.fromtimestamp(service_data['reset'])
                print(f"    Resets: {reset_time.strftime('%H:%M:%S')}")
        
        print()
        
        # Show recent activity
        print("📈 RECENT ACTIVITY:")
        recent_files = sorted(glob.glob(str(self.log_dir / "usage_report_*.json")))[-5:]
        
        for report_file in recent_files:
            try:
                with open(report_file) as f:
                    report = json.load(f)
                
                timestamp = datetime.datetime.fromisoformat(report['timestamp'])
                service_count = len(report.get('services', {}))
                print(f"  {timestamp.strftime('%H:%M:%S')} - {service_count} services checked")
                
            except Exception as e:
                print(f"  ❌ Error reading {Path(report_file).name}")
        
        print()
        
        # Show alerts
        alert_file = self.log_dir / "alerts.log"
        if alert_file.exists():
            print("🚨 RECENT ALERTS:")
            try:
                with open(alert_file) as f:
                    alert_lines = f.readlines()[-5:]  # Last 5 alerts
                
                if alert_lines:
                    for line in alert_lines:
                        print(f"  {line.strip()}")
                else:
                    print("  ✅ No recent alerts")
            except Exception:
                print("  ❌ Error reading alerts")
        else:
            print("🚨 ALERTS: No alert log found")
        
        print()
        print("🔗 MONITORING LINKS:")
        print("  • OpenAI Usage: https://platform.openai.com/usage")
        print("  • Azure Costs: https://portal.azure.com/#view/Microsoft_Azure_CostManagement")
        print("  • GitHub Actions: Repository → Settings → Secrets and variables")
        print()

if __name__ == "__main__":
    dashboard = MonitoringDashboard()
    dashboard.generate_dashboard()
