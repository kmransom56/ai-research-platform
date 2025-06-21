#!/bin/bash
# GitHub Collaborator Management Script
# Adds collaborators to multiple repositories with market-ready permissions

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $*${NC}"
}

success() {
    echo -e "${GREEN}✅ $*${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

error() {
    echo -e "${RED}❌ $*${NC}"
}

# Function to add collaborator to a repository
add_collaborator() {
    local repo="$1"
    local username="$2"
    local permission="$3"

    log "Adding $username as $permission to $repo..."

    if gh api repos/"$repo"/collaborators/"$username" \
        --method PUT \
        --field permission="$permission" >/dev/null 2>&1; then
        success "Added $username to $repo with $permission access"
        return 0
    else
        error "Failed to add $username to $repo"
        return 1
    fi
}

# Function to list current collaborators
list_collaborators() {
    local repo="$1"
    log "Current collaborators for $repo:"
    gh api repos/"$repo"/collaborators --jq '.[] | "\(.login) (\(.permissions.admin // false | if . then "admin" else (.permissions.push // false | if . then "push" else "pull" end) end))"' || true
}

# Main function
main() {
    echo -e "${BLUE}🤝 GitHub Collaborator Management${NC}"
    echo "=================================="

    # Get collaborator username
    read -p "Enter your brother's GitHub username: " BROTHER_USERNAME

    # Validate username exists
    if ! gh api users/"$BROTHER_USERNAME" >/dev/null 2>&1; then
        error "GitHub user '$BROTHER_USERNAME' not found. Please check the username."
        exit 1
    fi

    success "Found GitHub user: $BROTHER_USERNAME"

    # Get permission level
    echo ""
    echo "Permission levels:"
    echo "  admin - Full access (recommended for business partner)"
    echo "  push  - Read/write access (can modify code)"
    echo "  pull  - Read-only access"
    echo ""
    read -p "Enter permission level [admin/push/pull] (default: admin): " PERMISSION
    PERMISSION=${PERMISSION:-admin}

    # Validate permission
    case "$PERMISSION" in
    admin | push | pull) ;;
    *)
        error "Invalid permission. Use admin, push, or pull."
        exit 1
        ;;
    esac

    # Get repository selection
    echo ""
    echo "Repository selection:"
    echo "  1. Current repository only"
    echo "  2. All private repositories"
    echo "  3. All repositories (public + private)"
    echo "  4. Select specific repositories"
    echo ""
    read -p "Choose option [1-4]: " REPO_OPTION

    case "$REPO_OPTION" in
    1)
        # Current repository only
        CURRENT_REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
        success "Will add collaborator to: $CURRENT_REPO"
        add_collaborator "$CURRENT_REPO" "$BROTHER_USERNAME" "$PERMISSION"
        ;;
    2)
        # All private repositories
        log "Getting list of private repositories..."
        REPOS=($(gh repo list --limit 100 --visibility private --json nameWithOwner --jq '.[].nameWithOwner'))

        echo ""
        success "Found ${#REPOS[@]} private repositories"
        for repo in "${REPOS[@]}"; do
            echo "  - $repo"
        done

        echo ""
        read -p "Add $BROTHER_USERNAME to all private repositories? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for repo in "${REPOS[@]}"; do
                add_collaborator "$repo" "$BROTHER_USERNAME" "$PERMISSION"
                sleep 1 # Rate limiting
            done
        fi
        ;;
    3)
        # All repositories
        log "Getting list of all repositories..."
        REPOS=($(gh repo list --limit 100 --json nameWithOwner --jq '.[].nameWithOwner'))

        echo ""
        success "Found ${#REPOS[@]} repositories"
        for repo in "${REPOS[@]}"; do
            echo "  - $repo"
        done

        echo ""
        read -p "Add $BROTHER_USERNAME to ALL repositories? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for repo in "${REPOS[@]}"; do
                add_collaborator "$repo" "$BROTHER_USERNAME" "$PERMISSION"
                sleep 1 # Rate limiting
            done
        fi
        ;;
    4)
        # Select specific repositories
        log "Available repositories:"
        REPOS=($(gh repo list --limit 50 --json nameWithOwner --jq '.[].nameWithOwner'))

        for i in "${!REPOS[@]}"; do
            echo "  $((i + 1)). ${REPOS[i]}"
        done

        echo ""
        echo "Enter repository numbers (space-separated, e.g., 1 3 5):"
        read -a SELECTED_INDICES

        for index in "${SELECTED_INDICES[@]}"; do
            if [[ "$index" =~ ^[0-9]+$ ]] && [ "$index" -ge 1 ] && [ "$index" -le "${#REPOS[@]}" ]; then
                repo="${REPOS[$((index - 1))]}"
                add_collaborator "$repo" "$BROTHER_USERNAME" "$PERMISSION"
                sleep 1
            else
                warn "Invalid selection: $index"
            fi
        done
        ;;
    *)
        error "Invalid option"
        exit 1
        ;;
    esac

    echo ""
    success "🎉 Collaborator management complete!"

    # Business considerations
    echo ""
    echo -e "${YELLOW}💼 Business Partnership Considerations:${NC}"
    echo "=================================="
    echo "✅ Your brother now has access to the repositories"
    echo "📋 Next steps for commercialization:"
    echo "   1. Create a business plan document"
    echo "   2. Define roles and responsibilities"
    echo "   3. Set up revenue sharing agreement"
    echo "   4. Consider creating an organization account"
    echo "   5. Set up proper licensing for commercial use"
    echo "   6. Document intellectual property ownership"
    echo ""
    echo "🏢 Recommended: Create GitHub Organization"
    echo "   - Professional appearance for clients"
    echo "   - Better team management features"
    echo "   - Separate business identity"
    echo ""
    echo "💡 To create organization: https://github.com/organizations/new"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
