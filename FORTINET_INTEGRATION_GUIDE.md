# 🛡️ Fortinet FortiManager Integration Guide

## Multi-Vendor Restaurant Network Management with FortiManager

This guide explains how to integrate Fortinet FortiManager into your AI Restaurant Network Management System, enabling unified management of both Meraki and Fortinet devices across Arby's, Buffalo Wild Wings, and Sonic restaurant chains.

---

## 📋 **Overview**

### What This Integration Provides

✅ **Proven FortiManager API**: Using your existing battle-tested API from [kmransom56/meraki_management_application](https://github.com/kmransom56/meraki_management_application)  
✅ **Restaurant-Specific Enhancements**: Added organization detection and restaurant role classification  
✅ **Multi-Vendor Discovery**: Combined Meraki and Fortinet device inventory  
✅ **Enhanced Voice Commands**: Voice control for FortiGate firewalls and FortiAP access points  
✅ **Restaurant-Specific Queries**: Organization-aware device management (Arby's, BWW, Sonic)  
✅ **Neo4j Database Integration**: Unified graph database for all vendor equipment  
✅ **Redis Session Caching**: Your existing session management for performance  

### Supported Fortinet Devices

- **FortiGate Firewalls**: Security appliances and NGFW
- **FortiAP Access Points**: Wireless access points managed by FortiManager
- **FortiSwitch**: Network switches (if managed through FortiManager)

### Restaurant-Specific Enhancements

Your proven FortiManager API has been enhanced with restaurant network intelligence:

**🏢 Organization Detection:**
- Automatically detects Arby's, Buffalo Wild Wings, and Sonic from device names
- Uses device metadata and site information for classification
- Falls back to FortiManager site configuration

**🍽️ Restaurant Role Classification:**
```python
# FortiGate roles
'Store Firewall'      # Branch/store protection
'Corporate Firewall'  # HQ/datacenter security

# FortiAP roles  
'Customer WiFi'       # Guest network access
'Staff WiFi'         # Employee network access
'Kitchen Operations'  # Back-of-house connectivity

# FortiSwitch roles
'POS Network'        # Point-of-sale systems
'Kitchen Network'    # Kitchen display systems
```

**📊 Enhanced Inventory Data:**
- Device count by restaurant chain
- Role-based device categorization  
- Restaurant-specific health monitoring
- Business impact assessment

---

## 🚀 **Quick Setup**

### 1. Configure FortiManager Credentials

Copy the environment template:
```bash
cp .env.fortinet.template .env
```

Edit `.env` with your FortiManager details:
```env
# Primary FortiManager (Arby's & BWW)
FORTIMANAGER_HOST=192.168.1.100
FORTIMANAGER_USERNAME=admin
FORTIMANAGER_PASSWORD=your-password
FORTIMANAGER_SITE=arbys-bww

# Sonic FortiManager (if separate)
FORTIMANAGER1_HOST=192.168.2.100
FORTIMANAGER1_USERNAME=admin
FORTIMANAGER1_PASSWORD=sonic-password
FORTIMANAGER1_SITE=sonic
```

### 2. Start Multi-Vendor System

```bash
./start-multi-vendor-network-system.sh
```

### 3. Access Interfaces

**🎤 Main AI Network Management System**: http://localhost:11040

**Voice Interfaces:**
- **Restaurant Operations**: http://localhost:11032
- **IT & Network Management**: http://localhost:11030

**Monitoring & Visualization:**
- **📈 Grafana Dashboards**: http://localhost:11002 (admin/admin)
- **🔍 Prometheus Metrics**: http://localhost:9090
- **📊 Neo4j Database**: http://localhost:7474 (neo4j/password)

---

## 🔍 **Discovery & Data Loading**

### Automated Multi-Vendor Discovery

Run comprehensive discovery across all vendors:
```bash
cd network-agents
python3 multi-vendor-discovery.py
```

This will:
1. Discover all Meraki devices (existing functionality)
2. Connect to FortiManager instances
3. Retrieve Fortinet device inventory
4. Load everything into Neo4j database
5. Generate unified inventory reports

### Test FortiManager Connection

```bash
cd network-agents
python3 fortimanager-connector.py
```

Expected output:
```
✅ Successfully connected to FortiManager: 192.168.1.100
📊 Found 25 managed devices
  - FGT-Branch-01 (FortiGate-100F) - online
  - FGT-Branch-02 (FortiGate-60F) - online  
  - FAP-Store-001 (FortiAP-431F) - online
📈 Inventory stats: {'total_devices': 25, 'online_devices': 24, 'fortigates': 15, 'fortiaps': 10}
```

---

## 🎤 **Enhanced Voice Commands**

### New FortiManager-Specific Commands

**Fortinet Device Queries:**
- *"Show Fortinet devices"*
- *"How many FortiGate firewalls do we have?"*
- *"List FortiAP access points"*
- *"Fortinet device status"*

**Security-Focused Commands:**
- *"How are our firewalls?"*
- *"Security device status"*  
- *"Show offline security devices"*
- *"Critical security issues"*

**Restaurant Chain Queries:**
- *"How is Arby's network?"* (includes both Meraki and Fortinet)
- *"Buffalo Wild Wings device status"*
- *"Sonic network health"*

**Multi-Vendor Comparisons:**
- *"Device count by vendor"*
- *"Network health overview"*
- *"Show all offline devices"*

### Example Voice Interactions

```
🎤 "How are our firewalls?"
🤖 "Restaurant security status: 15 security devices with 93.3% online. 
    Devices: 10 Fortinet FortiGate, 5 Meraki Security Appliance. 
    ⚠️ 1 security device is offline - immediate attention needed!"

🎤 "Show Fortinet devices"  
🤖 "We have 25 Fortinet devices with 96.0% online. 
    Types: 15 FortiGates, 10 FortiAPs. 
    ✅ All systems operating normally."

🎤 "How is Sonic network?"
🤖 "Sonic network status: 18 devices with 94.4% health. 
    Equipment: 8 Fortinet FortiGate, 6 Fortinet FortiAP, 4 Meraki Access Point. 
    ⚠️ 1 device needs attention."
```

---

## 🗄️ **Neo4j Database Schema**

### New Node Types

**Fortinet Devices:**
```cypher
// FortiGate Firewall
CREATE (d:Device {
  id: "fortinet_FGT-001",
  name: "FGT-Branch-01", 
  vendor: "Fortinet",
  device_type: "FortiGate",
  model: "FortiGate-100F",
  serial: "FGT60F1234567890",
  status: "online",
  ip_address: "192.168.1.1",
  os_version: "7.2.0",
  fortimanager_host: "192.168.1.100"
})

// FortiAP Access Point  
CREATE (d:Device {
  id: "fortinet_FAP-001",
  name: "FAP-Store-001",
  vendor: "Fortinet", 
  device_type: "FortiAP",
  model: "FortiAP-431F",
  status: "online"
})
```

### Useful Queries

**Find all Fortinet devices:**
```cypher
MATCH (d:Device {vendor: 'Fortinet'})
RETURN d.name, d.device_type, d.status, d.organization_name
ORDER BY d.device_type, d.name
```

**Security devices across all vendors:**
```cypher
MATCH (d:Device)
WHERE d.device_type IN ['FortiGate', 'Security Appliance', 'Firewall']
RETURN d.vendor, d.device_type, d.status, count(d) as count
```

**Multi-vendor summary by organization:**
```cypher
MATCH (d:Device)
RETURN d.organization_name, d.vendor, count(d) as device_count
ORDER BY d.organization_name, device_count DESC
```

---

## 🔧 **API Integration Details**

### FortiManager JSON-RPC API

The integration uses FortiManager's JSON-RPC API with the following endpoints:

**Authentication:**
```json
{
  "method": "exec",
  "params": [{
    "url": "/sys/login/user", 
    "data": {"user": "admin", "passwd": "password"}
  }]
}
```

**Device Discovery:**
```json
{
  "method": "get",
  "params": [{"url": "/dvmdb/device"}],
  "session": "session_token"
}
```

**Device Interfaces:**
```json
{
  "method": "get", 
  "params": [{"url": "/pm/config/device/FGT-001/global/system/interface"}],
  "session": "session_token"
}
```

### SSL Certificate Handling

The integration automatically handles SSL certificate issues common in corporate environments:
- Disables SSL verification warnings
- Supports self-signed certificates
- Corporate proxy compatibility

---

## 📊 **Monitoring & Visualization**

### Network Topology Dashboard

The existing network topology dashboard (http://localhost:11050) now includes:

- **Fortinet Device Icons**: 🛡️ FortiGate firewalls, 📶 FortiAP access points
- **Vendor Color Coding**: Fortinet red (#d43527), Meraki teal (#00d4aa)
- **Multi-vendor Health Status**: Combined health metrics
- **Device Type Filtering**: Filter by vendor or device type

### Health Monitoring

**Device Status Tracking:**
- Online/offline status for all Fortinet devices
- Last seen timestamps from FortiManager
- Connection status to FortiManager
- Interface up/down status

**Alert Generation:**
- Critical: FortiGate firewalls offline
- Warning: FortiAP access points offline  
- Info: Configuration sync issues

---

## 🔐 **Security Considerations**

### FortiManager Access

**Authentication:**
- Use dedicated service account with minimal privileges
- Enable read-only access where possible
- Rotate passwords regularly

**Network Security:**
- FortiManager access over secure networks only
- Consider VPN or private network connectivity
- Firewall rules restricting API access

### Data Protection

**Sensitive Information:**
- Device configurations are not retrieved
- Only inventory and status data collected
- No security policies or rules accessed
- Credentials stored in environment variables only

---

## 🚨 **Troubleshooting**

### Common Issues

**Connection Failures:**
```bash
# Test FortiManager connectivity
telnet your-fortimanager-ip 443

# Check credentials
cd network-agents
python3 fortimanager-connector.py
```

**SSL Certificate Errors:**
```bash
# Verify certificate issues
openssl s_client -connect fortimanager-ip:443

# Use environment variable to skip SSL verification
export PYTHONHTTPSVERIFY=0
```

**Discovery Issues:**
```bash
# Check Neo4j connection
docker ps | grep neo4j

# Verify database connectivity
python3 -c "from neo4j import GraphDatabase; print('Neo4j OK')"

# Check discovery logs
cd network-agents
python3 multi-vendor-discovery.py 2>&1 | tee discovery.log
```

### Error Messages

**"Failed to login to FortiManager":**
- Verify host, username, password in .env file
- Check FortiManager is accessible from your network
- Ensure FortiManager has JSON-RPC API enabled

**"No Fortinet devices found":**
- Verify devices are managed by FortiManager
- Check device license status
- Ensure devices are not in maintenance mode

**"SSL verification failed":**
- Use self-signed certificate handling
- Check corporate firewall/proxy settings
- Verify FortiManager certificate configuration

---

## 📈 **Advanced Features**

### Multiple FortiManager Support

Configure multiple FortiManager instances:
```env
# Arby's FortiManager
FORTIMANAGER_HOST=arbys-fortimanager.local
FORTIMANAGER_USERNAME=admin
FORTIMANAGER_PASSWORD=arbys-password
FORTIMANAGER_SITE=arbys

# BWW FortiManager  
FORTIMANAGER1_HOST=bww-fortimanager.local
FORTIMANAGER1_USERNAME=admin
FORTIMANAGER1_PASSWORD=bww-password
FORTIMANAGER1_SITE=bww

# Sonic FortiManager
FORTIMANAGER2_HOST=sonic-fortimanager.local
FORTIMANAGER2_USERNAME=admin  
FORTIMANAGER2_PASSWORD=sonic-password
FORTIMANAGER2_SITE=sonic
```

### Custom Device Classification

Override device types based on naming patterns:
```python
# In fortimanager-connector.py
def _determine_device_type(self, platform_str):
    if 'store' in platform_str.lower():
        return 'Store FortiGate'
    elif 'corp' in platform_str.lower():
        return 'Corporate FortiGate' 
    # ... existing logic
```

### Automated Discovery Scheduling

Set up automated discovery every hour:
```bash
# Add to crontab
0 * * * * cd /path/to/chat-copilot/network-agents && python3 multi-vendor-discovery.py --quiet
```

---

## 🎯 **Next Steps**

### Immediate Actions

1. **Configure Credentials**: Update .env file with FortiManager details
2. **Test Connection**: Run FortiManager connector test
3. **Run Discovery**: Execute multi-vendor discovery
4. **Try Voice Commands**: Test enhanced voice interface

### Advanced Integration

1. **Predictive Maintenance**: Extend AI predictions to Fortinet devices
2. **Automated Remediation**: Add FortiManager device management
3. **Custom Dashboards**: Create restaurant-specific monitoring views
4. **Business Intelligence**: Multi-vendor reporting and analytics

---

## 📞 **Support & Resources**

### Documentation Links
- [FortiManager API Documentation](https://docs.fortinet.com/fortimanager-api)
- [Meraki Dashboard API](https://developer.cisco.com/meraki/api/)
- [Neo4j Graph Database](https://neo4j.com/docs/)

### Integration Support
- Check logs in network-agents/ directory
- Test individual components before full integration
- Use verbose logging for troubleshooting
- Neo4j browser for database verification

**🎯 Your multi-vendor restaurant network management system is now ready to support both Meraki and Fortinet infrastructure with unified voice control and comprehensive monitoring!**