# Chat Copilot Configuration Notes

## Issue Resolution - Configuration Drift

**Problem:** Application fails to start after reboots due to configuration drift

**Root Causes Identified:**
1. MUI dependencies conflicted with existing FluentUI components
2. TypeScript esModuleInterop setting was incorrectly changed
3. Backend/Frontend port mismatches (backend on 40443, frontend expecting 10500)
4. Built frontend assets overwriting source HTML
5. Multiple overlapping startup scripts with different configurations

**Fixes Applied:**
1. Removed MUI dependencies from package.json (@mui/material, @emotion/react, @emotion/styled, ajv)
2. Reverted esModuleInterop to false in tsconfig.json
3. Fixed backend port configuration to 40443 in appsettings.json
4. Restored clean index.html in webapi/wwwroot
5. Standardized service startup configuration

**Current Configuration:**
- Backend: http://0.0.0.0:11000 (configured in webapi/appsettings.json)
- Frontend Development: http://0.0.0.0:3000 (npm start)
- Frontend Production: Served from backend at :11000
- Authentication: None (for development)
- AI Provider: OpenAI via Ollama (localhost:11434)

**Service Management:**
- Use `./startup-platform.sh` for service startup
- Backend serves frontend in production
- Frontend development uses npm/yarn start
- All logs in `/home/keith/chat-copilot/logs/`

**Port Configuration:**
- Backend API: 11000
- AutoGen Studio: 11001
- Webhook Server: 11002
- Magentic-One: 11003
- Port Scanner: 11010
- Nginx Proxy Manager Web UI: 11080
- Nginx Proxy Manager HTTP: 11081
- Nginx Proxy Manager HTTPS: 11082
- Ollama: 11434
- Frontend Dev: 3000

## Commands to Run After Fixing Configuration Drift:

```bash
# Clean frontend build
cd webapp && rm -rf build/ node_modules/.cache

# Reinstall dependencies
yarn install

# Build frontend for production
yarn build

# Copy build to backend
cp -r build/* ../webapi/wwwroot/

# Start backend (serves frontend)
cd ../webapi && dotnet run
```

## Configuration Drift Prevention (CRITICAL)

**ROOT CAUSE:** The `/home/keith/chat-copilot/scripts/configure.sh` script was forcibly overwriting `webapp/.env` on every reboot via cron job.

**PERMANENT FIXES APPLIED:**
1. **Modified configure.sh** to preserve existing .env files and use correct port (11000)
2. **Modified Configure.ps1** to preserve existing .env files and use correct port (11000)
3. **Updated startup-platform.sh** to use new port configuration (11000-11003 range)
4. **Updated auto_startup_manager.py** with correct port assignments
5. **Fixed hostname** in default .env creation (now uses `100.123.10.72:11000`)

**Configuration Backup System:**
- **Local Backups:** Run `./backup-configs.sh` to create timestamped backups
- **Restore:** Use `config-backups/[timestamp]/restore.sh` to restore configurations
- **Bacula Integration:** Use `bacula-chat-copilot-configs.conf` for remote backups

**Prevention Checklist:**
- ✅ Configure scripts no longer overwrite existing .env files
- ✅ Backup system in place for critical configurations
- ✅ Frontend .env points to correct backend URI (100.123.10.72:40443)
- ✅ Backend configured for correct port (40443)

**Manual Backup Before Changes:**
```bash
# Create configuration backup before making changes
./backup-configs.sh

# Check current configuration
cat webapp/.env
cat webapi/appsettings.json
```

**Emergency Restore:**
```bash
# List available backups
ls -la config-backups/

# Restore from latest backup
config-backups/config_backup_[latest]/restore.sh
```

## Lint/Typecheck Commands:
- `cd webapp && yarn lint` - Run ESLint
- `cd webapp && yarn lint:fix` - Fix ESLint errors  
- `cd webapp && yarn build` - TypeScript compile check
- `cd webapi && dotnet build` - Backend build check

## Configuration Drift Troubleshooting

**Memory:** How can we be sure that config drift won't happen on the next reboot, it hasn't been successful in a couple days now
- Recommendation: Implement strict configuration validation in startup scripts
- Add explicit configuration checks before service startup
- Create a pre-flight configuration verification script that:
  1. Validates .env file integrity
  2. Checks port configurations
  3. Verifies file permissions
  4. Logs any inconsistencies before allowing services to start
- Consider adding a failsafe mechanism that prevents startup if critical configuration parameters are incorrect