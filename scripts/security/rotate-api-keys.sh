#!/bin/bash

# =============================================================================
# API Key Rotation Assistant Script
# =============================================================================
# This script provides step-by-step guidance for rotating exposed API keys
# and updating GitHub repository secrets.
#
# ⚠️  CRITICAL: This script guides you through manual rotation steps.
# The actual key revocation and generation must be done through service portals.
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if GitHub CLI is available
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed or not in PATH"
        echo "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated"
        echo "Run: gh auth login"
        exit 1
    fi
    
    print_status "GitHub CLI is ready"
}

# Function to pause for user input
wait_for_user() {
    echo
    read -p "Press Enter to continue after completing this step..."
    echo
}

# Function to update GitHub secret
update_github_secret() {
    local secret_name="$1"
    local description="$2"
    
    echo
    print_step "Updating GitHub secret: $secret_name"
    echo "Description: $description"
    echo
    read -s -p "Enter the new $secret_name: " secret_value
    echo
    
    if [ -z "$secret_value" ]; then
        print_warning "Empty value provided. Skipping $secret_name"
        return
    fi
    
    if gh secret set "$secret_name" --body "$secret_value"; then
        print_status "✅ Successfully updated $secret_name in GitHub secrets"
    else
        print_error "❌ Failed to update $secret_name"
    fi
}

