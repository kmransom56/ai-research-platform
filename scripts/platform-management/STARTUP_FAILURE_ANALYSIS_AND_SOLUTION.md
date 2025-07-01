# Startup Failure Analysis & Permanent Solution

## 🔍 Root Cause Analysis

### Primary Issue: Conflicting Service Management

The repeated startup failures after reboot are caused by **multiple systemd services trying to manage the same Docker containers**, creating conflicts and preventing proper startup.

### Identified Conflicts:

1. **ai-platform-consolidated.service** (enabled)

   - Tries to run `/home/keith/chat-copilot/start-ssl-platform.sh`
   - Uses `docker-compose-full-stack.yml`
   - Status: **FAILING** (auto-restart loop)

2. **Manual Docker Compose** (what we've been using)

   - Uses `/home/keith/chat-copilot/docker/docker-compose.yml`
   - Works when started manually
   - Conflicts with systemd service

3. **Additional Enabled Services:**
   - `ai-platform-restore.service` (enabled)
   - `ai-platform-validator.service` (enabled)
   - `ai-platform.service` (enabled)
   - `ollama-ai-platform.service` (enabled)

## 🚨 Current Problems

### Service Status Issues:

```bash
# ai-platform-consolidated.service is in auto-restart loop
systemctl status ai-platform-consolidated.service
# Shows: activating (auto-restart) (Result: exit-code)
```

### Container Conflicts:

- Systemd services try to start containers
- Manual docker-compose commands conflict
- Containers get stopped/started repeatedly
- Port conflicts and resource contention

### URL Issues in HTML Files:

Both `control-panel.html` and `applications.html` contain:

- **Hardcoded IP addresses** (100.123.10.72)
- **Hardcoded Tailscale domains** (ubuntuaicodeserver-1.tail5137b4.ts.net)
- **Mixed port references** that may not match actual running services

## ✅ Permanent Solution

### Step 1: Disable Conflicting Systemd Services

```bash
# Stop and disable all conflicting AI platform services
sudo systemctl stop ai-platform-consolidated.service
sudo systemctl disable ai-platform-consolidated.service

sudo systemctl stop ai-platform-restore.service
sudo systemctl disable ai-platform-restore.service

sudo systemctl stop ai-platform-validator.service
sudo systemctl disable ai-platform-validator.service

sudo systemctl stop ai-platform.service
sudo systemctl disable ai-platform.service

sudo systemctl stop ollama-ai-platform.service
sudo systemctl disable ollama-ai-platform.service

# Reload systemd to apply changes
sudo systemctl daemon-reload
```

### Step 2: Create Single Unified Startup Service

Create a new, simplified service that properly manages the platform:

```bash
# Create new unified service
sudo tee /etc/systemd/system/ai-platform-unified.service << 'EOF'
[Unit]
Description=AI Research Platform - Unified Stack
Documentation=https://github.com/kmransom56/ai-research-platform
After=network-online.target docker.service tailscaled.service
Wants=network-online.target
Requires=docker.service

[Service]
Type=forking
User=keith
Group=keith
WorkingDirectory=/home/keith/chat-copilot/scripts/platform-management

# Environment setup
Environment=HOME=/home/keith
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/keith/.local/bin
Environment=DOCKER_HOST=unix:///var/run/docker.sock

# Use the working startup script
ExecStart=/home/keith/chat-copilot/scripts/platform-management/startup-platform.sh
ExecStop=/home/keith/chat-copilot/scripts/platform-management/stop-platform.sh

# Restart policy
Restart=on-failure
RestartSec=60
TimeoutStartSec=300
TimeoutStopSec=120

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-platform-unified

[Install]
WantedBy=multi-user.target
EOF

# Enable the new service
sudo systemctl enable ai-platform-unified.service
```

### Step 3: Fix URL Issues in HTML Files

The HTML files need dynamic host detection instead of hardcoded IPs:

#### Issues Found:

1. **control-panel.html**: Contains hardcoded `100.123.10.72` and `ubuntuaicodeserver-1.tail5137b4.ts.net`
2. **applications.html**: Contains hardcoded `100.123.10.72` references
3. **Port mismatches**: Some services may be on different ports than expected

#### Solution:

Both files already contain JavaScript patches for dynamic host rewriting, but they need verification:

```javascript
// The files contain this dynamic patching code:
const LEGACY_HOSTS = [
  "ubuntuaicodeserver-1.tail5137b4.ts.net",
  "100.123.10.72",
];
// This should rewrite URLs to use current host
```

### Step 4: Create Startup Validation Script

```bash
# Create validation script
cat > /home/keith/chat-copilot/scripts/platform-management/validate-startup.sh << 'EOF'
#!/bin/bash

echo "🔍 AI Platform Startup Validation"
echo "=================================="

# Check systemd services
echo "📋 Checking systemd services..."
systemctl is-active ai-platform-unified.service
systemctl is-enabled ai-platform-unified.service

# Check Docker containers
echo "🐳 Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(chat-copilot|openwebui|genai|nginx|rabbitmq|qdrant)"

# Check key services
echo "🌐 Testing service endpoints..."
services=(
    "http://localhost:3000"
    "http://localhost:3080/healthz"
    "http://localhost:11880"
    "http://localhost:8505"
    "http://localhost:11082"
)

for service in "${services[@]}"; do
    if curl -s -o /dev/null -w "%{http_code}" "$service" | grep -q "200"; then
        echo "✅ $service - OK"
    else
        echo "❌ $service - FAILED"
    fi
done

echo "🎯 Validation complete"
EOF

chmod +x /home/keith/chat-copilot/scripts/platform-management/validate-startup.sh
```

### Step 5: Update Existing Startup Scripts

Ensure the startup scripts handle dependencies properly:

```bash
# Update startup-platform.sh to be more robust
# Add proper dependency checking
# Add container health checks
# Add retry logic for failed services
```

## 🔧 Implementation Commands

### Immediate Fix (Run Now):

```bash
# 1. Stop conflicting services
sudo systemctl stop ai-platform-consolidated.service ai-platform-restore.service ai-platform-validator.service ai-platform.service ollama-ai-platform.service

# 2. Disable them permanently
sudo systemctl disable ai-platform-consolidated.service ai-platform-restore.service ai-platform-validator.service ai-platform.service ollama-ai-platform.service

# 3. Clean up any orphaned containers
docker system prune -f

# 4. Start services manually for now
cd /home/keith/chat-copilot/docker && docker-compose up -d

# 5. Verify everything works
docker ps
curl http://localhost:3000
curl http://localhost:3080/healthz
```

### Long-term Fix (After Testing):

```bash
# Create and enable unified service
sudo systemctl enable ai-platform-unified.service
sudo systemctl start ai-platform-unified.service

# Test reboot behavior
sudo reboot
# After reboot, run validation
./validate-startup.sh
```

## 📊 Expected Results

### After Implementation:

- ✅ **No more startup failures** - Single service manages everything
- ✅ **Consistent post-reboot behavior** - Services start automatically
- ✅ **No container conflicts** - Unified management
- ✅ **Proper dependency handling** - Services start in correct order
- ✅ **Better logging** - Centralized service logs
- ✅ **Easier troubleshooting** - Single point of control

### Service URLs Will Work:

- ✅ Chat Copilot: http://localhost:3000
- ✅ Open WebUI: http://localhost:11880
- ✅ GenAI Stack: http://localhost:8505
- ✅ All other services as configured

## 🎯 Next Steps

1. **Implement the immediate fix** to stop current conflicts
2. **Test the unified service approach**
3. **Validate all URLs in HTML files** work with current setup
4. **Create monitoring** to detect future startup issues
5. **Document the final configuration** for future reference

This solution addresses the root cause of repeated startup failures and provides a robust, maintainable platform management system.
