# AI Restaurant Network Management System
## Installation Guide

### 🍽️ For Restaurant Managers (Non-Technical)

This system helps you monitor and manage your restaurant network equipment with AI-powered voice commands and visual dashboards.

#### What This System Does
- **Monitor POS Systems**: Keeps your payment systems running smoothly
- **Track Kitchen Equipment**: Monitors kitchen displays and drive-thru systems
- **Predict Problems**: AI tells you about issues before they cause downtime
- **Voice Commands**: Ask questions like "Are my POS systems working?" 
- **Visual Dashboard**: See your entire network health at a glance

#### Quick Start (Have IT Run This)
```bash
# 1. Get the code
git clone https://github.com/kmransom56/ai-research-platform.git
cd ai-research-platform

# 2. Set up your restaurant network credentials
cp .env.template .env
# Edit .env file with your Meraki API key

# 3. Start the system
./start-restaurant-network-system.sh
```

#### Daily Use - Access Points
After installation, you can access these tools:

1. **🎤 Main AI Network Management System** - http://localhost:11040
   - Click here first - central hub for all tools
   - Choose Restaurant Operations or IT Management

2. **🍴 Restaurant Operations Voice** - http://localhost:11032
   - Say: "Check store equipment status"
   - Say: "Are the kiosks working?"
   - Say: "How are our POS systems?"

3. **🌐 IT & Network Management Voice** - http://localhost:11030
   - Say: "Check network health"
   - Say: "How many devices do we have?"
   - Say: "Show me FortiManager status"

4. **📈 Grafana Monitoring Dashboards** - http://localhost:11002
   - Visual charts and graphs (Login: admin/admin)
   - Real-time restaurant network monitoring
   - Device performance and alerts

5. **🔍 Prometheus Metrics** - http://localhost:9090
   - Network performance metrics
   - FortiManager connectivity status
   - System health monitoring

6. **📊 Neo4j Network Visualization** - http://localhost:7474
   - Interactive network topology (Login: neo4j/password)
   - Multi-vendor device relationships

#### What to Watch For
- **Red devices** = Need immediate attention
- **Yellow devices** = Schedule maintenance soon
- **Green devices** = Working normally

#### Getting Help
- System automatically creates tickets for problems
- AI suggests solutions before you call IT
- All issues are logged with business impact

---

### 🔧 For IT Professionals (Technical)

This is a comprehensive AI-powered network management platform built on Microsoft's Chat Copilot with restaurant-specific intelligence.

#### System Architecture
- **Backend**: .NET 8.0 with Semantic Kernel
- **Frontend**: React 18 with Material-UI
- **AI Stack**: AutoGen Studio, GenAI Stack, Magentic-One
- **Database**: Neo4j for network topology
- **Voice**: WebAPI speech recognition/synthesis
- **Network APIs**: Meraki Dashboard API integration

#### Prerequisites
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Runtime**: .NET 8.0, Node.js 18+, Python 3.10+
- **Database**: Neo4j 5.x
- **Memory**: 16GB RAM minimum (32GB recommended)
- **Storage**: 50GB free space
- **Network**: Meraki Dashboard API access

#### Installation Steps

##### 1. System Dependencies
```bash
# Install .NET 8.0
wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3.10 and pip
sudo apt-get install -y python3.10 python3.10-pip python3.10-venv

# Install Docker for Neo4j
sudo apt-get install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

##### 2. Clone and Setup
```bash
# Clone repository
git clone https://github.com/kmransom56/ai-research-platform.git
cd ai-research-platform

# Setup environment variables
cp .env.template .env
nano .env  # Configure your API keys and settings
```

##### 3. Environment Configuration
Edit `.env` file with your credentials:
```env
# Meraki API Configuration
MERAKI_API_KEY=your_meraki_api_key_here
MERAKI_BASE_URL=https://api.meraki.com/api/v1

# Azure OpenAI (Optional - for enhanced AI features)
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_endpoint