# Main rotation process
main() {
    echo
    echo "🚨 API KEY ROTATION ASSISTANT"
    echo "=============================================="
    echo
    print_warning "This script will guide you through rotating ALL exposed API keys."
    print_warning "You will need access to the service provider dashboards."
    echo
    read -p "Are you ready to begin the rotation process? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Rotation cancelled."
        exit 0
    fi
    
    # Check prerequisites
    check_gh_cli
    
    echo
    echo "==============================================================================" 
    echo "🔥 PHASE 1: REVOKE EXPOSED KEYS"
    echo "=============================================================================="
    
    print_step "1.1: Revoke OpenAI API Key"
    echo "   → Go to: https://platform.openai.com/api-keys"
    echo "   → Find and DELETE the key starting with: sk-proj-6OPuDLCF4X2Jjh..."
    echo "   → This key was found in Docker containers and main .env file"
    wait_for_user
    
    print_step "1.2: Revoke Anthropic API Key"
    echo "   → Go to: https://console.anthropic.com/settings/keys"
    echo "   → Find and REVOKE the key starting with: sk-ant-api03-cen99Iv..."
    echo "   → This key was exposed in the main environment file"
    wait_for_user
    
    print_step "1.3: Revoke GitHub Personal Access Token"
    echo "   → Go to: https://github.com/settings/tokens"
    echo "   → Find and DELETE the token starting with: github_pat_11AI6SDFA0..."
    echo "   → This token had broad repository access"
    wait_for_user
    
    print_step "1.4: Revoke Azure OpenAI Key"
    echo "   → Go to: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.CognitiveServices%2Faccount"
    echo "   → Select your Cognitive Services resource"
    echo "   → Go to 'Keys and Endpoint' → Regenerate Key 1"
    echo "   → The exposed key started with: 5cg6k21wanDiscRtit..."
    wait_for_user
    
    print_step "1.5: Revoke Google API Keys"
    echo "   → Go to: https://console.cloud.google.com/apis/credentials"
    echo "   → Find and DELETE keys starting with: AIzaSyB4fISJUpD2uq... and AIzaSyAp68fLIrmdO-..."
    echo "   → These were Gemini and Maps API keys"
    wait_for_user
    
    print_step "1.6: Revoke Additional Service Keys"
    echo "   🔹 Meraki API (fd3b9969d25792d90f...): Meraki Dashboard → Organization → Settings → Dashboard API access"
    echo "   🔹 Groq API (gsk_vbotbYFfbPF2vjS...): https://console.groq.com/keys"
    echo "   🔹 Hugging Face (hf_DRpJKiiBbTQmHdq...): https://huggingface.co/settings/tokens"
    echo "   🔹 Brave Search (BSAraRLiwdxjg43P7u...): https://api.search.brave.com/app/dashboard"
    wait_for_user
    
    echo
    echo "=============================================================================="
    echo "🔑 PHASE 2: GENERATE NEW KEYS"
    echo "=============================================================================="
    
    print_step "2.1: Generate New OpenAI API Key"
    echo "   → Go to: https://platform.openai.com/api-keys"
    echo "   → Click 'Create new secret key'"
    echo "   → Name: 'AI Research Platform - $(date +%Y%m%d)'"
    echo "   → Set permissions: Restrict to necessary actions only"
    echo "   → Copy the new key (starts with sk-)"
    update_github_secret "OPENAI_API_KEY" "OpenAI API key for AI services"
    
    print_step "2.2: Generate New Anthropic API Key"
    echo "   → Go to: https://console.anthropic.com/settings/keys"
    echo "   → Click 'Create Key'"  
    echo "   → Name: 'AI Research Platform'"
    echo "   → Copy the new key (starts with sk-ant-)"
    update_github_secret "ANTHROPIC_API_KEY" "Anthropic Claude API key"
    
    print_step "2.3: Generate New GitHub Personal Access Token"
    echo "   → Go to: https://github.com/settings/personal-access-tokens/fine-grained"
    echo "   → Click 'Generate new token'"
    echo "   → Repository access: Select specific repositories"
    echo "   → Permissions: Contents (read/write), Metadata (read), Actions (read)"
    echo "   → Expiration: 90 days (set calendar reminder to rotate)"
    update_github_secret "GH_TOKEN" "GitHub fine-grained personal access token"
    
    print_step "2.4: Get New Azure OpenAI Key"
    echo "   → After regenerating in Azure Portal, copy the new key"
    update_github_secret "AZURE_OPENAI_KEY" "Azure OpenAI service key"
    
    print_step "2.5: Generate New Google API Keys"
    echo "   → In Google Cloud Console, create new credentials"
    echo "   → Set API restrictions (Gemini AI, Maps if needed)"
    echo "   → Set application restrictions (HTTP referrers, IP addresses)"
    update_github_secret "GEMINI_API_KEY" "Google Gemini API key"
    
    # Optional: Update other service keys
    echo
    read -p "Do you want to update additional service keys (Meraki, Groq, HuggingFace, etc.)? (y/N): " update_others
    
    if [[ "$update_others" =~ ^[Yy]$ ]]; then
        update_github_secret "MERAKI_API_KEY" "Cisco Meraki Dashboard API key"
        update_github_secret "GROQ_API_KEY" "Groq AI API key" 
        update_github_secret "HF_API_KEY" "Hugging Face API token"
        update_github_secret "BRAVE_API_KEY" "Brave Search API key"
    fi
    
    echo
    echo "=============================================================================="
    echo "🧪 PHASE 3: TESTING & VALIDATION"
    echo "=============================================================================="
    
    print_step "3.1: Test GitHub Secrets Integration"
    if gh secret list > /dev/null 2>&1; then
        print_status "✅ GitHub secrets are accessible"
        echo "Current secrets:"
        gh secret list | grep -E "(OPENAI|ANTHROPIC|GITHUB|AZURE|GEMINI)" || echo "No matching secrets found"
    else
        print_error "❌ Cannot access GitHub secrets"
    fi
    
    print_step "3.2: Test Application Deployment"
    echo "   → Run: docker compose -f docker-compose.portable.yml config"
    echo "   → Should show no warnings about missing environment variables"
    echo "   → Test deployment: docker compose -f docker-compose.portable.yml up -d"
    
    print_step "3.3: Verify API Connectivity"
    echo "   → Test endpoints after deployment:"
    echo "     - http://localhost:11000/healthz (Backend health)"
    echo "     - http://localhost:7474 (Neo4j browser)"
    echo "     - Check application logs for API authentication errors"
    
    echo
    echo "=============================================================================="
    echo "✅ ROTATION COMPLETE"
    echo "=============================================================================="
    echo
    print_status "All exposed API keys should now be rotated and secured!"
    echo
    echo "📋 NEXT STEPS:"
    echo "1. Monitor service usage for next 24-48 hours"
    echo "2. Set up billing alerts for all API services"  
    echo "3. Enable security notifications in service dashboards"
    echo "4. Schedule regular key rotation (recommended: 90 days)"
    echo "5. Run secret scanner: python3 scripts/security/secret-scanner.py"
    echo
    echo "📱 MONITORING DASHBOARDS:"
    echo "• OpenAI Usage: https://platform.openai.com/usage"
    echo "• Azure Costs: https://portal.azure.com/#view/Microsoft_Azure_CostManagement"
    echo "• GitHub Actions: Repository → Settings → Secrets and variables"
    echo
    print_warning "Keep monitoring for unusual activity for the next week!"
}

# Run main function
main "$@"