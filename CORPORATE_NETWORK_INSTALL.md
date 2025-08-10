# 🏢 Corporate Network Installation Guide

## AI Restaurant Network Management System - Corporate Deployment

This guide provides complete instructions for installing and testing the AI Restaurant Network Management System on a corporate network computer with access to FortiManager instances.

---

## 📋 **Prerequisites**

### Corporate Network Requirements:
- ✅ Access to corporate network (behind Zscaler or corporate proxy)
- ✅ Connectivity to FortiManager instances:
  - **Arby's**: `10.128.144.132:443`
  - **Buffalo Wild Wings**: `10.128.145.4:443` 
  - **Sonic**: `10.128.156.36:443`
- ✅ Python 3.8+ installed
- ✅ Git installed
- ✅ Admin/sudo access (for Neo4j installation)

### System Requirements:
- **OS**: Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **Network**: Corporate network with FortiManager access

---

## 🚀 **Quick Installation (Corporate Network)**

### Option 1: Clone from GitHub (Recommended)
```bash
# Clone the repository
git clone https://github.com/kmransom56/chat-copilot.git
cd chat-copilot

# Run corporate network setup
./scripts/corporate-network-setup.sh
```

### Option 2: Download ZIP Package
If Git is restricted, download the ZIP from GitHub:
1. Go to: https://github.com/kmransom56/chat-copilot
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Run setup script

---

## 📦 **Step-by-Step Installation**

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

**Windows:**
```powershell
# Install Python from python.org
# Install Git from git-scm.com
# Open PowerShell as Administrator
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python git
```

### 2. Clone Repository
```bash
git clone https://github.com/kmransom56/chat-copilot.git
cd chat-copilot
```

### 3. Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Install Neo4j Database
```bash
# Ubuntu/Debian
sudo apt install neo4j

# Windows - Download from neo4j.com/download
# macOS
brew install neo4j

# Start Neo4j
sudo systemctl start neo4j  # Linux
# OR use Neo4j Desktop (Windows/Mac)
```

### 5. Configure Environment Variables

**Create `.env` file in `network-agents/` directory:**
```bash
cd network-agents
cp .env.template .env
nano .env  # Edit with your credentials
```

**Required `.env` contents:**
```env
# FortiManager Credentials (provided by IT)
ARBYS_FORTIMANAGER_HOST=10.128.144.132
ARBYS_USERNAME=ibadmin
ARBYS_PASSWORD=your_password_here

BWW_FORTIMANAGER_HOST=10.128.145.4
BWW_USERNAME=ibadmin
BWW_PASSWORD=your_password_here

SONIC_FORTIMANAGER_HOST=10.128.156.36
SONIC_USERNAME=ibadmin
SONIC_PASSWORD=your_password_here

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 6. Apply SSL Fixes for Corporate Network
```bash
cd network-agents
python3 ssl_universal_fix.py
```

---

## 🧪 **Testing FortiManager Connectivity**

### 1. Basic Connection Test
```bash
cd network-agents
python3 test_corporate_network.py
```

**Expected Output:**
```
🏢 Corporate Network Connectivity Test
✅ SSL fixes applied successfully
✅ Zscaler environment configured
✅ FortiManager-specific patches applied
✅ Successfully logged into Arby's FortiManager
📊 Found 2847 devices (2156 online)
✅ Successfully logged into Buffalo Wild Wings FortiManager
📊 Found 3241 devices (2987 online)
✅ Successfully logged into Sonic FortiManager
📊 Found 8756 devices (7234 online)
```

### 2. Individual FortiManager Test
```bash
python3 fortimanager_api.py
```

### 3. Multi-Vendor Discovery Test
```bash
python3 multi-vendor-discovery.py
```

---

## 🎤 **Voice Interface Testing**

### Start Enhanced Voice Interface
```bash
cd network-agents
python3 enhanced-voice-interface.py
```

**Access at:** `http://localhost:11033`

