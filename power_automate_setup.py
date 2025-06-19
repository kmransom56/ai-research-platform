#!/usr/bin/env python3
"""
Power Automate Setup and Testing Utility
Helps configure and test Power Automate integration
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
import aiohttp


class PowerAutomateSetup:
    """Setup utility for Power Automate integration"""
    
    def __init__(self):
        self.config_file = Path.home() / ".platform_config" / "power_automate.json"
        self.env_file = Path.home() / ".platform_config" / ".env"
    
    def create_directories(self):
        """Create necessary directories"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created config directory: {self.config_file.parent}")
    
    def create_sample_config(self):
        """Create sample Power Automate configuration"""
        sample_config = {
            "webhook_url": "https://prod-xx.westus.logic.azure.com:443/workflows/YOUR_WORKFLOW_ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR_SIGNATURE",
            "enabled": True,
            "timeout": 30,
            "retry_attempts": 3,
            "events": [
                "platform_startup",
                "service_health",
                "config_cleanup",
                "error_alert",
                "daily_report"
            ],
            "device_management": {
                "fortigate_monitoring": True,
                "fortimanager_alerts": True,
                "config_backup_notifications": True,
                "network_topology_updates": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"✅ Created sample config: {self.config_file}")
        print("📝 Edit this file with your actual Power Automate webhook URL")
    
    def create_env_file(self):
        """Create environment file for sensitive configuration"""
        env_content = """# Power Automate Configuration
# Replace with your actual webhook URL from Power Automate
POWER_AUTOMATE_WEBHOOK_URL=https://prod-xx.westus.logic.azure.com:443/workflows/YOUR_WORKFLOW_ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR_SIGNATURE

# Enable/disable Power Automate integration
POWER_AUTOMATE_ENABLED=true

# Device management settings
FORTIGATE_API_TOKEN=your_fortigate_api_token_here
FORTIMANAGER_USERNAME=your_fortimanager_username
FORTIMANAGER_PASSWORD=your_fortimanager_password

# Platform settings
PLATFORM_ENVIRONMENT=production
ALERT_EMAIL=your-email@company.com
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created environment file: {self.env_file}")
        print("🔒 Remember to update with your actual credentials")
    
    async def test_webhook(self, webhook_url: str):
        """Test Power Automate webhook connectivity"""
        print(f"🧪 Testing webhook: {webhook_url[:50]}...")
        
        test_payload = {
            "timestamp": "2025-06-19T10:30:00",
            "event_type": "test_connection",
            "platform": "AI Research Platform",
            "source": "setup_utility",
            "data": {
                "test": True,
                "message": "This is a test webhook from the platform setup utility",
                "services_count": 12,
                "cleanup_enabled": True
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        print("✅ Webhook test successful!")
                        response_text = await response.text()
                        print(f"📝 Response: {response_text[:100]}...")
                        return True
                    else:
                        print(f"❌ Webhook responded with status: {response.status}")
                        error_text = await response.text()
                        print(f"📝 Error: {error_text[:200]}...")
                        return False
        
        except Exception as e:
            print(f"❌ Webhook test failed: {e}")
            return False
    
    def generate_power_automate_flow_template(self):
        """Generate Power Automate flow template"""
        flow_template = {
            "definition": {
                "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {},
                "triggers": {
                    "manual": {
                        "type": "Request",
                        "kind": "Http",
                        "inputs": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "timestamp": {"type": "string"},
                                    "event_type": {"type": "string"},
                                    "platform": {"type": "string"},
                                    "source": {"type": "string"},
                                    "data": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "actions": {
                    "Parse_JSON": {
                        "type": "ParseJson",
                        "inputs": {
                            "content": "@triggerBody()",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "timestamp": {"type": "string"},
                                    "event_type": {"type": "string"},
                                    "platform": {"type": "string"},
                                    "source": {"type": "string"},
                                    "data": {"type": "object"}
                                }
                            }
                        }
                    },
                    "Switch_on_Event_Type": {
                        "type": "Switch",
                        "expression": "@body('Parse_JSON')?['event_type']",
                        "cases": {
                            "platform_startup": {
                                "case": "platform_startup",
                                "actions": {
                                    "Send_Teams_Message_Startup": {
                                        "type": "ApiConnection",
                                        "inputs": {
                                            "host": {
                                                "connection": {
                                                    "name": "@parameters('$connections')['teams']['connectionId']"
                                                }
                                            },
                                            "method": "post",
                                            "path": "/flowbot/actions/notification/recipienttypes/channel",
                                            "queries": {
                                                "recipient": "your-channel-id"
                                            },
                                            "body": {
                                                "messageBody": "🚀 **Platform Startup Complete**\n\n✅ Services: @{body('Parse_JSON')?['data']?['healthy_services']}/@{body('Parse_JSON')?['data']?['total_services']}\n📊 Health: @{body('Parse_JSON')?['data']?['health_percentage']}%\n🕐 Time: @{body('Parse_JSON')?['timestamp']}"
                                            }
                                        }
                                    }
                                }
                            },
                            "service_health": {
                                "case": "service_health",
                                "actions": {
                                    "Condition_Service_Unhealthy": {
                                        "type": "If",
                                        "expression": {
                                            "and": [
                                                {
                                                    "equals": [
                                                        "@body('Parse_JSON')?['data']?['is_healthy']",
                                                        false
                                                    ]
                                                }
                                            ]
                                        },
                                        "actions": {
                                            "Send_Alert_Email": {
                                                "type": "ApiConnection",
                                                "inputs": {
                                                    "host": {
                                                        "connection": {
                                                            "name": "@parameters('$connections')['outlook']['connectionId']"
                                                        }
                                                    },
                                                    "method": "post",
                                                    "path": "/Mail",
                                                    "body": {
                                                        "To": "admin@company.com",
                                                        "Subject": "🚨 Service Alert: @{body('Parse_JSON')?['data']?['service_name']}",
                                                        "Body": "Service @{body('Parse_JSON')?['data']?['service_name']} is unhealthy.\n\nTimestamp: @{body('Parse_JSON')?['timestamp']}\nDetails: @{body('Parse_JSON')?['data']?['details']}"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "config_cleanup": {
                                "case": "config_cleanup",
                                "actions": {
                                    "Log_Cleanup_Results": {
                                        "type": "Compose",
                                        "inputs": "Cleanup completed: @{body('Parse_JSON')?['data']?['total_files_processed']} files processed, @{body('Parse_JSON')?['data']?['total_space_freed_mb']} MB freed"
                                    }
                                }
                            },
                            "error_alert": {
                                "case": "error_alert",
                                "actions": {
                                    "Send_Critical_Alert": {
                                        "type": "ApiConnection",
                                        "inputs": {
                                            "host": {
                                                "connection": {
                                                    "name": "@parameters('$connections')['teams']['connectionId']"
                                                }
                                            },
                                            "method": "post",
                                            "path": "/flowbot/actions/notification/recipienttypes/channel",
                                            "queries": {
                                                "recipient": "alerts-channel-id"
                                            },
                                            "body": {
                                                "messageBody": "🚨 **Critical Platform Error**\n\n❌ Type: @{body('Parse_JSON')?['data']?['error_type']}\n📝 Message: @{body('Parse_JSON')?['data']?['message']}\n🕐 Time: @{body('Parse_JSON')?['timestamp']}"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        template_file = self.config_file.parent / "power_automate_flow_template.json"
        with open(template_file, 'w') as f:
            json.dump(flow_template, f, indent=2)
        
        print(f"✅ Generated Power Automate flow template: {template_file}")
        return template_file
    
    def print_setup_instructions(self):
        """Print detailed setup instructions"""
        print("\n" + "="*60)
        print("🔧 POWER AUTOMATE SETUP INSTRUCTIONS")
        print("="*60)
        
        print("\n1️⃣ CREATE POWER AUTOMATE FLOW:")
        print("   • Go to https://make.powerautomate.com")
        print("   • Create new 'Instant cloud flow'")
        print("   • Choose 'When an HTTP request is received' trigger")
        print("   • Use the generated JSON schema from the template")
        
        print("\n2️⃣ CONFIGURE WEBHOOK URL:")
        print(f"   • Copy the HTTP POST URL from your flow")
        print(f"   • Update the webhook URL in: {self.config_file}")
        print(f"   • Or set environment variable: POWER_AUTOMATE_WEBHOOK_URL")
        
        print("\n3️⃣ ADD ACTIONS TO YOUR FLOW:")
        print("   • Parse JSON action (use provided schema)")
        print("   • Switch/Condition based on event_type")
        print("   • Teams notifications for platform events")
        print("   • Email alerts for service failures")
        print("   • Log cleanup results to SharePoint/Excel")
        
        print("\n4️⃣ TEST THE INTEGRATION:")
        print("   • Run: python power_automate_setup.py --test")
        print("   • Check your Power Automate run history")
        print("   • Verify Teams/Email notifications work")
        
        print("\n5️⃣ DEVICE MANAGEMENT INTEGRATION:")
        print("   • FortiGate health monitoring")
        print("   • Config backup notifications")
        print("   • Network topology change alerts")
        print("   • Automated incident creation")
        
        print("\n6️⃣ ENVIRONMENT SETUP:")
        print(f"   • Update credentials in: {self.env_file}")
        print("   • Set up service principal for Azure integration")
        print("   • Configure Teams channels and email groups")
        
        print("\n📊 AVAILABLE EVENT TYPES:")
        events = [
            "platform_startup - Platform initialization complete",
            "service_health - Individual service health status",
            "config_cleanup - Backup directory cleanup results",
            "device_status - FortiGate/FortiManager status updates",
            "error_alert - Critical errors and failures",
            "daily_report - Daily platform summary"
        ]
        for event in events:
            print(f"   • {event}")
        
        print(f"\n📁 Configuration files created in: {self.config_file.parent}")
        print("\n✅ Ready to integrate with your device management platform!")


async def main():
    setup = PowerAutomateSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - try to test webhook
        try:
            with open(setup.config_file, 'r') as f:
                config = json.load(f)
            
            webhook_url = config.get('webhook_url', '')
            if not webhook_url or 'YOUR_WORKFLOW_ID' in webhook_url:
                print("❌ Please configure your webhook URL first")
                print(f"📝 Edit: {setup.config_file}")
                return
            
            success = await setup.test_webhook(webhook_url)
            if success:
                print("🎉 Power Automate integration is working!")
            else:
                print("❌ Integration test failed - check your flow configuration")
        
        except FileNotFoundError:
            print("❌ Configuration file not found. Run setup first:")
            print("python power_automate_setup.py")
        
        return
    
    # Setup mode
    print("🚀 Setting up Power Automate Integration")
    
    setup.create_directories()
    setup.create_sample_config()
    setup.create_env_file()
    template_file = setup.generate_power_automate_flow_template()
    
    setup.print_setup_instructions()
    
    print(f"\n🔧 Next steps:")
    print(f"1. Edit configuration: {setup.config_file}")
    print(f"2. Update environment: {setup.env_file}")
    print(f"3. Import flow template: {template_file}")
    print(f"4. Test integration: python {__file__} --test")


if __name__ == "__main__":
    try:
        import aiohttp
    except ImportError:
        print("📦 Installing aiohttp...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        import aiohttp
    
    asyncio.run(main())