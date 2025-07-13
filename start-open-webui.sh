#!/bin/bash

# Open WebUI Startup Script - AI Platform Integration
# This script integrates with the AI Research Platform structure
# Part of: AI Research Platform - Complete Stack

# Configuration - matching platform standards
WEBUI_HOST="100.123.10.72"
WEBUI_PORT="11880" # Within platform's 11000-12000 range
VENV_PATH="/home/keith/venv"
WORK_DIR="/home/keith/chat-copilot"
SERVICE_NAME="ai-platform-open-webui"

# Colors for output - matching platform style
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as the correct user
if [ "$USER" != "keith" ]; then
    print_error "This script should be run as user 'keith'"
    exit 1
fi

# Change to working directory
cd "$WORK_DIR" || {
    print_error "Failed to change to working directory: $WORK_DIR"
    exit 1
}

print_status "Starting Open WebUI startup sequence..."

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    print_error "Virtual environment not found at: $VENV_PATH"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_PATH/bin/activate" || {
    print_error "Failed to activate virtual environment"
    exit 1
}

# Check if Open WebUI is installed
if ! command -v open-webui &>/dev/null; then
    print_error "Open WebUI is not installed in the virtual environment"
    exit 1
fi

# Check if Open WebUI is already running
if pgrep -f "open-webui serve" >/dev/null; then
    print_warning "Open WebUI appears to be already running"
    print_status "Current Open WebUI processes:"
    ps aux | grep "open-webui serve" | grep -v grep

    # Check if it's running as a systemd service
    if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
        print_status "Open WebUI is running as systemd service: $SERVICE_NAME"
        print_status "Use './manage-open-webui.sh' to manage the service"
        print_status "Or use 'sudo systemctl stop $SERVICE_NAME' to stop it first"
        exit 0
    fi

    read -p "Do you want to restart Open WebUI? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping existing Open WebUI processes..."
        pkill -f "open-webui serve"
        sleep 3
    else
        print_status "Keeping existing Open WebUI processes running"
        exit 0
    fi
fi

# Start Open WebUI
print_status "Starting Open WebUI on $WEBUI_HOST:$WEBUI_PORT..."
nohup open-webui serve --host "$WEBUI_HOST" --port "$WEBUI_PORT" >/tmp/open-webui.log 2>&1 &

# Wait a moment for startup
sleep 5

# Check if the service started successfully
if curl -s "http://$WEBUI_HOST:$WEBUI_PORT/" >/dev/null; then
    print_status "✅ Open WebUI started successfully!"
    print_status "🌐 Access it at: http://$WEBUI_HOST:$WEBUI_PORT/"
    print_status "📋 Logs available at: /tmp/open-webui.log"
else
    print_error "❌ Failed to start Open WebUI or service is not responding"
    print_error "Check the logs at: /tmp/open-webui.log"
    exit 1
fi

print_status "Startup sequence completed!"
