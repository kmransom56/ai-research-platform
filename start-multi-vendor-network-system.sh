#!/bin/bash

# Multi-Vendor Restaurant Network Management System Startup
# Supports Meraki and Fortinet (FortiManager) devices for Arby's, BWW, and Sonic

set -e

echo "🚀 Starting Multi-Vendor Restaurant Network Management System"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "network-agents/multi-vendor-discovery.py" ]; then
    echo -e "${RED}❌ Please run this script from the chat-copilot directory${NC}"
    exit 1
fi

# Check Python environment
echo -e "${BLUE}🐍 Checking Python environment...${NC}"
if [ ! -d "network-agents/neo4j-env" ]; then
    echo -e "${RED}❌ Neo4j Python environment not found${NC}"
    echo "Please run the setup first or check your installation"
    exit 1
fi

# Activate Python environment
source network-agents/neo4j-env/bin/activate

# Check Neo4j
echo -e "${BLUE}🗄️  Checking Neo4j database...${NC}"
if ! docker ps | grep -q neo4j; then
    echo -e "${YELLOW}⚠️  Starting Neo4j database...${NC}"
    docker run -d \
        --name ai-platform-neo4j-multi-vendor \
        --restart unless-stopped \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password \
        -e NEO4J_PLUGINS='["apoc"]' \
        -e NEO4J_server_memory_heap_initial__size=2g \
        -e NEO4J_server_memory_heap_max__size=4g \
        -v neo4j_multi_vendor_data:/data \
        neo4j:5.23-community
    
    echo -e "${YELLOW}⏳ Waiting for Neo4j to start...${NC}"
    sleep 15
fi

# Check environment variables
echo -e "${BLUE}🔧 Checking configuration...${NC}"

