#!/usr/bin/env python3
"""
Fix AI Research Platform Startup Services
Addresses common systemd service issues and creates robust startup
"""

import os
import subprocess
import json
from pathlib import Path

class StartupServicesFixer:
    """Fixes and optimizes startup services"""
    
    def __init__(self):
        self.platform_dir = "/home/keith/chat-copilot"
        self.user_services_dir = os.path.expanduser("~/.config/systemd/user")
        self.current_user = os.getenv("USER", "keith")
    
    def stop_all_services(self):
        """Stop all platform services before fixing"""
        
        print("🛑 Stopping existing services...")
        
        services = [
            "autogen-studio-ai-platform",
            "webhook-server-ai-platform", 
            "chat-copilot-backend",
            "chat-copilot-frontend"
        ]
        
        for service in services:
            try:
                subprocess.run(f"systemctl --user stop {service}", shell=True, check=False)
                subprocess.run(f"systemctl --user disable {service}", shell=True, check=False)
                print(f"✅ Stopped {service}")
            except:
                pass
    
    def create_simplified_services(self):
        """Create simplified, more reliable service configurations"""
        
        # AutoGen Studio service
        autogen_service = f"""[Unit]
Description=AutoGen Studio Multi-Agent Platform
After=network.target ollama-ai-platform.service
Wants=ollama-ai-platform.service

[Service]
Type=simple
ExecStart={self.platform_dir}/autogen-env/bin/python -m autogenstudio.ui --port 8085 --host 0.0.0.0
WorkingDirectory={self.platform_dir}
Environment=PATH={self.platform_dir}/autogen-env/bin:/usr/local/bin:/usr/bin:/bin
Environment=VIRTUAL_ENV={self.platform_dir}/autogen-env
Environment=PYTHONPATH={self.platform_dir}/autogen-env/lib/python3.12/site-packages
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""
        
        # Webhook Server service  
        webhook_service = f"""[Unit]
Description=GitHub Webhook Server for AI Research Platform
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/node {self.platform_dir}/webhook-server.js
WorkingDirectory={self.platform_dir}
Environment=NODE_ENV=production
Environment=WEBHOOK_PORT=9001
Environment=WEBHOOK_SECRET=ai-research-platform-webhook-secret
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""
        
        # Simple startup service that manages all others
        startup_service = f"""[Unit]
Description=AI Research Platform Startup Manager
After=network.target ollama-ai-platform.service
Wants=ollama-ai-platform.service

[Service]
Type=oneshot
ExecStart={self.platform_dir}/startup-platform.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""
        
        # Write service files
        services = {
            "autogen-studio-ai-platform.service": autogen_service,
            "webhook-server-ai-platform.service": webhook_service,
            "ai-research-platform-startup.service": startup_service
        }
        
        os.makedirs(self.user_services_dir, exist_ok=True)
        
        for filename, content in services.items():
            service_path = f"{self.user_services_dir}/{filename}"
            with open(service_path, 'w') as f:
                f.write(content)
            os.chmod(service_path, 0o644)
            print(f"✅ Created {filename}")
    
    def create_robust_startup_script(self):
        """Create a more robust startup script"""
        
        script_content = f"""#!/bin/bash
# AI Research Platform Robust Startup Script

set -e

echo "🚀 AI Research Platform Startup Script"
echo "Current time: $(date)"
echo "User: $(whoami)"
echo "Working directory: $(pwd)"

# Function to wait for service
wait_for_service() {{
    local name=$1
    local url=$2
    local max_attempts=$3
    local attempt=1
    
    echo "⏳ Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 5 "$url" &> /dev/null; then
            echo "✅ $name is ready (attempt $attempt/$max_attempts)"
            return 0
        fi
        echo "Waiting for $name... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    echo "⚠️ $name not ready after $max_attempts attempts"
    return 1
}}

# Function to start service in background
start_service() {{
    local name=$1
    local command=$2
    local pidfile=$3
    
    echo "🚀 Starting $name..."
    
    # Kill existing process if running
    if [ -f "$pidfile" ]; then
        local old_pid=$(cat "$pidfile")
        if kill -0 "$old_pid" 2>/dev/null; then
            echo "Stopping existing $name process..."
            kill "$old_pid" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$pidfile"
    fi
    
    # Start new process
    nohup $command > "{self.platform_dir}/logs/$name.log" 2>&1 &
    local new_pid=$!
    echo $new_pid > "$pidfile"
    echo "✅ Started $name with PID $new_pid"
}}

# Create logs directory
mkdir -p {self.platform_dir}/logs

