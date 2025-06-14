#!/usr/bin/env node

/**
 * GitHub Webhook Server for AI Research Platform Auto-Deployment
 * Automatically pulls and deploys changes when pushed to GitHub repository
 */

const http = require('http');
const crypto = require('crypto');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    port: process.env.WEBHOOK_PORT || 9001,
    secret: process.env.WEBHOOK_SECRET || 'ai-research-platform-webhook-secret',
    repositoryPath: '/home/keith/chat-copilot',
    branch: 'main',
    logFile: '/home/keith/chat-copilot/webhook.log',
    deployScript: '/home/keith/chat-copilot/deploy.sh'
};

// Logging function
function log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${type.toUpperCase()}] ${message}\n`;
    
    console.log(logMessage.trim());
    
    // Append to log file
    fs.appendFileSync(CONFIG.logFile, logMessage, { encoding: 'utf8' });
}

// Verify GitHub webhook signature
function verifySignature(payload, signature) {
    if (!signature) {
        return false;
    }

    const expectedSignature = 'sha256=' + crypto
        .createHmac('sha256', CONFIG.secret)
        .update(payload, 'utf8')
        .digest('hex');

    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
    );
}

// Execute shell command
function executeCommand(command, options = {}) {
    return new Promise((resolve, reject) => {
        log(`Executing: ${command}`);
        
        exec(command, {
            cwd: CONFIG.repositoryPath,
            timeout: 300000, // 5 minutes timeout
            ...options
        }, (error, stdout, stderr) => {
            if (error) {
                log(`Command failed: ${error.message}`, 'error');
                log(`stderr: ${stderr}`, 'error');
                reject(error);
            } else {
                if (stdout) log(`stdout: ${stdout}`);
                if (stderr) log(`stderr: ${stderr}`, 'warn');
                resolve({ stdout, stderr });
            }
        });
    });
}

// Deploy function
async function deploy() {
    log('Starting deployment process...');
    
    try {
        // Step 1: Git pull
        log('Pulling latest changes from repository...');
        await executeCommand('git pull origin main');
        
        // Step 2: Install dependencies if package.json changed
        if (fs.existsSync(path.join(CONFIG.repositoryPath, 'webapp/package.json'))) {
            log('Installing frontend dependencies...');
            await executeCommand('cd webapp && yarn install');
        }
        
        // Step 3: Build frontend if needed
        log('Building frontend application...');
        await executeCommand('cd webapp && yarn build || echo "Build skipped"');
        
        // Step 4: Restart backend if running
        log('Checking backend status...');
        try {
            await executeCommand('pkill -f "dotnet.*CopilotChatWebApi" || echo "Backend not running"');
            await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
            
            // Start backend in background
            log('Starting backend server...');
            const backend = spawn('dotnet', ['run', '--urls', 'https://100.123.10.72:40443'], {
                cwd: path.join(CONFIG.repositoryPath, 'webapi'),
                detached: true,
                stdio: 'ignore'
            });
            backend.unref();
            
        } catch (error) {
            log('Backend restart failed, continuing...', 'warn');
        }
        
        // Step 5: Restart Docker services if needed
        log('Restarting Docker services...');
        await executeCommand('docker-compose restart || echo "Docker restart skipped"');
        
        // Step 6: Update environment variables
        log('Sourcing updated environment variables...');
        await executeCommand('source ~/.bashrc || echo "Environment reload skipped"');
        
        // Step 7: Run custom deploy script if exists
        if (fs.existsSync(CONFIG.deployScript)) {
            log('Running custom deployment script...');
            await executeCommand(`chmod +x ${CONFIG.deployScript} && ${CONFIG.deployScript}`);
        }
        
        log('Deployment completed successfully!', 'success');
        return { success: true, message: 'Deployment completed successfully' };
        
    } catch (error) {
        log(`Deployment failed: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

// HTTP server
const server = http.createServer(async (req, res) => {
    // CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Hub-Signature-256');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // Health check endpoint
    if (req.method === 'GET' && req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'healthy',
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            repositoryPath: CONFIG.repositoryPath
        }));
        return;
    }
    
    // Status endpoint
    if (req.method === 'GET' && req.url === '/status') {
        try {
            const logs = fs.readFileSync(CONFIG.logFile, 'utf8').split('\n').slice(-20);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'running',
                recentLogs: logs.filter(line => line.trim()),
                lastDeployment: fs.statSync(CONFIG.logFile).mtime
            }));
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to get status' }));
        }
        return;
    }
    
    // Manual deploy endpoint
    if (req.method === 'POST' && req.url === '/deploy') {
        log('Manual deployment triggered via API');
        const result = await deploy();
        
        res.writeHead(result.success ? 200 : 500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
        return;
    }
    
    // GitHub webhook endpoint
    if (req.method === 'POST' && req.url === '/webhook') {
        let body = '';
        
        req.on('data', chunk => {
            body += chunk.toString();
        });
        
        req.on('end', async () => {
            try {
                // Verify signature
                const signature = req.headers['x-hub-signature-256'];
                if (!verifySignature(body, signature)) {
                    log('Invalid webhook signature', 'error');
                    res.writeHead(401, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Invalid signature' }));
                    return;
                }
                
                const payload = JSON.parse(body);
                
                log(`Received webhook: ${payload.repository?.full_name || 'unknown'}`);
                log(`Event: ${req.headers['x-github-event']}`);
                log(`Ref: ${payload.ref || 'unknown'}`);
                
                // Only deploy on push to main branch
                if (req.headers['x-github-event'] === 'push' && payload.ref === `refs/heads/${CONFIG.branch}`) {
                    log('Push to main branch detected, starting deployment...');
                    
                    const result = await deploy();
                    
                    res.writeHead(result.success ? 200 : 500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        message: result.success ? 'Deployment started' : 'Deployment failed',
                        ...result
                    }));
                } else {
                    log('Ignoring webhook (not a push to main branch)');
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ message: 'Webhook received but ignored' }));
                }
                
            } catch (error) {
                log(`Webhook processing error: ${error.message}`, 'error');
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Internal server error' }));
            }
        });
        
        return;
    }
    
    // 404 for all other routes
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
});

// Start server
server.listen(CONFIG.port, '0.0.0.0', () => {
    log(`GitHub webhook server started on port ${CONFIG.port}`);
    log(`Repository path: ${CONFIG.repositoryPath}`);
    log(`Branch: ${CONFIG.branch}`);
    log(`Log file: ${CONFIG.logFile}`);
    log('Endpoints:');
    log('  POST /webhook - GitHub webhook');
    log('  POST /deploy - Manual deployment');
    log('  GET /health - Health check');
    log('  GET /status - Server status');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    log('Received SIGTERM, shutting down gracefully');
    server.close(() => {
        log('Server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    log('Received SIGINT, shutting down gracefully');
    server.close(() => {
        log('Server closed');
        process.exit(0);
    });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    log(`Uncaught exception: ${error.message}`, 'error');
    log(error.stack, 'error');
});

process.on('unhandledRejection', (reason, promise) => {
    log(`Unhandled rejection at ${promise}: ${reason}`, 'error');
});