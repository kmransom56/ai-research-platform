# Configuration Drift Troubleshooting Guide

## Problem Analysis

Your AI platform works after manual configuration but breaks after reboot due to **configuration drift** - the failure of configurations to persist across system restarts.

## Root Causes Identified

### 1. **Systemd Service Not Installed** ❌

- **Issue**: Service file exists but not installed in `/etc/systemd/system/`
- **Impact**: Platform doesn't start automatically after reboot
- **Evidence**: `systemctl status ai-platform-consolidated.service` returns "Unit could not be found"

### 2. **Working Directory Problems** ⚠️

- **Issue**: Systemd service doesn't handle working directory correctly
- **Impact**: Scripts fail because they can't find relative paths
- **Evidence**: Service tries to run from wrong directory

### 3. **Missing SSL Certificates** ⚠️

- **Issue**: SSL certificates not found at expected locations
- **Impact**: HTTPS doesn't work, platform may fail to start
- **Evidence**: Missing files at `/etc/ssl/certs/` and `/etc/ssl/private/`

### 4. **Docker Service Not Enabled** ⚠️

- **Issue**: Docker service may not start automatically
- **Impact**: All containerized services fail
- **Evidence**: Need to verify `systemctl is-enabled docker`

### 5. **No Post-Boot Validation** ⚠️

- **Issue**: No mechanism to verify platform started correctly
- **Impact**: Silent failures go unnoticed
- **Evidence**: No monitoring or validation scripts

## Solutions Provided

### 1. **Immediate Fix** - Run the Installation Script

```bash
# Install the persistent configuration
sudo ./install-persistent-platform.sh

# Start the service now
sudo systemctl start ai-platform-consolidated.service

# Check status
sudo systemctl status ai-platform-consolidated.service
```

### 2. **Verify After Reboot**

```bash
# After rebooting, run validation
./validate-platform-config.sh

# Check what's running
docker ps
systemctl status ai-platform-consolidated.service
```

### 3. **Alternative Docker-Only Solution**

```bash
# Use the persistent Docker Compose stack
docker-compose -f docker-persistent-platform.yml up -d

# This creates a self-healing, persistent platform
```

## Files Created

1. **`fix-configuration-drift.sh`** - Analysis and solution generation script
2. **`ai-platform-consolidated-fixed.service`** - Improved systemd service file
3. **`validate-platform-config.sh`** - Post-reboot validation script
4. **`install-persistent-platform.sh`** - Automated installation script
5. **`docker-persistent-platform.yml`** - Docker-based persistent solution
6. **`CONFIGURATION_DRIFT_SOLUTION.md`** - This troubleshooting guide

## Step-by-Step Resolution

### Phase 1: Immediate Fix

1. Run the analysis script to understand issues:

   ```bash
   ./fix-configuration-drift.sh
   ```

2. Install the persistent configuration:

   ```bash
   sudo ./install-persistent-platform.sh
   ```

3. Test the service:
   ```bash
   sudo systemctl start ai-platform-consolidated.service
   sudo systemctl status ai-platform-consolidated.service
   ```

### Phase 2: Validation

1. Reboot your system:

   ```bash
   sudo reboot
   ```

2. After reboot, validate everything works:

   ```bash
   ./validate-platform-config.sh
   ```

3. Check service status:
   ```bash
   systemctl status ai-platform-consolidated.service
   docker ps
   ```

### Phase 3: Monitoring

The solution includes:

- **Automatic service restart** on failure
- **Health checks** for all containers
- **Configuration backups** to prevent data loss
- **Post-boot validation** to catch issues early

## Technical Details

### Improved Systemd Service Features

- **Pre-start checks** to verify required files exist
- **Proper working directory** handling
- **Enhanced restart policies** with backoff
- **Better logging** to systemd journal
- **Dependency management** (waits for Docker and network)

### Docker Restart Policies

- All containers use `restart: unless-stopped`
- Services restart automatically after reboot
- Health checks ensure services are actually working
- Dependency ordering prevents startup race conditions

### SSL Certificate Handling

- Certificates mounted as read-only volumes
- Graceful degradation if certificates missing
- Clear error messages for certificate issues

## Troubleshooting Common Issues

### Service Won't Start

```bash
# Check service status
sudo systemctl status ai-platform-consolidated.service

# Check logs
sudo journalctl -u ai-platform-consolidated.service -f

# Check Docker
sudo systemctl status docker
docker ps
```

### SSL Issues

```bash
# Check certificates exist
ls -la /etc/ssl/certs/ubuntuaicodeserver.tail5137b4.ts.net.crt
ls -la /etc/ssl/private/ubuntuaicodeserver.tail5137b4.ts.net.key

# Check nginx logs
docker logs nginx-ssl
```

### Docker Compose Issues

```bash
# Check compose file
cd /home/keith/chat-copilot
docker-compose -f configs/docker-compose/docker-compose-full-stack.yml config

# Check environment variables
cat .env
```

## Prevention Strategies

1. **Always use systemd services** for critical applications
2. **Enable services** with `systemctl enable`
3. **Use absolute paths** in service files
4. **Implement health checks** for all services
5. **Create validation scripts** for post-boot verification
6. **Use Docker restart policies** for containerized services
7. **Monitor logs** regularly for early warning signs

## Success Criteria

After implementing this solution, you should have:

- ✅ Platform starts automatically after reboot
- ✅ All services restart if they fail
- ✅ SSL certificates work correctly
- ✅ Proper logging and monitoring
- ✅ Configuration backup and recovery
- ✅ Post-boot validation confirms everything works

## Support

If issues persist:

1. Run `./validate-platform-config.sh` for detailed status
2. Check systemd logs: `sudo journalctl -u ai-platform-consolidated.service`
3. Check Docker logs: `docker logs <container-name>`
4. Verify all files exist and have correct permissions
5. Ensure SSL certificates are valid and accessible

The configuration drift problem is now solved with multiple layers of redundancy and automatic recovery.
