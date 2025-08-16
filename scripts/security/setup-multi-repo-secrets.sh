#!/bin/bash
"""
Multi-Repository Secret Management Setup Script
Automates the setup of organization-wide secret management

This script will:
1. Discover all repositories in your organization
2. Deploy your master secrets to all repositories
3. Deploy secret management workflows to all repositories
4. Generate organization inventory report
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}🏢 Multi-Repository Secret Management Setup${NC}"
echo -e "${BLUE}=============================================${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check GitHub CLI
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) is required but not installed${NC}"
        echo "Please install it from: https://cli.github.com/"
        exit 1
    fi
    
    # Check GitHub authentication
    if ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI is not authenticated${NC}"
        echo "Please run: gh auth login"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Function to get organization info
get_organization_info() {
    echo -e "${BLUE}🏢 Getting organization information...${NC}"
    
    # Get current user
    CURRENT_USER=$(gh api user --jq '.login')
    echo "Current user: ${CURRENT_USER}"
    
    # List organizations
    ORGS=$(gh api user/orgs --jq '.[].login' 2>/dev/null || echo "")
    
    if [ -n "$ORGS" ]; then
        echo ""
        echo "Available organizations:"
        echo "$ORGS" | nl -w2 -s') '
        echo ""
        read -p "Select organization (number) or press Enter for personal repositories: " ORG_CHOICE
        
        if [ -n "$ORG_CHOICE" ] && [ "$ORG_CHOICE" -gt 0 ]; then
            OWNER=$(echo "$ORGS" | sed -n "${ORG_CHOICE}p")
            OWNER_TYPE="org"
        else
            OWNER="$CURRENT_USER"
            OWNER_TYPE="user"
        fi
    else
        OWNER="$CURRENT_USER"
        OWNER_TYPE="user"
    fi
    
    echo -e "Using ${YELLOW}${OWNER_TYPE}: ${OWNER}${NC}"
    export OWNER_TYPE OWNER
}

# Function to discover repositories
discover_repositories() {
    echo -e "${BLUE}🔍 Discovering repositories...${NC}"
    
    python3 "$SCRIPT_DIR/multi-repo-secret-manager.py" \
        --owner-type "$OWNER_TYPE" \
        --owner "$OWNER" \
        discover --include-forks > /tmp/repo-discovery.json
    
    REPO_COUNT=$(cat /tmp/repo-discovery.json | tail -1 | grep -o '[0-9]\+' | head -1)
    echo -e "${GREEN}📊 Found ${REPO_COUNT} repositories${NC}"
    
    # Show repository breakdown
    echo ""
    echo -e "${BLUE}📋 Repository Breakdown:${NC}"
    head -20 /tmp/repo-discovery.json
    
    if [ "$REPO_COUNT" -gt 20 ]; then
        echo "... (showing first 20 repositories)"
    fi
    
    echo ""
    read -p "Continue with deployment to all ${REPO_COUNT} repositories? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
}

# Function to setup master secrets
setup_master_secrets() {
    echo -e "${BLUE}🔐 Setting up master secrets...${NC}"
    
    SECRETS_FILE="$PROJECT_DIR/github_secrets.txt.converted"
    
    if [ ! -f "$SECRETS_FILE" ]; then
        echo -e "${YELLOW}⚠️  Master secrets file not found: $SECRETS_FILE${NC}"
        echo ""
        echo "Please ensure you have a secrets file. You can:"
        echo "1. Use the existing converted file: github_secrets.txt.converted"
        echo "2. Create a new one with: python3 scripts/security/bulk-import-secrets.py --create-template my-secrets.txt"
        echo ""
        read -p "Enter path to your secrets file: " CUSTOM_SECRETS_FILE
        
        if [ -f "$CUSTOM_SECRETS_FILE" ]; then
            SECRETS_FILE="$CUSTOM_SECRETS_FILE"
        else
            echo -e "${RED}❌ Secrets file not found: $CUSTOM_SECRETS_FILE${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Using secrets file: $SECRETS_FILE${NC}"
    
    # Validate secrets file
    echo "Validating secrets file..."
    if ! python3 "$SCRIPT_DIR/bulk-import-secrets.py" "$SECRETS_FILE" --validate; then
        echo -e "${RED}❌ Secrets file validation failed${NC}"
        exit 1
    fi
    
    export SECRETS_FILE
}

# Function to deploy secrets to all repositories
deploy_secrets_bulk() {
    echo -e "${BLUE}🚀 Deploying secrets to all repositories...${NC}"
    echo ""
    echo "This will deploy your master secrets to ALL discovered repositories."
    echo "Each repository will receive the same set of secrets."
    echo ""
    read -p "Proceed with bulk deployment? (y/N): " CONFIRM_DEPLOY
    
    if [[ ! "$CONFIRM_DEPLOY" =~ ^[Yy]$ ]]; then
        echo "Skipping bulk deployment"
        return 0
    fi
    
    echo ""
    read -p "Overwrite existing secrets in repositories? (y/N): " OVERWRITE
    OVERWRITE_FLAG=""
    if [[ "$OVERWRITE" =~ ^[Yy]$ ]]; then
        OVERWRITE_FLAG="--overwrite"
    fi
    
    echo -e "${YELLOW}🔄 Starting bulk deployment...${NC}"
    
    python3 "$SCRIPT_DIR/multi-repo-secret-manager.py" \
        --owner-type "$OWNER_TYPE" \
        --owner "$OWNER" \
        --secrets-file "$SECRETS_FILE" \
        deploy $OVERWRITE_FLAG --max-workers 5
    
    echo -e "${GREEN}✅ Bulk deployment completed${NC}"
}

# Function to deploy workflows to all repositories
deploy_workflows() {
    echo -e "${BLUE}📋 Deploying secret management workflows...${NC}"
    echo ""
    echo "This will add the secret management GitHub Actions workflow to all repositories."
    echo "This enables automatic secret scanning and management in each repository."
    echo ""
    read -p "Deploy workflows to all repositories? (y/N): " CONFIRM_WORKFLOW
    
    if [[ ! "$CONFIRM_WORKFLOW" =~ ^[Yy]$ ]]; then
        echo "Skipping workflow deployment"
        return 0
    fi
    
    echo -e "${YELLOW}🔄 Deploying workflows...${NC}"
    
    python3 "$SCRIPT_DIR/multi-repo-secret-manager.py" \
        --owner-type "$OWNER_TYPE" \
        --owner "$OWNER" \
        deploy-workflow
    
    echo -e "${GREEN}✅ Workflow deployment completed${NC}"
}

# Function to generate organization inventory
generate_inventory() {
    echo -e "${BLUE}📊 Generating organization inventory...${NC}"
    
    INVENTORY_FILE="$PROJECT_DIR/organization-secret-inventory-$(date +%Y%m%d-%H%M%S).json"
    
    python3 "$SCRIPT_DIR/multi-repo-secret-manager.py" \
        --owner-type "$OWNER_TYPE" \
        --owner "$OWNER" \
        inventory --output "$INVENTORY_FILE"
    
    echo -e "${GREEN}✅ Inventory saved to: $INVENTORY_FILE${NC}"
    
    # Show summary
    echo ""
    echo -e "${BLUE}📋 Organization Summary:${NC}"
    python3 -c "
import json
with open('$INVENTORY_FILE') as f:
    data = json.load(f)

print(f'Organization: {data[\"organization\"]}')
print(f'Total Repositories: {data[\"total_repositories\"]}')
print(f'Repositories with Secrets: {data[\"repositories_with_secrets\"]}')
print(f'Total Secrets Deployed: {data[\"total_secrets_deployed\"]}')
print()

if data['recommendations']:
    print('🔍 Key Recommendations:')
    for rec in data['recommendations'][:3]:
        print(f'  • {rec[\"description\"]}')
"
}

# Function to setup organization-wide workflow
setup_org_workflow() {
    echo -e "${BLUE}🏢 Setting up organization-wide workflow...${NC}"
    echo ""
    echo "This will add the organization-wide secret management workflow to this repository."
    echo "This workflow can manage secrets across ALL repositories in your organization."
    echo ""
    read -p "Setup organization-wide workflow? (y/N): " CONFIRM_ORG_WORKFLOW
    
    if [[ ! "$CONFIRM_ORG_WORKFLOW" =~ ^[Yy]$ ]]; then
        echo "Skipping organization workflow setup"
        return 0
    fi
    
    # Copy organization workflow
    ORG_WORKFLOW="$PROJECT_DIR/.github/workflows/org-wide-secret-management.yml"
    
    if [ -f "$ORG_WORKFLOW" ]; then
        echo -e "${GREEN}✅ Organization-wide workflow already exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Organization-wide workflow not found${NC}"
        echo "Please ensure the workflow file exists at: $ORG_WORKFLOW"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}🔧 Next Steps for Organization Workflow:${NC}"
    echo "1. Commit and push the organization workflow to your repository"
    echo "2. Go to Actions tab in GitHub and manually run the workflow"
    echo "3. Choose from available actions:"
    echo "   - scan: Scan all repositories for secrets"
    echo "   - deploy-to-all: Deploy master secrets to all repositories" 
    echo "   - deploy-workflows: Deploy secret management workflows"
    echo "   - generate-inventory: Create organization inventory report"
    echo ""
    echo "The workflow will run automatically every Monday at 2 AM for security audits."
}

# Function to show completion summary
show_completion_summary() {
    echo ""
    echo -e "${GREEN}🎉 Multi-Repository Secret Management Setup Complete!${NC}"
    echo -e "${GREEN}==========================================================${NC}"
    echo ""
    echo -e "${BLUE}✅ What was completed:${NC}"
    echo "  • Discovered repositories in your organization"
    echo "  • Deployed master secrets to all repositories"
    echo "  • Added secret management workflows to repositories"  
    echo "  • Generated organization inventory report"
    echo "  • Setup organization-wide management workflow"
    echo ""
    echo -e "${BLUE}🔧 Next Steps:${NC}"
    echo "1. Review the organization inventory report"
    echo "2. Monitor GitHub Actions for workflow execution"
    echo "3. Use organization-wide workflow for ongoing management"
    echo "4. Set up scheduled secret rotation (quarterly recommended)"
    echo ""
    echo -e "${BLUE}🛠️  Available Commands:${NC}"
    echo "  # Scan specific repositories"
    echo "  python3 scripts/security/multi-repo-secret-manager.py scan --repos repo1 repo2"
    echo ""
    echo "  # Deploy specific secrets"  
    echo "  python3 scripts/security/multi-repo-secret-manager.py deploy --secrets OPENAI_API_KEY GITHUB_TOKEN"
    echo ""
    echo "  # Generate fresh inventory"
    echo "  python3 scripts/security/multi-repo-secret-manager.py inventory --output inventory.json"
    echo ""
    echo -e "${BLUE}🔐 Security Best Practices:${NC}"
    echo "  • Run organization-wide scans weekly"
    echo "  • Rotate secrets quarterly"
    echo "  • Review inventory reports monthly"
    echo "  • Monitor for new repositories and apply secret management"
    echo ""
}

# Main execution flow
main() {
    check_prerequisites
    get_organization_info
    discover_repositories
    setup_master_secrets
    deploy_secrets_bulk
    deploy_workflows
    generate_inventory
    setup_org_workflow
    show_completion_summary
}

# Handle script arguments
case "${1:-setup}" in
    "discover")
        check_prerequisites
        get_organization_info
        discover_repositories
        ;;
    "deploy")
        check_prerequisites
        get_organization_info
        setup_master_secrets
        deploy_secrets_bulk
        ;;
    "workflows")
        check_prerequisites
        get_organization_info
        deploy_workflows
        ;;
    "inventory")
        check_prerequisites
        get_organization_info
        generate_inventory
        ;;
    "setup"|*)
        main
        ;;
esac