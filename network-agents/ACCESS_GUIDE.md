# 🎤 AI Network Management System - Easy Access Guide

## 🚀 Quick Start - Choose Your Interface

### 🍴 **For Restaurant Operations** (Recommended for Store Managers)
**Perfect for:** Store managers, restaurant operations, troubleshooting POS/kitchen equipment

**🌐 Access:** [http://localhost:11032](http://localhost:11032)

**🎤 Try These Commands:**
- "How are our POS systems?"
- "Check kitchen equipment at Buffalo Wild Wings"
- "Any drive-thru issues?"
- "Are the kiosks working at store 4472?"
- "Check Inspire Brands menu boards"

---

### 🌐 **For IT/Network Management** (Recommended for Technical Users)
**Perfect for:** IT administrators, network engineers, technical troubleshooting

**🌐 Access:** [http://localhost:11030](http://localhost:11030)

**🎤 Try These Commands:**
- "How many devices do we have?"
- "Check network health"
- "Show me critical issues"
- "Device count by organization"
- "Network summary"

---

## 📱 **How to Use (Super Simple!)**

### **Step 1: Click the Link Above** 
Choose restaurant operations OR network management

### **Step 2: Click the Big Microphone Button** 🎤
The microphone will turn green when listening

### **Step 3: Speak Your Question**
Use natural language - no technical jargon required!

### **Step 4: Listen to the Response**
The system will both display text and speak the answer

---

## 🏢 **Restaurant Organizations Supported**
- **Arby's** (~2,000-3,000 FortiManager devices)
- **Buffalo Wild Wings** (~2,500-3,500 FortiManager devices)  
- **Sonic** (~7,000-10,000 FortiManager devices)
- **Plus 7,816 existing Meraki devices**
- **25,000+ total devices across restaurant networks**
- **Multi-vendor support: Meraki + Fortinet**

---

## 🛠 **Advanced Features Access**

### **📈 Grafana Dashboards** (Restaurant Network Monitoring)
- **URL:** [http://localhost:11002](http://localhost:11002)
- **Username:** `admin`
- **Password:** `admin`
- **Use For:** Real-time monitoring, restaurant network dashboards, alerts

### **🔍 Prometheus Metrics** (Network Performance Monitoring)
- **URL:** [http://localhost:9090](http://localhost:9090)
- **Use For:** Network health metrics, FortiManager status, performance monitoring

### **📊 Neo4j Database Browser** (For Advanced Users)
- **URL:** [http://localhost:7474](http://localhost:7474)
- **Username:** `neo4j`
- **Password:** `password`
- **Use For:** Custom queries, data exploration, reports

### **API Endpoints** (For Developers)
- **Restaurant API:** `http://localhost:11032/api/restaurant-command`
- **Network API:** `http://localhost:11030/api/process-command`
- **Method:** POST with JSON: `{"command": "your voice command"}`

### **Sample API Calls:**
```bash
# Restaurant Equipment Check
curl -X POST http://localhost:11032/api/restaurant-command \
  -H "Content-Type: application/json" \
  -d '{"command": "How are our POS systems?"}'

# Network Health Check  
curl -X POST http://localhost:11030/api/process-command \
  -H "Content-Type: application/json" \
  -d '{"command": "Check network health"}'
```

---

## 🎯 **Quick Reference - Voice Commands**

### 🍴 **Restaurant Commands:**
| What You Want to Know | Say This |
|----------------------|----------|
| Payment systems status | "How are our POS systems?" |
| Kitchen equipment | "Check kitchen equipment" |
| Drive-thru problems | "Any drive-thru issues?" |
| Self-service kiosks | "Are the kiosks working?" |
| Digital menu boards | "Check menu boards" |
| Specific location | "Check equipment at store 4472" |
| Specific brand | "How is Buffalo Wild Wings?" |
| Critical issues | "What equipment is down?" |

### 🌐 **Network Commands:**
| What You Want to Know | Say This |
|----------------------|----------|
| Total devices | "How many devices?" |
| Network health | "Check network health" |
| Problems | "Any critical issues?" |
| Device breakdown | "Show device types" |
| Organization summary | "Network summary" |
| Health by org | "Check Inspire Brands health" |

---

## 📞 **Getting Help**

### **If Voice Recognition Doesn't Work:**
1. **Check browser:** Use Chrome, Edge, or Safari (Firefox may have issues)
2. **Check microphone:** Make sure your browser has microphone permission
3. **Speak clearly:** Wait for the green microphone before speaking

### **If You Get No Response:**
1. **Check the services:** Make sure the applications are running
2. **Try simpler commands:** Start with "How many devices?" 
3. **Check network connection:** Ensure localhost access is working

### **For Technical Support:**
- **System Status:** Check if services are running on ports 11030 and 11032
- **Database Access:** Try [http://localhost:7474](http://localhost:7474)
- **Logs:** Check console output for error messages

---

## 🚀 **Advanced Use Cases**

### **For Restaurant Regional Managers:**
- Monitor equipment across multiple brands
- Check critical systems during peak hours  
- Identify locations with recurring issues
- Voice-control for hands-free monitoring

### **For IT Operations:**
- Network health monitoring
- Device inventory management
- Proactive issue identification
- Integration with existing monitoring tools

### **For C-Level Executives:**
- High-level operational dashboards
- Business impact of technical issues
- Multi-location performance overview
- Voice-controlled executive reporting

---

## 💡 **Pro Tips for Maximum Adoption**

### **For Restaurant Staff:**
- **Bookmark:** [http://localhost:11032](http://localhost:11032) 
- **Mobile Friendly:** Works on tablets and phones
- **No Training Required:** Use natural language
- **Quick Checks:** Perfect for shift handovers

### **For IT Teams:**
- **Bookmark:** [http://localhost:11030](http://localhost:11030)
- **API Integration:** Build custom dashboards
- **Scheduled Monitoring:** Automate health checks
- **Custom Queries:** Use Neo4j browser for deep analysis

### **Making It Stick:**
1. **Start Simple:** Begin with basic commands
2. **Daily Use:** Check systems during shift changes
3. **Share Success:** Show colleagues how easy it is
4. **Build Habits:** Integrate into daily workflows

---

*📧 Questions? Issues? Want new features? This system is designed to grow with your needs!*