#!/bin/bash

# =============================================================================
# Verify GH_TOKEN Update Script
# =============================================================================
# This script verifies that all GITHUB_TOKEN references have been updated
# to use GH_TOKEN to comply with GitHub Actions naming restrictions.
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo
echo "🔍 VERIFYING GH_TOKEN UPDATES"
echo "=============================="
echo

# Check for remaining GITHUB_TOKEN references (excluding documentation)
echo "1. Checking for remaining GITHUB_TOKEN references in code..."

# Exclude documentation and backup files
remaining_refs=$(grep -r "GITHUB_TOKEN" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude="*.md" \
    --exclude="*.backup*" \
    --exclude="GITHUB_SECRET_FIX.md" \
    --exclude="*checklist*" \
    --exclude="*rotation*" \
    --exclude=".env.backup" 2>/dev/null || true)

if [ -n "$remaining_refs" ]; then
    print_error "Found remaining GITHUB_TOKEN references:"
    echo "$remaining_refs" | head -10
    echo
    if [ $(echo "$remaining_refs" | wc -l) -gt 10 ]; then
        echo "... and $(($(echo "$remaining_refs" | wc -l) - 10)) more"
    fi
    echo
    print_warning "These references should be reviewed and possibly updated to GH_TOKEN"
else
    print_status "✅ No remaining GITHUB_TOKEN references found in code"
fi

echo
echo "2. Verifying GH_TOKEN is properly referenced..."

# Check for GH_TOKEN references
gh_token_refs=$(grep -r "GH_TOKEN" . \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude="*.backup*" 2>/dev/null || true)

if [ -n "$gh_token_refs" ]; then
    print_status "✅ Found GH_TOKEN references:"
    echo "$gh_token_refs" | grep -v ".md:" | head -5
else
    print_warning "No GH_TOKEN references found - this may indicate incomplete update"
fi

echo
echo "3. Checking GitHub secret can be set..."

# Test GitHub CLI availability
if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
    print_status "GitHub CLI is available and authenticated"
    
    # Check if GH_TOKEN secret exists
    if gh secret list | grep -q "^GH_TOKEN"; then
        print_status "✅ GH_TOKEN secret exists in repository"
    else
        print_warning "GH_TOKEN secret not yet set in repository"
        echo "   Run: gh secret set GH_TOKEN --body \"your_github_token\""
    fi
else
    print_warning "GitHub CLI not available or not authenticated"
    echo "   Install from: https://cli.github.com/"
    echo "   Authenticate: gh auth login"
fi

echo
echo "4. Checking environment template consistency..."

template_files=(
    ".env.template"
    "configs/env-templates/.env.development.template"
    "configs/env-templates/.env.production.template"
)

inconsistent_files=()
for file in "${template_files[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "GITHUB_TOKEN" "$file"; then
            inconsistent_files+=("$file")
        fi
    fi
done

if [ ${#inconsistent_files[@]} -eq 0 ]; then
    print_status "✅ Environment templates are consistent (using GH_TOKEN)"
else
    print_error "Inconsistent environment templates found:"
    for file in "${inconsistent_files[@]}"; do
        echo "   ❌ $file still references GITHUB_TOKEN"
    done
fi

echo
echo "5. Testing secret replacement patterns..."

# Test the secret replacer patterns
if [ -f "scripts/security/secret-replacer.py" ]; then
    if grep -q "GH_TOKEN" "scripts/security/secret-replacer.py"; then
        print_status "✅ Secret replacer patterns updated"
    else
        print_error "Secret replacer still uses GITHUB_TOKEN patterns"
    fi
else
    print_warning "Secret replacer script not found"
fi

echo
echo "=============================="
echo "📋 SUMMARY:"
echo "=============================="

if [ -z "$remaining_refs" ] && [ -n "$gh_token_refs" ] && [ ${#inconsistent_files[@]} -eq 0 ]; then
    print_status "✅ GH_TOKEN update appears to be successful!"
    echo
    echo "Next steps:"
    echo "1. Set the GH_TOKEN secret: gh secret set GH_TOKEN --body \"your_new_token\""
    echo "2. Test deployment: docker compose -f docker-compose.portable.yml config"
    echo "3. Verify GitHub integration works in your application"
else
    print_warning "⚠️  Some issues found during verification"
    echo
    echo "Review the issues above and:"
    echo "1. Update any remaining GITHUB_TOKEN references to GH_TOKEN"
    echo "2. Ensure all environment templates are consistent"
    echo "3. Test that your application can access the renamed secret"
fi

echo
echo "🔗 Related files to verify manually:"
echo "   - Any custom Python scripts using os.getenv('GITHUB_TOKEN')"
echo "   - Docker environment files"  
echo "   - CI/CD pipeline configurations"
echo "   - Application configuration files"