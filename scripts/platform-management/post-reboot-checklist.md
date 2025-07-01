# Post-Reboot Validation Checklist

## After Reboot - Validation Steps:

### 1. Basic System Check

```bash
cd /home/keith/chat-copilot/scripts/platform-management
./health-check.sh
```

### 2. Clean Platform Startup

```bash
./startup-platform-clean.sh
```

### 3. Verify All Services

```bash
./manage-platform.sh status
```

### 4. Check for Configuration Drift

```bash
./check-platform-status.sh
```

### 5. Validate Port Configuration

```bash
cd /home/keith/chat-copilot/python/config-management
python3 /home/keith/chat-copilot/python/config-management/port-config-validator.py
```

## Expected Results:

- 17/17 services healthy
- All ports correct (webhook-server on 11025, nginx-proxy on 8080, etc.)
- No Caddy/HTTPS references
- No Fortinet references
- All Docker containers start properly
- No port conflicts

## Key Services to Verify:

- webhook-server: http://localhost:11025
- nginx-proxy-manager: http://localhost:8080
- chat-copilot: http://localhost:11000
- All GenAI Stack services
- ntopng, Neo4j services

## If Issues Found:

1. Check logs in /home/keith/chat-copilot/logs/
2. Run ./fix-configuration-drift.sh
3. Use ./fix-existing-service.sh for individual services
