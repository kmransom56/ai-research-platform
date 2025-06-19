#!/usr/bin/env python3
"""
AI Research Platform Auto-Startup Manager
Creates systemd services for automatic boot startup
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

class AutoStartupManager:
    """Manages automatic startup of AI Research Platform services"""
    
    def __init__(self):
        self.platform_dir = "/home/keith/chat-copilot"
        self.services_dir = "/etc/systemd/system"
        self.user_services_dir = os.path.expanduser("~/.config/systemd/user")
        self.current_user = os.getenv("USER", "keith")
        
        # Service configurations
        self.services = {
            "ollama": {
                "name": "ollama-ai-platform",
                "description": "Ollama Local LLM Server for AI Research Platform",
                "type": "system",
                "exec_start": "/usr/local/bin/ollama serve",
                "user": "keith",
                "environment": {
                    "OLLAMA_HOST": "0.0.0.0:11434",
                    "OLLAMA_MODELS": "/home/keith/.ollama/models"
                },
                "restart": "always",
                "wanted_by": "multi-user.target"
            },
            "autogen_studio": {
                "name": "autogen-studio-ai-platform",
                "description": "AutoGen Studio Multi-Agent Platform",
                "type": "user",
                "exec_start": f"{self.platform_dir}/autogen-env/bin/autogenstudio ui --port 11001 --host 0.0.0.0",
                "working_directory": self.platform_dir,
                "user": "keith",
                "environment": {
                    "PATH": f"{self.platform_dir}/autogen-env/bin:/usr/local/bin:/usr/bin:/bin",
                    "VIRTUAL_ENV": f"{self.platform_dir}/autogen-env"
                },
                "restart": "always",
                "restart_sec": 10,
                "wanted_by": "default.target"
            },
            "webhook_server": {
                "name": "webhook-server-ai-platform",
                "description": "GitHub Webhook Server for AI Research Platform",
                "type": "user",
                "exec_start": f"/usr/bin/node {self.platform_dir}/webhook-server.js",
                "working_directory": self.platform_dir,
                "user": "keith",
                "environment": {
                    "NODE_ENV": "production",
                    "WEBHOOK_PORT": "11002",
                    "WEBHOOK_SECRET": "ai-research-platform-webhook-secret"
                },
                "restart": "always",
                "restart_sec": 5,
                "wanted_by": "default.target"
            },
            "chat_copilot_backend": {
                "name": "chat-copilot-backend",
                "description": "Chat Copilot Backend API Server",
                "type": "user",
                "exec_start": f"/usr/bin/dotnet run --urls http://0.0.0.0:11000",
                "working_directory": f"{self.platform_dir}/webapi",
                "user": "keith",
                "environment": {
                    "ASPNETCORE_ENVIRONMENT": "Development",
                    "ASPNETCORE_URLS": "http://0.0.0.0:11000"
                },
                "restart": "always",
                "restart_sec": 15,
                "wanted_by": "default.target"
            },
            "chat_copilot_frontend": {
                "name": "chat-copilot-frontend",
                "description": "Chat Copilot Frontend Server",
                "type": "user",
                "exec_start": f"/usr/bin/yarn start",
                "working_directory": f"{self.platform_dir}/webapp",
                "user": "keith",
                "environment": {
                    "PORT": "3000",
                    "HOST": "0.0.0.0",
                    "NODE_ENV": "production"
                },
                "restart": "always",
                "restart_sec": 10,
                "wanted_by": "default.target"
            }
        }
    
    def create_systemd_service(self, service_name: str, config: dict) -> str:
        """Create a systemd service file"""
        
        service_content = f"""[Unit]
Description={config['description']}
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart={config['exec_start']}
WorkingDirectory={config.get('working_directory', self.platform_dir)}
User={config.get('user', self.current_user)}
Restart={config.get('restart', 'always')}
RestartSec={config.get('restart_sec', 5)}
StandardOutput=journal
StandardError=journal
"""

        # Add environment variables
        if config.get('environment'):
            for key, value in config['environment'].items():
                service_content += f"Environment={key}={value}\n"
        
        service_content += f"""
