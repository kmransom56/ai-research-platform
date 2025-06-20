#!/bin/bash
# AI Research Platform - Deployment Package Creator
# Creates a portable installation package for easy deployment

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PACKAGE_NAME="ai-research-platform-$(date +%Y%m%d)"
readonly PACKAGE_DIR="/tmp/$PACKAGE_NAME"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $*${NC}"
}

create_deployment_package() {
    log "Creating deployment package: $PACKAGE_NAME"

    # Create package directory
    mkdir -p "$PACKAGE_DIR"

    # Copy essential files
    log "Copying platform files..."

    # Core scripts
    cp "$SCRIPT_DIR/install-ai-platform.sh" "$PACKAGE_DIR/"
    cp "$SCRIPT_DIR/startup-platform-clean.sh" "$PACKAGE_DIR/"
    cp "$SCRIPT_DIR/INSTALLATION_GUIDE.md" "$PACKAGE_DIR/"

    # Configuration templates (sanitized)
    mkdir -p "$PACKAGE_DIR/config-templates"

    # Create sanitized Caddyfile template
    if [[ -f "$SCRIPT_DIR/Caddyfile" ]]; then
        sed 's/ubuntuaicodeserver-1\.tail5137b4\.ts\.net/YOUR_TAILSCALE_DOMAIN/g' \
            "$SCRIPT_DIR/Caddyfile" >"$PACKAGE_DIR/config-templates/Caddyfile.template"
    fi

    # Create sanitized environment template
    cat >"$PACKAGE_DIR/config-templates/.env.template" <<EOF
# AI Research Platform Configuration
# Copy this to config/.env and fill in your values

# API Keys (Required)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-claude-key-here

# Optional API Keys
HUGGINGFACE_TOKEN=hf_your-huggingface-token
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=gsk_your-groq-key

# Tailscale Configuration
TAILSCALE_DOMAIN=your-machine.tail12345.ts.net

# Service Configuration
PLATFORM_VERSION=3.1
INSTALL_DIR=/home/\$USER/chat-copilot

# Database (if using external database)
DB_CONNECTION_STRING=your_database_connection_string

# Security
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here
EOF

    # Copy essential configuration files
    if [[ -d "$SCRIPT_DIR/webapi" ]]; then
        log "Copying Chat Copilot backend..."
        mkdir -p "$PACKAGE_DIR/webapi"
        cp -r "$SCRIPT_DIR/webapi"/* "$PACKAGE_DIR/webapi/" 2>/dev/null || true
    fi

    # Copy Python scripts
    if [[ -f "$SCRIPT_DIR/autogen_config.py" ]]; then
        cp "$SCRIPT_DIR/autogen_config.py" "$PACKAGE_DIR/"
    fi

    if [[ -f "$SCRIPT_DIR/magentic_one_simple.py" ]]; then
        cp "$SCRIPT_DIR/magentic_one_simple.py" "$PACKAGE_DIR/"
    fi

    # Copy documentation
    mkdir -p "$PACKAGE_DIR/docs"
    if [[ -d "$SCRIPT_DIR/docs" ]]; then
        cp -r "$SCRIPT_DIR/docs"/* "$PACKAGE_DIR/docs/" 2>/dev/null || true
    fi

    # Create requirements files
    log "Creating requirements files..."

    # Python requirements
    cat >"$PACKAGE_DIR/requirements.txt" <<EOF
# AI Research Platform Python Dependencies
autogenstudio>=0.4.0
pyautogen>=0.2.0
openai>=1.0.0
anthropic>=0.8.0
fastapi>=0.100.0
uvicorn>=0.20.0
websockets>=11.0
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.0.0
jupyter>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
plotly>=5.15.0
streamlit>=1.28.0
gradio>=4.0.0

# GPU-specific (install if GPU available)
# torch>=2.0.0
# torchvision>=0.15.0
# torchaudio>=2.0.0
# transformers>=4.30.0
# accelerate>=0.20.0
# bitsandbytes>=0.40.0
# xformers>=0.20.0
EOF

    # Node.js dependencies
    if [[ -f "$SCRIPT_DIR/package.json" ]]; then
        cp "$SCRIPT_DIR/package.json" "$PACKAGE_DIR/"
    else
        cat >"$PACKAGE_DIR/package.json" <<EOF
{
  "name": "ai-research-platform",
  "version": "3.1.0",
  "description": "AI Research Platform Node.js Dependencies",
  "dependencies": {
    "express": "^4.18.0",
    "ws": "^8.14.0",
    "node-fetch": "^3.3.0",
    "dotenv": "^16.3.0"
  }
}
EOF
    fi

    # Create deployment instructions
    cat >"$PACKAGE_DIR/DEPLOY_README.md" <<EOF
# AI Research Platform - Deployment Package

This package contains everything needed to deploy the AI Research Platform on a new system.

## Quick Start

1. **Transfer package to target system:**
   \`\`\`bash
   scp -r $PACKAGE_NAME user@target-server:~/
   \`\`\`

2. **Run installation:**
   \`\`\`bash
   cd ~/$PACKAGE_NAME
   ./install-ai-platform.sh
   \`\`\`

3. **Configure:**
   - Copy \`config-templates/.env.template\` to \`config/.env\` and fill in your API keys
   - Update \`config-templates/Caddyfile.template\` with your Tailscale domain
   - Run \`sudo tailscale up\` to connect to your Tailscale network

4. **Start platform:**
   \`\`\`bash
   cd /home/\$USER/chat-copilot
   ./startup-platform-clean.sh
   \`\`\`

## System Requirements

- Ubuntu 20.04+ or Debian-based Linux
- 16GB+ RAM (64GB+ recommended for AI workloads)
- 100GB+ free disk space
- NVIDIA GPU with 8GB+ VRAM (optional but recommended)
- Internet connection for initial setup

## Package Contents

- \`install-ai-platform.sh\`: Main installation script
- \`startup-platform-clean.sh\`: Platform startup script
- \`config-templates/\`: Configuration file templates
- \`webapi/\`: Chat Copilot backend (if included)
- \`requirements.txt\`: Python dependencies
- \`package.json\`: Node.js dependencies
- \`INSTALLATION_GUIDE.md\`: Detailed installation guide

## Support

See \`INSTALLATION_GUIDE.md\` for detailed instructions and troubleshooting.

Package created: $(date)
Source system: $(hostname)
Platform version: 3.1
EOF

    # Create quick deployment script
    cat >"$PACKAGE_DIR/quick-deploy.sh" <<EOF
#!/bin/bash
# Quick deployment script for AI Research Platform

set -e

echo "🚀 AI Research Platform - Quick Deployment"
echo "=========================================="

# Check if running as root
if [[ \$EUID -eq 0 ]]; then
    echo "❌ Do not run as root. Please run as a regular user."
    exit 1
fi

# Run main installer
echo "📦 Starting installation..."
./install-ai-platform.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure API keys: nano config/.env"
echo "2. Set up Tailscale: sudo tailscale up"
echo "3. Update domain in Caddyfile"
echo "4. Start platform: cd /home/\$USER/chat-copilot && ./startup-platform-clean.sh"
EOF
    chmod +x "$PACKAGE_DIR/quick-deploy.sh"

    # Create archive
    log "Creating deployment archive..."
    cd /tmp
    tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

    echo -e "\n${GREEN}✅ Deployment package created successfully!${NC}"
    echo -e "${YELLOW}📦 Package: /tmp/$PACKAGE_NAME.tar.gz${NC}"
    echo -e "${YELLOW}📁 Directory: $PACKAGE_DIR${NC}"
    echo ""
    echo "📋 To deploy on another system:"
    echo "1. Transfer: scp /tmp/$PACKAGE_NAME.tar.gz user@target-server:~/"
    echo "2. Extract: tar -xzf $PACKAGE_NAME.tar.gz"
    echo "3. Deploy: cd $PACKAGE_NAME && ./quick-deploy.sh"
    echo ""
    echo "📖 For detailed instructions, see DEPLOY_README.md in the package"
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    create_deployment_package
fi
