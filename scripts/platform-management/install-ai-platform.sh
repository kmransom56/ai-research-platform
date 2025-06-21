#!/bin/bash
# AI Research Platform - Automated Installation Script
# Supports Ubuntu 20.04+ and Debian-based systems
# Optimized for GPU-enabled systems with CUDA support
# Version: 1.0

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

readonly PLATFORM_NAME="AI Research Platform"
readonly PLATFORM_VERSION="3.1"
readonly MIN_RAM_GB=16
readonly MIN_DISK_GB=100
readonly RECOMMENDED_GPU_RAM_GB=8

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly NC='\033[0m'

# Installation paths
readonly INSTALL_DIR="/home/$USER/chat-copilot"
readonly LOGS_DIR="$INSTALL_DIR/logs"
readonly CONFIG_DIR="$INSTALL_DIR/config"
readonly BACKUP_DIR="$INSTALL_DIR/backups"

# =============================================================================
# LOGGING & UTILITIES
# =============================================================================

log() {
    local level="$1"
    shift
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
    "ERROR") echo -e "${RED}❌ [$timestamp] ERROR: $*${NC}" ;;
    "SUCCESS") echo -e "${GREEN}✅ [$timestamp] SUCCESS: $*${NC}" ;;
    "INFO") echo -e "${BLUE}ℹ️  [$timestamp] INFO: $*${NC}" ;;
    "WARN") echo -e "${YELLOW}⚠️  [$timestamp] WARN: $*${NC}" ;;
    "TITLE") echo -e "${PURPLE}🚀 [$timestamp] $*${NC}" ;;
    esac
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log ERROR "This script should not be run as root. Please run as a regular user."
        exit 1
    fi
}

check_system_requirements() {
    log INFO "Checking system requirements..."

    # Check OS
    if ! command -v apt &>/dev/null; then
        log ERROR "This installer requires a Debian-based system (Ubuntu/Debian)"
        exit 1
    fi

    # Check RAM
    local ram_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $ram_gb -lt $MIN_RAM_GB ]]; then
        log WARN "System has ${ram_gb}GB RAM, recommended minimum is ${MIN_RAM_GB}GB"
    else
        log SUCCESS "RAM check passed: ${ram_gb}GB available"
    fi

    # Check disk space
    local disk_gb=$(df / | awk 'NR==2 {print int($4/1024/1024)}')
    if [[ $disk_gb -lt $MIN_DISK_GB ]]; then
        log ERROR "Insufficient disk space. Required: ${MIN_DISK_GB}GB, Available: ${disk_gb}GB"
        exit 1
    else
        log SUCCESS "Disk space check passed: ${disk_gb}GB available"
    fi

    # Check GPU
    if command -v nvidia-smi &>/dev/null; then
        local gpu_ram=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        gpu_ram=$((gpu_ram / 1024))
        log SUCCESS "NVIDIA GPU detected with ${gpu_ram}GB VRAM"
        export HAS_GPU=true
        export GPU_RAM_GB=$gpu_ram
    else
        log WARN "No NVIDIA GPU detected. Some AI features may be limited."
        export HAS_GPU=false
        export GPU_RAM_GB=0
    fi
}

# =============================================================================
# INSTALLATION FUNCTIONS
# =============================================================================

install_system_dependencies() {
    log INFO "Installing system dependencies..."

    sudo apt update
    sudo apt install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        build-essential \
        python3 \
        python3-pip \
        python3-venv \
        nodejs \
        npm \
        docker.io \
        docker-compose \
        nginx \
        ufw \
        htop \
        tree \
        jq \
        nano \
        vim

    # Add user to docker group
    sudo usermod -aG docker $USER

    log SUCCESS "System dependencies installed"
}

install_gpu_support() {
    if [[ "$HAS_GPU" == "true" ]]; then
        log INFO "Installing GPU support (CUDA/Docker)..."

        # Install NVIDIA Container Toolkit
        distribution=$(
            . /etc/os-release
            echo $ID$VERSION_ID
        ) &&
            curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg &&
            curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list |
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' |
                sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

        sudo apt update
        sudo apt install -y nvidia-container-toolkit
        sudo systemctl restart docker

        log SUCCESS "GPU support installed"
    else
        log INFO "Skipping GPU support installation (no GPU detected)"
    fi
}

install_dotnet() {
    log INFO "Installing .NET 8.0..."

    wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    sudo dpkg -i packages-microsoft-prod.deb
    rm packages-microsoft-prod.deb

    sudo apt update
    sudo apt install -y dotnet-sdk-8.0 aspnetcore-runtime-8.0

    log SUCCESS ".NET 8.0 installed"
}

