#!/usr/bin/env python3
"""
Speech-Enabled AI Network Management System
Voice commands for restaurant chain infrastructure management
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
from neo4j import GraphDatabase
import asyncio
import sys

class SpeechEnabledNetworkManager:
    """
    Voice-controlled network management system for restaurant chains
    """
    
    def __init__(self, neo4j_uri: str = "neo4j://localhost:7687", 
                 neo4j_user: str = "neo4j", neo4j_password: str = "password"):
        # Initialize Neo4j connection
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Initialize speech components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_tts_voice()
        
        # Speech processing
        self.listening = False
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
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
            'specific_location': [
                r'devices at (.+)',
                r'(.+) location',
                r'show me (.+) network'
            ]
        }
        
        print("🎤 SPEECH-ENABLED NETWORK MANAGER INITIALIZED")
        print("🔊 Voice recognition and text-to-speech ready")
        
    def setup_tts_voice(self):
        """Configure text-to-speech voice"""
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find a professional/clear voice
        for voice in voices:
            if 'english' in voice.name.lower() or 'en_' in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)  # Slightly slower for clarity
        self.tts_engine.setProperty('volume', 0.9)
        
    def speak(self, text: str):
        """Convert text to speech"""
        print(f"🔊 Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for voice command"""
        try:
            with self.microphone as source:
                print("🎤 Listening for command...")
                self.speak("Ready for your network management command")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for command with timeout
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                
                print("🔄 Processing speech...")
                self.speak("Processing your command")
                
                # Use Google Speech Recognition
                command = self.recognizer.recognize_google(audio)
                print(f"📝 Heard: {command}")
                
                return command.lower()
                
        except sr.WaitTimeoutError:
            print("⏰ No command heard, timeout")
            self.speak("I didn't hear a command. Please try again.")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            self.speak("I couldn't understand that. Please speak clearly and try again.")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            self.speak("I'm having trouble with speech recognition. Please try again.")
            return None
    
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
        
        # Default to general query
        return {
            'intent': 'general_query',
            'command': command,
            'match': None,
            'parameters': []
        }
    
    def execute_device_count_query(self) -> str:
        """Get total device count"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                RETURN count(d) as total_devices
            """)
            total = result.single()["total_devices"]
            
            # Get breakdown by organization
            result = session.run("""
                MATCH (d:Device)
                RETURN d.organization_name as org, count(d) as count
                ORDER BY count DESC
                LIMIT 3
            """)
            
            top_orgs = []
            for record in result:
                top_orgs.append(f"{record['org']} has {record['count']} devices")
            
            response = f"Your network has {total} total devices. "
            if top_orgs:
                response += f"The largest deployments are: {', '.join(top_orgs)}."
            
            return response
    
    def execute_organization_status_query(self, org_name: str) -> str:
        """Get organization health status"""
        with self.driver.session() as session:
            # Find organization by partial name match
            result = session.run("""
                MATCH (d:Device)
                WHERE toLower(d.organization_name) CONTAINS toLower($org_name)
                WITH d.organization_name as org_name,
                     count(d) as device_count,
                     avg(d.health_score) as avg_health,
                     count(CASE WHEN d.status = 'critical' THEN 1 END) as critical,
                     count(CASE WHEN d.status = 'warning' THEN 1 END) as warning
                RETURN org_name, device_count, round(avg_health, 1) as avg_health, critical, warning
                ORDER BY device_count DESC
                LIMIT 1
            """, org_name=org_name)
            
            record = result.single()
            if not record:
                return f"I couldn't find an organization matching {org_name}. Please check the name and try again."
            
            org = record["org_name"]
            devices = record["device_count"]
            health = record["avg_health"]
            critical = record["critical"]
            warning = record["warning"]
            
            status = "excellent" if health > 90 else "good" if health > 80 else "needs attention"
            
            response = f"{org} has {devices} devices with an average health score of {health} percent, which is {status}. "
            
            if critical > 0:
                response += f"However, {critical} devices are in critical status and need immediate attention. "
            elif warning > 0:
                response += f"{warning} devices have warnings that should be investigated. "
            else:
                response += "All devices are operating normally. "
            
            return response
    
    def execute_device_model_query(self, model_pattern: str) -> str:
        """Get device model information"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WHERE toLower(d.model) CONTAINS toLower($pattern) OR toLower(d.product_type) CONTAINS toLower($pattern)
                WITH d.model as model, d.organization_name as org, count(d) as count
                RETURN model, org, count
                ORDER BY count DESC
                LIMIT 10
            """, pattern=model_pattern)
            
            results = list(result)
            if not results:
                return f"I couldn't find devices matching {model_pattern}. Try being more specific or check the model name."
            
            total_count = sum(r["count"] for r in results)
            response = f"Found {total_count} devices matching {model_pattern}. "
            
            if len(results) <= 3:
                details = []
                for record in results:
                    details.append(f"{record['count']} {record['model']} devices at {record['org']}")
                response += "Breakdown: " + ", ".join(details) + "."
            else:
                top_model = results[0]
                response += f"Most common is {top_model['model']} with {top_model['count']} devices at {top_model['org']}."
            
            return response
    
    def execute_critical_devices_query(self) -> str:
        """Get critical devices information"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Device)
                WHERE d.status IN ['critical', 'warning'] OR d.health_score < 80
                RETURN d.name as device, d.organization_name as org, d.status as status, d.health_score as health
                ORDER BY 
                    CASE d.status 
                        WHEN 'critical' THEN 1 
                        WHEN 'warning' THEN 2 
                        ELSE 3 
                    END,
                    d.health_score ASC
                LIMIT 5
            """)
            
            results = list(result)
            if not results:
                return "Excellent news! All devices are healthy with no critical issues detected."
            
            critical = [r for r in results if r["status"] == "critical"]
            warning = [r for r in results if r["status"] == "warning"]
            
            response = f"Found {len(results)} devices needing attention. "
            
            if critical:
                response += f"{len(critical)} are critical: "
                crit_details = [f"{r['device']} at {r['org']}" for r in critical[:2]]
                response += ", ".join(crit_details)
                if len(critical) > 2:
                    response += f" and {len(critical) - 2} more"
                response += ". "
            
            if warning:
                response += f"{len(warning)} have warnings that should be investigated soon."
            
            return response
    
    def execute_network_summary_query(self) -> str:
        """Get executive network summary"""
        with self.driver.session() as session:
            # Get overall stats
            result = session.run("""
                MATCH (o:Organization)
                OPTIONAL MATCH (o)-[:HAS_NETWORK]->(n:Network)
                OPTIONAL MATCH (n)-[:CONTAINS]->(d:Device)
                RETURN count(DISTINCT o) as orgs, count(DISTINCT n) as networks, count(d) as devices
            """)
            stats = result.single()
            
            # Get health overview
            result = session.run("""
                MATCH (d:Device)
                WITH count(d) as total,
                     count(CASE WHEN d.status = 'critical' THEN 1 END) as critical,
                     count(CASE WHEN d.status = 'warning' THEN 1 END) as warning,
                     avg(d.health_score) as avg_health
                RETURN total, critical, warning, round(avg_health, 1) as avg_health
            """)
            health = result.single()
            
            response = f"Network infrastructure summary: "
            response += f"You have {stats['devices']} devices across {stats['networks']} networks in {stats['orgs']} organizations. "
            response += f"Overall health score is {health['avg_health']} percent. "
            
            if health['critical'] > 0:
                response += f"Immediate attention needed: {health['critical']} critical devices. "
            elif health['warning'] > 0:
                response += f"{health['warning']} devices have warnings. "
            else:
                response += "All systems are operating normally. "
            
            return response
    
    def execute_command(self, parsed_command: Dict[str, Any]) -> str:
        """Execute the parsed command and return response"""
        intent = parsed_command['intent']
        parameters = parsed_command['parameters']
        
        try:
            if intent == 'device_count':
                return self.execute_device_count_query()
            
            elif intent == 'organization_status' and parameters:
                org_name = parameters[0]
                return self.execute_organization_status_query(org_name)
            
            elif intent == 'device_model' and parameters:
                model = parameters[0]
                return self.execute_device_model_query(model)
            
            elif intent == 'critical_devices':
                return self.execute_critical_devices_query()
            
            elif intent == 'network_summary':
                return self.execute_network_summary_query()
            
            elif intent == 'specific_location' and parameters:
                location = parameters[0]
                return self.execute_organization_status_query(location)
            
            else:
                # General query - try to find relevant information
                return self.handle_general_query(parsed_command['command'])
                
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return "I encountered an error while processing your request. Please try again or rephrase your command."
    
    def handle_general_query(self, command: str) -> str:
        """Handle general queries by keyword matching"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['help', 'what can you do', 'commands']):
            return """I can help you manage your restaurant chain network infrastructure with voice commands. 
                     Try saying: How many devices do we have? What's the status of Inspire Brands? 
                     Show me critical devices. Give me a network summary. Or ask about specific device models."""
        
        elif 'meraki' in command_lower:
            return "Your network uses Meraki devices including access points, switches, and firewalls across all restaurant locations."
        
        else:
            return "I'm not sure how to help with that. Try asking about device counts, organization status, or critical devices."
    
    def run_interactive_session(self):
        """Run interactive speech session"""
        print("🎤 SPEECH-ENABLED NETWORK MANAGEMENT")
        print("=" * 50)
        print("🔊 Say 'exit' or 'quit' to stop")
        print("🎯 Try: 'How many devices do we have?'")
        print("🎯 Try: 'What's the status of Inspire Brands?'")
        print("🎯 Try: 'Show me critical devices'")
        print("=" * 50)
        
        self.speak("Speech-enabled network management system is ready. What would you like to know about your restaurant infrastructure?")
        
        while True:
            try:
                # Listen for command
                command = self.listen_for_command()
                
                if not command:
                    continue
                
                # Check for exit commands
                if any(exit_word in command.lower() for exit_word in ['exit', 'quit', 'stop', 'goodbye']):
                    self.speak("Goodbye! Your network infrastructure is in good hands.")
                    break
                
                # Parse and execute command
                parsed = self.parse_command(command)
                print(f"🧠 Intent: {parsed['intent']}")
                
                response = self.execute_command(parsed)
                
                # Speak the response
                self.speak(response)
                
                # Also show on screen
                print(f"📊 Response: {response}\n")
                
                # Brief pause before next command
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.speak("Session ended by user. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Session error: {e}")
                self.speak("I encountered an error. Let me try again.")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.close()

def main():
    """Main function"""
    print("🚀 INITIALIZING SPEECH-ENABLED NETWORK MANAGER")
    print("Connecting to your restaurant chain infrastructure...")
    
    try:
        # Create speech-enabled manager
        manager = SpeechEnabledNetworkManager()
        
        # Test Neo4j connection
        with manager.driver.session() as session:
            result = session.run("MATCH (d:Device) RETURN count(d) as count")
            device_count = result.single()["count"]
            print(f"✅ Connected to network with {device_count} devices")
        
        # Run interactive session
        manager.run_interactive_session()
        
    except Exception as e:
        print(f"❌ Failed to start speech manager: {e}")
        print("Make sure Neo4j is running and microphone is available")
    finally:
        if 'manager' in locals():
            manager.close()

if __name__ == "__main__":
    main()