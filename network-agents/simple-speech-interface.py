#!/usr/bin/env python3
"""
Simple Speech Interface for Non-Technical Users
Easy-to-use voice control for network management
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import json
import os
import webbrowser
import threading
import time
from datetime import datetime
from neo4j import GraphDatabase
import re

app = Flask(__name__)

class SimpleSpeechManager:
    """
    Simplified speech manager for non-technical users
    """
    
    def __init__(self):
        self.driver = None
        self.connect_database()
        
        # Simple command patterns that anyone can understand
        self.simple_commands = {
            'device_count': {
                'patterns': ['how many', 'total devices', 'device count', 'devices do we have'],
                'description': 'Ask about total number of devices',
                'examples': ['How many devices do we have?', 'What is the total device count?']
            },
            'organization_health': {
                'patterns': ['status of', 'how is', 'health of', 'doing'],
                'description': 'Check organization health',
                'examples': ['How is Inspire Brands doing?', 'What is the status of Buffalo Wild Wings?']
            },
            'network_summary': {
                'patterns': ['summary', 'overview', 'report', 'everything'],
                'description': 'Get complete network overview',
                'examples': ['Give me a summary', 'Show me everything', 'Network overview']
            },
            'device_models': {
                'patterns': ['device models', 'what devices', 'models', 'equipment'],
                'description': 'See what types of equipment you have',
                'examples': ['What device models do we have?', 'Show me our equipment']
            },
            'problems': {
                'patterns': ['problems', 'issues', 'critical', 'broken', 'down'],
                'description': 'Check for network problems',
                'examples': ['Any problems?', 'Show me issues', 'What is broken?']
            }
        }
    
    def connect_database(self):
        """Connect to database with retry logic"""
        for attempt in range(5):
            try:
                self.driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
                with self.driver.session() as session:
                    session.run("RETURN 1")
                return True
            except Exception as e:
                print(f"Database connection attempt {attempt + 1}/5 failed: {e}")
                time.sleep(2)
        return False
    
    def parse_simple_command(self, command):
        """Parse command using simple pattern matching"""
        command_lower = command.lower()
        
        for intent, info in self.simple_commands.items():
            for pattern in info['patterns']:
                if pattern in command_lower:
                    # Extract organization name if mentioned
                    org_match = None
                    org_names = ['inspire brands', 'inspire', 'buffalo wild wings', 'buffalo', 'bww',
                                'arbys', 'arby', 'baskin robbins', 'baskin', 'dunkin', 'comcast']
                    
                    for org in org_names:
                        if org in command_lower:
                            org_match = org
                            break
                    
                    return {
                        'intent': intent,
                        'organization': org_match,
                        'original_command': command
                    }
        
        return {
            'intent': 'unknown',
            'organization': None,
            'original_command': command
        }
    
    def execute_simple_command(self, parsed_command):
        """Execute command with simple, clear responses"""
        if not self.driver:
            return {
                'success': False,
                'response': 'I cannot connect to the network database right now. Please check if the system is running.',
                'data': None
            }
        
        intent = parsed_command['intent']
        org = parsed_command['organization']
        
        try:
            with self.driver.session() as session:
                if intent == 'device_count':
                    result = session.run("MATCH (d:Device) RETURN count(d) as total")
                    total = result.single()["total"]
                    
                    # Get breakdown by organization
                    result = session.run("""
                        MATCH (d:Device)
                        RETURN d.organization_name as org, count(d) as count
                        ORDER BY count DESC
                        LIMIT 3
                    """)
                    
                    response = f"You have {total} devices total in your network. "
                    
                    top_orgs = []
                    for record in result:
                        if record['org']:
                            top_orgs.append(f"{record['org']}: {record['count']} devices")
                    
                    if top_orgs:
                        response += f"Your biggest locations are: {', '.join(top_orgs)}."
                    
                    return {
                        'success': True,
                        'response': response,
                        'data': {'total_devices': total, 'breakdown': top_orgs}
                    }
                
                elif intent == 'organization_health' and org:
                    result = session.run("""
                        MATCH (d:Device)
                        WHERE toLower(d.organization_name) CONTAINS toLower($org_name)
                        RETURN d.organization_name as org, 
                               count(d) as devices, 
                               avg(d.health_score) as health,
                               count(CASE WHEN d.status = 'critical' THEN 1 END) as critical
                        ORDER BY devices DESC
                        LIMIT 1
                    """, org_name=org)
                    
                    record = result.single()
                    if not record:
                        return {
                            'success': True,
                            'response': f"I could not find information about {org}. Try saying the full name like 'Inspire Brands' or 'Buffalo Wild Wings'.",
                            'data': None
                        }
                    
                    health = record['health']
                    status_word = "excellent" if health > 90 else "good" if health > 80 else "needs attention"
                    
                    response = f"{record['org']} has {record['devices']} devices. Their network health is {status_word} at {health:.1f}%. "
                    
                    if record['critical'] > 0:
                        response += f"However, {record['critical']} devices need immediate attention."
                    else:
                        response += "All devices are working normally."
                    
                    return {
                        'success': True,
                        'response': response,
                        'data': {
                            'organization': record['org'],
                            'devices': record['devices'],
                            'health_score': health,
                            'status': status_word
                        }
                    }
                
                elif intent == 'network_summary':
                    # Get overall stats
                    result = session.run("""
                        MATCH (d:Device)
                        RETURN count(d) as devices,
                               count(DISTINCT d.organization_name) as orgs,
                               avg(d.health_score) as avg_health,
                               count(CASE WHEN d.status = 'critical' THEN 1 END) as critical
                    """)
                    
                    stats = result.single()
                    health_status = "excellent" if stats['avg_health'] > 90 else "good" if stats['avg_health'] > 80 else "needs attention"
                    
                    response = f"Your network has {stats['devices']} devices across {stats['orgs']} locations. "
                    response += f"Overall health is {health_status} at {stats['avg_health']:.1f}%. "
                    
                    if stats['critical'] > 0:
                        response += f"You have {stats['critical']} devices that need immediate attention."
                    else:
                        response += "All devices are running normally."
                    
                    return {
                        'success': True,
                        'response': response,
                        'data': stats
                    }
                
                elif intent == 'device_models':
                    result = session.run("""
                        MATCH (d:Device)
                        WHERE d.model IS NOT NULL
                        RETURN d.model as model, count(d) as count
                        ORDER BY count DESC
                        LIMIT 5
                    """)
                    
                    models = []
                    for record in result:
                        models.append(f"{record['model']}: {record['count']} devices")
                    
                    if not models:
                        response = "I don't have device model information available right now."
                    else:
                        response = f"Your top equipment types are: {', '.join(models)}. "
                        response += "These include wireless access points, switches, and firewalls."
                    
                    return {
                        'success': True,
                        'response': response,
                        'data': {'models': models}
                    }
                
                elif intent == 'problems':
                    result = session.run("""
                        MATCH (d:Device)
                        WHERE d.status IN ['critical', 'warning'] OR d.health_score < 80
                        RETURN count(d) as problem_count
                    """)
                    
                    count = result.single()['problem_count']
                    
                    if count == 0:
                        response = "Great news! I don't see any network problems. All your devices are working normally."
                    else:
                        response = f"I found {count} devices that may need attention. These could be devices with low performance or connectivity issues."
                    
                    return {
                        'success': True,
                        'response': response,
                        'data': {'problem_count': count}
                    }
                
                else:
                    return {
                        'success': True,
                        'response': "I'm not sure what you're asking about. Try asking about device counts, organization status, or network problems. You can also ask for help to see what I can do.",
                        'data': None
                    }
        
        except Exception as e:
            return {
                'success': False,
                'response': f"I had trouble getting that information from the database. The error was: {str(e)}",
                'data': None
            }

# Initialize the simple speech manager
speech_manager = SimpleSpeechManager()

@app.route('/')
def simple_interface():
    """Simple interface for non-technical users"""
    return render_template('simple_interface.html')

@app.route('/api/simple-command', methods=['POST'])
def process_simple_command():
    """Process simple voice commands"""
    data = request.json
    command = data.get('command', '')
    
    if not command:
        return jsonify({
            'success': False,
            'response': 'I did not hear your command. Please try again.'
        })
    
    # Parse and execute command
    parsed = speech_manager.parse_simple_command(command)
    result = speech_manager.execute_simple_command(parsed)
    
    return jsonify({
        'success': result['success'],
        'response': result['response'],
        'data': result['data'],
        'intent': parsed['intent'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/help')
def get_help():
    """Get help information"""
    return jsonify({
        'success': True,
        'commands': speech_manager.simple_commands,
        'sample_phrases': [
            "How many devices do we have?",
            "How is Inspire Brands doing?",
            "Give me a network summary",
            "What device models do we have?",
            "Are there any problems?"
        ]
    })

@app.route('/api/status')
def get_status():
    """Check system status"""
    try:
        if speech_manager.driver:
            with speech_manager.driver.session() as session:
                result = session.run("MATCH (d:Device) RETURN count(d) as count")
                device_count = result.single()["count"]
            
            return jsonify({
                'success': True,
                'status': 'connected',
                'device_count': device_count,
                'message': f'Connected to network with {device_count} devices'
            })
        else:
            return jsonify({
                'success': False,
                'status': 'disconnected',
                'message': 'Cannot connect to network database'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    print("🎤 Starting Simple Speech Interface for Non-Technical Users")
    print("🌐 Access at: http://localhost:11031")
    print("🎯 Designed for easy voice control of network management")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:11031')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=11031, debug=False)