install_caddy() {
    log INFO "Installing Caddy web server..."

    sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

    sudo apt update
    sudo apt install -y caddy

    log SUCCESS "Caddy installed"
}

install_tailscale() {
    log INFO "Installing Tailscale..."

    curl -fsSL https://tailscale.com/install.sh | sh

    log SUCCESS "Tailscale installed"
    log WARN "Remember to run 'sudo tailscale up' after installation"
}

install_ollama() {
    log INFO "Installing Ollama for local LLM support..."

    curl -fsSL https://ollama.com/install.sh | sh

    # Configure Ollama systemd service
    sudo tee /etc/systemd/system/ollama.service >/dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=$USER
Group=$USER
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=default.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ollama

    log SUCCESS "Ollama installed"
}

install_perplexica() {
    log INFO "Installing Perplexica AI search engine..."

    cd "$INSTALL_DIR"

    # Clone Perplexica
    if [[ ! -d "perplexica" ]]; then
        git clone https://github.com/ItzCrazyKns/Perplexica.git perplexica
    fi

    cd perplexica

    # Create environment file
    if [[ ! -f ".env" ]]; then
        cat >.env <<EOF
PORT=11020
OLLAMA_API_BASE_URL=http://localhost:11434
OPENAI_API_KEY=\${OPENAI_API_KEY:-your-openai-key-here}
ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY:-your-anthropic-key-here}
SEARXNG_API_ENDPOINT=http://localhost:11021
EOF
    fi

    # Build and start with Docker Compose
    docker-compose -f compose.yaml up -d --build

    log SUCCESS "Perplexica installed and started on port 11020"
}

install_searxng() {
    log INFO "Installing SearXNG privacy search engine..."

    cd "$INSTALL_DIR"
    mkdir -p searxng
    cd searxng

    # Create SearXNG configuration
    cat >settings.yml <<EOF
use_default_settings: true
server:
  secret_key: "$(openssl rand -hex 32)"
  bind_address: "0.0.0.0"
  port: 11021
search:
  safe_search: 1
  autocomplete: "google"
outgoing:
  request_timeout: 5.0
  max_request_timeout: 15.0
engines:
  - name: google
    disabled: false
  - name: bing
    disabled: false
  - name: duckduckgo
    disabled: false
EOF

    # Create Docker Compose for SearXNG
    cat >docker-compose.yml <<EOF
version: '3.8'
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "11021:8080"
    volumes:
      - "./settings.yml:/etc/searxng/settings.yml:ro"
    environment:
      - SEARXNG_BASE_URL=http://localhost:11021/
    restart: unless-stopped
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    logging:
      driver: "json-file"
      options:
        max-size: "1m"
        max-file: "1"
EOF

    # Start SearXNG
    docker-compose up -d

    log SUCCESS "SearXNG installed and started on port 11021"
}

install_vscode_server() {
    log INFO "Installing VS Code Server..."

    # Install VS Code Server
    cd "$INSTALL_DIR"

    # Download and install code-server
    curl -fsSL https://code-server.dev/install.sh | sh -s -- --method=standalone --prefix="$INSTALL_DIR/code-server"

    # Create VS Code configuration
    mkdir -p "$HOME/.config/code-server"
    cat >"$HOME/.config/code-server/config.yaml" <<EOF
bind-addr: 0.0.0.0:57081
auth: password
password: $(openssl rand -base64 32)
cert: false
EOF

    # Create systemd service for code-server
    sudo tee /etc/systemd/system/code-server.service >/dev/null <<EOF
[Unit]
Description=VS Code Server
After=network.target

[Service]
Type=exec
ExecStart=$INSTALL_DIR/code-server/bin/code-server --bind-addr 0.0.0.0:57081 --user-data-dir $HOME/.local/share/code-server --extensions-dir $HOME/.local/share/code-server/extensions
Restart=always
User=$USER
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=HOME=$HOME

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start the service
    sudo systemctl daemon-reload
    sudo systemctl enable code-server
    sudo systemctl start code-server

    # Get the password for display later
    local vscode_password=$(grep 'password:' "$HOME/.config/code-server/config.yaml" | cut -d' ' -f2)
    echo "$vscode_password" >"$CONFIG_DIR/vscode-password.txt"

    log SUCCESS "VS Code Server installed on port 57081"
    log INFO "VS Code password saved to: $CONFIG_DIR/vscode-password.txt"
}

