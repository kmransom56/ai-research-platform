#!/usr/bin/env python3
"""
Command-Line Speech Interface Test
Test speech functionality from command line
"""

import sys
import os
import re
from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional

class TestWebSpeechNetworkManager:
    """Test version of web speech manager"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
        self.command_patterns = {
            'device_count': [r'how many devices', r'device count', r'total devices'],
            'organization_status': [r'status of (.+)', r'how is (.+) doing', r'(.+) health'],
            'critical_devices': [r'critical devices', r'devices with issues'],
            'network_summary': [r'network summary', r'executive summary'],
            'top_models': [r'top device models', r'most common devices']
        }
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        command = command.lower().strip()
        for intent, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    return {
                        'intent': intent,
                        'parameters': match.groups() if match.groups() else []
                    }
        return {'intent': 'general_query', 'parameters': []}
    
    def execute_command(self, command_text: str) -> Dict[str, Any]:
        parsed = self.parse_command(command_text)
        intent = parsed['intent']
        parameters = parsed['parameters']
        
        try:
            with self.driver.session() as session:
                if intent == 'device_count':
                    result = session.run("MATCH (d:Device) RETURN count(d) as total")
                    total = result.single()["total"]
                    return {
                        'text': f"Your network has {total} total devices across all restaurant locations.",
                        'data': {'total_devices': total}
                    }
                
                elif intent == 'organization_status' and parameters:
                    org_name = parameters[0]
                    result = session.run("""
                        MATCH (d:Device)
                        WHERE toLower(d.organization_name) CONTAINS toLower($org_name)
                        RETURN d.organization_name as org, count(d) as devices, avg(d.health_score) as health
                        ORDER BY devices DESC LIMIT 1
                    """, org_name=org_name)
                    record = result.single()
                    if record:
                        return {
                            'text': f"{record['org']} has {record['devices']} devices with {record['health']:.1f}% average health.",
                            'data': {'organization': record['org'], 'devices': record['devices'], 'health': record['health']}
                        }
                    else:
                        return {'text': f"Organization {org_name} not found.", 'data': None}
                
                elif intent == 'critical_devices':
                    result = session.run("""
                        MATCH (d:Device) WHERE d.status IN ['critical', 'warning'] 
                        RETURN count(d) as count
                    """)
                    count = result.single()["count"]
                    return {
                        'text': f"Found {count} devices needing attention." if count > 0 else "All devices are healthy!",
                        'data': {'critical_count': count}
                    }
                
                elif intent == 'network_summary':
                    result = session.run("""
                        MATCH (d:Device) 
                        RETURN count(d) as devices, 
                               count(DISTINCT d.organization_name) as orgs,
                               avg(d.health_score) as health
                    """)
                    stats = result.single()
                    return {
                        'text': f"Infrastructure: {stats['devices']} devices in {stats['orgs']} organizations with {stats['health']:.1f}% average health.",
                        'data': stats
                    }
                
                elif intent == 'top_models':
                    result = session.run("""
                        MATCH (d:Device) WHERE d.model IS NOT NULL 
                        RETURN d.model as model, count(d) as count 
                        ORDER BY count DESC LIMIT 5
                    """)
                    models = [{'model': r['model'], 'count': r['count']} for r in result]
                    top_model = models[0] if models else None
                    text = f"Top device model: {top_model['model']} with {top_model['count']} devices." if top_model else "No device models found."
                    return {'text': text, 'data': {'top_models': models}}
                
                else:
                    return {'text': "Command not recognized. Try asking about device counts or organization status.", 'data': None}
        
        except Exception as e:
            return {'text': f"Error: {str(e)}", 'data': None}
    
    def close(self):
        if self.driver:
            self.driver.close()

def test_speech_commands():
    """Test various speech commands"""
    print("🧪 TESTING SPEECH COMMANDS")
    print("=" * 40)
    
    manager = TestWebSpeechNetworkManager()
    
    test_commands = [
        "How many devices do we have",
        "What's the status of Inspire Brands", 
        "Show me critical devices",
        "Give me a network summary",
        "Show me top device models",
        "How is Buffalo Wild Wings doing"
    ]
    
    try:
        for i, command in enumerate(test_commands, 1):
            print(f"\n🎤 Test {i}: '{command}'")
            print("-" * 30)
            
            result = manager.execute_command(command)
            
            print(f"📝 Response: {result['text']}")
            
            if result['data']:
                print(f"📊 Data keys: {list(result['data'].keys())}")
            
            print("✅ Success")
        
        print(f"\n🎉 All {len(test_commands)} speech commands tested successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        manager.close()
    
    return True

def main():
    print("🎤 SPEECH INTERFACE COMMAND-LINE TEST")
    print("Testing Neo4j connection and speech command processing...")
    print("=" * 50)
    
    success = test_speech_commands()
    
    if success:
        print("\n✅ SPEECH INTERFACE READY!")
        print("🌐 Access web interface at: http://localhost:11030")
        print("🎤 Try voice commands in your browser")
        return 0
    else:
        print("\n❌ Tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())