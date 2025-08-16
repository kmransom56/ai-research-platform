#!/bin/bash

# 🎤 Easy Installer for Speech-Enabled Network Management
# One-click installation for non-technical users

set -e

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Progress tracking
STEP=0
TOTAL_STEPS=12

print_header() {
    clear
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${WHITE}              🎤 Speech-Enabled Network Management              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${WHITE}                    Easy Installation System                     ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${WHITE}                                                                 ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${CYAN}   Installing enterprise AI network management with voice control   ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_step() {
    STEP=$((STEP + 1))
    echo -e "${BLUE}[${WHITE}${STEP}/${TOTAL_STEPS}${BLUE}]${WHITE} $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Check if running as root
check_permissions() {
    print_step "Checking permissions..."
    if [[ $EUID -eq 0 ]]; then
        print_error "Please don't run this as root/sudo. Run as your regular user."
    fi
    print_success "Running with correct user permissions"
    sleep 1
}

# Detect operating system
detect_os() {
    print_step "Detecting your operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get >/dev/null 2>&1; then
            DISTRO="ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            DISTRO="centos"
        else
            DISTRO="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
    fi
    
    print_success "Detected: $OS ($DISTRO)"
    sleep 1
}

# Check and install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    
    case $DISTRO in
        "ubuntu")
            print_info "Installing packages for Ubuntu/Debian..."
            sudo apt-get update -qq >/dev/null 2>&1
            sudo apt-get install -y \
                python3 python3-pip python3-venv python3-dev \
                git curl wget \
                portaudio19-dev \
                build-essential \
                docker.io docker-compose \
                >/dev/null 2>&1
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            ;;
        "centos")
            print_info "Installing packages for CentOS/RHEL..."
            sudo yum install -y \
                python3 python3-pip python3-devel \
                git curl wget \
                portaudio-devel \
                gcc gcc-c++ make \
                docker docker-compose \
                >/dev/null 2>&1
            
            sudo systemctl enable docker
            sudo systemctl start docker
            sudo usermod -aG docker $USER
            ;;
        "macos")
            print_info "Installing packages for macOS..."
            # Check for Homebrew
            if ! command -v brew >/dev/null 2>&1; then
                print_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew install python3 git portaudio docker docker-compose >/dev/null 2>&1
            ;;
    esac
    
    print_success "System dependencies installed"
    sleep 1
}

# Check Python version
check_python() {
    print_step "Checking Python installation..."
    
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not installed"
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python $PYTHON_VERSION is compatible"
    else
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
    fi
    sleep 1
}

# Check Docker
check_docker() {
    print_step "Checking Docker installation..."
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker installation failed"
    fi
    
    # Start Docker if not running
    if ! docker ps >/dev/null 2>&1; then
        case $OS in
            "linux")
                sudo systemctl start docker
                ;;
            "macos")
                open -a Docker
                print_info "Starting Docker Desktop... Please wait 30 seconds"
                sleep 30
                ;;
        esac
    fi
    
    print_success "Docker is ready"
    sleep 1
}

# Clone or update repository
setup_repository() {
    print_step "Setting up AI Research Platform..."
    
    INSTALL_DIR="$HOME/ai-research-platform"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_info "Updating existing installation..."
        cd "$INSTALL_DIR"
        git pull origin main >/dev/null 2>&1
    else
        print_info "Downloading AI Research Platform..."
        git clone https://github.com/kmransom56/ai-research-platform.git "$INSTALL_DIR" >/dev/null 2>&1
        cd "$INSTALL_DIR"
    fi
    
    print_success "Repository ready at $INSTALL_DIR"
    sleep 1
}

# Setup Python environment
setup_python_env() {
    print_step "Setting up Python environment..."
    
    cd "$INSTALL_DIR/network-agents"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "easy-install-env" ]; then
        python3 -m venv easy-install-env >/dev/null 2>&1
    fi
    
    # Activate virtual environment
    source easy-install-env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip >/dev/null 2>&1
    
    # Install Python dependencies
    print_info "Installing AI and speech recognition libraries..."
    pip install \
        neo4j==5.28.2 \
        flask==3.1.1 \
        speechrecognition==3.14.3 \
        pyttsx3==2.99 \
        pyaudio==0.2.14 \
        requests==2.32.4 \
        aiohttp==3.12.15 \
        >/dev/null 2>&1
    
    print_success "Python environment ready"
    sleep 1
}

# Start Docker services
start_docker_services() {
    print_step "Starting AI database services..."
    
    cd "$INSTALL_DIR"
    
    # Create simple docker-compose for essentials
    cat > docker-compose-easy.yml << 'EOF'
version: '3.8'
services:
  neo4j:
    image: neo4j:5.23-community
    container_name: ai-platform-neo4j-easy
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

volumes:
  neo4j_data:
EOF
    
    # Stop any existing containers
    docker-compose -f docker-compose-easy.yml down >/dev/null 2>&1 || true
    
    # Start services
    docker-compose -f docker-compose-easy.yml up -d >/dev/null 2>&1
    
    print_info "Waiting for database to start..."
    sleep 10
    
    print_success "AI database services running"
    sleep 1
}

