#!/usr/bin/env python3
"""
Restaurant Equipment Voice Interface
Enhanced voice commands for troubleshooting restaurant devices:
- Point of Sale (POS) systems
- Kitchen display systems
- Drive-thru equipment
- Kiosks and digital menu boards
"""

from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
from neo4j import GraphDatabase
import re
from typing import Dict, List, Any

app = Flask(__name__)

class RestaurantEquipmentVoiceManager:
    """
    Voice interface specifically designed for restaurant equipment management
    """
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Restaurant-specific voice commands
        self.restaurant_commands = {
            'pos_status': {
                'patterns': ['pos', 'point of sale', 'register', 'payment', 'checkout'],
                'description': 'Check POS system status',
                'examples': ['How are our POS systems?', 'Any POS issues?', 'Check payment systems']
            },
            'kitchen_equipment': {
                'patterns': ['kitchen', 'kds', 'display', 'prep', 'cook', 'food prep'],
                'description': 'Kitchen equipment status',
                'examples': ['Check kitchen displays', 'How is the kitchen equipment?']
            },
            'drive_thru': {
                'patterns': ['drive thru', 'drive through', 'dt', 'drive-thru'],
                'description': 'Drive-thru equipment status',  
                'examples': ['Check drive-thru', 'Any drive-thru issues?']
            },
            'kiosk_status': {
                'patterns': ['kiosk', 'self order', 'self service', 'ordering'],
                'description': 'Self-service kiosk status',
                'examples': ['How are the kiosks?', 'Check self-order systems']
            },
            'menu_boards': {
                'patterns': ['menu board', 'digital menu', 'signage', 'display board'],
                'description': 'Digital menu board status',
                'examples': ['Check menu boards', 'Are digital menus working?']
            },
            'store_equipment': {
                'patterns': ['store', 'location', 'restaurant', 'site'],
                'description': 'All equipment for specific location',
                'examples': ['Check store 4472', 'How is location A01217?']
            },
            'critical_equipment': {
                'patterns': ['critical', 'down', 'offline', 'broken', 'urgent'],
                'description': 'Critical equipment issues',
                'examples': ['What equipment is down?', 'Critical issues?']
            }
        }
    
    def parse_restaurant_command(self, command: str) -> Dict[str, Any]:
        """Parse restaurant-specific voice commands"""
        command_lower = command.lower()
        
        for intent, info in self.restaurant_commands.items():
            for pattern in info['patterns']:
                if pattern in command_lower:
                    # Extract location/store info if mentioned
                    location_match = None
                    
                    # Look for store numbers, location codes
                    location_patterns = [
                        r'store\s*(\d+)',
                        r'location\s*([a-z]\d+)',
                        r'site\s*(\d+)',
                        r'restaurant\s*(\d+)',
                        r'([a-z]\d{5})'  # Like A01217
                    ]
                    
                    for loc_pattern in location_patterns:
                        match = re.search(loc_pattern, command_lower)
                        if match:
                            location_match = match.group(1)
                            break
                    
                    # Look for organization names
                    org_match = None
                    org_names = ['inspire brands', 'inspire', 'buffalo wild wings', 'buffalo', 'bww',
                                'arbys', 'arby', 'baskin robbins', 'baskin', 'dunkin', 'comcast']
                    
                    for org in org_names:
                        if org in command_lower:
                            org_match = org
                            break
                    
                    return {
                        'intent': intent,
                        'location': location_match,
                        'organization': org_match,
                        'original_command': command
                    }
        
        return {
            'intent': 'general_restaurant',
            'location': None,
            'organization': None,
            'original_command': command
        }
    
    def execute_restaurant_command(self, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute restaurant equipment commands"""
        if not self.driver:
            return {
                'success': False,
                'response': 'Cannot connect to restaurant equipment database.',
                'data': None
            }
        
        intent = parsed_command['intent']
        location = parsed_command['location']
        org = parsed_command['organization']
        
        try:
            with self.driver.session() as session:
                if intent == 'pos_status':
                    return self.check_pos_systems(session, location, org)
                elif intent == 'kitchen_equipment':
                    return self.check_kitchen_equipment(session, location, org)
                elif intent == 'drive_thru':
                    return self.check_drive_thru(session, location, org)
                elif intent == 'kiosk_status':
                    return self.check_kiosks(session, location, org)
                elif intent == 'menu_boards':
                    return self.check_menu_boards(session, location, org)
                elif intent == 'store_equipment':
                    return self.check_store_equipment(session, location, org)
                elif intent == 'critical_equipment':
                    return self.check_critical_equipment(session, location, org)
                else:
                    return self.general_equipment_status(session, location, org)
                    
        except Exception as e:
            return {
                'success': False,
                'response': f'Error checking restaurant equipment: {str(e)}',
                'data': None
            }
    
    def check_pos_systems(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check POS system status"""
        
        # Since we don't have actual POS data yet, simulate based on network infrastructure
        base_query = """
            MATCH (d:Device)
            WHERE d.model CONTAINS 'MX' OR d.product_type = 'appliance'
        """
        
        if location:
            base_query += f" AND (d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}')"
        
        if org and 'inspire' in org.lower():
            base_query += " AND d.organization_name = 'Inspire Brands'"
        elif org and 'buffalo' in org.lower():
            base_query += " AND d.organization_name = 'Buffalo-Wild-Wings'"
        elif org and 'arby' in org.lower():
            base_query += " AND d.organization_name = 'Arby\\'s'"
        
        base_query += """
            RETURN count(d) as device_count,
                   avg(d.health_score) as avg_health,
                   count(CASE WHEN d.health_score < 80 THEN 1 END) as low_health
        """
        
        result = session.run(base_query)
        record = result.single()
        
        if record and record['device_count'] > 0:
            device_count = record['device_count']
            avg_health = record['avg_health']
            low_health = record['low_health']
            
            health_status = "excellent" if avg_health > 95 else "good" if avg_health > 85 else "needs attention"
            
            location_text = f" at {location}" if location else ""
            org_text = f" for {org}" if org else ""
            
            if low_health == 0:
                response = f"POS systems{location_text}{org_text} are running smoothly. Network infrastructure supporting {device_count} devices with {health_status} health at {avg_health:.1f}%. All payment processing should be operational."
            else:
                response = f"Found {low_health} network devices{location_text}{org_text} with low health scores that could impact POS operations. Overall infrastructure health is {avg_health:.1f}%. I recommend checking these locations for potential payment system issues."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'device_count': device_count,
                    'health_score': avg_health,
                    'issues': low_health
                }
            }
        else:
            return {
                'success': True,
                'response': f"No network infrastructure found{' for ' + location if location else ''}{' in ' + org if org else ''}. Unable to assess POS system status.",
                'data': None
            }
    
    def check_kitchen_equipment(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check kitchen equipment status based on network infrastructure"""
        
        # Kitchen equipment typically connects to switches
        base_query = """
            MATCH (d:Device)
            WHERE d.product_type = 'switch' OR d.model CONTAINS 'MS'
        """
        
        if location:
            base_query += f" AND (d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}')"
        
        if org:
            base_query += self.get_org_filter(org)
        
        base_query += """
            RETURN count(d) as switch_count,
                   avg(d.health_score) as avg_health,
                   count(CASE WHEN d.health_score < 85 THEN 1 END) as issues
        """
        
        result = session.run(base_query)
        record = result.single()
        
        if record and record['switch_count'] > 0:
            switch_count = record['switch_count']
            avg_health = record['avg_health']
            issues = record['issues']
            
            location_text = f" at {location}" if location else ""
            org_text = f" for {org}" if org else ""
            
            if issues == 0:
                response = f"Kitchen network infrastructure{location_text}{org_text} is running well. {switch_count} switches with {avg_health:.1f}% health. Kitchen display systems, prep timers, and cooking equipment should have good connectivity."
            else:
                response = f"Found {issues} network switches{location_text}{org_text} with potential issues that could affect kitchen equipment. Average health is {avg_health:.1f}%. Kitchen displays or prep systems may be experiencing connectivity problems."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'switches': switch_count,
                    'health': avg_health,
                    'issues': issues
                }
            }
        else:
            return {
                'success': True,
                'response': f"No kitchen network infrastructure found{' for ' + location if location else ''}. Unable to assess kitchen equipment status.",
                'data': None
            }
    
    def check_critical_equipment(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check for critical equipment issues"""
        
        base_query = """
            MATCH (d:Device)
            WHERE d.health_score < 75 OR d.status IN ['critical', 'warning']
        """
        
        if location:
            base_query += f" AND (d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}')"
        
        if org:
            base_query += self.get_org_filter(org)
        
        base_query += """
            RETURN d.name as device_name,
                   d.network_name as location,
                   d.model as model,
                   d.health_score as health,
                   d.organization_name as org
            ORDER BY d.health_score ASC
            LIMIT 10
        """
        
        result = session.run(base_query)
        critical_devices = list(result)
        
        if critical_devices:
            location_text = f" at {location}" if location else ""
            org_text = f" for {org}" if org else ""
            
            response = f"Found {len(critical_devices)} critical network devices{location_text}{org_text} that could impact restaurant operations:\\n\\n"
            
            for device in critical_devices:
                response += f"• {device['location']}: {device['model']} ({device['health']}% health) - Could affect POS, kitchen displays, or other critical systems\\n"
            
            response += "\\nI recommend immediate attention to restore full restaurant functionality."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'critical_devices': len(critical_devices),
                    'locations': list(set([d['location'] for d in critical_devices if d['location']]))
                }
            }
        else:
            response = f"Great news! No critical network infrastructure issues found{location_text}{org_text}. All restaurant equipment should be operating normally."
            
            return {
                'success': True,
                'response': response,
                'data': {'critical_devices': 0}
            }
    
    def get_org_filter(self, org: str) -> str:
        """Get organization filter for queries"""
        if 'inspire' in org.lower():
            return " AND d.organization_name = 'Inspire Brands'"
        elif 'buffalo' in org.lower():
            return " AND d.organization_name = 'Buffalo-Wild-Wings'"
        elif 'arby' in org.lower():
            return " AND d.organization_name = 'Arby\\'s'"
        elif 'baskin' in org.lower():
            return " AND d.organization_name = 'BASKIN ROBBINS'"
        elif 'dunkin' in org.lower():
            return " AND d.organization_name CONTAINS 'Dunkin'"
        else:
            return ""
    
    def general_equipment_status(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """General restaurant equipment status"""
        
        base_query = """
            MATCH (d:Device)
            RETURN count(d) as total_devices,
                   avg(d.health_score) as avg_health,
                   count(CASE WHEN d.health_score < 80 THEN 1 END) as low_health,
                   count(DISTINCT d.network_name) as locations
        """
        
        if location:
            base_query = base_query.replace("MATCH (d:Device)", 
                f"MATCH (d:Device) WHERE d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}'")
        
        if org:
            org_filter = self.get_org_filter(org)
            if "WHERE" in base_query:
                base_query = base_query.replace("RETURN", f"{org_filter} RETURN")
            else:
                base_query = base_query.replace("MATCH (d:Device)", f"MATCH (d:Device) WHERE {org_filter[5:]}")
        
        result = session.run(base_query)
        record = result.single()
        
        if record:
            total = record['total_devices']
            health = record['avg_health']
            issues = record['low_health']
            locations = record['locations']
            
            location_text = f" at {location}" if location else f" across {locations} locations"
            org_text = f" for {org}" if org else ""
            
            if issues == 0:
                response = f"Restaurant equipment network{location_text}{org_text} is running smoothly. {total} network devices with {health:.1f}% average health. POS systems, kitchen equipment, and customer-facing devices should all be operational."
            else:
                response = f"Restaurant equipment network{location_text}{org_text} shows {issues} devices with potential issues out of {total} total. Average health is {health:.1f}%. Some POS, kitchen, or customer systems may be affected."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'total_devices': total,
                    'health_score': health,
                    'issues': issues,
                    'locations': locations
                }
            }
        else:
            return {
                'success': True,
                'response': "No restaurant network infrastructure found for the specified criteria.",
                'data': None
            }
    
    def check_store_equipment(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check all equipment for a specific store/location"""
        if location:
            return self.general_equipment_status(session, location, org)
        else:
            return self.general_equipment_status(session, None, org)
    
    def check_kiosks(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check kiosk status based on network infrastructure"""
        base_query = """
            MATCH (d:Device)
            WHERE d.model CONTAINS 'MR' OR d.model CONTAINS 'MX'
        """
        
        if location:
            base_query += f" AND (d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}')"
        
        if org:
            base_query += self.get_org_filter(org)
        
        base_query += """
            RETURN count(d) as device_count,
                   avg(d.health_score) as avg_health,
                   count(CASE WHEN d.health_score < 80 THEN 1 END) as issues
        """
        
        result = session.run(base_query)
        record = result.single()
        
        if record and record['device_count'] > 0:
            device_count = record['device_count']
            avg_health = record['avg_health']
            issues = record['issues']
            
            location_text = f" at {location}" if location else ""
            org_text = f" for {org}" if org else ""
            
            if issues == 0:
                response = f"Kiosk network connectivity{location_text}{org_text} looks good. {device_count} network devices with {avg_health:.1f}% health should support self-service ordering systems."
            else:
                response = f"Found {issues} network issues{location_text}{org_text} that could affect kiosk operations. Overall health is {avg_health:.1f}%. Self-service systems may experience connectivity problems."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'device_count': device_count,
                    'health_score': avg_health,
                    'issues': issues
                }
            }
        else:
            return {
                'success': True,
                'response': f"No kiosk network infrastructure found{' for ' + location if location else ''}.",
                'data': None
            }
    
    def check_menu_boards(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check digital menu board connectivity"""
        base_query = """
            MATCH (d:Device)
            RETURN count(d) as device_count,
                   avg(d.health_score) as avg_health,
                   count(CASE WHEN d.health_score < 85 THEN 1 END) as issues
        """
        
        if location:
            base_query = base_query.replace("MATCH (d:Device)", 
                f"MATCH (d:Device) WHERE d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}'")
        
        if org:
            org_filter = self.get_org_filter(org)
            if "WHERE" in base_query:
                base_query = base_query.replace("RETURN", f"{org_filter} RETURN")
            else:
                base_query = base_query.replace("MATCH (d:Device)", f"MATCH (d:Device) WHERE {org_filter[5:]}")
        
        result = session.run(base_query)
        record = result.single()
        
        if record:
            device_count = record['device_count']
            avg_health = record['avg_health']
            issues = record['issues']
            
            location_text = f" at {location}" if location else ""
            org_text = f" for {org}" if org else ""
            
            if issues == 0:
                response = f"Digital menu board connectivity{location_text}{org_text} is good. Network infrastructure ({device_count} devices at {avg_health:.1f}% health) should support digital signage and menu displays."
            else:
                response = f"Found {issues} network devices{location_text}{org_text} with potential issues. Menu boards may experience display problems with {avg_health:.1f}% network health."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'device_count': device_count,
                    'health_score': avg_health,
                    'issues': issues
                }
            }
        else:
            return {
                'success': True,
                'response': "No menu board network infrastructure found.",
                'data': None
            }
    
    def check_drive_thru(self, session, location: str = None, org: str = None) -> Dict[str, Any]:
        """Check drive-thru equipment connectivity"""
        base_query = """
            MATCH (d:Device)
            WHERE d.model CONTAINS 'MX' OR d.model CONTAINS 'MR'
        """
        
        if location:
            base_query += f" AND (d.network_name CONTAINS '{location}' OR d.name CONTAINS '{location}')"
        
        if org:
            base_query += self.get_org_filter(org)
        
        base_query += """
            RETURN count(d) as device_count,
                   avg(d.health_score) as avg_health,
                   count(CASE WHEN d.health_score < 80 THEN 1 END) as issues
        """
        
        result = session.run(base_query)
        record = result.single()
        
        if record and record['device_count'] > 0:
            device_count = record['device_count']
            avg_health = record['avg_health']
            issues = record['issues']
            
            location_text = f" at {location}" if location else ""
            org_text = f" for {org}" if org else ""
            
            if issues == 0:
                response = f"Drive-thru network connectivity{location_text}{org_text} is excellent. {device_count} network devices with {avg_health:.1f}% health should support drive-thru timers, speakers, and ordering systems."
            else:
                response = f"Found {issues} network issues{location_text}{org_text} that could affect drive-thru operations. Average health is {avg_health:.1f}%. Drive-thru equipment may experience connectivity problems."
            
            return {
                'success': True,
                'response': response,
                'data': {
                    'device_count': device_count,
                    'health_score': avg_health,
                    'issues': issues
                }
            }
        else:
            return {
                'success': True,
                'response': f"No drive-thru network infrastructure found{' for ' + location if location else ''}.",
                'data': None
            }

# Initialize the restaurant equipment voice manager
restaurant_manager = RestaurantEquipmentVoiceManager()

@app.route('/')
def restaurant_interface():
    """Restaurant equipment voice interface"""
    return render_template('restaurant_interface.html')

@app.route('/api/restaurant-command', methods=['POST'])
def process_restaurant_command():
    """Process restaurant equipment voice commands"""
    data = request.json
    command = data.get('command', '')
    
    if not command:
        return jsonify({
            'success': False,
            'response': 'I didn\'t hear your command. Please try asking about POS systems, kitchen equipment, or other restaurant devices.'
        })
    
    # Parse and execute command
    parsed = restaurant_manager.parse_restaurant_command(command)
    result = restaurant_manager.execute_restaurant_command(parsed)
    
    return jsonify({
        'success': result['success'],
        'response': result['response'],
        'data': result['data'],
        'intent': parsed['intent'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/restaurant-help')
def get_restaurant_help():
    """Get restaurant equipment voice commands help"""
    return jsonify({
        'success': True,
        'commands': restaurant_manager.restaurant_commands,
        'sample_phrases': [
            "How are our POS systems?",
            "Check kitchen equipment at store 4472", 
            "Any drive-thru issues?",
            "What restaurant equipment is down?",
            "Check Buffalo Wild Wings kiosks",
            "Are the menu boards working?"
        ]
    })

if __name__ == '__main__':
    print("🍴 Starting Restaurant Equipment Voice Interface")
    print("🎤 Access at: http://localhost:11032")
    print("🏪 Optimized for restaurant operations troubleshooting")
    
    app.run(host='0.0.0.0', port=11032, debug=False)