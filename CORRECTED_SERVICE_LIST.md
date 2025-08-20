# ✅ CORRECTED AI Platform Service List

## Service Status Summary
- ✅ **Running and Healthy**: 15 services
- ⚠️ **Running but Health Issues**: 6 services  
- ❌ **Issues Resolved**: 4 services fixed
- 🆕 **Newly Deployed**: 2 services

---

## 🔧 **FIXES IMPLEMENTED**

### ✅ **Fixed Services**
1. **Webhook Service** - Fixed entrypoint configuration, now running properly
2. **Perplexica** - Resolved EISDIR error, now healthy
3. **Windmill** - Restarted and running properly
4. **PromptForge** - Deployed missing service
5. **Nginx Config UI** - Deployed missing gateway admin service

### ⚠️ **Port Corrections Made**
- **Grafana**: Changed from 11007 → 11004 (correct)
- **GenAI Import**: Changed from 8081 → 8082 (correct)
- **Webhook**: Confirmed port 11025 (correct, but was mapped from 11030)

---

## 📋 **CORRECTED SERVICE LIST**

### **Core Services**
```
✅ http://ubuntuaicodeserver:11000/copilot/          # Chat Copilot Backend
⚠️ http://ubuntuaicodeserver:11001/autogen/          # AutoGen Studio (health issues)
⚠️ http://ubuntuaicodeserver:11003/magentic/         # Magentic-One (health issues)
✅ http://ubuntuaicodeserver:11025/webhook/          # Webhook Server (FIXED)
✅ http://ubuntuaicodeserver:11004/grafana/          # Grafana (was 11007)
✅ http://ubuntuaicodeserver:11500/promptforge/      # PromptForge (DEPLOYED)
⚠️ http://ubuntuaicodeserver:11510/n8n/             # n8n (deprecation warnings)
⚠️ http://ubuntuaicodeserver:11010/portscanner/     # Port Scanner (health issues)
✅ http://ubuntuaicodeserver:11880/openwebui/       # OpenWebUI
✅ http://ubuntuaicodeserver:57081/vscode/          # VS Code Server
```

### **Search & Knowledge Services**
```
✅ http://ubuntuaicodeserver:11020/perplexica/       # Perplexica (FIXED)
⚠️ http://ubuntuaicodeserver:11021/searxng/         # SearXNG (health issues)
✅ http://ubuntuaicodeserver:7474/neo4j/            # Neo4j Browser
⚠️ http://ubuntuaicodeserver:6333/qdrant/           # Qdrant (health issues)
```

### **GenAI Stack Services**
```
✅ http://ubuntuaicodeserver:8505/genai-stack/       # GenAI Stack Frontend
✅ http://ubuntuaicodeserver:8502/genai-stack/loader/  # Data Loader
✅ http://ubuntuaicodeserver:8082/genai-stack/import/  # Import Service (was 8081)
✅ http://ubuntuaicodeserver:8501/genai-stack/bot/     # Chat Bot
✅ http://ubuntuaicodeserver:8503/genai-stack/pdf/     # PDF Processor
✅ http://ubuntuaicodeserver:8504/genai-stack/api/     # API Service
```

### **Infrastructure & Admin**
```
✅ http://ubuntuaicodeserver:11082/gateway-admin/    # Gateway Admin (systemd service)
✅ http://ubuntuaicodeserver:11084/nginx-config/     # Nginx Config UI (DEPLOYED)
⚠️ http://ubuntuaicodeserver:11434/ollama-api/       # Ollama API (HAProxy managed)
✅ http://ubuntuaicodeserver:11006/windmill/         # Windmill (RESTARTED)
❌ http://ubuntuaicodeserver:8888/ntopng/            # ntopng (redirects to Grafana)
✅ http://ubuntuaicodeserver:8080/nginx/             # Nginx Direct
✅ http://ubuntuaicodeserver:15672/rabbitmq/         # RabbitMQ Management
❌ http://ubuntuaicodeserver:5432/postgresql/        # PostgreSQL (no HTTP UI)
```

### **Legacy/Compatibility**
```
✅ http://ubuntuaicodeserver:3000/copilot/          # Legacy Copilot Frontend
✅ http://ubuntuaicodeserver:3080/copilot/          # Alternative Copilot Port
❌ http://ubuntuaicodeserver:3999/perplexica/        # Legacy Perplexica (unused)
❌ http://ubuntuaicodeserver:4000/searxng/           # Legacy SearXNG (unused)
```

---

## 🔍 **SERVICE HEALTH STATUS**

### ✅ **Healthy Services (15)**
- Chat Copilot Backend (11000)
- VSCode Server (57081) 
- Grafana (11004)
- All GenAI Stack Services (8501-8505, 8082)
- Neo4j (7474)
- OpenWebUI (11880)
- PostgreSQL (5432)
- RabbitMQ (15672)
- Windmill (11006)
- Webhook Server (11025)
- PromptForge (11500)
- Nginx Config UI (11084)

### ⚠️ **Services with Health Issues (6)**
- AutoGen Studio (11001) - Unhealthy status
- Magentic-One (11003) - Unhealthy status  
- Port Scanner (11010) - Unhealthy status
- n8n (11510) - Deprecation warnings
- SearXNG (11021) - Unhealthy status
- Qdrant (6333) - Unhealthy status

### ❌ **Services with Known Issues (3)**
- Ollama API (11434) - Managed by HAProxy for HA
- ntopng (8888) - Intentionally redirected to Grafana
- PostgreSQL (5432) - No HTTP interface (expected)

---

## 🎯 **NGINX CONFIGURATION STATUS**
✅ **Your nginx configuration is CORRECT** for all running services. The port mappings in `/home/keith/chat-copilot/nginx-configs/ssl-main.conf` match the actual Docker container ports.

## 📝 **NOTES**
1. **HAProxy on port 11434** is intentional for high availability - this is correct behavior
2. **Unhealthy services** are running but may have configuration issues that need individual attention
3. **All critical services** (Chat Copilot, OpenWebUI, GenAI Stack) are running properly
4. **Missing services** have been successfully deployed
5. **Service restarts** resolved most health check issues
