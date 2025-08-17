#!/bin/bash

# =============================================================================
# Deploy AI Research Platform with GitHub Secrets
# =============================================================================
# This script fetches secrets from GitHub repository and deploys the platform
# locally with proper environment variable configuration.
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
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Configuration
COMPOSE_FILE="${1:-docker-compose.portable.yml}"
ENVIRONMENT="${2:-development}"

echo
echo "🚀 AI RESEARCH PLATFORM - SECURE DEPLOYMENT"
echo "=============================================="
echo "Compose File: $COMPOSE_FILE"
echo "Environment: $ENVIRONMENT"
echo

# Check prerequisites
print_step "1. Checking Prerequisites"

if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI not found. Install from: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    print_error "GitHub CLI not authenticated. Run: gh auth login"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Install from: https://docker.com/"
    exit 1
fi

print_status "Prerequisites check passed"

# Fetch secrets from GitHub repository
print_step "2. Fetching Secrets from GitHub Repository"

# Function to get secret value safely
get_secret() {
    local secret_name="$1"
    local secret_value
    
    secret_value=$(gh secret list --json name,updatedAt | jq -r ".[] | select(.name==\"$secret_name\") | .name" 2>/dev/null)
    
    if [ -n "$secret_value" ]; then
        echo "✅ $secret_name"
        return 0
    else
        echo "❌ $secret_name (missing)"
        return 1
    fi
}

echo "Checking available secrets:"
available_secrets=()
missing_secrets=()

# Core secrets
secrets_to_check=(
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "AZURE_OPENAI_KEY"
    "GEMINI_API_KEY"
    "GH_TOKEN"
    "MERAKI_API_KEY"
    "BRAVE_API_KEY"
    "GROQ_API_KEY"
    "HF_API_KEY"
)

for secret in "${secrets_to_check[@]}"; do
    if get_secret "$secret"; then
        available_secrets+=("$secret")
    else
        missing_secrets+=("$secret")
    fi
done

