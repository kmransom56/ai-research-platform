#!/usr/bin/env python3
"""
Magentic-One Server - Temporary Health Check Implementation
This is a simple Flask server that provides health check endpoints
while the full Magentic-One implementation is being set up.
"""

from flask import Flask, jsonify
import sys
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "magentic-one",
        "message": "Magentic-One service is running (temporary implementation)",
        "port": 11003
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Status endpoint"""
    return jsonify({
        "service": "magentic-one", 
        "version": "0.1.0-temporary",
        "status": "active",
        "description": "Multi-agent AI platform temporary health check"
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "Magentic-One Server",
        "endpoints": ["/health", "/api/status"],
        "message": "Magentic-One multi-agent platform (temporary implementation)",
        "note": "Full implementation available in magentic_one_server.py.backup"
    }), 200

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List available agents"""
    return jsonify({
        "agents": [
            {"id": "web_surfer", "status": "available", "description": "Web browsing agent"},
            {"id": "file_surfer", "status": "available", "description": "File management agent"},
            {"id": "coder", "status": "available", "description": "Code generation agent"},
            {"id": "orchestrator", "status": "available", "description": "Task orchestration agent"}
        ]
    }), 200

if __name__ == '__main__':
    try:
        logger.info("Starting Magentic-One Server (temporary) on port 11003...")
        app.run(host='0.0.0.0', port=11003, debug=False)
    except Exception as e:
        logger.error(f"Error starting Magentic-One server: {e}")
        sys.exit(1)
