#!/bin/bash
"""
Bulk Secret Import Script for AI Research Platform
Reads secrets from a file and imports them to GitHub repository secrets

Usage:
  ./bulk-import-secrets.sh [secrets_file] [options]

Options:
  --dry-run     Show what would be imported without actually doing it
  --overwrite   Overwrite existing secrets (default: skip existing)
  --validate    Validate secrets file format without importing
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
SECRETS_FILE=""
DRY_RUN=false
OVERWRITE=false
VALIDATE_ONLY=false

# Repository information
REPO_OWNER="${GITHUB_REPOSITORY_OWNER:-$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\).*/\1/' 2>/dev/null || echo '')}"
REPO_NAME="${GITHUB_REPOSITORY_NAME:-$(git config --get remote.origin.url | sed 's/.*\/\([^/]*\)\.git$/\1/' 2>/dev/null || echo '')}"

echo -e "${BLUE}🔐 Bulk Secret Import for AI Research Platform${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [secrets_file] [options]

Arguments:
  secrets_file    Path to file containing secrets (default: configs/secrets-import.txt)

Options:
  --dry-run      Show what would be imported without actually doing it
  --overwrite    Overwrite existing secrets (default: skip existing)
  --validate     Validate secrets file format without importing
  --help         Show this help message

File Format:
  SECRET_NAME=secret_value
  # Comments start with #
  # Empty lines are ignored

Examples:
  $0 my-secrets.txt                    # Import from my-secrets.txt
  $0 --dry-run                         # Preview import from default file
  $0 my-secrets.txt --overwrite        # Import and overwrite existing
  $0 --validate my-secrets.txt         # Just validate file format

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --overwrite)
            OVERWRITE=true
            shift
            ;;
        --validate)
            VALIDATE_ONLY=true
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$SECRETS_FILE" ]; then
                SECRETS_FILE="$1"
            else
                echo -e "${RED}Too many arguments${NC}"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Set default secrets file if not provided
if [ -z "$SECRETS_FILE" ]; then
    SECRETS_FILE="configs/secrets-import.txt"
fi

# Check if file exists
if [ ! -f "$SECRETS_FILE" ]; then
    echo -e "${RED}❌ Secrets file not found: $SECRETS_FILE${NC}"
    echo ""
    echo "Create a secrets file using this template:"
    echo "cp configs/secrets-import-template.txt $SECRETS_FILE"
    echo "# Edit $SECRETS_FILE with your actual secrets"
    exit 1
fi

echo -e "📁 Secrets file: ${YELLOW}$SECRETS_FILE${NC}"
echo -e "🏢 Repository: ${YELLOW}$REPO_OWNER/$REPO_NAME${NC}"
echo ""

# Function to check if GitHub CLI is installed and authenticated
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
        echo -e "${YELLOW}Please install it from: https://cli.github.com/${NC}"
        exit 1
    fi
    
    # Check if authenticated (only if not validating)
    if [ "$VALIDATE_ONLY" = false ] && ! gh auth status &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI is not authenticated.${NC}"
        echo -e "${YELLOW}Please run: gh auth login${NC}"
        exit 1
    fi
    
    if [ "$VALIDATE_ONLY" = false ]; then
        echo -e "${GREEN}✅ GitHub CLI is installed and authenticated${NC}"
    fi
}

# Function to validate secrets file format
validate_secrets_file() {
    local file="$1"
    local line_num=0
    local valid_secrets=0
    local invalid_lines=()
    local duplicate_keys=()
    local seen_keys=()
    
    echo -e "${BLUE}🔍 Validating secrets file format...${NC}"
    
    while IFS= read -r line || [ -n "$line" ]; do
        line_num=$((line_num + 1))
        
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Check if line matches SECRET_NAME=value format
        if [[ "$line" =~ ^[A-Z_][A-Z0-9_]*=.+ ]]; then
            # Extract secret name
            secret_name="${line%%=*}"
            secret_value="${line#*=}"
            
            # Check for duplicates
            if [[ " ${seen_keys[@]} " =~ " ${secret_name} " ]]; then
                duplicate_keys+=("Line $line_num: $secret_name (duplicate)")
            else
                seen_keys+=("$secret_name")
            fi
            
            # Validate secret value is not empty
            if [ -z "$secret_value" ]; then
                invalid_lines+=("Line $line_num: $secret_name has empty value")
            else
                valid_secrets=$((valid_secrets + 1))
            fi
        else
            invalid_lines+=("Line $line_num: Invalid format - $line")
        fi
    done < "$file"
    
    # Report validation results
    echo -e "📊 Validation Results:"
    echo -e "  Valid secrets: ${GREEN}$valid_secrets${NC}"
    echo -e "  Total lines processed: $line_num"
    
    if [ ${#invalid_lines[@]} -gt 0 ]; then
        echo -e "  ${RED}Invalid lines: ${#invalid_lines[@]}${NC}"
        for invalid in "${invalid_lines[@]}"; do
            echo -e "    ${RED}❌ $invalid${NC}"
        done
    fi
    
    if [ ${#duplicate_keys[@]} -gt 0 ]; then
        echo -e "  ${YELLOW}Duplicate keys: ${#duplicate_keys[@]}${NC}"
        for duplicate in "${duplicate_keys[@]}"; do
            echo -e "    ${YELLOW}⚠️  $duplicate${NC}"
        done
    fi
    
    if [ ${#invalid_lines[@]} -eq 0 ] && [ ${#duplicate_keys[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ File format is valid!${NC}"
        return 0
    else
        echo -e "${RED}❌ File has validation errors${NC}"
        return 1
    fi
}

# Function to get existing secrets
get_existing_secrets() {
    if [ "$DRY_RUN" = false ] && [ "$VALIDATE_ONLY" = false ]; then
        gh secret list --repo "$REPO_OWNER/$REPO_NAME" --json name -q '.[].name' 2>/dev/null || echo ""
    fi
}

# Function to import secrets from file
import_secrets() {
    local file="$1"
    local imported=0
    local skipped=0
    local failed=0
    local existing_secrets
    
    if [ "$VALIDATE_ONLY" = true ]; then
        return 0
    fi
    
    # Get existing secrets if not overwriting
    if [ "$OVERWRITE" = false ]; then
        existing_secrets=$(get_existing_secrets)
    fi
    
    echo -e "${BLUE}🔄 ${DRY_RUN:+[DRY RUN] }Importing secrets...${NC}"
    echo ""
    
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Parse SECRET_NAME=value
        if [[ "$line" =~ ^[A-Z_][A-Z0-9_]*=.+ ]]; then
            secret_name="${line%%=*}"
            secret_value="${line#*=}"
            
            # Check if secret already exists and we're not overwriting
            if [ "$OVERWRITE" = false ] && echo "$existing_secrets" | grep -q "^$secret_name$" 2>/dev/null; then
                echo -e "${YELLOW}⏭️  Skipped: $secret_name (already exists)${NC}"
                skipped=$((skipped + 1))
                continue
            fi
            
            # Import the secret
            if [ "$DRY_RUN" = true ]; then
                echo -e "${GREEN}✓ Would import: $secret_name${NC}"
                imported=$((imported + 1))
            else
                if echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO_OWNER/$REPO_NAME" 2>/dev/null; then
                    echo -e "${GREEN}✅ Imported: $secret_name${NC}"
                    imported=$((imported + 1))
                else
                    echo -e "${RED}❌ Failed: $secret_name${NC}"
                    failed=$((failed + 1))
                fi
            fi
        fi
    done < "$file"
    
    # Summary
    echo ""
    echo -e "${BLUE}📊 Import Summary:${NC}"
    echo -e "  Imported: ${GREEN}$imported${NC}"
    if [ $skipped -gt 0 ]; then
        echo -e "  Skipped: ${YELLOW}$skipped${NC}"
    fi
    if [ $failed -gt 0 ]; then
        echo -e "  Failed: ${RED}$failed${NC}"
    fi
    
    return $failed
}

# Main execution
if [ "$VALIDATE_ONLY" = false ]; then
    check_gh_cli
fi

# Validate file format
if ! validate_secrets_file "$SECRETS_FILE"; then
    exit 1
fi

if [ "$VALIDATE_ONLY" = true ]; then
    echo -e "${GREEN}✅ Validation complete!${NC}"
    exit 0
fi

echo ""

# Import secrets
if import_secrets "$SECRETS_FILE"; then
    echo ""
    if [ "$DRY_RUN" = true ]; then
        echo -e "${GREEN}🎉 Dry run completed successfully!${NC}"
        echo ""
        echo -e "${BLUE}To actually import the secrets, run:${NC}"
        echo -e "$0 $SECRETS_FILE"
    else
        echo -e "${GREEN}🎉 Secrets imported successfully!${NC}"
        echo ""
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Verify secrets: gh secret list --repo $REPO_OWNER/$REPO_NAME"
        echo "2. Test the secret scanner: python3 scripts/security/secret-scanner.py"
        echo "3. Run secret replacement: python3 scripts/security/secret-replacer.py --dry-run"
    fi
    echo ""
else
    echo -e "${RED}❌ Some secrets failed to import${NC}"
    exit 1
fi