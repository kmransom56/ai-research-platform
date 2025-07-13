# AI Research Platform Scripts Reference

## Core Platform Management

### `startup-platform.sh` 🚀
**Primary startup script** - Comprehensive service startup with all phases
- ✅ UV environment support
- ✅ All services (Backend:11000, AutoGen:11001, Webhook:11002, Magentic-One:11003, Port Scanner:11010)
- ✅ Health verification
- ✅ Docker services
- ✅ Infrastructure dependencies
- **Usage:** `./startup-platform.sh`

### `stop-platform.sh` 🛑
**Complete shutdown script** - Graceful service shutdown
- ✅ Phased shutdown (monitoring → core → network → docker → cleanup)
- ✅ PID management
- ✅ Port verification
- ✅ Log rotation
- **Usage:** `./scripts/platform-management/stop-platform.sh`

### `check-platform-status.sh` 📊
**Comprehensive status checker** - Full platform health check
- ✅ All service endpoints
- ✅ PID verification
- ✅ Docker containers
- ✅ Systemd services
- ✅ Platform health summary
- **Usage:** `./scripts/platform-management/check-platform-status.sh`

### `manage-platform.sh` 🎛️
**User-friendly management interface** - Simple platform control
- Commands: `status`, `start`, `stop`, `restart`, `logs`, `backup`, `restore`
- **Usage:** `./manage-platform.sh status`

## Configuration Management

### `scripts/config-management/validate-config.sh` ✅
**Configuration validation** - Runs every 15 minutes via cron
- Port configuration checking
- Service health verification
- Configuration snapshots
- **Usage:** Automatic via cron

### `scripts/config-management/protect-config.sh` 🔒
**Configuration protection** - Prevents unauthorized changes
- File protection mechanisms
- Backup validation
- **Usage:** `./scripts/config-management/protect-config.sh`

### `scripts/config-management/fix-configuration-drift.sh` 🔧
**Configuration drift fix** - Solves reboot configuration issues
- Fixes systemd conflicts
- Consolidates startup systems
- **Usage:** `./scripts/config-management/fix-configuration-drift.sh`

### `scripts/utilities/switch-ai-provider.sh` 🔄
**AI provider switching** - Switch between OpenAI/Azure
- Configuration backup
- Provider switching
- Health testing
- **Usage:** `./scripts/utilities/switch-ai-provider.sh openai`

## Backup & Recovery

### `scripts/backup-recovery/backup-configs.sh` 💾
**Manual configuration backup**
- Creates timestamped backups
- **Usage:** `./scripts/backup-recovery/backup-configs.sh`

### `scripts/backup-recovery/backup-configs-auto.sh` ⏰
**Automated backup** - Runs every 6 hours via cron
- **Usage:** Automatic via cron

### `scripts/backup-recovery/restore-config.sh` 🔄
**Configuration restoration**
- **Usage:** `./scripts/backup-recovery/restore-config.sh [backup_name]`

### `scripts/backup-recovery/emergency-reset.sh` 🚨
**Emergency platform reset**
- Resets to default configuration
- **Usage:** `./emergency-reset.sh`

## Monitoring

### `health-monitor.sh` 🏥
**Continuous health monitoring**
- Service health checks
- Auto-recovery
- **Usage:** Runs in background

### `file-monitor.sh` 👁️
**Configuration file monitoring**
- Watches for configuration changes
- **Usage:** Runs in background

## Certificate Management (NEW)

### `scripts/infrastructure/request-ca-certificate.sh` 🔐
**CA Certificate Integration** - Request certificates from internal CA server
- ✅ Automated certificate generation from CA at https://192.168.0.2
- ✅ Multi-endpoint fallback system
- ✅ nginx configuration automation
- ✅ Self-signed certificate fallback
- **Usage:** `./scripts/infrastructure/request-ca-certificate.sh -d domain.local -p 11005 -s servicename`

### `scripts/infrastructure/check-ca-server-status.sh` 📊
**CA Server Monitoring** - Monitor CA server health and API status
- ✅ API endpoint testing (generate-cert, sign-csr, ca, setup-chain)
- ✅ Certificate generation testing
- ✅ Health monitoring and logging
- **Usage:** `./scripts/infrastructure/check-ca-server-status.sh`

### `scripts/infrastructure/generate-self-signed-cert.sh` 🛡️
**Self-signed Certificate Generator** - Fallback certificate generation
- ✅ Automatic certificate generation
- ✅ nginx configuration
- ✅ Proper permissions and security
- **Usage:** `./scripts/infrastructure/generate-self-signed-cert.sh domain.local 11005`

### `scripts/infrastructure/renew-ca-certificates.sh` 🔄
**Certificate Renewal Automation** - Automated certificate lifecycle management
- ✅ Certificate expiration monitoring
- ✅ Automated renewal workflow
- ✅ Health checks and validation
- **Usage:** `./scripts/infrastructure/renew-ca-certificates.sh`

### `scripts/platform-management/add-application.sh` ⚡
**Application Addition Automation** - Standardized application deployment
- ✅ Complete application integration
- ✅ CA certificate automation
- ✅ nginx configuration
- ✅ Docker service management
- ✅ Dashboard integration
- **Usage:** `./scripts/platform-management/add-application.sh --name windmill --port 11005 --description "Workflow Automation"`

## Deployment

### `deploy.sh` 🚀
**Deployment automation**
- Git pull and build
- Service restart
- **Usage:** `./deploy.sh`

## Port Assignments

- **Backend API:** 11000
- **AutoGen Studio:** 11001  
- **Webhook Server:** 11002
- **Magentic-One:** 11003
- **Windmill (SSL):** 11005 (NEW)
- **Windmill (Container):** 11006 (NEW)
- **Port Scanner:** 11010
- **Nginx Proxy Manager:** 11080-11082
- **Ollama:** 11434

## Quick Commands

```bash
# Start platform
./startup-platform.sh

# Check status
./check-platform-status.sh

# Stop platform  
./stop-platform.sh

# User-friendly management
./manage-platform.sh status
./manage-platform.sh start
./manage-platform.sh logs autogen-studio

# Certificate Management (NEW)
./scripts/infrastructure/check-ca-server-status.sh
./scripts/infrastructure/request-ca-certificate.sh -d windmill.local -p 11005 -s windmill
./scripts/platform-management/add-application.sh --name newapp --port 11007

# Fix configuration issues
./fix-configuration-drift.sh

# Backup configuration
./backup-configs.sh
```

## Certificate Automation Features (NEW)

### CA Server Integration
- **CA Server URL:** https://192.168.0.2
- **Supported Endpoints:** `/api/generate-cert`, `/api/sign-csr`, `/api/ca`, `/api/setup-chain`
- **Certificate Inventory:** 5 active certificates managed
- **Download Support:** Full certificate and key retrieval
- **Validation:** OpenSSL verification integrated

### Certificate Types Supported
- **Server Certificates:** Standard SSL certificates
- **HTTPS Certificates:** Web server certificates  
- **nginx Certificates:** nginx-specific configurations
- **CSR-based Certificates:** Custom certificate signing requests

### Automation Capabilities
- **Automatic Generation:** CA API integration
- **Self-signed Fallback:** Development certificate support
- **nginx Integration:** Automatic SSL configuration
- **Certificate Monitoring:** Expiration tracking and renewal
- **Multi-endpoint Support:** Robust API communication
