#!/usr/bin/env python3
"""
Landing Page Server for AI Network Management System
Provides easy access to both Restaurant and Network voice interfaces
"""

from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def landing_page():
    """Main landing page with interface selection"""
    return render_template('landing_page.html')

@app.route('/status')
def system_status():
    """API endpoint to check system status"""
    try:
        # Try to check if both interfaces are accessible
        import requests
        
        restaurant_status = "running"
        network_status = "running"
        
        try:
            requests.get("http://localhost:11032", timeout=2)
        except:
            restaurant_status = "offline"
        
        try:
            requests.get("http://localhost:11030", timeout=2)
        except:
            network_status = "offline"
        
        return jsonify({
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "restaurant_interface": {
                    "status": restaurant_status,
                    "port": 11032,
                    "url": "http://localhost:11032"
                },
                "network_interface": {
                    "status": network_status,
                    "port": 11030,
                    "url": "http://localhost:11030"
                },
                "neo4j_browser": {
                    "status": "available",
                    "port": 7474,
                    "url": "http://localhost:7474"
                }
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/help')
def help_page():
    """Help and documentation endpoint"""
    help_content = {
        "restaurant_commands": [
            "How are our POS systems?",
            "Check kitchen equipment at Buffalo Wild Wings",
            "Any drive-thru issues?",
            "Are the kiosks working?",
            "Check menu boards at store 4472",
            "What restaurant equipment is down?"
        ],
        "network_commands": [
            "How many devices do we have?",
            "Check network health",
            "Show me critical issues",
            "Device count by organization",
            "Network summary",
            "Check Inspire Brands health"
        ],
        "access_urls": {
            "restaurant_interface": "http://localhost:11032",
            "network_interface": "http://localhost:11030", 
            "neo4j_browser": "http://localhost:7474",
            "landing_page": "http://localhost:11040"
        },
        "supported_organizations": [
            "Inspire Brands (2,192 devices)",
            "Buffalo Wild Wings (1,429 devices)",
            "Arby's",
            "Baskin Robbins",
            "Dunkin' Donuts (Comcast)",
            "7,816 total devices across 4,458 locations"
        ]
    }
    
    return jsonify(help_content)

if __name__ == '__main__':
    print("🚀 Starting AI Network Management Landing Page")
    print("🌐 Access at: http://localhost:11040")
    print("📖 Choose between Restaurant Operations or IT Network Management")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=11040, debug=False)