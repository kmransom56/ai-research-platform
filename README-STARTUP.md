# AI Research Platform Startup Guide

## Enhanced Startup Scripts with Automatic Cleanup

The startup process now includes comprehensive cleanup to prevent port conflicts and ensure reliable platform startup.

## Quick Start

### Option 1: Direct Startup (Recommended)
```bash
./start-ssl-platform.sh
```
This script now automatically:
- Stops all competing systemd services
- Stops and removes all Docker containers
- Kills processes on critical ports
- Cleans up Docker networks and volumes
- Runs pre-flight checks
- Starts the platform cleanly

### Option 2: Manual Cleanup First
If you want to run cleanup separately:
```bash
./cleanup-platform.sh
./start-ssl-platform.sh
```

## What the Enhanced Scripts Do

### Automatic Cleanup Features:
1. **Systemd Service Cleanup**:
   - Stops: `ai-platform-*`, `ollama-ai-platform`, `multifamily-valuation-app`
   - Disables auto-restart for competing services

2. **Docker Container Cleanup**:
   - Stops all running containers
   - Removes stopped containers
   - Prunes unused networks and volumes

3. **Port Cleanup**:
   - Kills processes on critical ports: 11000-11021, 8501-8505, 3000, 7474, 7687
   - Verifies ports are free before starting

4. **Pre-flight Checks**:
   - Verifies Docker is installed and running
   - Checks for remaining port conflicts
   - Re-runs cleanup if conflicts detected

### Critical Ports Monitored:
- **11000**: Chat Copilot Backend
- **11001**: AutoGen Studio  
- **11007**: Grafana
- **11020**: Perplexica
- **8502**: GenAI Stack Loader
- **8505**: GenAI Stack Frontend
- **3000**: React Frontend
- **7474, 7687**: Neo4j Database

## Troubleshooting

### If startup still fails with port conflicts:
1. Run manual cleanup: `./cleanup-platform.sh`
2. Check for stubborn processes: `sudo netstat -tulpn | grep -E ':(11001|11007|11020|8502|8505)'`
3. Manually kill any remaining processes: `sudo kill -9 <PID>`
4. Try startup again: `./start-ssl-platform.sh`

### If Docker services won't stop:
```bash
# Force stop all containers
docker kill $(docker ps -aq) 2>/dev/null || true

# Clean up everything
docker system prune -af --volumes

# Restart Docker daemon
sudo systemctl restart docker
```

### If systemd services keep restarting:
```bash
# Disable problematic services permanently
sudo systemctl disable --now ai-platform-*.service
sudo systemctl disable --now multifamily-valuation-app.service
```

## Files Modified:
- `start-ssl-platform.sh`: Enhanced with cleanup and pre-flight checks
- `cleanup-platform.sh`: Standalone comprehensive cleanup script
- `README-STARTUP.md`: This documentation

## Benefits:
- ✅ **Eliminates port conflicts** - No more "address already in use" errors
- ✅ **Reliable startup** - Consistent environment every time
- ✅ **Automatic conflict resolution** - Handles competing services
- ✅ **Resource cleanup** - Prevents Docker resource buildup
- ✅ **Validation checks** - Ensures prerequisites are met

The platform should now start reliably without manual intervention!