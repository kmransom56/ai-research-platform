#!/bin/bash
# Quick GitHub Collaborator Adder
# Usage: ./quick-add-collaborator.sh USERNAME [PERMISSION]

USERNAME="$1"
PERMISSION="${2:-admin}"

if [[ -z "$USERNAME" ]]; then
    echo "Usage: $0 USERNAME [admin|push|pull]"
    echo "Example: $0 kyle-ransom admin"
    exit 1
fi

echo "Adding $USERNAME as $PERMISSION to current repository..."

# Get current repository
REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
echo "Repository: $REPO"

# Add collaborator
if gh api repos/"$REPO"/collaborators/"$USERNAME" \
    --method PUT \
    --field permission="$PERMISSION" >/dev/null 2>&1; then
    echo "✅ Successfully added $USERNAME to $REPO with $PERMISSION access"
    echo "🔗 Invitation sent! They'll receive an email notification."
else
    echo "❌ Failed to add $USERNAME. Check username and permissions."
    exit 1
fi