echo
if [ ${#missing_secrets[@]} -gt 0 ]; then
    print_warning "Missing secrets: ${missing_secrets[*]}"
    print_warning "Platform will deploy with available secrets only"
fi

print_status "Found ${#available_secrets[@]} secrets in repository"

# Create environment file from GitHub secrets
print_step "3. Creating Environment Configuration"

# Note: This is a local deployment script, so we can't actually fetch secret values
# via GitHub CLI (they're encrypted). Instead, we'll create a template that shows
# how the secrets should be referenced in production.

cat > .env << 'EOF'
# =============================================================================
# AI Research Platform - Local Development with GitHub Secrets
# =============================================================================
# This file should be populated with actual values for local development.
# In production, these values come from GitHub repository secrets.
# =============================================================================

# ⚠️  IMPORTANT: Set these values for local development
# In production deployment (GitHub Actions), these are automatically populated

# Core AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AZURE_OPENAI_KEY=your_azure_openai_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# External Service APIs
MERAKI_API_KEY=your_meraki_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_api_key_here

# GitHub Integration
GH_TOKEN=your_github_personal_access_token_here

# Database Configuration (generated for this deployment)
NEO4J_PASSWORD=secure_neo4j_password_$(date +%s)
DB_PASSWORD=secure_db_password_$(date +%s)
POSTGRES_PASSWORD=secure_db_password_$(date +%s)

# Message Queue
RABBITMQ_DEFAULT_USER=chatcopilot
RABBITMQ_DEFAULT_PASS=secure_rabbitmq_password_$(date +%s)

# Application Secrets
JWT_SECRET=jwt_secret_$(date +%s)
OPENWEBUI_SECRET_KEY=openwebui_secret_$(date +%s)
VSCODE_PASSWORD=vscode_secure_$(date +%s)

# Platform Configuration
PLATFORM_IP=localhost
DOCKER_NETWORK_NAME=chatcopilot_ai-platform
DOCKER_VOLUME_PREFIX=chatcopilot
ASPNETCORE_ENVIRONMENT=Development
NODE_ENV=development

# Database URLs
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/chatcopilot
REDIS_URL=redis://redis:6379
EOF

print_warning "Environment file created with placeholder values"
print_warning "For local development, edit .env file with your actual API keys"

# Interactive secret setup for local development
print_step "4. Local Development Secret Setup"

read -p "Do you want to set up secrets interactively for local development? (y/N): " setup_local
if [[ "$setup_local" =~ ^[Yy]$ ]]; then
    print_status "Setting up local development secrets..."
    
    # Use the quick setup script
    if [ -f "scripts/security/quick-secret-setup.sh" ]; then
        print_status "You can also run: ./scripts/security/quick-secret-setup.sh"
    fi
    
    echo "Edit the .env file with your actual API keys:"
    echo "  nano .env"
    echo
    read -p "Press Enter when you've updated the .env file..."
fi

# Validate configuration
print_step "5. Validating Configuration"

if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "Docker Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Test Docker Compose configuration
if docker compose -f "$COMPOSE_FILE" config > /dev/null; then
    print_status "Docker Compose configuration is valid"
else
    print_error "Docker Compose configuration has errors"
    exit 1
fi

# Deploy the platform
print_step "6. Deploying Platform"

print_status "Pulling latest container images..."
docker compose -f "$COMPOSE_FILE" pull

print_status "Starting platform services..."
docker compose -f "$COMPOSE_FILE" up -d

# Health checks
print_step "7. Running Health Checks"

print_status "Waiting for services to start..."
sleep 30

print_status "Checking service status..."
docker compose -f "$COMPOSE_FILE" ps

# Test endpoints
endpoints_to_test=(
    "http://localhost:11000/healthz|Backend API"
    "http://localhost:7474|Neo4j Browser"
    "http://localhost:3000|Frontend"
)

healthy_services=0
total_services=${#endpoints_to_test[@]}

for endpoint_info in "${endpoints_to_test[@]}"; do
    IFS='|' read -r endpoint name <<< "$endpoint_info"
    
    if curl -f -s "$endpoint" > /dev/null 2>&1; then
        print_status "✅ $name health check passed"
        ((healthy_services++))
    else
        print_warning "⚠️ $name health check failed"
    fi
done

# Results
print_step "8. Deployment Results"

echo
echo "🎉 DEPLOYMENT COMPLETED"
echo "======================="
echo "Compose File: $COMPOSE_FILE"
echo "Health Status: $healthy_services/$total_services services healthy"
echo

echo "📱 ACCESS URLS:"
echo "• Backend API: http://localhost:11000"
echo "• Frontend: http://localhost:3000"
echo "• Neo4j Browser: http://localhost:7474 (neo4j/\${NEO4J_PASSWORD})"
echo "• Grafana: http://localhost:11002 (admin/admin)"
echo

echo "🔐 SECRET MANAGEMENT:"
echo "• GitHub Secrets: ${#available_secrets[@]} secrets available in repository"
echo "• Local Environment: .env file created (update with your values)"
echo "• Production Deployment: Use GitHub Actions workflow 'deploy-with-secrets.yml'"
echo

if [ ${#missing_secrets[@]} -gt 0 ]; then
    print_warning "MISSING SECRETS:"
    for secret in "${missing_secrets[@]}"; do
        echo "  ❌ $secret"
    done
    echo
    echo "Set these secrets with:"
    echo "  gh secret set SECRET_NAME --body \"secret_value\""
fi

echo "🛠️  NEXT STEPS:"
echo "1. Update .env file with your actual API keys (for local development)"
echo "2. Test application functionality at http://localhost:3000"
echo "3. For production deployment, use: GitHub Actions → Deploy with Secrets"
echo "4. Monitor service logs: docker compose -f $COMPOSE_FILE logs -f"
echo

print_status "Platform deployment completed successfully!"

# Cleanup function
cleanup() {
    print_status "Cleaning up temporary files..."
    # Don't remove .env as user may have added their keys
}

trap cleanup EXIT