# Wait for network
echo "🌐 Checking network connectivity..."
until ping -c 1 8.8.8.8 &> /dev/null; do
    echo "Waiting for network..."
    sleep 2
done
echo "✅ Network is available"

# Wait for Ollama
wait_for_service "Ollama" "http://localhost:11434/api/version" 30

# Start AutoGen Studio
start_service "AutoGen Studio" \\
    "source {self.platform_dir}/autogen-env/bin/activate && {self.platform_dir}/autogen-env/bin/python -m autogenstudio.ui --port 8085 --host 0.0.0.0" \\
    "{self.platform_dir}/pids/autogen-studio.pid"

# Start Webhook Server
start_service "Webhook Server" \\
    "node {self.platform_dir}/webhook-server.js" \\
    "{self.platform_dir}/pids/webhook-server.pid"

# Wait for services to be ready
sleep 5

# Test endpoints
echo "🧪 Testing service endpoints..."
wait_for_service "AutoGen Studio" "http://100.123.10.72:8085" 10
wait_for_service "Webhook Server" "http://100.123.10.72:9001/health" 10

echo "🎉 AI Research Platform startup complete!"
echo "📊 Platform Status:"
echo "   🌐 Control Panel: http://100.123.10.72:10500/control-panel.html"
echo "   🤖 AutoGen Studio: http://100.123.10.72:8085"
echo "   💻 VS Code Web: http://100.123.10.72:57081"
echo "   🔗 Webhook Server: http://100.123.10.72:9001/health"

# Create status file
cat > {self.platform_dir}/platform-status.json << EOF
{{
    "startup_time": "$(date -Iseconds)",
    "services": {{
        "ollama": "$(curl -s http://localhost:11434/api/version &> /dev/null && echo 'running' || echo 'stopped')",
        "autogen_studio": "$(curl -s http://100.123.10.72:8085 &> /dev/null && echo 'running' || echo 'stopped')",
        "webhook_server": "$(curl -s http://100.123.10.72:9001/health &> /dev/null && echo 'running' || echo 'stopped')",
        "vscode_web": "$(curl -s http://100.123.10.72:57081 &> /dev/null && echo 'running' || echo 'stopped')"
    }}
}}
EOF

echo "📋 Status saved to platform-status.json"
"""
        
        script_path = f"{self.platform_dir}/startup-platform.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Create necessary directories
        os.makedirs(f"{self.platform_dir}/logs", exist_ok=True)
        os.makedirs(f"{self.platform_dir}/pids", exist_ok=True)
        
        print(f"✅ Created robust startup script: {script_path}")
    
    def create_systemd_startup_timer(self):
        """Create a systemd timer for delayed startup"""
        
        # Timer service
        timer_content = f"""[Unit]
Description=AI Research Platform Startup Timer
Requires=ai-research-platform-startup.service

[Timer]
OnBootSec=60
Unit=ai-research-platform-startup.service

[Install]
WantedBy=timers.target
"""
        
        timer_path = f"{self.user_services_dir}/ai-research-platform-startup.timer"
        with open(timer_path, 'w') as f:
            f.write(timer_content)
        os.chmod(timer_path, 0o644)
        
        print(f"✅ Created startup timer: {timer_path}")
    
    def create_cron_backup(self):
        """Create a cron job as backup startup method"""
        
        cron_entry = f"@reboot sleep 120 && {self.platform_dir}/startup-platform.sh > {self.platform_dir}/logs/cron-startup.log 2>&1"
        
        # Add to user crontab
        try:
            # Get existing crontab
            result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
            existing_cron = result.stdout if result.returncode == 0 else ""
            
            # Check if our entry already exists
            if "@reboot" not in existing_cron or "startup-platform.sh" not in existing_cron:
                new_cron = existing_cron + f"\n{cron_entry}\n"
                
                # Write new crontab
                process = subprocess.Popen("crontab -", shell=True, stdin=subprocess.PIPE, text=True)
                process.communicate(new_cron)
                
                if process.returncode == 0:
                    print("✅ Added cron job for startup backup")
                else:
                    print("⚠️ Could not add cron job")
            else:
                print("✅ Cron job already exists")
                
        except Exception as e:
            print(f"⚠️ Could not configure cron job: {e}")
    
    def enable_services(self):
        """Enable the simplified services"""
        
        print("🔧 Enabling startup services...")
        
        try:
            # Reload systemd
            subprocess.run("systemctl --user daemon-reload", shell=True, check=True)
            
            # Enable core services
            subprocess.run("systemctl --user enable ai-research-platform-startup.service", shell=True, check=True)
            subprocess.run("systemctl --user enable ai-research-platform-startup.timer", shell=True, check=True)
            
            # Start timer
            subprocess.run("systemctl --user start ai-research-platform-startup.timer", shell=True, check=True)
            
            print("✅ Services enabled successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to enable services: {e}")
    
    def create_manual_control_scripts(self):
        """Create scripts for manual control"""
        
        # Start script
        start_script = f"""#!/bin/bash
echo "🚀 Starting AI Research Platform manually..."
{self.platform_dir}/startup-platform.sh
"""
        
        # Stop script  
        stop_script = f"""#!/bin/bash
echo "🛑 Stopping AI Research Platform..."

# Stop services
if [ -f "{self.platform_dir}/pids/autogen-studio.pid" ]; then
    kill $(cat "{self.platform_dir}/pids/autogen-studio.pid") 2>/dev/null || true
    rm -f "{self.platform_dir}/pids/autogen-studio.pid"
fi

if [ -f "{self.platform_dir}/pids/webhook-server.pid" ]; then
    kill $(cat "{self.platform_dir}/pids/webhook-server.pid") 2>/dev/null || true
    rm -f "{self.platform_dir}/pids/webhook-server.pid"
fi

# Stop any running processes
pkill -f "autogenstudio" || true
pkill -f "webhook-server.js" || true

echo "✅ AI Research Platform stopped"
"""
        
        # Status script
        status_script = f"""#!/bin/bash
echo "📊 AI Research Platform Status"
echo "=" * 40

check_service() {{
    local name=$1
    local url=$2
    if curl -s --max-time 3 "$url" &> /dev/null; then
        echo "✅ $name: Running"
    else
        echo "❌ $name: Stopped"
    fi
}}

check_service "Ollama" "http://localhost:11434/api/version"
check_service "AutoGen Studio" "http://100.123.10.72:8085"
check_service "Webhook Server" "http://100.123.10.72:9001/health"
check_service "VS Code Web" "http://100.123.10.72:57081"
check_service "Chat Copilot" "http://100.123.10.72:10500"

echo ""
echo "📋 Process Information:"
ps aux | grep -E "(autogenstudio|webhook-server|ollama)" | grep -v grep || echo "No platform processes found"

if [ -f "{self.platform_dir}/platform-status.json" ]; then
    echo ""
    echo "📊 Last Startup Status:"
    cat "{self.platform_dir}/platform-status.json"
fi
"""
        
        scripts = {
            "start-platform.sh": start_script,
            "stop-platform.sh": stop_script,
            "status-platform.sh": status_script
        }
        
        for filename, content in scripts.items():
            script_path = f"{self.platform_dir}/{filename}"
            with open(script_path, 'w') as f:
                f.write(content)
            os.chmod(script_path, 0o755)
            print(f"✅ Created {filename}")

def main():
    """Main fixing function"""
    
    print("🔧 AI Research Platform Startup Services Fixer")
    print("=" * 50)
    
    fixer = StartupServicesFixer()
    
    # Stop existing problematic services
    fixer.stop_all_services()
    
    # Create improved configurations
    print("\n📝 Creating improved service configurations...")
    fixer.create_simplified_services()
    fixer.create_robust_startup_script()
    fixer.create_systemd_startup_timer()
    
    # Enable services
    print("\n🔧 Enabling services...")
    fixer.enable_services()
    
    # Create backup methods
    print("\n💾 Creating backup startup methods...")
    fixer.create_cron_backup()
    
    # Create manual control scripts
    print("\n🎛️ Creating manual control scripts...")
    fixer.create_manual_control_scripts()
    
    print("\n🎉 Startup services fixed and optimized!")
    print("\n🔧 Available Commands:")
    print("   🚀 Start: ./start-platform.sh")
    print("   🛑 Stop: ./stop-platform.sh") 
    print("   📊 Status: ./status-platform.sh")
    
    print("\n📋 Systemd Commands:")
    print("   📊 Check timer: systemctl --user status ai-research-platform-startup.timer")
    print("   🔄 Run now: systemctl --user start ai-research-platform-startup.service")
    print("   📋 View logs: journalctl --user -f -u ai-research-platform-startup")
    
    print("\n🎯 Startup Methods Configured:")
    print("   1. ✅ Systemd timer (starts 60 seconds after boot)")
    print("   2. ✅ Cron job backup (starts 2 minutes after boot)")
    print("   3. ✅ Manual scripts for control")
    
    print("\n💡 Test the setup:")
    print("   ./start-platform.sh  # Test manual startup")
    print("   ./status-platform.sh # Check current status")

if __name__ == "__main__":
    main()