#!/usr/bin/env python3
"""
API Usage Tracking Script
Monitors API usage across all services for security incident response
"""

import os
import json
import requests
import datetime
from pathlib import Path
import time

class APIUsageTracker:
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.log_dir = Path("logs/monitoring")
        self.log_dir.mkdir(exist_ok=True)
        
    def check_openai_usage(self):
        """Check OpenAI API usage"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  OpenAI API key not found in environment")
            return None
            
        try:
            # Note: OpenAI doesn't have a real-time usage API
            # This would need to be implemented with usage tracking in your app
            print("✅ OpenAI API key is configured")
            return {"status": "configured", "service": "openai"}
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return None
    
    def check_anthropic_usage(self):
        """Check Anthropic API usage"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  Anthropic API key not found in environment")
            return None
            
        try:
            # Anthropic doesn't provide usage API, monitor via logs
            print("✅ Anthropic API key is configured")
            return {"status": "configured", "service": "anthropic"}
        except Exception as e:
            print(f"❌ Anthropic API error: {e}")
            return None
    
    def check_github_usage(self):
        """Check GitHub API usage and rate limits"""
        token = os.getenv('GH_TOKEN')
        if not token:
            print("⚠️  GitHub token not found in environment")
            return None
            
        try:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get('https://api.github.com/rate_limit', headers=headers)
            if response.status_code == 200:
                data = response.json()
                core_limit = data['resources']['core']
                print(f"✅ GitHub API: {core_limit['used']}/{core_limit['limit']} requests used")
                return {
                    "service": "github",
                    "used": core_limit['used'],
                    "limit": core_limit['limit'],
                    "reset": core_limit['reset']
                }
            else:
                print(f"❌ GitHub API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ GitHub API error: {e}")
            return None
    
    def check_azure_openai_usage(self):
        """Check Azure OpenAI usage"""
        api_key = os.getenv('AZURE_OPENAI_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        
        if not api_key or not endpoint:
            print("⚠️  Azure OpenAI credentials not found")
            return None
            
        try:
            print("✅ Azure OpenAI credentials configured")
            return {"status": "configured", "service": "azure_openai"}
        except Exception as e:
            print(f"❌ Azure OpenAI error: {e}")
            return None
    
    def generate_usage_report(self):
        """Generate comprehensive usage report"""
        print("\n📊 GENERATING API USAGE REPORT")
        print("=" * 40)
        
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "monitoring_duration": str(datetime.datetime.now() - self.start_time),
            "services": {}
        }
        
        # Check each service
        services = [
            ("OpenAI", self.check_openai_usage),
            ("Anthropic", self.check_anthropic_usage),
            ("GitHub", self.check_github_usage),
            ("Azure OpenAI", self.check_azure_openai_usage)
        ]
        
        for service_name, check_func in services:
            print(f"\nChecking {service_name}...")
            result = check_func()
            if result:
                report["services"][service_name.lower().replace(" ", "_")] = result
        
        # Save report
        report_file = self.log_dir / f"usage_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📝 Report saved to: {report_file}")
        return report

if __name__ == "__main__":
    tracker = APIUsageTracker()
    report = tracker.generate_usage_report()
    
    # Print summary
    print("\n📋 MONITORING SUMMARY")
    print("=" * 30)
    print(f"Services monitored: {len(report['services'])}")
    print(f"Report timestamp: {report['timestamp']}")
    
    # Check for any concerning usage
    if 'github' in report['services']:
        github_data = report['services']['github']
        usage_pct = (github_data['used'] / github_data['limit']) * 100
        if usage_pct > 80:
            print(f"⚠️  GitHub API usage is high: {usage_pct:.1f}%")
        else:
            print(f"✅ GitHub API usage normal: {usage_pct:.1f}%")
