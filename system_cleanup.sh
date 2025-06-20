#!/bin/bash
##############################################################################
# System Package Cleanup Script
# Fixes APT repository duplicates, GPG key issues, and package conflicts
##############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

##############################################################################
# 1. Fix NodeSource Repository Duplicates
##############################################################################
fix_nodesource_duplicates() {
    log "🔧 Fixing NodeSource repository duplicates..."
    
    # Check if duplicate files exist
    if [[ -f /etc/apt/sources.list.d/nodesource.list ]] && [[ -f /etc/apt/sources.list.d/nodesource.sources ]]; then
        warning "Found duplicate NodeSource repository configurations"
        
        # Backup the old format file
        sudo cp /etc/apt/sources.list.d/nodesource.list /etc/apt/sources.list.d/nodesource.list.backup
        success "Backed up nodesource.list to nodesource.list.backup"
        
        # Remove the old format file (keep the newer .sources format)
        sudo rm /etc/apt/sources.list.d/nodesource.list
        success "Removed duplicate nodesource.list file"
        
    elif [[ -f /etc/apt/sources.list.d/nodesource.list ]]; then
        success "Only nodesource.list exists - no duplicates to fix"
    elif [[ -f /etc/apt/sources.list.d/nodesource.sources ]]; then
        success "Only nodesource.sources exists - no duplicates to fix"
    else
        warning "No NodeSource repositories found"
    fi
}

##############################################################################
# 2. Fix Yarn GPG Key Issues
##############################################################################
fix_yarn_gpg() {
    log "🔧 Fixing Yarn GPG key issues..."
    
    # Check if yarn repository exists
    if [[ -f /etc/apt/sources.list.d/yarn.list ]]; then
        # Remove old GPG key from legacy keyring
        if sudo apt-key list 2>/dev/null | grep -q "yarn"; then
            warning "Found Yarn key in legacy keyring, migrating..."
            
            # Download and add the proper GPG key
            curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/yarn.gpg
            
            # Update the sources list to use the new keyring
            echo "deb [signed-by=/usr/share/keyrings/yarn.gpg] https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
            
            success "Updated Yarn GPG key to modern format"
        else
            success "Yarn GPG key already in correct format"
        fi
    else
        success "No Yarn repository found - no GPG key to fix"
    fi
}

##############################################################################
# 3. Fix .NET Package Conflicts
##############################################################################
fix_dotnet_conflicts() {
    log "🔧 Fixing .NET package conflicts..."
    
    # Check which .NET packages are installed
    if dpkg -l | grep -q "dotnet-host"; then
        warning "Found existing .NET host packages"
        
        # Show current .NET packages
        log "Current .NET packages:"
        dpkg -l | grep dotnet | awk '{print "  " $2 " - " $3}'
        
        echo
        read -p "Do you want to remove ALL existing .NET packages and do a clean install? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Remove all .NET packages
            log "Removing all existing .NET packages..."
            sudo apt remove --purge $(dpkg -l | grep dotnet | awk '{print $2}') -y
            sudo apt autoremove -y
            success "Removed all .NET packages"
            
            # Clean package cache
            sudo apt clean
            sudo apt autoclean
            
            # Update package lists
            sudo apt update
            
            # Install the specific version you want
            echo
            echo "Available .NET installation options:"
            echo "1. Install .NET 6.0 (LTS)"
            echo "2. Install .NET 8.0 (LTS)" 
            echo "3. Install .NET 9.0 (Current)"
            echo "4. Skip .NET installation"
            
            read -p "Choose option (1-4): " choice
            case $choice in
                1)
                    log "Installing .NET 6.0..."
                    sudo apt install dotnet-sdk-6.0 -y
                    success "Installed .NET 6.0"
                    ;;
                2)
                    log "Installing .NET 8.0..."
                    sudo apt install dotnet-sdk-8.0 -y
                    success "Installed .NET 8.0"
                    ;;
                3)
                    log "Installing .NET 9.0..."
                    sudo apt install dotnet-sdk-9.0 -y
                    success "Installed .NET 9.0"
                    ;;
                4)
                    warning "Skipped .NET installation"
                    ;;
                *)
                    warning "Invalid choice, skipped .NET installation"
                    ;;
            esac
        else
            warning "Skipped .NET package cleanup"
        fi
    else
        success "No .NET packages found - no conflicts to resolve"
    fi
}

##############################################################################
# 4. General System Cleanup
##############################################################################
system_cleanup() {
    log "🧹 Performing general system cleanup..."
    
    # Update package lists
    sudo apt update
    
    # Fix broken packages
    sudo apt --fix-broken install -y
    
    # Remove unnecessary packages
    sudo apt autoremove -y
    
    # Clean package cache
    sudo apt autoclean
    
    success "System cleanup completed"
}

##############################################################################
# 5. Verify System Health
##############################################################################
verify_system() {
    log "🔍 Verifying system health..."
    
    echo
    echo "=== APT Repository Status ==="
    if sudo apt update 2>&1 | grep -q "Warning\|Error"; then
        warning "Still some warnings/errors in APT"
        sudo apt update
    else
        success "APT repositories clean"
    fi
    
    echo
    echo "=== Package Status ==="
    
    # Check Node.js
    if command -v node &> /dev/null; then
        success "Node.js: $(node --version)"
    else
        warning "Node.js not installed"
    fi
    
    # Check Yarn
    if command -v yarn &> /dev/null; then
        success "Yarn: $(yarn --version)"
    else
        warning "Yarn not installed"
    fi
    
    # Check .NET
    if command -v dotnet &> /dev/null; then
        success ".NET: $(dotnet --version)"
    else
        warning ".NET not installed"
    fi
    
    echo
    echo "=== Disk Space ==="
    df -h / | tail -1 | awk '{print "Root filesystem: " $3 " used of " $2 " (" $5 " full)"}'
    
    success "System verification completed"
}

##############################################################################
# Main Execution
##############################################################################
main() {
    echo "🚀 System Package Cleanup Tool"
    echo "=============================="
    echo
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        error "Do not run this script as root! Run as regular user with sudo access."
        exit 1
    fi
    
    # Check sudo access
    if ! sudo -n true 2>/dev/null; then
        log "This script requires sudo access. You may be prompted for your password."
        sudo true
    fi
    
    echo
    log "Starting system cleanup process..."
    
    # Execute cleanup steps
    fix_nodesource_duplicates
    echo
    
    fix_yarn_gpg
    echo
    
    fix_dotnet_conflicts
    echo
    
    system_cleanup
    echo
    
    verify_system
    
    echo
    success "🎉 System cleanup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Try your package installation again"
    echo "2. If you still have issues, check the specific error messages"
    echo "3. Consider using package managers like snap or flatpak for problematic packages"
}

# Run main function
main "$@"