# Neo4j Database
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=change_this_password
NEO4J_DATABASE=restaurant_network

# Restaurant Configuration
RESTAURANT_ORGANIZATION_PREFIX=your_org_prefix
BUSINESS_HOURS_START=06:00
BUSINESS_HOURS_END=23:00
```

##### 4. Database Setup
```bash
# Start Neo4j with Docker
docker run --name restaurant-neo4j \
  --restart unless-stopped \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_server_memory_heap_initial__size=2g \
  -e NEO4J_server_memory_heap_max__size=4g \
  -v neo4j_restaurant_data:/data \
  -d neo4j:5.23-community

# Wait for Neo4j to start
sleep 30
```

##### 5. Application Setup
```bash
# Install Python dependencies
python3 -m venv neo4j-env
source neo4j-env/bin/activate
pip install -r requirements.txt

# Install .NET dependencies
dotnet restore CopilotChat.sln

# Install Node.js dependencies
cd webapp && npm install && cd ..
```

##### 6. Initial Data Load
```bash
# Load network topology from Meraki
source neo4j-env/bin/activate
python3 network-agents/load-real-meraki-topology.py

# Discover restaurant equipment (runs in background)
python3 network-agents/discover-endpoint-devices.py &
```

##### 7. Start Services
```bash
# Option 1: Start individual services
./start-restaurant-network-system.sh

# Option 2: Start with Docker Compose
docker-compose up -d

# Option 3: Development mode
./scripts/start.sh  # Basic Chat Copilot
```

#### Service Architecture

##### Core Services
- **Backend API** (11000): Main .NET application
- **Frontend** (3000): React web interface  
- **Neo4j** (7474/7687): Graph database
- **AutoGen Studio** (11001): Multi-agent AI

##### Restaurant-Specific Services
- **Network Topology Dashboard** (11050): Interactive visualization
- **Restaurant Voice Interface** (11032): Business-focused voice commands
- **IT Voice Interface** (11031): Technical troubleshooting
- **Landing Page** (11040): User-friendly access point

##### AI Services
- **GenAI Stack** (8501-8505): Knowledge graph AI
- **Predictive Maintenance** (Background): Failure prediction
- **Automated Remediation** (Background): Self-healing network
- **Intelligent Incident Response** (Background): Smart alerting

#### Configuration Files

##### Key Configuration Files
```bash
webapi/appsettings.json          # Backend API settings
webapp/.env                      # Frontend environment
network-agents/config.py         # Network agent settings
docker-compose.yml               # Container orchestration
```

##### Network Agent Configuration
```python
# network-agents/config.py
MERAKI_CONFIG = {
    "api_key": os.getenv("MERAKI_API_KEY"),
    "base_url": "https://api.meraki.com/api/v1",
    "rate_limit": 5,  # requests per second
    "timeout": 30
}

RESTAURANT_CONFIG = {
    "business_hours": {
        "start": "06:00",
        "end": "23:00"
    },
    "critical_functions": ["pos", "kitchen", "payment"],
    "maintenance_window": "02:00-06:00"
}
```

#### Monitoring and Maintenance

##### Health Checks
```bash
# Check all services
./scripts/platform-management/check-platform-status.sh

# Individual service health
curl http://localhost:11000/healthz  # Backend API
curl http://localhost:11040/health   # Landing page
curl http://localhost:11050/api/health-summary  # Network health
```

##### Logs and Debugging
```bash
# Service logs
docker logs restaurant-neo4j
docker logs ai-platform-backend
docker logs ai-platform-frontend

# Network agent logs
tail -f network-agents/logs/discovery.log
tail -f network-agents/logs/health-assessment.log
tail -f network-agents/logs/incident-response.log
```

##### Backup and Recovery
```bash
# Backup Neo4j database
docker exec restaurant-neo4j neo4j-admin database dump --to-path=/tmp restaurant_network

