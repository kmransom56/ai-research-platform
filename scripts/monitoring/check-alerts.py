#!/usr/bin/env python3
"""
Alert System for API Monitoring
Checks for suspicious activity and sends notifications
"""

import json
import os
import datetime
from pathlib import Path
import glob

class AlertMonitor:
    def __init__(self):
        self.log_dir = Path("logs/monitoring")
        self.alert_log = self.log_dir / "alerts.log"
        
    def check_github_usage(self, report_data):
        """Check for GitHub API usage anomalies"""
        alerts = []
        
        if 'github' in report_data.get('services', {}):
            github_data = report_data['services']['github']
            usage_pct = (github_data['used'] / github_data['limit']) * 100
            
            if usage_pct > 85:
                alerts.append({
                    "severity": "HIGH",
                    "service": "GitHub",
                    "message": f"High API usage: {usage_pct:.1f}% ({github_data['used']}/{github_data['limit']})",
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        return alerts
    
    def check_for_unusual_patterns(self):
        """Check recent reports for unusual patterns"""
        alerts = []
        
        # Get recent reports (last 4 hours)
        recent_reports = []
        report_files = glob.glob(str(self.log_dir / "usage_report_*.json"))
        
        for report_file in sorted(report_files)[-8:]:  # Last 8 reports (4 hours if every 30 min)
            try:
                with open(report_file) as f:
                    recent_reports.append(json.load(f))
            except Exception as e:
                print(f"Warning: Could not read {report_file}: {e}")
        
        if len(recent_reports) < 2:
            return alerts
        
        # Check for increasing usage trends
        github_usage = []
        for report in recent_reports:
            if 'github' in report.get('services', {}):
                github_data = report['services']['github']
                usage_pct = (github_data['used'] / github_data['limit']) * 100
                github_usage.append(usage_pct)
        
        if len(github_usage) >= 3:
            # Check if usage is increasing rapidly
            recent_increase = github_usage[-1] - github_usage[-3]
            if recent_increase > 20:  # 20% increase in recent reports
                alerts.append({
                    "severity": "MEDIUM",
                    "service": "GitHub",
                    "message": f"Rapid usage increase detected: +{recent_increase:.1f}% in recent checks",
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        return alerts
    
    def log_alert(self, alert):
        """Log alert to file and print to console"""
        alert_line = f"[{alert['timestamp']}] {alert['severity']}: {alert['service']} - {alert['message']}\n"
        
        with open(self.alert_log, 'a') as f:
            f.write(alert_line)
        
        # Color-coded console output
        color = '\033[0;31m' if alert['severity'] == 'HIGH' else '\033[1;33m'  # Red for HIGH, Yellow for MEDIUM
        print(f"{color}🚨 ALERT: {alert['service']} - {alert['message']}\033[0m")
    
    def run_alert_check(self):
        """Run comprehensive alert check"""
        print("🔍 Running alert check...")
        
        # Get latest usage report
        report_files = glob.glob(str(self.log_dir / "usage_report_*.json"))
        if not report_files:
            print("No usage reports found")
            return
        
        latest_report_file = max(report_files)
        try:
            with open(latest_report_file) as f:
                latest_report = json.load(f)
        except Exception as e:
            print(f"Error reading latest report: {e}")
            return
        
        # Check various alert conditions
        all_alerts = []
        all_alerts.extend(self.check_github_usage(latest_report))
        all_alerts.extend(self.check_for_unusual_patterns())
        
        # Process alerts
        if all_alerts:
            print(f"⚠️  Found {len(all_alerts)} alerts")
            for alert in all_alerts:
                self.log_alert(alert)
        else:
            print("✅ No alerts detected")
        
        return all_alerts

if __name__ == "__main__":
    monitor = AlertMonitor()
    alerts = monitor.run_alert_check()
    
    if alerts:
        print(f"\n📢 ALERT SUMMARY: {len(alerts)} alerts generated")
        print("Check logs/monitoring/alerts.log for full details")
    else:
        print("\n✅ All systems normal")
