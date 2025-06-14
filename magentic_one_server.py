#!/usr/bin/env python3
"""
Magentic-One Web Server for AI Research Platform
FastAPI-based web interface for Magentic-One multi-agent system
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# FastAPI for web server
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import our Magentic-One implementation
from magentic_one_simple import MagenticOnePlatform

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    agent_type: Optional[str] = "coordinator"

class ChatResponse(BaseModel):
    response: str
    agent: str
    timestamp: str
    session_id: str

class AgentInfo(BaseModel):
    name: str
    role: str
    status: str
    model: str

class SystemStatus(BaseModel):
    status: str
    agents: List[AgentInfo]
    active_sessions: int
    uptime: str

# Global Magentic-One system instance
magentic_one_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global magentic_one_system
    try:
        magentic_one_system = MagenticOnePlatform()
        logger.info("Magentic-One platform initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Magentic-One platform: {e}")
        magentic_one_system = None
    
    yield
    
    # Shutdown
    if magentic_one_system:
        logger.info("Shutting down Magentic-One system")

# Create FastAPI app
app = FastAPI(
    title="Magentic-One Multi-Agent Platform",
    description="Web interface for Magentic-One multi-agent system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Main dashboard page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Magentic-One Multi-Agent Platform</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Arial', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px; color: #333;
            }
            .container { 
                max-width: 1200px; margin: 0 auto; 
                background: rgba(255,255,255,0.95); 
                border-radius: 15px; padding: 30px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header { 
                text-align: center; margin-bottom: 30px; 
                border-bottom: 2px solid #667eea; padding-bottom: 20px;
            }
            .header h1 { color: #333; font-size: 2.5em; margin-bottom: 10px; }
            .status-grid { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; margin-bottom: 30px;
            }
            .status-card { 
                background: white; border-radius: 10px; padding: 20px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
                border-left: 4px solid #667eea;
            }
            .agent-list { background: #f8f9fa; border-radius: 8px; padding: 15px; }
            .agent-item { 
                display: flex; justify-content: space-between; 
                padding: 10px 0; border-bottom: 1px solid #ddd;
            }
            .status-indicator { 
                width: 12px; height: 12px; border-radius: 50%; 
                background: #4caf50; margin-right: 8px;
            }
            .chat-section { 
                background: white; border-radius: 10px; padding: 20px; 
                margin-top: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .chat-messages { 
                background: #f8f9fa; border-radius: 8px; padding: 15px; 
                height: 300px; overflow-y: auto; margin-bottom: 15px;
            }
            .message { padding: 10px; margin: 5px 0; border-radius: 8px; }
            .user-message { background: #e3f2fd; text-align: right; }
            .agent-message { background: #f3e5f5; }
            .input-group { display: flex; gap: 10px; }
            .input-group input { 
                flex: 1; padding: 12px; border: 1px solid #ddd; 
                border-radius: 8px; font-size: 14px;
            }
            .btn { 
                padding: 12px 20px; background: #667eea; color: white; 
                border: none; border-radius: 8px; cursor: pointer; 
                font-size: 14px; transition: background 0.3s;
            }
            .btn:hover { background: #5a6fd8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌟 Magentic-One Multi-Agent Platform</h1>
                <p>Coordinated AI agents working together on your Tailscale network</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>System Status</h3>
                    <div id="systemStatus">
                        <p>🔄 Loading system status...</p>
                    </div>
                </div>
                
                <div class="status-card">
                    <h3>Active Agents</h3>
                    <div class="agent-list" id="agentList">
                        <div class="agent-item">
                            <span><div class="status-indicator"></div>Coordinator</span>
                            <span>llama3.2:3b</span>
                        </div>
                        <div class="agent-item">
                            <span><div class="status-indicator"></div>Web Surfer</span>
                            <span>mistral:latest</span>
                        </div>
                        <div class="agent-item">
                            <span><div class="status-indicator"></div>File Surfer</span>
                            <span>deepseek-coder:6.7b</span>
                        </div>
                        <div class="agent-item">
                            <span><div class="status-indicator"></div>Coder</span>
                            <span>deepseek-coder:6.7b</span>
                        </div>
                        <div class="agent-item">
                            <span><div class="status-indicator"></div>Terminal</span>
                            <span>llama3.2:3b</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chat-section">
                <h3>Multi-Agent Chat Interface</h3>
                <div class="chat-messages" id="chatMessages">
                    <div class="message agent-message">
                        <strong>Coordinator:</strong> Hello! I'm the Magentic-One coordinator. I can help you with complex tasks by coordinating multiple AI agents. What would you like to work on today?
                    </div>
                </div>
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Ask the multi-agent system anything..." 
                           onkeypress="if(event.key==='Enter') sendMessage()">
                    <button class="btn" onclick="sendMessage()">Send</button>
                    <button class="btn" onclick="clearChat()">Clear</button>
                </div>
            </div>
        </div>
        
        <script>
            let sessionId = 'web-session-' + Date.now();
            
            async function loadSystemStatus() {
                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    document.getElementById('systemStatus').innerHTML = `
                        <p>📊 Status: ${status.status}</p>
                        <p>🤖 Active Agents: ${status.agents.length}</p>
                        <p>💬 Sessions: ${status.active_sessions}</p>
                        <p>⏱️ Uptime: ${status.uptime}</p>
                    `;
                } catch (error) {
                    document.getElementById('systemStatus').innerHTML = 
                        '<p>❌ Could not load system status</p>';
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, 'user');
                input.value = '';
                
                // Show loading indicator
                addMessage('🤔 Multi-agent system is thinking...', 'agent', 'System');
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            session_id: sessionId
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        // Remove loading message
                        const messages = document.getElementById('chatMessages');
                        messages.removeChild(messages.lastChild);
                        // Add agent response
                        addMessage(result.response, 'agent', result.agent);
                    } else {
                        addMessage('❌ Error: Could not get response from agents', 'agent', 'System');
                    }
                } catch (error) {
                    addMessage('❌ Network error: ' + error.message, 'agent', 'System');
                }
            }
            
            function addMessage(text, type, agent = 'User') {
                const messages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                
                if (type === 'agent') {
                    messageDiv.innerHTML = `<strong>${agent}:</strong> ${text}`;
                } else {
                    messageDiv.innerHTML = `<strong>You:</strong> ${text}`;
                }
                
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function clearChat() {
                const messages = document.getElementById('chatMessages');
                messages.innerHTML = `
                    <div class="message agent-message">
                        <strong>Coordinator:</strong> Chat cleared. How can I help you today?
                    </div>
                `;
                sessionId = 'web-session-' + Date.now();
            }
            
            // Load status on page load
            window.addEventListener('load', loadSystemStatus);
            
            // Refresh status every 30 seconds
            setInterval(loadSystemStatus, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/status")
async def get_status():
    """Get system status"""
    start_time = datetime.now()
    
    agents = [
        AgentInfo(name="Coordinator", role="coordinator", status="active", model="llama3.2:3b"),
        AgentInfo(name="Web Surfer", role="web_surfer", status="active", model="mistral:latest"),
        AgentInfo(name="File Surfer", role="file_surfer", status="active", model="deepseek-coder:6.7b"),
        AgentInfo(name="Coder", role="coder", status="active", model="deepseek-coder:6.7b"),
        AgentInfo(name="Terminal", role="terminal", status="active", model="llama3.2:3b")
    ]
    
    return SystemStatus(
        status="operational" if magentic_one_system else "initializing",
        agents=agents,
        active_sessions=1,
        uptime="Running"
    )

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Process chat message through Magentic-One system"""
    if not magentic_one_system:
        raise HTTPException(status_code=503, detail="Magentic-One platform not initialized")
    
    try:
        # Determine best workflow based on request
        workflow = "complex_task"  # Default to full team
        if "research" in request.message.lower() or "search" in request.message.lower():
            workflow = "web_research"
        elif "code" in request.message.lower() or "program" in request.message.lower():
            workflow = "code_development"
        elif "analyze" in request.message.lower() or "data" in request.message.lower():
            workflow = "data_analysis"
        
        # Process message through Magentic-One workflow
        result = await magentic_one_system.run_workflow(workflow, request.message)
        
        return ChatResponse(
            response=result.get("final_result", "Multi-agent task completed successfully!"),
            agent="Magentic-One Team",
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return ChatResponse(
            response=f"I encountered an error while processing your request: {str(e)}. Please try again with a simpler request.",
            agent="System",
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )

@app.get("/api/agents")
async def get_agents():
    """Get information about all agents"""
    if not magentic_one_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {
        "agents": [
            {"name": "Coordinator", "role": "coordinator", "model": "llama3.2:3b", "status": "active"},
            {"name": "Web Surfer", "role": "web_surfer", "model": "mistral:latest", "status": "active"},
            {"name": "File Surfer", "role": "file_surfer", "model": "deepseek-coder:6.7b", "status": "active"},
            {"name": "Coder", "role": "coder", "model": "deepseek-coder:6.7b", "status": "active"},
            {"name": "Terminal", "role": "terminal", "model": "llama3.2:3b", "status": "active"}
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_initialized": magentic_one_system is not None
    }

if __name__ == "__main__":
    # Configure uvicorn server
    uvicorn.run(
        "magentic_one_server:app",
        host="0.0.0.0",
        port=8086,
        reload=False,
        log_level="info"
    )