install_openwebui() {
    log INFO "Installing OpenWebUI..."

    cd "$INSTALL_DIR"
    mkdir -p openwebui
    cd openwebui

    # Create Docker Compose for OpenWebUI
    cat >docker-compose.yml <<EOF
version: '3.8'
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "11880:8080"
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - WEBUI_SECRET_KEY=$(openssl rand -hex 32)
    volumes:
      - open-webui:/app/backend/data
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped

volumes:
  open-webui:
EOF

    # Start OpenWebUI
    docker-compose up -d

    log SUCCESS "OpenWebUI installed and started on port 11880"
}

setup_python_environment() {
    log INFO "Setting up Python environment..."

    cd "$INSTALL_DIR"
    python3 -m venv autogen-env
    source autogen-env/bin/activate

    pip install --upgrade pip setuptools wheel
    pip install \
        autogenstudio \
        pyautogen \
        openai \
        anthropic \
        fastapi \
        uvicorn \
        websockets \
        requests \
        python-dotenv \
        pydantic \
        jupyter \
        pandas \
        numpy \
        matplotlib \
        plotly \
        streamlit \
        gradio

    # Install GPU-specific packages if GPU is available
    if [[ "$HAS_GPU" == "true" ]]; then
        pip install \
            torch \
            torchvision \
            torchaudio \
            transformers \
            accelerate \
            bitsandbytes \
            xformers
    fi

    deactivate
    log SUCCESS "Python environment configured"
}

