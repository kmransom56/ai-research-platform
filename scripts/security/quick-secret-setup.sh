#!/bin/bash

# =============================================================================
# Quick GitHub Secrets Setup Script
# =============================================================================
# This script helps you quickly set up the most critical GitHub repository 
# secrets after key rotation.
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Check GitHub CLI
if ! command -v gh &> /dev/null || ! gh auth status &> /dev/null; then
    print_error "GitHub CLI not available or not authenticated"
    echo "Install and authenticate: https://cli.github.com/"
    exit 1
fi

echo
echo "🔐 QUICK GITHUB SECRETS SETUP"
echo "==============================="
echo

# Essential secrets for platform operation
declare -A secrets=(
    ["OPENAI_API_KEY"]="OpenAI API key (starts with sk-)"
    ["NEO4J_PASSWORD"]="Neo4j database password"
    ["DB_PASSWORD"]="PostgreSQL database password"
    ["ANTHROPIC_API_KEY"]="Anthropic Claude API key (optional)"
    ["AZURE_OPENAI_KEY"]="Azure OpenAI service key (optional)"
)

# Function to set a secret
set_secret() {
    local key="$1"
    local description="$2"
    
    echo
    print_status "Setting up: $key"
    echo "Description: $description"
    
    # Check if secret already exists
    if gh secret list | grep -q "^$key"; then
        read -p "Secret '$key' already exists. Update it? (y/N): " update
        if [[ ! "$update" =~ ^[Yy]$ ]]; then
            print_warning "Skipping $key"
            return
        fi
    fi
    
    # Get secret value
    read -s -p "Enter value for $key: " secret_value
    echo
    
    if [ -z "$secret_value" ]; then
        print_warning "Empty value. Skipping $key"
        return
    fi
    
    # Set the secret
    if gh secret set "$key" --body "$secret_value"; then
        print_status "✅ Set $key"
    else
        print_error "❌ Failed to set $key"
    fi
}

# Main setup process
main() {
    print_status "Setting up essential GitHub repository secrets..."
    echo
    
    # Set core secrets
    for key in "${!secrets[@]}"; do
        set_secret "$key" "${secrets[$key]}"
    done
    
    echo
    echo "=============================================="
    echo "✅ SECRETS SETUP COMPLETE"
    echo "=============================================="
    echo
    
    # Show current secrets
    print_status "Current repository secrets:"
    gh secret list
    
    echo
    echo "📋 NEXT STEPS:"
    echo "1. Test deployment: docker compose -f docker-compose.portable.yml up -d"
    echo "2. Check application health: curl -f http://localhost:11000/healthz"
    echo "3. Verify Neo4j access: curl -f http://localhost:7474"
    echo
    print_warning "Remember to rotate these secrets regularly (every 90 days recommended)"
}

main "$@"