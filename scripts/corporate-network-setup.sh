#!/bin/bash

# Corporate Network Setup Script for AI Restaurant Network Management
# Automated installation and configuration for corporate network deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🏢 AI Restaurant Network Management - Corporate Network Setup"
echo "=============================================================="
echo "📅 $(date)"
echo "📂 Project Root: $PROJECT_ROOT"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            echo "ubuntu"
        elif command_exists yum; then
            echo "centos"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Step 1: System Information
log_info "Detecting system information..."
OS_TYPE=$(detect_os)
log_info "Detected OS: $OS_TYPE"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python3 detected: $PYTHON_VERSION"
else
    log_error "Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Step 2: Install System Dependencies
log_info "Installing system dependencies..."

install_dependencies() {
    case $OS_TYPE in
        "ubuntu")
            log_info "Installing Ubuntu/Debian dependencies..."
            sudo apt update
            sudo apt install -y python3-pip python3-venv git curl wget unzip
            ;;
        "centos")
            log_info "Installing CentOS/RHEL dependencies..."
            sudo yum install -y python3-pip git curl wget unzip
            ;;
        "macos")
            log_info "Installing macOS dependencies..."
            if ! command_exists brew; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python git curl wget
            ;;
        *)
            log_warning "Unknown OS type. Please install dependencies manually:"
            log_warning "- Python 3.8+"
            log_warning "- pip"
            log_warning "- git"
            log_warning "- curl"
            ;;
    esac
}

if ! command_exists pip3; then
    install_dependencies
else
    log_success "System dependencies already installed"
fi

# Step 3: Setup Python Virtual Environment
log_info "Setting up Python virtual environment..."

cd "$PROJECT_ROOT"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Created virtual environment"
else
    log_success "Virtual environment already exists"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate || {
    log_error "Failed to activate virtual environment"
    exit 1
}

# Step 4: Install Python Dependencies
log_info "Installing Python dependencies..."

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    log_info "Creating requirements.txt..."
    cat > requirements.txt << 'EOF'
requests>=2.32.0
urllib3>=2.0.0
certifi
neo4j>=5.0.0
redis>=4.0.0
flask>=2.3.0
python-dotenv>=1.0.0
speech_recognition>=3.10.0
pyaudio>=0.2.11
pyttsx3>=2.90
aiohttp>=3.8.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
networkx>=3.0
matplotlib>=3.7.0
plotly>=5.14.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
seaborn>=0.12.0
EOF
    log_success "Created requirements.txt"
fi

pip install --upgrade pip
pip install -r requirements.txt

log_success "Python dependencies installed"

# Step 5: Setup Network Agents Directory
log_info "Setting up network agents..."

cd "$PROJECT_ROOT"
if [ ! -d "network-agents" ]; then
    mkdir -p network-agents
    log_success "Created network-agents directory"
fi

# Step 6: Setup Environment Configuration
log_info "Setting up environment configuration..."

cd "$PROJECT_ROOT/network-agents"

if [ ! -f ".env" ]; then
    log_info "Creating .env template..."
    cat > .env << 'EOF'
# FortiManager Credentials - Corporate Network Access Required
# Update these with your actual FortiManager credentials

ARBYS_FORTIMANAGER_HOST=10.128.144.132
ARBYS_USERNAME=ibadmin
ARBYS_PASSWORD=your_password_here

BWW_FORTIMANAGER_HOST=10.128.145.4
BWW_USERNAME=ibadmin
BWW_PASSWORD=your_password_here

SONIC_FORTIMANAGER_HOST=10.128.156.36
SONIC_USERNAME=ibadmin
SONIC_PASSWORD=your_password_here

# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
SESSION_TIMEOUT=3600

# API Configuration
MERAKI_API_KEY=your_meraki_key_here
MERAKI_BASE_URL=https://api.meraki.com/api/v1
FLASK_PORT=10000
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
SSL_VERIFY=False
REQUEST_TIMEOUT=30
EOF
    log_warning "Created .env file - PLEASE UPDATE WITH ACTUAL CREDENTIALS"
    log_warning "Edit: $PROJECT_ROOT/network-agents/.env"
else
    log_success "Environment file already exists"
fi

# Step 7: Install and Configure Neo4j
log_info "Setting up Neo4j database..."

setup_neo4j() {
    case $OS_TYPE in
        "ubuntu")
            log_info "Installing Neo4j on Ubuntu..."
            curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/neo4j.gpg
            echo 'deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list
            sudo apt update
            sudo apt install neo4j -y
            sudo systemctl enable neo4j
            sudo systemctl start neo4j
            ;;
        "macos")
            log_info "Installing Neo4j on macOS..."
            brew install neo4j
            brew services start neo4j
            ;;
        *)
            log_warning "Please install Neo4j manually:"
            log_warning "Download from: https://neo4j.com/download/"
            log_warning "Or use Neo4j Desktop for easier management"
            ;;
    esac
}