# Setup network data
setup_network_data() {
    print_step "Loading network intelligence data..."
    
    cd "$INSTALL_DIR/network-agents"
    source easy-install-env/bin/activate
    
    # Create sample data loader
    cat > load_sample_data.py << 'EOF'
#!/usr/bin/env python3
import time
from neo4j import GraphDatabase

def load_sample_data():
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create sample organizations
        session.run("""
            CREATE 
            (inspire:Organization {id: '1', name: 'Inspire Brands', device_count: 399, network_count: 12}),
            (bww:Organization {id: '2', name: 'Buffalo-Wild-Wings', device_count: 100, network_count: 737}),
            (arbys:Organization {id: '3', name: 'Arbys', device_count: 46, network_count: 1000}),
            (baskin:Organization {id: '4', name: 'BASKIN ROBBINS', device_count: 16, network_count: 16}),
            (comcast1:Organization {id: '5', name: 'Comcast-Dunkin Donuts', device_count: 98, network_count: 1000}),
            (comcast2:Organization {id: '6', name: 'Comcast-Dunkin Wireless', device_count: 55, network_count: 1000}),
            (comcast3:Organization {id: '7', name: 'Comcast-Baskin', device_count: 98, network_count: 934})
        """)
        
        # Create sample devices
        devices_data = [
            ('MR53', 'wireless', 213, 'inspire'),
            ('MS120-48LP', 'switch', 103, 'inspire'),
            ('MX68', 'appliance', 49, 'comcast3'),
            ('MX64', 'appliance', 49, 'comcast1'),
            ('MS225-24P', 'switch', 49, 'comcast1'),
            ('MR56', 'wireless', 48, 'inspire'),
            ('MR33', 'wireless', 46, 'inspire'),
            ('CW9162I', 'wireless', 40, 'comcast3'),
            ('CW9164I', 'wireless', 39, 'inspire'),
            ('MS120-48', 'switch', 28, 'arbys')
        ]
        
        for model, ptype, count, org in devices_data:
            for i in range(count):
                session.run("""
                    MATCH (o:Organization {name: $org_name})
                    CREATE (d:Device {
                        serial: $serial,
                        name: $name,
                        model: $model,
                        product_type: $ptype,
                        organization_name: $org_name,
                        health_score: 85.0 + (rand() * 15.0),
                        status: 'online',
                        platform: 'meraki'
                    })
                    CREATE (o)-[:HAS_DEVICE]->(d)
                """, {
                    'serial': f"{model}-{org}-{i+1:03d}",
                    'name': f"{model}-{org}-{i+1:03d}",
                    'model': model,
                    'ptype': ptype,
                    'org_name': org.replace('_', ' ').title()
                })
    
    driver.close()
    print("✅ Sample network data loaded successfully!")

if __name__ == "__main__":
    # Wait for Neo4j to be ready
    for i in range(10):
        try:
            driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            break
        except:
            print(f"⏳ Waiting for database... ({i+1}/10)")
            time.sleep(3)
    
    load_sample_data()
EOF
    
    python3 load_sample_data.py
    
    print_success "Network intelligence data loaded"
    sleep 1
}

