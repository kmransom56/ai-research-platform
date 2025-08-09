#!/usr/bin/env python3
"""
Web-Based Speech Interface for Network Management
Provides browser-based speech interaction with network infrastructure
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
from neo4j import GraphDatabase
import re
from typing import Dict, List, Any, Optional

app = Flask(__name__)

class WebSpeechNetworkManager:
    """
    Web-based speech interface for network management
    """
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Command patterns for network management
        self.command_patterns = {
            'device_count': [
                r'how many devices',
                r'device count',
                r'total devices',
                r'number of devices'
            ],
            'organization_status': [
                r'status of (.+)',
                r'how is (.+) doing',
                r'(.+) health',
                r'(.+) performance'
            ],
            'device_model': [
                r'show me (.+) devices',
                r'list (.+) models',
                r'(.+) inventory'
            ],
            'critical_devices': [
                r'critical devices',
                r'devices with issues',
                r'problem devices',
                r'devices needing attention'
            ],
            'network_summary': [
                r'network summary',
                r'executive summary',
                r'overall status',
                r'infrastructure overview'
            ],
            'top_models': [
                r'top device models',
                r'most common devices',
                r'device breakdown'
            ]
        }
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse voice command and extract intent"""
        command = command.lower().strip()
        
        for intent, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    return {
                        'intent': intent,
                        'command': command,
                        'match': match,
                        'parameters': match.groups() if match.groups() else []
                    }
        
        return {
            'intent': 'general_query',
            'command': command,
            'match': None,
            'parameters': []
        }
    
    def execute_device_count_query(self) -> Dict[str, Any]:
        """Get total device count with details"""
        with self.driver.session() as session:
            # Total devices
            result = session.run("MATCH (d:Device) RETURN count(d) as total_devices")
            total = result.single()["total_devices"]
            
            # Breakdown by organization
            result = session.run("""
                MATCH (d:Device)
                RETURN d.organization_name as org, count(d) as count
                ORDER BY count DESC
            """)
            
            org_breakdown = []
            for record in result:
                org_breakdown.append({
                    'organization': record['org'],
                    'count': record['count']
                })
            
            response_text = f"Your network infrastructure has {total} total devices. "
            if org_breakdown:
                top_3 = org_breakdown[:3]
                details = [f"{org['organization']} has {org['count']} devices" for org in top_3]
                response_text += f"Top deployments: {', '.join(details)}."
            
            return {
                'text': response_text,
                'data': {
                    'total_devices': total,
                    'organization_breakdown': org_breakdown
                }
            }
    
    def execute_organization_status_query(self, org_name: str) -> Dict[str, Any]:
        """Get organization health status"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WHERE toLower(d.organization_name) CONTAINS toLower($org_name)
                WITH d.organization_name as org_name,
                     count(d) as device_count,
                     avg(d.health_score) as avg_health,
                     count(CASE WHEN d.status = 'critical' THEN 1 END) as critical,
                     count(CASE WHEN d.status = 'warning' THEN 1 END) as warning,
                     count(CASE WHEN d.status = 'online' THEN 1 END) as healthy
                RETURN org_name, device_count, round(avg_health, 1) as avg_health, critical, warning, healthy
                ORDER BY device_count DESC
                LIMIT 1
            """, org_name=org_name)
            
            record = result.single()
            if not record:
                return {
                    'text': f"I couldn't find an organization matching {org_name}. Please check the name.",
                    'data': None
                }
            
            org = record["org_name"]
            devices = record["device_count"]
            health = record["avg_health"]
            critical = record["critical"]
            warning = record["warning"]
            healthy = record["healthy"]
            
            status = "excellent" if health > 90 else "good" if health > 80 else "needs attention"
            
            response_text = f"{org} has {devices} devices with {health}% average health, which is {status}. "
            
            if critical > 0:
                response_text += f"{critical} critical devices need immediate attention. "
            elif warning > 0:
                response_text += f"{warning} devices have warnings. "
            else:
                response_text += "All devices are operating normally. "
            
            return {
                'text': response_text,
                'data': {
                    'organization': org,
                    'total_devices': devices,
                    'avg_health_score': health,
                    'critical_count': critical,
                    'warning_count': warning,
                    'healthy_count': healthy
                }
            }
    
    def execute_critical_devices_query(self) -> Dict[str, Any]:
        """Get critical devices information"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WHERE d.status IN ['critical', 'warning'] OR d.health_score < 80
                RETURN d.name as device, d.organization_name as org, d.status as status, 
                       d.health_score as health, d.model as model
                ORDER BY 
                    CASE d.status 
                        WHEN 'critical' THEN 1 
                        WHEN 'warning' THEN 2 
                        ELSE 3 
                    END,
                    d.health_score ASC
                LIMIT 10
            """)
            
            devices = []
            for record in result:
                devices.append({
                    'name': record['device'],
                    'organization': record['org'],
                    'status': record['status'],
                    'health_score': record['health'],
                    'model': record['model']
                })
            
            if not devices:
                return {
                    'text': "Excellent! All devices are healthy with no critical issues detected.",
                    'data': {'critical_devices': []}
                }
            
            critical_count = len([d for d in devices if d['status'] == 'critical'])
            warning_count = len([d for d in devices if d['status'] == 'warning'])
            
            response_text = f"Found {len(devices)} devices needing attention: "
            if critical_count > 0:
                response_text += f"{critical_count} critical, "
            if warning_count > 0:
                response_text += f"{warning_count} warnings. "
            
            response_text += f"Top priority: {devices[0]['name']} at {devices[0]['organization']}."
            
            return {
                'text': response_text,
                'data': {
                    'critical_devices': devices,
                    'total_issues': len(devices),
                    'critical_count': critical_count,
                    'warning_count': warning_count
                }
            }
    
    def execute_network_summary_query(self) -> Dict[str, Any]:
        """Get executive network summary"""
        with self.driver.session() as session:
            # Overall stats
            result = session.run("""
                MATCH (d:Device)
                RETURN count(d) as total_devices,
                       count(DISTINCT d.organization_name) as orgs,
                       count(DISTINCT d.network_name) as networks,
                       avg(d.health_score) as avg_health,
                       count(CASE WHEN d.status = 'critical' THEN 1 END) as critical,
                       count(CASE WHEN d.status = 'warning' THEN 1 END) as warning
            """)
            stats = result.single()
            
            health_status = "excellent" if stats['avg_health'] > 90 else "good" if stats['avg_health'] > 80 else "needs attention"
            
            response_text = f"Infrastructure summary: {stats['total_devices']} devices across {stats['networks']} networks in {stats['orgs']} organizations. "
            response_text += f"Overall health is {stats['avg_health']:.1f}%, which is {health_status}. "
            
            if stats['critical'] > 0:
                response_text += f"Immediate action needed for {stats['critical']} critical devices. "
            elif stats['warning'] > 0:
                response_text += f"{stats['warning']} devices have warnings. "
            else:
                response_text += "All systems operating normally. "
            
            return {
                'text': response_text,
                'data': {
                    'total_devices': stats['total_devices'],
                    'organizations': stats['orgs'],
                    'networks': stats['networks'],
                    'avg_health_score': round(stats['avg_health'], 1),
                    'critical_count': stats['critical'],
                    'warning_count': stats['warning']
                }
            }
    
    def execute_top_models_query(self) -> Dict[str, Any]:
        """Get top device models"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WHERE d.model IS NOT NULL AND d.model <> ''
                WITH d.model as model, count(d) as count, collect(DISTINCT d.organization_name)[0..3] as orgs
                RETURN model, count, orgs
                ORDER BY count DESC
                LIMIT 10
            """)
            
            models = []
            total_devices = 0
            for record in result:
                models.append({
                    'model': record['model'],
                    'count': record['count'],
                    'organizations': record['orgs']
                })
                total_devices += record['count']
            
            if not models:
                return {
                    'text': "No device model information available.",
                    'data': {'top_models': []}
                }
            
            top_model = models[0]
            response_text = f"Top device models in your network: {top_model['model']} leads with {top_model['count']} devices. "
            response_text += f"Total of {len(models)} different models across {total_devices} devices."
            
            return {
                'text': response_text,
                'data': {
                    'top_models': models,
                    'total_models': len(models),
                    'total_devices': total_devices
                }
            }
    
    def execute_command(self, command_text: str) -> Dict[str, Any]:
        """Execute voice command and return structured response"""
        parsed = self.parse_command(command_text)
        intent = parsed['intent']
        parameters = parsed['parameters']
        
        try:
            if intent == 'device_count':
                return self.execute_device_count_query()
            
            elif intent == 'organization_status' and parameters:
                org_name = parameters[0]
                return self.execute_organization_status_query(org_name)
            
            elif intent == 'critical_devices':
                return self.execute_critical_devices_query()
            
            elif intent == 'network_summary':
                return self.execute_network_summary_query()
            
            elif intent == 'top_models':
                return self.execute_top_models_query()
            
            else:
                return {
                    'text': "I can help with device counts, organization status, critical devices, network summaries, or top device models. What would you like to know?",
                    'data': None
                }
                
        except Exception as e:
            return {
                'text': f"I encountered an error processing your request: {str(e)}. Please try again.",
                'data': None
            }
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()

# Initialize the manager
speech_manager = WebSpeechNetworkManager()

@app.route('/')
def index():
    """Main speech interface page"""
    return render_template('speech_interface.html')

@app.route('/api/process-command', methods=['POST'])
def process_command():
    """Process voice command via API"""
    data = request.json
    command_text = data.get('command', '')
    
    if not command_text:
        return jsonify({
            'success': False,
            'error': 'No command provided'
        })
    
    try:
        result = speech_manager.execute_command(command_text)
        return jsonify({
            'success': True,
            'response': result['text'],
            'data': result['data'],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/test-connection')
def test_connection():
    """Test database connection"""
    try:
        with speech_manager.driver.session() as session:
            result = session.run("MATCH (d:Device) RETURN count(d) as count")
            device_count = result.single()["count"]
            
        return jsonify({
            'success': True,
            'device_count': device_count,
            'message': f'Connected to network with {device_count} devices'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🌐 Starting Web Speech Interface for Network Management")
    print("🎤 Access at: http://localhost:11030")
    app.run(host='0.0.0.0', port=11030, debug=True)