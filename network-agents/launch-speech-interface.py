#!/usr/bin/env python3
"""
Launch Speech-Enabled Network Management Interface
Quick launcher for voice-controlled network management
"""

import subprocess
import sys
import time
import webbrowser
from threading import Timer

def check_neo4j_connection():
    """Check if Neo4j is accessible"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            result = session.run("MATCH (d:Device) RETURN count(d) as count")
            device_count = result.single()["count"]
        driver.close()
        return True, device_count
    except Exception as e:
        return False, str(e)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    print("🌐 Opening speech interface in browser...")
    webbrowser.open('http://localhost:11030')

def main():
    print("🎤 LAUNCHING SPEECH-ENABLED NETWORK MANAGEMENT")
    print("=" * 55)
    
    # Check Neo4j connection
    print("🔍 Checking Neo4j connection...")
    neo4j_ok, result = check_neo4j_connection()
    
    if neo4j_ok:
        print(f"✅ Neo4j connected: {result} devices available")
    else:
        print(f"❌ Neo4j connection failed: {result}")
        print("🔧 Make sure Neo4j is running: docker restart ai-platform-neo4j")
        return 1
    
    print("🚀 Starting speech web interface...")
    print("🌐 Web interface will be available at: http://localhost:11030")
    print("🎤 Features:")
    print("   • Voice commands for network management")
    print("   • Text-to-speech responses")
    print("   • Real-time device status")
    print("   • Executive network summaries")
    print("=" * 55)
    print("🎯 Try saying:")
    print("   • 'How many devices do we have?'")
    print("   • 'What's the status of Inspire Brands?'")
    print("   • 'Show me critical devices'")
    print("   • 'Give me a network summary'")
    print("=" * 55)
    
    try:
        # Start Flask app
        subprocess.run([
            sys.executable, 
            "speech-web-interface.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Speech interface stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())