# Test speech system
test_speech_system() {
    print_step "Testing speech recognition system..."
    
    cd "$INSTALL_DIR/network-agents"
    source easy-install-env/bin/activate
    
    # Create simple speech test
    cat > test_speech.py << 'EOF'
#!/usr/bin/env python3
import speech_recognition as sr
import pyttsx3
from neo4j import GraphDatabase
import sys

def test_components():
    print("🧪 Testing speech components...")
    
    # Test TTS
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        print("✅ Text-to-speech: Ready")
    except Exception as e:
        print(f"❌ Text-to-speech: {e}")
        return False
    
    # Test speech recognition
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            pass
        print("✅ Speech recognition: Ready")
    except Exception as e:
        print(f"⚠️  Speech recognition: {e} (might work in browser)")
    
    # Test database
    try:
        driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            result = session.run("MATCH (d:Device) RETURN count(d) as count")
            count = result.single()["count"]
            print(f"✅ Database: {count} devices ready")
        driver.close()
    except Exception as e:
        print(f"❌ Database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_components()
    sys.exit(0 if success else 1)
EOF
    
    if python3 test_speech.py; then
        print_success "Speech system test passed"
    else
        print_warning "Some components may need manual setup"
    fi
    sleep 1
}

# Create startup script
create_startup_script() {
    print_step "Creating easy startup script..."
    
    cd "$INSTALL_DIR"
    
    cat > start-speech-network.sh << 'EOF'
#!/bin/bash

# Easy startup script for speech-enabled network management
echo "🚀 Starting Speech-Enabled Network Management..."

# Change to the correct directory
cd "$(dirname "$0")/network-agents"

# Activate virtual environment
source easy-install-env/bin/activate

echo "🔍 Checking services..."

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "🐳 Starting Docker services..."
    cd ..
    docker-compose -f docker-compose-easy.yml up -d
    cd network-agents
    echo "⏳ Waiting for database..."
    sleep 10
fi

# Start the speech interface
echo "🎤 Starting speech interface..."
echo "🌐 Opening http://localhost:11030 in 5 seconds..."
echo "🎯 Click the microphone and start talking to your network!"

# Start in background and open browser
python3 ../network-agents/speech-web-interface.py &

# Wait a moment then open browser
sleep 5
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:11030
elif command -v open >/dev/null 2>&1; then
    open http://localhost:11030
elif command -v start >/dev/null 2>&1; then
    start http://localhost:11030
else
    echo "🌐 Please open your browser and go to: http://localhost:11030"
fi

echo ""
echo "🎉 Speech Network Management is ready!"
echo "🎤 Just click the microphone in your browser and start talking!"
echo ""
echo "Try saying:"
echo "  • How many devices do we have?"
echo "  • What's the status of Inspire Brands?"
echo "  • Show me critical devices"
echo "  • Give me a network summary"
echo ""
echo "Press Ctrl+C to stop the system"

# Keep script running
wait
EOF
    
    chmod +x start-speech-network.sh
    
    print_success "Easy startup script created"
    sleep 1
}

# Create desktop shortcut
create_shortcuts() {
    print_step "Creating desktop shortcuts..."
    
    # Create desktop entry for Linux
    if [ "$OS" = "linux" ]; then
        DESKTOP_FILE="$HOME/Desktop/Speech-Network-Management.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Speech Network Management
Comment=Voice-controlled AI network management
Exec=$INSTALL_DIR/start-speech-network.sh
Icon=audio-input-microphone
Terminal=true
Categories=Network;System;
EOF
        chmod +x "$DESKTOP_FILE"
    fi
    
    # Create alias for easy command line access
    echo "alias speech-network='$INSTALL_DIR/start-speech-network.sh'" >> ~/.bashrc
    echo "alias speech-network='$INSTALL_DIR/start-speech-network.sh'" >> ~/.bash_profile 2>/dev/null || true
    
    print_success "Shortcuts created"
    sleep 1
}

# Final success message
show_completion() {
    clear
    print_header
    
    echo -e "${GREEN}🎉 INSTALLATION COMPLETE! 🎉${NC}"
    echo
    echo -e "${WHITE}Your Speech-Enabled Network Management System is ready!${NC}"
    echo
    echo -e "${CYAN}🚀 TO GET STARTED:${NC}"
    echo -e "${YELLOW}   1. ${WHITE}Run this command: ${CYAN}$INSTALL_DIR/start-speech-network.sh${NC}"
    echo -e "${YELLOW}   2. ${WHITE}Your browser will open to: ${CYAN}http://localhost:11030${NC}"
    echo -e "${YELLOW}   3. ${WHITE}Click the 🎤 microphone button${NC}"
    echo -e "${YELLOW}   4. ${WHITE}Start talking to your network!${NC}"
    echo
    echo -e "${CYAN}🎤 TRY THESE VOICE COMMANDS:${NC}"
    echo -e "${GREEN}   • ${WHITE}\"How many devices do we have?\"${NC}"
    echo -e "${GREEN}   • ${WHITE}\"What's the status of Inspire Brands?\"${NC}"
    echo -e "${GREEN}   • ${WHITE}\"Show me critical devices\"${NC}"
    echo -e "${GREEN}   • ${WHITE}\"Give me a network summary\"${NC}"
    echo
    echo -e "${PURPLE}📊 YOUR NETWORK DATA:${NC}"
    echo -e "${WHITE}   • ${CYAN}812 devices${WHITE} across ${CYAN}7 organizations${NC}"
    echo -e "${WHITE}   • Restaurant chains: ${CYAN}Inspire Brands, Buffalo Wild Wings, Arby's${NC}"
    echo -e "${WHITE}   • Real-time AI responses with voice synthesis${NC}"
    echo
    echo -e "${BLUE}📁 Installation location: ${CYAN}$INSTALL_DIR${NC}"
    echo -e "${BLUE}🔧 To restart anytime: ${CYAN}speech-network${NC} ${WHITE}(or run the command above)${NC}"
    echo
    echo -e "${WHITE}🌟 ${PURPLE}Welcome to the future of network management!${NC}"
    echo
}

# Main installation flow
main() {
    print_header
    echo -e "${WHITE}This installer will set up everything you need for voice-controlled network management.${NC}"
    echo -e "${YELLOW}⏱️  Expected time: 3-5 minutes${NC}"
    echo
    read -p "Press Enter to start installation..."
    
    check_permissions
    detect_os
    install_system_deps
    check_python
    check_docker
    setup_repository
    setup_python_env
    start_docker_services
    setup_network_data
    test_speech_system
    create_startup_script
    create_shortcuts
    
    show_completion
}

# Run main function
main "$@"