clone_platform_repository() {
    log INFO "Setting up platform files..."

    mkdir -p "$INSTALL_DIR" "$LOGS_DIR" "$CONFIG_DIR" "$BACKUP_DIR"
    cd "$(dirname "$INSTALL_DIR")"

    # If running from existing installation, copy files
    if [[ -f "$(dirname "$0")/startup-platform-clean.sh" ]]; then
        log INFO "Copying platform files from current installation..."
        cp -r "$(dirname "$0")"/* "$INSTALL_DIR/"
    else
        log INFO "Creating platform structure..."
        # Create basic structure if not copying from existing
        mkdir -p "$INSTALL_DIR"/{webapi,docs,scripts,config,logs,pids}
    fi

    log SUCCESS "Platform files configured"
}

configure_firewall() {
    log INFO "Configuring firewall..."

    sudo ufw --force enable

    # SSH
    sudo ufw allow 22

    # Platform ports
    sudo ufw allow 11000:12000/tcp

    # Caddy
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw allow 8080

    # VS Code
    sudo ufw allow 57081

    log SUCCESS "Firewall configured"
}

generate_configuration_files() {
    log INFO "Generating configuration files..."

    # Create environment file
    cat >"$CONFIG_DIR/.env" <<EOF
# AI Research Platform Configuration
PLATFORM_VERSION=$PLATFORM_VERSION
INSTALL_DIR=$INSTALL_DIR
HAS_GPU=$HAS_GPU
GPU_RAM_GB=$GPU_RAM_GB

# OpenAI Configuration (add your keys)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Tailscale Configuration
TAILSCALE_DOMAIN=your_tailscale_domain_here

# Service Ports
CHAT_COPILOT_PORT=11000
AUTOGEN_STUDIO_PORT=11001
WEBHOOK_SERVER_PORT=11002
MAGENTIC_ONE_PORT=11003
PORT_SCANNER_PORT=11010
NGINX_PROXY_PORT=11080
PERPLEXICA_PORT=11020
SEARXNG_PORT=11021
OPENWEBUI_PORT=11880
OLLAMA_PORT=11434

# Database Configuration
DB_CONNECTION_STRING=your_db_connection_here
EOF

    # Create basic Caddyfile
    cat >"$CONFIG_DIR/Caddyfile.template" <<EOF
{
    admin 0.0.0.0:2019
}

http://:8080 {
    # Landing page
    @root host YOUR_TAILSCALE_DOMAIN
    handle @root {
        respond "AI Research Platform - Please configure your domain" 200
    }
    
    # Service proxies will be configured here
    # Copy from your existing Caddyfile and update domain
}
EOF

    log SUCCESS "Configuration files generated in $CONFIG_DIR"
}

create_startup_scripts() {
    log INFO "Creating startup and management scripts..."

    # Copy the main startup script if it exists
    if [[ -f "$(dirname "$0")/startup-platform-clean.sh" ]]; then
        cp "$(dirname "$0")/startup-platform-clean.sh" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/startup-platform-clean.sh"
    fi

    # Create installation status script
    cat >"$INSTALL_DIR/check-installation.sh" <<EOF
#!/bin/bash
echo "=== AI Research Platform Installation Status ==="
echo "Installation Directory: $INSTALL_DIR"
echo "GPU Support: $HAS_GPU"
echo "GPU RAM: ${GPU_RAM_GB}GB"
echo ""
echo "Services Status:"
systemctl is-active docker || echo "Docker: Not running"
systemctl is-active caddy || echo "Caddy: Not running"
systemctl is-active ollama || echo "Ollama: Not running"
tailscale status 2>/dev/null || echo "Tailscale: Not connected"
echo ""
echo "Next steps:"
echo "1. Configure API keys in $CONFIG_DIR/.env"
echo "2. Update Tailscale domain in configuration"
echo "3. Run ./startup-platform-clean.sh to start services"
EOF
    chmod +x "$INSTALL_DIR/check-installation.sh"

    log SUCCESS "Management scripts created"
}

post_installation_setup() {
    log TITLE "Post-installation setup..."

    # Start essential services
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo systemctl start caddy
    sudo systemctl enable caddy
    sudo systemctl start ollama

    # Create desktop shortcut if GUI is available
    if [[ -n "${DISPLAY:-}" ]]; then
        cat >"$HOME/Desktop/AI Research Platform.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Research Platform
Comment=Launch AI Research Platform
Exec=gnome-terminal -- bash -c "cd $INSTALL_DIR && ./startup-platform-clean.sh; bash"
Icon=applications-development
Terminal=false
Categories=Development;
EOF
        chmod +x "$HOME/Desktop/AI Research Platform.desktop"
        log SUCCESS "Desktop shortcut created"
    fi

    log SUCCESS "Post-installation setup complete"
}

# =============================================================================
# MAIN INSTALLATION FLOW
# =============================================================================

main() {
    log TITLE "Starting $PLATFORM_NAME v$PLATFORM_VERSION Installation"

    # Pre-flight checks
    check_root
    check_system_requirements

    # Confirm installation
    echo -e "\n${YELLOW}This will install the AI Research Platform to: $INSTALL_DIR${NC}"
    echo -e "${YELLOW}GPU Support: $HAS_GPU (${GPU_RAM_GB}GB VRAM)${NC}"
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log INFO "Installation cancelled"
        exit 0
    fi

    # Main installation steps
    log TITLE "Installing system dependencies..."
    install_system_dependencies

    log TITLE "Installing GPU support..."
    install_gpu_support

    log TITLE "Installing .NET runtime..."
    install_dotnet

    log TITLE "Installing Caddy web server..."
    install_caddy

    log TITLE "Installing Tailscale..."
    install_tailscale

    log TITLE "Installing Ollama..."
    install_ollama

    log TITLE "Installing Perplexica..."
    install_perplexica

    log TITLE "Installing SearXNG..."
    install_searxng

    log TITLE "Installing VS Code Server..."
    install_vscode_server

    log TITLE "Installing OpenWebUI..."
    install_openwebui

    log TITLE "Setting up platform files..."
    clone_platform_repository

    log TITLE "Setting up Python environment..."
    setup_python_environment

    log TITLE "Configuring firewall..."
    configure_firewall

    log TITLE "Generating configuration files..."
    generate_configuration_files

    log TITLE "Creating management scripts..."
    create_startup_scripts

    log TITLE "Finalizing installation..."
    post_installation_setup

    # Installation complete
    log SUCCESS "🎉 Installation completed successfully!"
    echo -e "\n${GREEN}📋 Next Steps:${NC}"
    echo "1. Configure your API keys in: $CONFIG_DIR/.env"
    echo "2. Set up Tailscale: sudo tailscale up"
    echo "3. Update your domain in the Caddyfile"
    echo "4. Run: cd $INSTALL_DIR && ./startup-platform-clean.sh"
    echo "5. Check status: ./check-installation.sh"
    echo ""
    echo -e "${BLUE}📁 Installation Directory: $INSTALL_DIR${NC}"
    echo -e "${BLUE}📝 Configuration: $CONFIG_DIR${NC}"
    echo -e "${BLUE}📊 Logs: $LOGS_DIR${NC}"

    if [[ "$HAS_GPU" == "true" ]]; then
        echo ""
        echo -e "${GREEN}🎮 GPU Optimization Tips:${NC}"
        echo "- Your system has ${GPU_RAM_GB}GB VRAM - excellent for large models!"
        echo "- Consider installing local models via Ollama for privacy"
        echo "- GPU acceleration is configured for PyTorch and Transformers"
    fi
}

# Run installation
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
