#!/bin/bash
"""
GitHub Repository Secrets Setup Guide and Helper Script
For AI Research Platform Secret Management

This script helps you set up GitHub repository secrets for automated secret management.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\).*/\1/')}"
REPO_NAME="${GITHUB_REPOSITORY_NAME:-$(git config --get remote.origin.url | sed 's/.*\/\([^/]*\)\.git$/\1/')}"

echo -e "${BLUE}🔐 GitHub Secrets Setup for AI Research Platform${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""
echo -e "Repository: ${YELLOW}${REPO_OWNER}/${REPO_NAME}${NC}"
echo ""

# Function to check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
        echo -e "${YELLOW}Please install it from: https://cli.github.com/${NC}"
        exit 1
    fi
    
    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI is not authenticated.${NC}"
        echo -e "${YELLOW}Please run: gh auth login${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"
}

# Function to set a secret
set_secret() {
    local secret_name="$1"
    local secret_description="$2"
    local example_value="$3"
    
    echo ""
    echo -e "${BLUE}Setting up: ${YELLOW}${secret_name}${NC}"
    echo -e "Description: ${secret_description}"
    
    if [ -n "$example_value" ]; then
        echo -e "Example: ${example_value}"
    fi
    
    echo ""
    read -p "Enter value for ${secret_name} (or 'skip' to skip): " -s secret_value
    echo ""
    
    if [ "$secret_value" = "skip" ]; then
        echo -e "${YELLOW}⏭️  Skipped ${secret_name}${NC}"
        return
    fi
    
    if [ -z "$secret_value" ]; then
        echo -e "${YELLOW}⚠️  Empty value for ${secret_name}, skipping${NC}"
        return
    fi
    
    # Set the secret using GitHub CLI
    if echo "$secret_value" | gh secret set "$secret_name" --repo "${REPO_OWNER}/${REPO_NAME}"; then
        echo -e "${GREEN}✅ Successfully set ${secret_name}${NC}"
    else
        echo -e "${RED}❌ Failed to set ${secret_name}${NC}"
    fi
}

# Function to list existing secrets
list_secrets() {
    echo -e "${BLUE}📋 Current Repository Secrets:${NC}"
    echo ""
    
    if gh secret list --repo "${REPO_OWNER}/${REPO_NAME}" 2>/dev/null; then
        echo ""
    else
        echo -e "${YELLOW}No secrets found or unable to access secrets.${NC}"
        echo ""
    fi
}

# Function to generate random passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Main setup function
setup_secrets() {
    echo -e "${BLUE}Setting up required secrets for AI Research Platform...${NC}"
    echo ""
    
    # AI Service API Keys
    echo -e "${BLUE}🤖 AI Service API Keys${NC}"
    echo -e "${BLUE}=====================${NC}"
    
    set_secret "OPENAI_API_KEY" "OpenAI API key for GPT models" "sk-..."
    set_secret "ANTHROPIC_API_KEY" "Anthropic API key for Claude models" "sk-ant-api03-..."
    set_secret "AZURE_OPENAI_KEY" "Azure OpenAI service key" "your-azure-key"
    set_secret "GEMINI_API_KEY" "Google Gemini API key" "AIza..."
    set_secret "GOOGLE_API_KEY" "Google Cloud API key" "AIza..."
    set_secret "LANGCHAIN_API_KEY" "LangChain API key" "your-langchain-key"
    
    # Database Credentials
    echo ""
    echo -e "${BLUE}🗄️  Database Credentials${NC}"
    echo -e "${BLUE}========================${NC}"
    
    neo4j_password=$(generate_password)
    postgres_password=$(generate_password)
    
    set_secret "NEO4J_USERNAME" "Neo4j database username" "neo4j"
    echo "$neo4j_password" | gh secret set "NEO4J_PASSWORD" --repo "${REPO_OWNER}/${REPO_NAME}"
    echo -e "${GREEN}✅ Generated and set NEO4J_PASSWORD${NC}"
    
    echo "$postgres_password" | gh secret set "POSTGRES_PASSWORD" --repo "${REPO_OWNER}/${REPO_NAME}"
    echo -e "${GREEN}✅ Generated and set POSTGRES_PASSWORD${NC}"
    
    # Message Queue Credentials
    echo ""
    echo -e "${BLUE}📨 Message Queue Credentials${NC}"
    echo -e "${BLUE}=============================${NC}"
    
    rabbitmq_password=$(generate_password)
    echo "$rabbitmq_password" | gh secret set "RABBITMQ_PASSWORD" --repo "${REPO_OWNER}/${REPO_NAME}"
    echo -e "${GREEN}✅ Generated and set RABBITMQ_PASSWORD${NC}"
    
    set_secret "RABBITMQ_USER" "RabbitMQ username" "admin"
    
    # Application Secrets
    echo ""
    echo -e "${BLUE}🔧 Application Secrets${NC}"
    echo -e "${BLUE}======================${NC}"
    
    openwebui_secret=$(generate_password)
    vscode_password=$(generate_password)
    
    echo "$openwebui_secret" | gh secret set "OPENWEBUI_SECRET_KEY" --repo "${REPO_OWNER}/${REPO_NAME}"
    echo -e "${GREEN}✅ Generated and set OPENWEBUI_SECRET_KEY${NC}"
    
    echo "$vscode_password" | gh secret set "VSCODE_PASSWORD" --repo "${REPO_OWNER}/${REPO_NAME}"
    echo -e "${GREEN}✅ Generated and set VSCODE_PASSWORD${NC}"
    
    # GitHub Integration
    echo ""
    echo -e "${BLUE}🐙 GitHub Integration${NC}"
    echo -e "${BLUE}====================${NC}"
    
    set_secret "GITHUB_TOKEN" "GitHub personal access token" "ghp_..."
}

# Function to validate secrets
validate_secrets() {
    echo -e "${BLUE}🔍 Validating secrets setup...${NC}"
    echo ""
    
    required_secrets=(
        "OPENAI_API_KEY"
        "NEO4J_PASSWORD"
        "NEO4J_USERNAME"
        "POSTGRES_PASSWORD"
        "RABBITMQ_PASSWORD"
        "RABBITMQ_USER"
        "OPENWEBUI_SECRET_KEY"
        "VSCODE_PASSWORD"
    )
    
    missing_secrets=()
    
    for secret in "${required_secrets[@]}"; do
        if gh secret list --repo "${REPO_OWNER}/${REPO_NAME}" | grep -q "$secret"; then
            echo -e "${GREEN}✅ ${secret}${NC}"
        else
            echo -e "${RED}❌ ${secret}${NC}"
            missing_secrets+=("$secret")
        fi
    done
    
    if [ ${#missing_secrets[@]} -eq 0 ]; then
        echo ""
        echo -e "${GREEN}🎉 All required secrets are configured!${NC}"
        return 0
    else
        echo ""
        echo -e "${YELLOW}⚠️  Missing secrets: ${missing_secrets[*]}${NC}"
        return 1
    fi
}

# Function to show usage instructions
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     - Set up all required secrets interactively"
    echo "  list      - List current repository secrets"
    echo "  validate  - Validate that all required secrets are present"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup       # Interactive setup of all secrets"
    echo "  $0 list        # Show current secrets"
    echo "  $0 validate    # Check if all required secrets exist"
}

# Main script logic
case "${1:-setup}" in
    "setup")
        check_gh_cli
        list_secrets
        setup_secrets
        echo ""
        validate_secrets
        echo ""
        echo -e "${BLUE}📚 Next Steps:${NC}"
        echo "1. Run the secret scanner: python3 scripts/security/secret-scanner.py"
        echo "2. Test the secret replacement: python3 scripts/security/secret-replacer.py --dry-run"
        echo "3. Commit and push to trigger GitHub Actions workflows"
        echo ""
        ;;
    "list")
        check_gh_cli
        list_secrets
        ;;
    "validate")
        check_gh_cli
        validate_secrets
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac