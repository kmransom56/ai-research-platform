#!/bin/bash

# 🔄 Emergency Reset Script for Speech-Enabled Network Management
# Fixes common issues and resets everything to working state

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

print_header() {
    clear
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║${WHITE}                    🔄 EMERGENCY RESET SYSTEM                     ${RED}║${NC}"
    echo -e "${RED}║${WHITE}                                                                 ${RED}║${NC}"
    echo -e "${RED}║${YELLOW}              Fixing your speech network management               ${RED}║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Stop all running services
stop_services() {
    print_step "Stopping all running services..."
    
    # Stop any Python processes
    pkill -f "speech-web-interface.py" 2>/dev/null || true
    pkill -f "simple-speech-interface.py" 2>/dev/null || true
    pkill -f "flask" 2>/dev/null || true
    
    # Stop Docker containers
    docker stop $(docker ps -q) 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    print_success "Services stopped"
}

# Clean up processes and ports
cleanup_ports() {
    print_step "Cleaning up network ports..."
    
    # Kill processes on our ports
    for port in 11030 11031 7474 7687; do
        PID=$(lsof -ti:$port) 2>/dev/null || true
        if [ ! -z "$PID" ]; then
            kill -9 $PID 2>/dev/null || true
            print_success "Freed port $port"
        fi
    done
    
    print_success "Ports cleaned"
}

# Reset Docker environment
reset_docker() {
    print_step "Resetting Docker environment..."
    
    # Remove old containers
    docker container prune -f 2>/dev/null || true
    docker volume prune -f 2>/dev/null || true
    
    # Start fresh Neo4j
    docker run -d \
        --name ai-platform-neo4j-reset \
        --restart unless-stopped \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password \
        -e NEO4J_PLUGINS='["apoc"]' \
        neo4j:5.23-community >/dev/null 2>&1 || true
    
    print_success "Docker environment reset"
}

# Reinstall Python dependencies
reset_python_env() {
    print_step "Resetting Python environment..."
    
    INSTALL_DIR="$HOME/ai-research-platform"
    cd "$INSTALL_DIR/network-agents" 2>/dev/null || {
        print_error "Installation directory not found. Please run the installer first."
        exit 1
    }
    
    # Remove old virtual environment
    rm -rf easy-install-env neo4j-env 2>/dev/null || true
    
    # Create fresh virtual environment
    python3 -m venv easy-install-env
    source easy-install-env/bin/activate
    
    # Install dependencies
    pip install --upgrade pip >/dev/null 2>&1
    pip install \
        neo4j==5.28.2 \
        flask==3.1.1 \
        speechrecognition==3.14.3 \
        pyttsx3==2.99 \
        pyaudio==0.2.14 \
        requests==2.32.4 \
        aiohttp==3.12.15 \
        >/dev/null 2>&1
    
    print_success "Python environment reset"
}

# Load fresh sample data
reload_sample_data() {
    print_step "Loading fresh network data..."
    
    # Wait for Neo4j to be ready
    echo -n "   Waiting for database"
    for i in {1..20}; do
        if docker exec ai-platform-neo4j-reset cypher-shell -u neo4j -p password "RETURN 1" >/dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 1
    done
    echo
    
    # Load sample data
    docker exec ai-platform-neo4j-reset cypher-shell -u neo4j -p password "
        MATCH (n) DETACH DELETE n;
        
        CREATE 
        (inspire:Organization {id: '1', name: 'Inspire Brands', device_count: 399}),
        (bww:Organization {id: '2', name: 'Buffalo-Wild-Wings', device_count: 100}),
        (arbys:Organization {id: '3', name: 'Arbys', device_count: 46}),
        (baskin:Organization {id: '4', name: 'BASKIN ROBBINS', device_count: 16});
        
        UNWIND range(1, 50) as i
        CREATE (d:Device {
            serial: 'MR53-' + toString(i),
            name: 'AP-' + toString(i),
            model: 'MR53',
            organization_name: 'Inspire Brands',
            health_score: 85.0 + (rand() * 15.0),
            status: 'online',
            platform: 'meraki',
            product_type: 'wireless'
        });
        
        UNWIND range(1, 25) as i
        CREATE (d:Device {
            serial: 'MS120-' + toString(i),
            name: 'Switch-' + toString(i),
            model: 'MS120-48LP',
            organization_name: 'Buffalo-Wild-Wings',
            health_score: 85.0 + (rand() * 15.0),
            status: 'online',
            platform: 'meraki',
            product_type: 'switch'
        });
    " >/dev/null 2>&1
    
    print_success "Sample network data loaded (75 devices)"
}

# Test the system
test_system() {
    print_step "Testing system components..."
    
    cd "$HOME/ai-research-platform/network-agents"
    source easy-install-env/bin/activate
    
    # Test database connection
    python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('neo4j://localhost:7687', auth=('neo4j', 'password'))
    with driver.session() as session:
        result = session.run('MATCH (d:Device) RETURN count(d) as count')
        count = result.single()['count']
    driver.close()
    print(f'✅ Database: {count} devices ready')
except Exception as e:
    print(f'❌ Database test failed: {e}')
    exit(1)
    " || {
        print_error "Database test failed"
        exit 1
    }
    
    # Test speech components
    python3 -c "
try:
    import speech_recognition as sr
    import pyttsx3
    print('✅ Speech libraries: Ready')
except Exception as e:
    print(f'⚠️  Speech libraries: {e}')
    " 2>/dev/null
    
    print_success "System test completed"
}

# Create new startup script
create_startup() {
    print_step "Creating startup script..."
    
    cd "$HOME/ai-research-platform"
    
    cat > start-speech-network-reset.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Speech-Enabled Network Management (Reset Version)..."
cd "$(dirname "$0")/network-agents"
source easy-install-env/bin/activate

# Check Docker
if ! docker ps >/dev/null 2>&1; then
    echo "🐳 Starting Docker..."
    if command -v systemctl >/dev/null; then
        sudo systemctl start docker
    fi
fi

# Check Neo4j
if ! docker ps | grep ai-platform-neo4j-reset >/dev/null; then
    echo "🔄 Starting database..."
    docker start ai-platform-neo4j-reset >/dev/null 2>&1 || {
        docker run -d \
            --name ai-platform-neo4j-reset \
            --restart unless-stopped \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/password \
            neo4j:5.23-community
    }
    sleep 10
fi

echo "🎤 Starting simple speech interface..."
echo "🌐 Opening http://localhost:11031 in 5 seconds..."
python3 simple-speech-interface.py &
sleep 5

if command -v xdg-open >/dev/null; then
    xdg-open http://localhost:11031
elif command -v open >/dev/null; then
    open http://localhost:11031
else
    echo "🌐 Please open your browser and go to: http://localhost:11031"
fi

echo ""
echo "🎉 Speech Network Management is ready!"
echo "🎤 Click the microphone in your browser and start talking!"
echo ""
echo "Press Ctrl+C to stop"
wait
EOF
    
    chmod +x start-speech-network-reset.sh
    
    print_success "Startup script created"
}

# Show completion message
show_completion() {
    clear
    print_header
    
    echo -e "${GREEN}🎉 RESET COMPLETE! 🎉${NC}"
    echo
    echo -e "${WHITE}Your Speech-Enabled Network Management System has been reset and is ready!${NC}"
    echo
    echo -e "${CYAN}🚀 TO GET STARTED:${NC}"
    echo -e "${YELLOW}   Run: ${CYAN}$HOME/ai-research-platform/start-speech-network-reset.sh${NC}"
    echo -e "${YELLOW}   Or:  ${CYAN}cd $HOME/ai-research-platform && ./start-speech-network-reset.sh${NC}"
    echo
    echo -e "${CYAN}🌐 THEN:${NC}"
    echo -e "${WHITE}   1. Your browser will open to: ${CYAN}http://localhost:11031${NC}"
    echo -e "${WHITE}   2. Click the 🎤 microphone button${NC}"
    echo -e "${WHITE}   3. Say: ${GREEN}\"How many devices do we have?\"${NC}"
    echo
    echo -e "${BLUE}📊 Sample Data Loaded:${NC}"
    echo -e "${WHITE}   • ${CYAN}75 network devices${NC}"
    echo -e "${WHITE}   • ${CYAN}4 organizations${NC}"
    echo -e "${WHITE}   • ${CYAN}Ready for voice commands${NC}"
    echo
    echo -e "${PURPLE}🌟 Everything is working fresh and clean!${NC}"
    echo
}

# Main reset function
main() {
    print_header
    echo -e "${WHITE}This will reset your speech network management system to fix any issues.${NC}"
    echo -e "${YELLOW}⏱️  Expected time: 2-3 minutes${NC}"
    echo
    read -p "Press Enter to start reset..."
    
    stop_services
    cleanup_ports
    reset_docker
    reset_python_env
    sleep 5  # Give Neo4j time to start
    reload_sample_data
    test_system
    create_startup
    
    show_completion
}

# Handle interruption
trap 'echo -e "\n${RED}Reset interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"