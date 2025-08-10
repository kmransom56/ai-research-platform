#!/usr/bin/env python3
"""
Enhanced Voice Interface with Multi-Vendor Support
Supports Meraki and Fortinet device queries for restaurant networks
Uses proven FortiManager API from https://github.com/kmransom56/meraki_management_application
"""

import json
import logging
from flask import Flask, render_template, request, jsonify
from neo4j import GraphDatabase
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class EnhancedVoiceProcessor:
    """Enhanced voice command processor with multi-vendor support"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
        
        # Enhanced command patterns for multi-vendor support
        self.command_patterns = {
            # Device inventory commands
            'device_count': [
                r'how many (?:devices|equipment) do we have',
                r'total (?:device|equipment) count',
                r'device inventory',
                r'show me (?:all|our) devices'
            ],
            
            # Vendor-specific commands
            'fortinet_devices': [
                r'(?:show|list) (?:fortinet|fortigate|fortiap) (?:devices|equipment)',
                r'how many (?:fortinet|fortigate|fortiap) devices',
                r'fortinet (?:status|health|inventory)'
            ],
            
            'meraki_devices': [
                r'(?:show|list) meraki (?:devices|equipment)',
                r'how many meraki devices',
                r'meraki (?:status|health|inventory)'
            ],
            
            # Restaurant-specific commands
            'restaurant_security': [
                r'(?:how are|check|status of) (?:our|the) (?:firewalls|security)',
                r'(?:firewall|security) (?:status|health)',
                r'(?:show|list) security (?:devices|equipment|appliances)'
            ],
            
            'restaurant_wifi': [
                r'(?:how are|check|status of) (?:our|the) (?:wifi|wireless|access points)',
                r'(?:wifi|wireless|ap|access point) (?:status|health)',
                r'(?:show|list) (?:wifi|wireless|access points)'
            ],
            
            # Organization-specific commands
            'arbys_status': [
                r"(?:how is|check|status of) (?:arby's|arbys)",
                r"arby's? (?:devices|status|health)"
            ],
            
            'bww_status': [
                r'(?:how is|check|status of) (?:buffalo wild wings|bww)',
                r'(?:buffalo wild wings|bww) (?:devices|status|health)'
            ],
            
            'sonic_status': [
                r'(?:how is|check|status of) sonic',
                r'sonic (?:devices|status|health)'
            ],
            
            # Network health commands
            'network_health': [
                r'(?:network|overall) (?:health|status)',
                r'how (?:is|are) (?:our|the) networks?',
                r'system (?:overview|status|health)'
            ],
            
            # Critical issues
            'critical_issues': [
                r'(?:show|list|any) (?:critical|urgent|emergency) (?:issues|alerts|problems)',
                r'what (?:needs attention|is broken|is down)',
                r'(?:critical|urgent) (?:devices|alerts)'
            ]
        }
    
    def process_command(self, command):
        """Process voice command and return appropriate response"""
        try:
            command_lower = command.lower()
            logger.info(f"Processing command: {command}")
            
            # Match command to patterns
            for command_type, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, command_lower):
                        response = self._execute_command(command_type, command_lower)
                        return {
                            'success': True,
                            'response': response,
                            'command_type': command_type
                        }
            
            # If no pattern matches, try general query
            response = self._handle_general_query(command_lower)
            return {
                'success': True,
                'response': response,
                'command_type': 'general'
            }
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                'success': False,
                'response': f"Sorry, I encountered an error: {str(e)}",
                'command_type': 'error'
            }
    
    def _execute_command(self, command_type, command):
        """Execute specific command type"""
        try:
            with self.driver.session() as session:
                if command_type == 'device_count':
                    return self._get_device_count(session)
                
                elif command_type == 'fortinet_devices':
                    return self._get_fortinet_devices(session)
                
                elif command_type == 'meraki_devices':
                    return self._get_meraki_devices(session)
                
                elif command_type == 'restaurant_security':
                    return self._get_security_devices(session)
                
                elif command_type == 'restaurant_wifi':
                    return self._get_wifi_devices(session)
                
                elif command_type in ['arbys_status', 'bww_status', 'sonic_status']:
                    org_name = self._extract_organization_name(command_type)
                    return self._get_organization_status(session, org_name)
                
                elif command_type == 'network_health':
                    return self._get_network_health(session)
                
                elif command_type == 'critical_issues':
                    return self._get_critical_issues(session)
                
                else:
                    return "I'm not sure how to handle that command yet."
                    
        except Exception as e:
            logger.error(f"Error executing command {command_type}: {str(e)}")
            return f"Sorry, I couldn't process that request: {str(e)}"
    
    def _get_device_count(self, session):
        """Get total device count with vendor breakdown"""
        result = session.run("""
            MATCH (d:Device)
            RETURN d.vendor as vendor, count(d) as count
            ORDER BY count DESC
        """)
        
        vendor_counts = {}
        total_count = 0
        
        for record in result:
            vendor = record['vendor'] or 'Unknown'
            count = record['count']
            vendor_counts[vendor] = count
            total_count += count
        
        if total_count == 0:
            return "No devices found in the database. Please run device discovery first."
        
        response = f"We have {total_count:,} total devices across our restaurant networks. "
        
        if vendor_counts:
            response += "Breakdown by vendor: "
            vendor_parts = []
            for vendor, count in vendor_counts.items():
                vendor_parts.append(f"{count:,} {vendor} devices")
            response += ", ".join(vendor_parts) + "."
        
        return response
    
    def _get_fortinet_devices(self, session):
        """Get Fortinet device information"""
        result = session.run("""
            MATCH (d:Device {vendor: 'Fortinet'})
            RETURN d.device_type as device_type, d.status as status, count(d) as count
        """)
        
        device_types = {}
        total_count = 0
        online_count = 0
        
        for record in result:
            device_type = record['device_type'] or 'Unknown'
            status = record['status']
            count = record['count']
            
            if device_type not in device_types:
                device_types[device_type] = {'total': 0, 'online': 0}
            
            device_types[device_type]['total'] += count
            total_count += count
            
            if status == 'online':
                device_types[device_type]['online'] += count
                online_count += count
        
        if total_count == 0:
            return "No Fortinet devices found. They may not have been discovered yet."
        
        health_pct = (online_count / total_count) * 100 if total_count > 0 else 0
        
        response = f"We have {total_count} Fortinet devices with {health_pct:.1f}% online. "
        
        if device_types:
            type_parts = []
            for device_type, counts in device_types.items():
                type_parts.append(f"{counts['total']} {device_type}s")
            response += f"Types: {', '.join(type_parts)}. "
        
        if health_pct < 95:
            offline_count = total_count - online_count
            response += f"⚠️ {offline_count} devices need attention."
        
        return response
    
    def _get_meraki_devices(self, session):
        """Get Meraki device information"""
        result = session.run("""
            MATCH (d:Device {vendor: 'Meraki'})
            RETURN d.device_type as device_type, d.status as status, count(d) as count
        """)
        
        device_types = {}
        total_count = 0
        online_count = 0
        
        for record in result:
            device_type = record['device_type'] or 'Unknown'
            status = record['status']
            count = record['count']
            
            if device_type not in device_types:
                device_types[device_type] = {'total': 0, 'online': 0}
            
            device_types[device_type]['total'] += count
            total_count += count
            
            if status == 'online':
                device_types[device_type]['online'] += count
                online_count += count
        
        if total_count == 0:
            return "No Meraki devices found. They may not have been discovered yet."
        
        health_pct = (online_count / total_count) * 100 if total_count > 0 else 0
        
        response = f"We have {total_count} Meraki devices with {health_pct:.1f}% online. "
        
        if device_types:
            type_parts = []
            for device_type, counts in device_types.items():
                type_parts.append(f"{counts['total']} {device_type}s")
            response += f"Types: {', '.join(type_parts)}. "
        
        if health_pct < 95:
            offline_count = total_count - online_count
            response += f"⚠️ {offline_count} devices need attention."
        
        return response
    
    def _get_security_devices(self, session):
        """Get security devices (firewalls, security appliances)"""
        result = session.run("""
            MATCH (d:Device)
            WHERE d.device_type IN ['FortiGate', 'Security Appliance', 'Firewall']
               OR d.model CONTAINS 'MX'
            RETURN d.vendor as vendor, d.device_type as device_type, 
                   d.status as status, count(d) as count
        """)
        
        security_devices = {}
        total_count = 0
        online_count = 0
        
        for record in result:
            vendor = record['vendor'] or 'Unknown'
            device_type = record['device_type']
            status = record['status']
            count = record['count']
            
            key = f"{vendor} {device_type}"
            if key not in security_devices:
                security_devices[key] = {'total': 0, 'online': 0}
            
            security_devices[key]['total'] += count
            total_count += count
            
            if status == 'online':
                security_devices[key]['online'] += count
                online_count += count
        
        if total_count == 0:
            return "No security devices found in the network."
        
        health_pct = (online_count / total_count) * 100 if total_count > 0 else 0
        
        response = f"Restaurant security status: {total_count} security devices with {health_pct:.1f}% online. "
        
        if security_devices:
            device_parts = []
            for device_key, counts in security_devices.items():
                device_parts.append(f"{counts['total']} {device_key}")
            response += f"Devices: {', '.join(device_parts)}. "
        
        if health_pct < 100:
            offline_count = total_count - online_count
            response += f"🚨 {offline_count} security devices are offline - immediate attention needed!"
        else:
            response += "✅ All security systems operational."
        
        return response
    
    def _get_wifi_devices(self, session):
        """Get WiFi devices (access points)"""
        result = session.run("""
            MATCH (d:Device)
            WHERE d.device_type IN ['Access Point', 'FortiAP', 'WiFi']
               OR d.model CONTAINS 'MR'
               OR d.model CONTAINS 'FortiAP'
            RETURN d.vendor as vendor, d.status as status, count(d) as count
        """)
        
        wifi_devices = {}
        total_count = 0
        online_count = 0
        
        for record in result:
            vendor = record['vendor'] or 'Unknown'
            status = record['status']
            count = record['count']
            
            if vendor not in wifi_devices:
                wifi_devices[vendor] = {'total': 0, 'online': 0}
            
            wifi_devices[vendor]['total'] += count
            total_count += count
            
            if status == 'online':
                wifi_devices[vendor]['online'] += count
                online_count += count
        
        if total_count == 0:
            return "No WiFi access points found in the network."
        
        health_pct = (online_count / total_count) * 100 if total_count > 0 else 0
        
        response = f"Restaurant WiFi status: {total_count} access points with {health_pct:.1f}% online. "
        
        if wifi_devices:
            vendor_parts = []
            for vendor, counts in wifi_devices.items():
                vendor_parts.append(f"{counts['total']} {vendor} APs")
            response += f"Equipment: {', '.join(vendor_parts)}. "
        
        if health_pct < 95:
            offline_count = total_count - online_count
            response += f"⚠️ {offline_count} access points down - may affect customer WiFi."
        else:
            response += "✅ Customer WiFi systems operating normally."
        
        return response
    
    def _extract_organization_name(self, command_type):
        """Extract organization name from command type"""
        if command_type == 'arbys_status':
            return "Arby's"
        elif command_type == 'bww_status':
            return "Buffalo Wild Wings"
        elif command_type == 'sonic_status':
            return "Sonic"
        else:
            return "Unknown"
    
    def _get_organization_status(self, session, org_name):
        """Get status for specific restaurant organization"""
        # Try different name variations
        name_patterns = [org_name]
        if org_name == "Arby's":
            name_patterns.extend(["Arbys", "ARBYS"])
        elif org_name == "Buffalo Wild Wings":
            name_patterns.extend(["BWW", "Buffalo Wild Wings"])
        elif org_name == "Sonic":
            name_patterns.extend(["SONIC", "Sonic Drive-In"])
        
        for name_pattern in name_patterns:
            result = session.run("""
                MATCH (d:Device)
                WHERE d.organization_name CONTAINS $org_name
                   OR d.site CONTAINS $org_name
                RETURN d.vendor as vendor, d.device_type as device_type,
                       d.status as status, count(d) as count
            """, org_name=name_pattern)
            
            devices = {}
            total_count = 0
            online_count = 0
            
            for record in result:
                vendor = record['vendor'] or 'Unknown'
                device_type = record['device_type']
                status = record['status']
                count = record['count']
                
                key = f"{vendor} {device_type}"
                if key not in devices:
                    devices[key] = {'total': 0, 'online': 0}
                
                devices[key]['total'] += count
                total_count += count
                
                if status == 'online':
                    devices[key]['online'] += count
                    online_count += count
            
            if total_count > 0:
                health_pct = (online_count / total_count) * 100 if total_count > 0 else 0
                
                response = f"{org_name} network status: {total_count} devices with {health_pct:.1f}% health. "
                
                if devices:
                    device_parts = []
                    for device_key, counts in devices.items():
                        device_parts.append(f"{counts['total']} {device_key}")
                    response += f"Equipment: {', '.join(device_parts)}. "
                
                if health_pct < 95:
                    offline_count = total_count - online_count
                    response += f"⚠️ {offline_count} devices need attention."
                else:
                    response += "✅ All systems operating normally."
                
                return response
        
        return f"No devices found for {org_name}. The organization may not be in our system yet."
    
    def _get_network_health(self, session):
        """Get overall network health summary"""
        result = session.run("""
            MATCH (d:Device)
            RETURN d.vendor as vendor, d.status as status, count(d) as count
        """)
        
        vendor_stats = {}
        total_devices = 0
        total_online = 0
        
        for record in result:
            vendor = record['vendor'] or 'Unknown'
            status = record['status']
            count = record['count']
            
            if vendor not in vendor_stats:
                vendor_stats[vendor] = {'total': 0, 'online': 0}
            
            vendor_stats[vendor]['total'] += count
            total_devices += count
            
            if status == 'online':
                vendor_stats[vendor]['online'] += count
                total_online += count
        
        if total_devices == 0:
            return "No network data available. Please run device discovery first."
        
        overall_health = (total_online / total_devices) * 100 if total_devices > 0 else 0
        
        response = f"Overall network health: {overall_health:.1f}% ({total_online:,} of {total_devices:,} devices online). "
        
        if vendor_stats:
            vendor_parts = []
            for vendor, stats in vendor_stats.items():
                health = (stats['online'] / stats['total']) * 100 if stats['total'] > 0 else 0
                vendor_parts.append(f"{vendor} {health:.1f}%")
            response += f"By vendor: {', '.join(vendor_parts)}. "
        
        if overall_health >= 95:
            response += "✅ Network operating normally."
        elif overall_health >= 90:
            response += "⚠️ Minor issues detected - monitoring recommended."
        else:
            response += "🚨 Significant network issues - immediate attention required!"
        
        return response
    
    def _get_critical_issues(self, session):
        """Get critical issues that need immediate attention"""
        result = session.run("""
            MATCH (d:Device {status: 'offline'})
            WHERE d.device_type IN ['FortiGate', 'Security Appliance', 'Firewall'] 
               OR d.model CONTAINS 'MX'
            RETURN d.name as name, d.vendor as vendor, d.device_type as device_type,
                   d.organization_name as org
            LIMIT 10
        """)
        
        critical_devices = []
        for record in result:
            critical_devices.append({
                'name': record['name'],
                'vendor': record['vendor'],
                'type': record['device_type'],
                'organization': record['org']
            })
        
        if not critical_devices:
            # Check for other offline devices
            result = session.run("""
                MATCH (d:Device {status: 'offline'})
                RETURN d.name as name, d.vendor as vendor, d.device_type as device_type,
                       d.organization_name as org
                LIMIT 5
            """)
            
            offline_devices = []
            for record in result:
                offline_devices.append({
                    'name': record['name'],
                    'vendor': record['vendor'],
                    'type': record['device_type'],
                    'organization': record['org']
                })
            
            if not offline_devices:
                return "✅ No critical issues detected. All systems operating normally."
            else:
                response = f"⚠️ {len(offline_devices)} devices are offline but not critical: "
                device_names = [f"{d['name']} ({d['type']})" for d in offline_devices[:3]]
                response += ", ".join(device_names)
                if len(offline_devices) > 3:
                    response += f" and {len(offline_devices) - 3} others."
                return response
        else:
            response = f"🚨 CRITICAL: {len(critical_devices)} security devices are offline! "
            critical_names = [f"{d['name']} at {d['organization']}" for d in critical_devices[:3]]
            response += ", ".join(critical_names)
            if len(critical_devices) > 3:
                response += f" and {len(critical_devices) - 3} others."
            response += " - Immediate attention required for restaurant security!"
            return response
    
    def _handle_general_query(self, command):
        """Handle general queries that don't match specific patterns"""
        # Try to find relevant devices or networks
        with self.driver.session() as session:
            # Look for specific device names or types mentioned
            if 'fortigate' in command or 'firewall' in command:
                return self._get_security_devices(session)
            elif 'meraki' in command:
                return self._get_meraki_devices(session)
            elif 'fortinet' in command:
                return self._get_fortinet_devices(session)
            elif 'wifi' in command or 'wireless' in command:
                return self._get_wifi_devices(session)
            else:
                return "I can help you check device status, network health, or specific restaurant chains. Try asking about Fortinet devices, Meraki equipment, network health, or specific organizations like Arby's or Buffalo Wild Wings."

# Initialize voice processor
voice_processor = EnhancedVoiceProcessor()

@app.route('/')
def index():
    """Main voice interface page"""
    return render_template('enhanced_voice_interface.html')

@app.route('/api/process-command', methods=['POST'])
def process_command():
    """Process voice command API endpoint"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({
                'success': False,
                'response': 'No command provided'
            })
        
        result = voice_processor.process_command(command)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'response': f'Error processing command: {str(e)}'
        })

if __name__ == '__main__':
    print("🎤 Starting Enhanced Multi-Vendor Voice Interface...")
    print("🌐 Access at: http://localhost:11033")
    print("✅ Supporting Meraki and Fortinet devices")
    app.run(host='0.0.0.0', port=11033, debug=False)