[Install]
WantedBy={config.get('wanted_by', 'multi-user.target')}
"""
        
        return service_content
    
    def install_service(self, service_name: str, config: dict) -> bool:
        """Install a systemd service"""
        
        service_file = f"{config['name']}.service"
        service_content = self.create_systemd_service(service_name, config)
        
        if config['type'] == 'system':
            service_path = f"{self.services_dir}/{service_file}"
            needs_sudo = True
        else:
            # User service
            os.makedirs(self.user_services_dir, exist_ok=True)
            service_path = f"{self.user_services_dir}/{service_file}"
            needs_sudo = False
        
        try:
            if needs_sudo:
                # Write to temporary file first
                temp_file = f"/tmp/{service_file}"
                with open(temp_file, 'w') as f:
                    f.write(service_content)
                
                # Move to system directory with sudo
                subprocess.run(f"sudo mv {temp_file} {service_path}", shell=True, check=True)
                subprocess.run(f"sudo chmod 644 {service_path}", shell=True, check=True)
            else:
                # User service - direct write
                with open(service_path, 'w') as f:
                    f.write(service_content)
                os.chmod(service_path, 0o644)
            
            print(f"✅ Created service file: {service_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create service {service_name}: {e}")
            return False
    
    def enable_service(self, service_name: str, config: dict) -> bool:
        """Enable and start a systemd service"""
        
        service_file = f"{config['name']}.service"
        
        try:
            if config['type'] == 'system':
                # System service
                subprocess.run(f"sudo systemctl daemon-reload", shell=True, check=True)
                subprocess.run(f"sudo systemctl enable {service_file}", shell=True, check=True)
                subprocess.run(f"sudo systemctl start {service_file}", shell=True, check=True)
            else:
                # User service
                subprocess.run("systemctl --user daemon-reload", shell=True, check=True)
                subprocess.run(f"systemctl --user enable {service_file}", shell=True, check=True)
                subprocess.run(f"systemctl --user start {service_file}", shell=True, check=True)
            
            print(f"✅ Enabled and started service: {service_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to enable service {service_name}: {e}")
            return False
    
    def check_service_status(self, service_name: str, config: dict) -> dict:
        """Check the status of a systemd service"""
        
        service_file = f"{config['name']}.service"
        
        try:
            if config['type'] == 'system':
                result = subprocess.run(f"sudo systemctl status {service_file}", 
                                      shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run(f"systemctl --user status {service_file}", 
                                      shell=True, capture_output=True, text=True)
            
            is_active = "active (running)" in result.stdout
            is_enabled = subprocess.run(
                f"systemctl {'--user ' if config['type'] == 'user' else ''}is-enabled {service_file}",
                shell=True, capture_output=True, text=True
            ).returncode == 0
            
            return {
                "service": service_name,
                "active": is_active,
                "enabled": is_enabled,
                "status": "running" if is_active else "stopped"
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "active": False,
                "enabled": False,
                "status": "error",
                "error": str(e)
            }
    
    def create_startup_script(self) -> str:
        """Create a comprehensive startup script"""
        
        script_content = f"""#!/bin/bash
# AI Research Platform Startup Script
# Ensures all services are running properly

set -e

echo "🚀 Starting AI Research Platform Services..."
echo "=" * 50

# Function to check if a service is running
check_service() {{
    local service_name=$1
    local service_type=$2
    
    if [ "$service_type" == "system" ]; then
        if systemctl is-active --quiet $service_name; then
            echo "✅ $service_name: Running"
        else
            echo "❌ $service_name: Not running"
            sudo systemctl start $service_name
        fi
    else
        if systemctl --user is-active --quiet $service_name; then
            echo "✅ $service_name: Running"
        else
            echo "❌ $service_name: Not running"
            systemctl --user start $service_name
        fi
    fi
}}

# Wait for network
echo "🌐 Waiting for network connectivity..."
until ping -c 1 google.com &> /dev/null; do
    echo "Waiting for network..."
    sleep 2
