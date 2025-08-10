# 🏢 Quick Corporate Network Installation

## 30-Second Setup for Corporate FortiManager Testing

### Prerequisites
- Corporate network access to FortiManager instances
- Python 3.8+ and Git installed

---

## 🚀 **One-Command Installation**

```bash
# Clone and setup everything automatically
git clone https://github.com/kmransom56/chat-copilot.git
cd chat-copilot
./scripts/corporate-network-setup.sh
```

---

## ⚡ **Quick Test (Corporate Network Required)**

```bash
# Update credentials first
nano network-agents/.env

# Test all three FortiManagers
cd network-agents
python3 test_corporate_network.py
```

**Expected Results:**
- ✅ Arby's FortiManager: ~2,000-3,000 devices
- ✅ Buffalo Wild Wings: ~2,500-3,500 devices  
- ✅ Sonic: ~7,000-10,000 devices

---

## 🎯 **Start Complete System**

```bash
./corporate-quick-start.sh
```

**Access:**
- 📊 **Dashboard**: http://localhost:11040
- 🎤 **Voice**: http://localhost:11030
- 🗄️ **Database**: http://localhost:7474
- 📈 **Grafana**: http://localhost:11002
- 🔍 **Metrics**: http://localhost:9090

---

## 🔧 **If Issues Occur**

```bash
# Apply SSL fixes
cd network-agents
python3 ssl_universal_fix.py

# Test individual FortiManager
python3 fortimanager_api.py
```

---

## 📝 **Required Credentials**

Update `network-agents/.env`:
```env
ARBYS_FORTIMANAGER_HOST=10.128.144.132
ARBYS_USERNAME=ibadmin
ARBYS_PASSWORD=your_password

BWW_FORTIMANAGER_HOST=10.128.145.4
BWW_USERNAME=ibadmin  
BWW_PASSWORD=your_password

SONIC_FORTIMANAGER_HOST=10.128.156.36
SONIC_USERNAME=ibadmin
SONIC_PASSWORD=your_password
```

---

## 📊 **Grafana Dashboards Included**

```bash
# Launch all network dashboards
cd network-agents
python3 launch-grafana-dashboards.py
```

**Complete Monitoring Suite:**
- 📈 Grafana: Restaurant network dashboards (localhost:11002)
- 🔍 Prometheus: Network metrics and alerting (localhost:9090)  
- 📊 Neo4j: Interactive network topology (localhost:7474)
- 🎤 Voice: Natural language network queries (localhost:11030)
- 🍴 Restaurant: Operations-focused interface (localhost:11032)

---

**Total Setup Time:** ~5 minutes  
**First Discovery:** ~20 minutes  
**Ready to Test:** Within 30 minutes! 🚀