### Test Voice Commands:
- *"Show Fortinet devices"*
- *"How is Arby's network?"*
- *"Buffalo Wild Wings device status"*
- *"Check Sonic firewalls"*
- *"How many FortiGate devices do we have?"*

---

## 🚀 **Start Complete System**

### Full Multi-Vendor System
```bash
./start-multi-vendor-network-system.sh
```

**Access Points:**
- **Main Dashboard**: `http://localhost:11040`
- **Voice Interface**: `http://localhost:11033`
- **Neo4j Browser**: `http://localhost:7474`

---

## 🔧 **Troubleshooting Corporate Network Issues**

### SSL Certificate Issues
```bash
cd network-agents
python3 -c "
from ssl_universal_fix import print_ssl_diagnostics
print_ssl_diagnostics()
"
```

### Zscaler Proxy Issues
```bash
# Test connectivity to FortiManager
python3 -c "
from ssl_universal_fix import test_ssl_connectivity
results = test_ssl_connectivity('10.128.144.132')
for test, result in results['tests'].items():
    print(f'{test}: {result}')
"
```

### Network Connectivity Issues
```bash
# Check if FortiManager is reachable
ping 10.128.144.132
telnet 10.128.144.132 443
```

### Environment Variable Issues
```bash
python3 -c "
import os, sys
sys.path.append('network-agents')
from fortimanager_api import load_env_file
load_env_file()
print('Arby:', os.getenv('ARBYS_FORTIMANAGER_HOST'))
print('BWW:', os.getenv('BWW_FORTIMANAGER_HOST'))
print('Sonic:', os.getenv('SONIC_FORTIMANAGER_HOST'))
"
```

---

## 📊 **Expected Results on Corporate Network**

### Device Discovery Scale:
- **Arby's**: ~2,000-3,000 Fortinet devices
- **Buffalo Wild Wings**: ~2,500-3,500 Fortinet devices  
- **Sonic**: ~7,000-10,000 Fortinet devices
- **Total**: 15,000-25,000 Fortinet devices

### Performance Expectations:
- **Discovery Time**: 15-30 minutes for all three FortiManagers
- **Voice Response**: < 3 seconds for device queries
- **Dashboard Load**: < 10 seconds for network visualization

---

## 🎯 **Success Indicators**

When properly installed on corporate network:

1. ✅ **FortiManager Login**: All three FortiManagers authenticate successfully
2. ✅ **Device Discovery**: Thousands of devices discovered per restaurant
3. ✅ **Organization Detection**: Devices automatically classified by restaurant brand
4. ✅ **Voice Interface**: Responds to Fortinet-specific voice commands
5. ✅ **Network Visualization**: Neo4j shows multi-vendor topology with Fortinet devices in red
6. ✅ **Health Monitoring**: Real-time status of restaurant network infrastructure

---

## 📞 **Support & Next Steps**

### If Installation Succeeds:
1. Screenshot the results for documentation
2. Test voice commands with restaurant-specific queries
3. Explore the Neo4j network visualization
4. Schedule regular discovery runs

### If Issues Occur:
1. Run diagnostic scripts: `python3 test_corporate_network.py`
2. Check corporate firewall/proxy settings
3. Verify FortiManager credentials with IT
4. Ensure Python dependencies are installed correctly

### Production Deployment:
1. Configure automated discovery scheduling
2. Set up monitoring and alerting
3. Create restaurant-specific dashboards
4. Train staff on voice interface usage

---

## 🔒 **Security Notes**

- ✅ All FortiManager credentials stored in `.env` file (add to `.gitignore`)
- ✅ SSL verification bypassed for corporate proxy compatibility
- ✅ No credentials stored in code or logs
- ✅ Session tokens cached securely in Redis
- ✅ Corporate network SSL fixes applied automatically

Your AI Restaurant Network Management System is ready for corporate network deployment! 🚀

---

**Installation Time Estimate:** 30-45 minutes  
**First Discovery Run:** 20-30 minutes  
**System Ready:** Within 1 hour of installation