if [ -z "$MERAKI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  MERAKI_API_KEY not set${NC}"
else
    echo -e "${GREEN}✅ Meraki API key configured${NC}"
fi

if [ -z "$FORTIMANAGER_HOST" ]; then
    echo -e "${YELLOW}⚠️  FORTIMANAGER_HOST not set${NC}"
    echo -e "${YELLOW}   Copy .env.fortinet.template to .env and configure FortiManager settings${NC}"
else
    echo -e "${GREEN}✅ FortiManager configuration found${NC}"
fi

# Install/update required packages
echo -e "${BLUE}📦 Checking Python dependencies...${NC}"
pip install -q neo4j flask requests meraki

# Create templates directory if it doesn't exist
mkdir -p network-agents/templates

# Create enhanced voice interface template
echo -e "${BLUE}🎤 Creating voice interface template...${NC}"
cat > network-agents/templates/enhanced_voice_interface.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎤 Multi-Vendor Restaurant Network Voice Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #d43527 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 900px; margin: 0 auto; text-align: center; }
        
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2rem; opacity: 0.9; margin-bottom: 30px; }
        
        .vendor-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .vendor-badge {
            background: rgba(255,255,255,0.15);
            padding: 10px 20px;
            border-radius: 25px;
            backdrop-filter: blur(10px);
            font-weight: bold;
        }
        
        .meraki-badge { border: 2px solid #00d4aa; }
        .fortinet-badge { border: 2px solid #d43527; }
        
        .voice-controls {
            background: rgba(255,255,255,0.15);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        
        .microphone-button {
            width: 150px;
            height: 150px;
            background: #FF4444;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 auto 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4rem;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .microphone-button:hover { background: #FF2222; transform: scale(1.05); }
        .microphone-button.listening {
            background: #22FF22;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .status { font-size: 1.2rem; margin-bottom: 20px; min-height: 30px; }
        .command-display { background: rgba(0,0,0,0.2); border-radius: 10px; padding: 15px; margin-bottom: 20px; min-height: 50px; font-style: italic; }
        .response { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px; margin-bottom: 20px; min-height: 60px; text-align: left; }
        
        .example-commands {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .command-category {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        .command-category h3 {
            color: #FFE4B5;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(255, 228, 181, 0.3);
            padding-bottom: 10px;
        }
        
        .command-list { display: flex; flex-direction: column; gap: 8px; }
        .command-item {
            background: rgba(255,255,255,0.1);
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        
        .command-item:hover { background: rgba(255,255,255,0.2); }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .vendor-badges { flex-direction: column; align-items: center; }
            .example-commands { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Multi-Vendor Restaurant Network Control</h1>
            <p>Voice-controlled management for Meraki and Fortinet equipment</p>
            <p>Supporting Arby's, Buffalo Wild Wings, and Sonic</p>
        </div>
        
        <div class="vendor-badges">
            <div class="vendor-badge meraki-badge">📡 Meraki</div>
            <div class="vendor-badge fortinet-badge">🛡️ Fortinet</div>
        </div>
        
        <div class="voice-controls">
            <button class="microphone-button" id="micButton" onclick="toggleListening()">
                🎤
            </button>
            
            <div class="status" id="status">Click the microphone and speak</div>
            <div class="command-display" id="commandDisplay">Your command will appear here...</div>
            <div class="response" id="responseDisplay">AI response will appear here...</div>
        </div>
        
        <div class="example-commands">
            <div class="command-category">
                <h3>🏢 Restaurant Chains</h3>
                <div class="command-list">
                    <div class="command-item" onclick="executeCommand(this.textContent)">"How is Arby's network?"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Buffalo Wild Wings status"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Check Sonic devices"</div>
                </div>
            </div>
            
            <div class="command-category">
                <h3>🛡️ Security & Firewalls</h3>
                <div class="command-list">
                    <div class="command-item" onclick="executeCommand(this.textContent)">"How are our firewalls?"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Show Fortinet devices"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Security status"</div>
                </div>
            </div>
            
            <div class="command-category">
                <h3>📶 WiFi & Networking</h3>
                <div class="command-list">
                    <div class="command-item" onclick="executeCommand(this.textContent)">"WiFi access points status"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Show Meraki devices"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Network health overview"</div>
                </div>
            </div>
            
            <div class="command-category">
                <h3>🚨 Critical Monitoring</h3>
                <div class="command-list">
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Any critical issues?"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Show offline devices"</div>
                    <div class="command-item" onclick="executeCommand(this.textContent)">"Device count summary"</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let recognition;
        let isListening = false;

        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = function() {
                document.getElementById('status').textContent = 'Listening... Speak now!';
                document.getElementById('micButton').classList.add('listening');
            };

            recognition.onresult = function(event) {
                const command = event.results[0][0].transcript;
                document.getElementById('commandDisplay').textContent = '🎤 "' + command + '"';
                processCommand(command);
            };

            recognition.onerror = function(event) {
                document.getElementById('status').textContent = 'Error: ' + event.error;
                document.getElementById('micButton').classList.remove('listening');
                isListening = false;
            };

            recognition.onend = function() {
                document.getElementById('micButton').classList.remove('listening');
                isListening = false;
            };
        } else {
            document.getElementById('status').textContent = 'Speech recognition not supported in this browser';
        }

        function toggleListening() {
            if (isListening) {
                recognition.stop();
            } else {
                if (recognition) {
                    recognition.start();
                    isListening = true;
                } else {
                    document.getElementById('status').textContent = 'Speech recognition not available';
                }
            }
        }

        function executeCommand(command) {
            document.getElementById('commandDisplay').textContent = '🎤 "' + command + '"';
            processCommand(command);
        }

        async function processCommand(command) {
            try {
                document.getElementById('status').textContent = 'Processing command...';
                document.getElementById('responseDisplay').textContent = 'Thinking...';

                const response = await fetch('/api/process-command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command: command })
                });

                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('responseDisplay').textContent = '🤖 ' + result.response;
                    document.getElementById('status').textContent = 'Command processed successfully';
                    
                    // Text-to-speech response
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(result.response);
                        utterance.rate = 0.9;
                        utterance.pitch = 1.0;
                        speechSynthesis.speak(utterance);
                    }
                } else {
                    document.getElementById('responseDisplay').textContent = '❌ ' + result.response;
                    document.getElementById('status').textContent = 'Command failed';
                }
            } catch (error) {
                document.getElementById('responseDisplay').textContent = '❌ Connection error: ' + error.message;
                document.getElementById('status').textContent = 'Connection failed';
            }
        }

        // Update status when page loads
        window.onload = function() {
            if (recognition) {
                document.getElementById('status').textContent = 'Ready! Click microphone to start voice commands';
            }
        };
    </script>
</body>
</html>
EOF

echo -e "${GREEN}✅ Voice interface template created${NC}"

# Display startup information
echo
echo -e "${GREEN}🎯 Multi-Vendor Restaurant Network System Ready!${NC}"
echo "============================================================="
echo
echo -e "${BLUE}📊 Neo4j Database Browser:${NC}"
echo "   URL: http://localhost:7474"
echo "   Login: neo4j / password"
echo
echo -e "${BLUE}🎤 Enhanced Voice Interface:${NC}"  
echo "   URL: http://localhost:11033"
echo "   Features: Meraki and Fortinet device queries"
echo
echo -e "${BLUE}🔍 Discovery Commands:${NC}"
echo "   Multi-vendor discovery:"
echo "   cd network-agents && python3 multi-vendor-discovery.py"
echo
echo "   FortiManager test:"
echo "   cd network-agents && python3 fortimanager-connector.py"
echo
echo -e "${BLUE}🎯 Voice Command Examples:${NC}"
echo '   "How many devices do we have?"'
echo '   "Show Fortinet devices"'
echo '   "How is Arby'\''s network?"'
echo '   "Check security devices"'
echo '   "WiFi access points status"'
echo
echo -e "${YELLOW}⚙️  Configuration:${NC}"
echo "   Copy .env.fortinet.template to .env and configure:"
echo "   - FORTIMANAGER_HOST"
echo "   - FORTIMANAGER_USERNAME"  
echo "   - FORTIMANAGER_PASSWORD"
echo "   - MERAKI_API_KEY (existing)"
echo

# Start the enhanced voice interface
echo -e "${BLUE}🚀 Starting Enhanced Voice Interface...${NC}"
cd network-agents && python3 enhanced-voice-interface.py