if ! command_exists neo4j; then
    read -p "Install Neo4j database? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_neo4j
    else
        log_warning "Neo4j not installed. Install manually later."
    fi
else
    log_success "Neo4j already installed"
fi

# Step 8: Setup Redis (Optional)
log_info "Setting up Redis for session management..."

setup_redis() {
    case $OS_TYPE in
        "ubuntu")
            sudo apt install redis-server -y
            sudo systemctl enable redis-server
            sudo systemctl start redis-server
            ;;
        "macos")
            brew install redis
            brew services start redis
            ;;
        *)
            log_warning "Please install Redis manually for session caching"
            ;;
    esac
}

if ! command_exists redis-server && ! command_exists redis-cli; then
    read -p "Install Redis for session management? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_redis
    else
        log_warning "Redis not installed. Session caching disabled."
    fi
else
    log_success "Redis already available"
fi

# Step 9: Apply SSL Fixes for Corporate Network
log_info "Applying SSL fixes for corporate network..."

cd "$PROJECT_ROOT/network-agents"
if [ -f "ssl_universal_fix.py" ]; then
    python3 ssl_universal_fix.py
    log_success "SSL fixes applied for corporate environment"
else
    log_warning "SSL fix script not found - download from GitHub"
fi

# Step 10: Test Corporate Network Connectivity
log_info "Testing corporate network connectivity..."

test_connectivity() {
    log_info "Running corporate network connectivity test..."
    cd "$PROJECT_ROOT/network-agents"
    
    if [ -f "test_corporate_network.py" ]; then
        python3 test_corporate_network.py
    elif [ -f "fortimanager_api.py" ]; then
        python3 fortimanager_api.py
    else
        log_warning "Network test scripts not found"
        log_info "Please download all files from GitHub repository"
    fi
}

read -p "Test FortiManager connectivity now? (requires corporate network) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    test_connectivity
else
    log_info "Skipping connectivity test"
fi

# Step 11: Create Startup Scripts
log_info "Creating startup scripts..."

cd "$PROJECT_ROOT"

# Create quick start script
cat > corporate-quick-start.sh << 'EOF'
#!/bin/bash

echo "🏢 Starting AI Restaurant Network Management System"
echo "=================================================="

PROJECT_ROOT="$(dirname "$(readlink -f "$0")")"
cd "$PROJECT_ROOT"

# Activate virtual environment
source venv/bin/activate

# Apply SSL fixes
cd network-agents
python3 ssl_universal_fix.py

# Start the system
echo "🚀 Starting multi-vendor network system..."
cd ..
./start-multi-vendor-network-system.sh

echo ""
echo "🎯 Access Points:"
echo "📊 Main Dashboard: http://localhost:11040"
echo "🎤 Voice Interface: http://localhost:11033" 
echo "🗄️  Neo4j Browser: http://localhost:7474"
echo ""
echo "✅ System started! Ready for corporate network testing."
EOF

chmod +x corporate-quick-start.sh
log_success "Created corporate-quick-start.sh"

# Step 12: Installation Summary
echo ""
echo "🎉 CORPORATE NETWORK INSTALLATION COMPLETE!"
echo "=============================================="
echo ""
log_success "✅ Python virtual environment: $PROJECT_ROOT/venv"
log_success "✅ Network agents directory: $PROJECT_ROOT/network-agents"
log_success "✅ Environment template: $PROJECT_ROOT/network-agents/.env"
log_success "✅ SSL fixes applied for corporate networks"
log_success "✅ Quick start script: $PROJECT_ROOT/corporate-quick-start.sh"

if command_exists neo4j; then
    log_success "✅ Neo4j database installed and configured"
else
    log_warning "⚠️  Neo4j needs manual installation"
fi

if command_exists redis-cli; then
    log_success "✅ Redis session management available"
else
    log_warning "⚠️  Redis session management not installed"
fi

echo ""
echo "📋 NEXT STEPS:"
echo "1. Update FortiManager credentials in: $PROJECT_ROOT/network-agents/.env"
echo "2. Ensure you're connected to corporate network"
echo "3. Test connectivity: cd network-agents && python3 test_corporate_network.py"
echo "4. Start system: ./corporate-quick-start.sh"
echo ""
echo "📖 Full documentation: $PROJECT_ROOT/CORPORATE_NETWORK_INSTALL.md"
echo "🔧 Troubleshooting: $PROJECT_ROOT/FORTIMANAGER_TESTING_GUIDE.md"
echo ""
echo "🏢 Ready for corporate network FortiManager testing!"

# Deactivate virtual environment
deactivate 2>/dev/null || true

log_success "Setup complete! 🚀"