# Backup configuration
./scripts/backup-working-config.sh

# Quick restore after reboot
./config-backups-working/latest/quick-restore.sh
```

#### Troubleshooting

##### Common Issues

**Neo4j Connection Failed**
```bash
# Check Neo4j status
docker ps | grep neo4j
docker logs restaurant-neo4j

# Reset Neo4j password
docker exec -it restaurant-neo4j cypher-shell -u neo4j -p neo4j
# Then: ALTER USER neo4j SET PASSWORD 'password'
```

**Meraki API Rate Limiting**
```bash
# Check API rate limits in logs
grep "rate limit" network-agents/logs/*.log

# Adjust rate limiting in config
# Edit network-agents/config.py, reduce RATE_LIMIT value
```

**Voice Interface Not Responding**
```bash
# Check microphone permissions in browser
# Ensure HTTPS or localhost access
# Verify speech services are running
ps aux | grep speech
```

**High Memory Usage**
```bash
# Check Neo4j memory settings
docker exec restaurant-neo4j cat /var/lib/neo4j/conf/neo4j.conf | grep memory

# Adjust heap size in docker run command
# -e NEO4J_server_memory_heap_max__size=2g
```

#### Performance Optimization

##### For Large Deployments (1000+ devices)
```bash
# Increase Neo4j memory
-e NEO4J_server_memory_heap_max__size=8g
-e NEO4J_server_memory_pagecache_size=4g

# Enable query caching
-e NEO4J_dbms_query_cache_size=256m

# Optimize discovery batching
# Edit discover-endpoint-devices.py
BATCH_SIZE = 20  # Reduce from default 50
```

##### Network Topology Dashboard
```bash
# For datasets >5000 nodes, enable sampling
# Dashboard automatically warns and provides options
# Filter by organization before visualization
```

#### Security Considerations

##### Network Security
- Deploy behind corporate firewall
- Use VPN for remote access
- Enable HTTPS with proper certificates
- Rotate API keys regularly

##### Data Security
- Neo4j authentication enabled
- Sensitive data encrypted at rest
- API keys stored in environment variables
- Audit logging enabled

#### Integration with Existing Systems

##### Ticketing Systems
```python
# Extend intelligent-incident-response.py
def create_servicenow_ticket(incident_data):
    # Integrate with ServiceNow API
    pass

def create_jira_ticket(incident_data):
    # Integrate with Jira API  
    pass
```

##### Monitoring Systems
```python
# Add Grafana/Prometheus metrics
# Extend automated-health-assessment.py
def export_prometheus_metrics(health_data):
    # Export metrics for Grafana dashboards
    pass
```

##### Business Intelligence
```sql
-- Neo4j queries for business reporting
MATCH (o:Organization)-[:HAS_NETWORK]->(n:Network)
OPTIONAL MATCH (n)-[:CONTAINS]->(d:Device)
RETURN o.name, count(d) as device_count, avg(d.health_score) as avg_health
ORDER BY avg_health ASC
```

#### API Documentation

##### Network Health API
```bash
GET /api/health-summary
GET /api/topology?organization=Arbys
GET /api/network-map
GET /api/organizations
GET /api/predictive-maintenance
GET /api/remediation-history
```

##### Voice Command API
```bash
POST /api/voice/process-command
{
  "command": "check store equipment status",
  "interface": "restaurant"
}
```

#### Support and Updates

##### Getting Support
- GitHub Issues: https://github.com/kmransom56/ai-research-platform/issues
- Documentation: https://docs.anthropic.com/claude-code
- Community: Restaurant Network Management Discord

##### Updates and Upgrades
```bash
# Update to latest version
git pull origin main
./update-platform.sh

# Check for breaking changes in CHANGELOG.md
# Follow migration guides for major updates
```

This installation guide provides complete setup instructions for both restaurant managers and IT professionals to successfully deploy and operate the AI-powered restaurant network management system.