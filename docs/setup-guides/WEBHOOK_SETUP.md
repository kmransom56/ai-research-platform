# GitHub Webhook Auto-Deployment Setup Guide

This guide shows how to configure GitHub webhooks for automatic deployment of your AI Research Platform when you push changes to the repository.

## 🚀 Overview

The webhook system automatically:
- Pulls latest code from GitHub when you push to main branch
- Installs dependencies and builds the application
- Restarts services safely
- Creates backups before deployment
- Tests critical services after deployment

## 📋 Components

### 1. Webhook Server (`webhook-server.js`)
- **Port**: 9001
- **Endpoints**: 
  - `POST /webhook` - GitHub webhook endpoint
  - `POST /deploy` - Manual deployment trigger
  - `GET /health` - Server health check
  - `GET /status` - Deployment status and logs

### 2. Deployment Script (`deploy.sh`)
- Automated deployment workflow
- Service management
- Health checks
- Backup creation

### 3. Control Panel Integration
- **URL**: http://100.123.10.72:10500/control-panel.html
- Webhook management buttons
- Real-time deployment monitoring
- Manual deployment triggers

## 🔧 Setup Instructions

### Step 1: Configure GitHub Repository Webhook

1. **Go to your GitHub repository**:
   https://github.com/kmransom56/AI_Research_Platform-_Tailscale

2. **Navigate to Settings > Webhooks**

3. **Click "Add webhook"**

4. **Configure the webhook**:
   ```
   Payload URL: http://100.123.10.72:9001/webhook
   Content type: application/json
   Secret: ai-research-platform-webhook-secret
   
   Which events would you like to trigger this webhook?
   ☑️ Just the push event
   
   Active: ☑️ 
   ```

5. **Click "Add webhook"**

### Step 2: Start Webhook Server

#### Option A: Manual Start
```bash
cd /home/keith/chat-copilot
node webhook-server.js
```

#### Option B: Use Control Panel
1. Open http://100.123.10.72:10500/control-panel.html
2. Click "Start Webhook" button in Deployment section

#### Option C: Systemd Service (Production)
```bash
# Copy service file
sudo cp webhook-server.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable webhook-server.service
sudo systemctl start webhook-server.service

# Check status
sudo systemctl status webhook-server.service
```

### Step 3: Test the Setup

1. **Test webhook server manually**:
   ```bash
   curl http://100.123.10.72:9001/health
   ```

2. **Test manual deployment**:
   ```bash
   curl -X POST http://100.123.10.72:9001/deploy
   ```

3. **Make a test commit to trigger webhook**:
   ```bash
   echo "# Test deployment" >> README.md
   git add README.md
   git commit -m "Test auto-deployment webhook"
   git push origin main
   ```

## 🎛️ Control Panel Functions

### Webhook Management Buttons

| Button | Function | Description |
|--------|----------|-------------|
| **Webhook Status** | Check health | Shows server status and recent activity |
| **Manual Deploy** | Trigger deployment | Runs deployment without GitHub push |
| **Start Webhook** | Start server | Launches webhook server |
| **Stop Webhook** | Stop server | Gracefully shuts down webhook server |

### Manual Deployment
- Use when you want to deploy without pushing to GitHub
- Runs the same deployment process as automatic webhooks
- Shows real-time progress in control panel logs

## 📊 Monitoring & Logs

### Real-time Monitoring
- **Control Panel**: http://100.123.10.72:10500/control-panel.html
- **Webhook Status**: Shows server uptime and recent activity
- **Live Logs**: Real-time deployment progress

### Log Files
- **Webhook Server**: `/home/keith/chat-copilot/webhook.log`
- **Deployment**: `/home/keith/chat-copilot/deployment.log`
- **Service Logs**: `/home/keith/chat-copilot/webhook-service.log`

### Status Endpoints
```bash
# Server health
curl http://100.123.10.72:9001/health

# Recent activity
curl http://100.123.10.72:9001/status
```

## 🔒 Security Configuration

### Webhook Secret
- **Current Secret**: `ai-research-platform-webhook-secret`
- **Change Secret**: Update both GitHub webhook and `CONFIG.secret` in webhook-server.js
- **Environment Variable**: `WEBHOOK_SECRET`

### Network Security
- Webhook server only accepts requests with valid GitHub signatures
- HTTPS endpoints used where possible
- Automatic backup creation before deployment

## 🚀 Deployment Workflow

When you push to the main branch:

1. **GitHub sends webhook** to http://100.123.10.72:9001/webhook
2. **Webhook server verifies** signature and branch
3. **Deployment starts**:
   - Creates backup
   - Pulls latest code
   - Installs dependencies
   - Builds applications
   - Restarts services
   - Tests health endpoints
4. **Results logged** and available in control panel

## 🛠️ Troubleshooting

### Common Issues

#### Webhook Server Not Starting
```bash
# Check if port is in use
netstat -tlnp | grep 9001

# Check logs
tail -f /home/keith/chat-copilot/webhook.log
```

#### GitHub Webhook Failing
1. Check webhook secret matches
2. Verify server is accessible from internet
3. Check GitHub webhook delivery logs

#### Deployment Failures
```bash
# Check deployment logs
tail -f /home/keith/chat-copilot/deployment.log

# Manual deployment for debugging
/home/keith/chat-copilot/deploy.sh
```

### Health Checks
```bash
# Test all critical services
curl -k https://100.123.10.72:40443/healthz  # Backend API
curl http://100.123.10.72:10500              # Frontend
curl http://100.123.10.72:9001/health        # Webhook server
```

## 📈 Advanced Configuration

### Custom Deployment Script
Edit `/home/keith/chat-copilot/deploy.sh` to customize deployment process:
- Add custom build steps
- Include database migrations
- Add notification integrations

### Environment Variables
```bash
# Webhook configuration
export WEBHOOK_PORT=9001
export WEBHOOK_SECRET=your-secret-here

# Deployment notifications
export DEPLOYMENT_WEBHOOK_URL=your-slack-webhook-url
```

### Multiple Environments
- Modify `CONFIG.branch` for different environments
- Use different ports for staging/production
- Create environment-specific deployment scripts

## 🎉 Benefits

✅ **Zero-Downtime Deployments** - Automatic service management  
✅ **Backup Protection** - Pre-deployment backups  
✅ **Health Monitoring** - Automatic service testing  
✅ **Real-time Feedback** - Control panel integration  
✅ **Security** - Signed webhook verification  
✅ **Flexibility** - Manual and automatic deployment options  

Your AI Research Platform now has enterprise-grade continuous deployment!