done
echo "✅ Network is available"

# Start core services
echo "🦙 Starting Ollama service..."
check_service "ollama-ai-platform" "system"

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/version &> /dev/null; do
    echo "Waiting for Ollama..."
    sleep 2
done
echo "✅ Ollama is ready"

# Start user services
echo "🤖 Starting AutoGen Studio..."
check_service "autogen-studio-ai-platform" "user"

echo "🔗 Starting Webhook Server..."
check_service "webhook-server-ai-platform" "user"

echo "🖥️ Starting Chat Copilot Backend..."
check_service "chat-copilot-backend" "user"

echo "🌐 Starting Chat Copilot Frontend..."
check_service "chat-copilot-frontend" "user"

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test service endpoints
echo "🧪 Testing service endpoints..."

test_endpoint() {{
    local name=$1
    local url=$2
    
    if curl -s --max-time 5 "$url" &> /dev/null; then
        echo "✅ $name: Accessible"
    else
        echo "⚠️ $name: Not accessible yet"
    fi
}}

test_endpoint "Ollama" "http://localhost:11434/api/version"
test_endpoint "AutoGen Studio" "http://100.123.10.72:11001"
test_endpoint "Webhook Server" "http://100.123.10.72:11002/health"
test_endpoint "Chat Copilot Backend" "http://100.123.10.72:11000/healthz"
test_endpoint "Chat Copilot Frontend" "http://100.123.10.72:3000"

echo ""
echo "🎉 AI Research Platform startup complete!"
echo "📊 Access the platform at:"
echo "   🌐 Control Panel: http://100.123.10.72:11000/control-panel.html"
echo "   🤖 AutoGen Studio: http://100.123.10.72:11001"
echo "   💻 VS Code Web: http://100.123.10.72:57081"
echo "   🔍 OpenWebUI: https://ubuntuaicodeserver-1.tail5137b4.ts.net"
"""
        
        script_path = f"{self.platform_dir}/startup-platform.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"✅ Created startup script: {script_path}")
        
        return script_path
    
    def create_user_service_enabler(self):
        """Create a script to enable user services after login"""
        
        script_content = f"""#!/bin/bash
# Enable user services after login
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

# Enable lingering for user services to start at boot
sudo loginctl enable-linger {self.current_user}

# Start user services
systemctl --user daemon-reload
systemctl --user enable autogen-studio-ai-platform.service
systemctl --user enable webhook-server-ai-platform.service 
systemctl --user enable chat-copilot-backend.service
systemctl --user enable chat-copilot-frontend.service

echo "✅ User services enabled for auto-startup"
"""
        
        script_path = f"{self.platform_dir}/enable-user-services.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"✅ Created user services enabler: {script_path}")
        
        return script_path
    
    def install_all_services(self) -> dict:
        """Install all AI Research Platform services"""
        
        results = {}
        
        print("🚀 Installing AI Research Platform Auto-Startup Services")
        print("=" * 60)
        
        # Install each service
        for service_name, config in self.services.items():
            print(f"\n📦 Installing {service_name}...")
            
            # Create service file
            if self.install_service(service_name, config):
                # Enable and start service
                if self.enable_service(service_name, config):
                    results[service_name] = "success"
                else:
                    results[service_name] = "enabled_failed"
            else:
                results[service_name] = "install_failed"
        
        # Create helper scripts
        print(f"\n📝 Creating helper scripts...")
        self.create_startup_script()
        self.create_user_service_enabler()
        
        # Enable user service lingering
        try:
            subprocess.run(f"sudo loginctl enable-linger {self.current_user}", shell=True, check=True)
            print(f"✅ Enabled user service lingering for {self.current_user}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Could not enable user service lingering: {e}")
        
        return results
    
    def get_all_service_status(self) -> dict:
        """Get status of all services"""
        
        status = {}
        
        for service_name, config in self.services.items():
            status[service_name] = self.check_service_status(service_name, config)
        
        return status
    
    def create_status_script(self):
        """Create a script to check platform status"""
        
        script_content = f"""#!/bin/bash
# AI Research Platform Status Checker

echo "📊 AI Research Platform Service Status"
echo "=" * 50

check_systemd_service() {{
    local service_name=$1
    local service_type=$2
    
    if [ "$service_type" == "system" ]; then
        if systemctl is-active --quiet $service_name; then
            echo "✅ $service_name: Active"
        else
            echo "❌ $service_name: Inactive"
        fi
    else
        if systemctl --user is-active --quiet $service_name; then
            echo "✅ $service_name: Active"
        else
            echo "❌ $service_name: Inactive"
        fi
    fi
}}

check_endpoint() {{
    local name=$1
    local url=$2
    
    if curl -s --max-time 5 "$url" &> /dev/null; then
        echo "✅ $name: Accessible"
    else
        echo "❌ $name: Not accessible"
    fi
}}

echo "🔧 Systemd Services:"
check_systemd_service "ollama-ai-platform" "system"
check_systemd_service "autogen-studio-ai-platform" "user"
check_systemd_service "webhook-server-ai-platform" "user"
check_systemd_service "chat-copilot-backend" "user"
check_systemd_service "chat-copilot-frontend" "user"

echo ""
echo "🌐 Service Endpoints:"
check_endpoint "Ollama API" "http://localhost:11434/api/version"
check_endpoint "AutoGen Studio" "http://100.123.10.72:11001"
check_endpoint "Webhook Server" "http://100.123.10.72:11002/health"
check_endpoint "Chat Copilot API" "http://100.123.10.72:11000/healthz"
check_endpoint "Chat Copilot Web" "http://100.123.10.72:11000"
check_endpoint "VS Code Web" "http://100.123.10.72:57081"

echo ""
echo "🦙 Ollama Models:"
ollama list 2>/dev/null || echo "❌ Ollama not accessible"
"""
        
        script_path = f"{self.platform_dir}/check-platform-status.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"✅ Created status checker: {script_path}")
        
        return script_path

def main():
    """Main auto-startup setup function"""
    
    print("🚀 AI Research Platform Auto-Startup Setup")
    print("=" * 50)
    
    manager = AutoStartupManager()
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    # Check if running as user with sudo access
    if os.geteuid() == 0:
        print("❌ Don't run this script as root. Run as regular user with sudo access.")
        return
    
    # Check if required directories exist
    if not os.path.exists(manager.platform_dir):
        print(f"❌ Platform directory not found: {manager.platform_dir}")
        return
    
    if not os.path.exists(f"{manager.platform_dir}/autogen-env"):
        print(f"❌ AutoGen environment not found: {manager.platform_dir}/autogen-env")
        return
    
    print("✅ Prerequisites check passed")
    
    # Install services
    print(f"\n📦 Installing services...")
    results = manager.install_all_services()
    
    # Show results
    print(f"\n📊 Installation Results:")
    for service, result in results.items():
        status_icon = "✅" if result == "success" else "❌"
        print(f"   {status_icon} {service}: {result}")
    
    # Create status checker
    print(f"\n📝 Creating status checker...")
    manager.create_status_script()
    
    # Show final status
    print(f"\n🎉 Auto-startup setup complete!")
    print(f"\n🔧 Available Scripts:")
    print(f"   📋 Check Status: ./check-platform-status.sh")
    print(f"   🚀 Manual Start: ./startup-platform.sh")
    print(f"   ⚙️ Enable User Services: ./enable-user-services.sh")
    
    print(f"\n🔄 Service Management Commands:")
    print(f"   📊 Check all: systemctl --user status autogen-studio-ai-platform")
    print(f"   🔄 Restart service: systemctl --user restart autogen-studio-ai-platform")
    print(f"   📋 View logs: journalctl --user -f -u autogen-studio-ai-platform")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Reboot your system to test auto-startup")
    print(f"2. Run ./check-platform-status.sh to verify services")
    print(f"3. Access Control Panel: http://100.123.10.72:11000/control-panel.html")

if __name__ == "__main__":
    main()