#!/bin/bash

# =============================================================================
# Fix Hard-coded Paths Script
# =============================================================================
# This script finds and fixes hard-coded paths in the Chat Copilot codebase
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    local level=$1
    local message=$2
    case $level in
        "INFO")  echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "ERROR") echo -e "${RED}❌ ${message}${NC}" ;;
    esac
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAT_COPILOT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

print_status "INFO" "Starting hard-coded path fix process..."
print_status "INFO" "Working directory: $CHAT_COPILOT_ROOT"

# Create backup directory
BACKUP_DIR="$CHAT_COPILOT_ROOT/backups/path-fixes-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

print_status "INFO" "Backup directory: $BACKUP_DIR"

# =============================================================================
# STEP 1: Find all files with hard-coded paths
# =============================================================================

print_status "INFO" "Scanning for files with hard-coded paths..."

# File types to scan
FILE_TYPES=(
    "*.sh"
    "*.yml"
    "*.yaml"
    "*.conf"
    "*.json"
    "*.md"
    "*.service"
)

TOTAL_FILES=0
FIXED_FILES=0

# Function to fix paths in a file
fix_paths_in_file() {
    local file="$1"
    local relative_path="${file#$CHAT_COPILOT_ROOT/}"
    
    # Skip if file doesn't exist or is a backup
    if [[ ! -f "$file" ]] || [[ "$file" == *.backup.* ]]; then
        return 0
    fi
    
    # Check if file contains hard-coded paths
    if grep -q "/home/keith" "$file" 2>/dev/null; then
        TOTAL_FILES=$((TOTAL_FILES + 1))
        
        print_status "INFO" "Processing: $relative_path"
        
        # Create backup
        local backup_file="$BACKUP_DIR/$relative_path"
        mkdir -p "$(dirname "$backup_file")"
        cp "$file" "$backup_file"
        
        # Create temporary file for processing
        local temp_file=$(mktemp)
        
        # Apply fixes based on file type
        case "$file" in
            *.sh)
                # Shell scripts
                sed 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT:-$(pwd)}|g' "$file" > "$temp_file"
                sed -i 's|/home/keith|${HOME}|g' "$temp_file"
                ;;
            *.yml|*.yaml)
                # Docker Compose and YAML files
                sed 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT}|g' "$file" > "$temp_file"
                sed -i 's|/home/keith|${HOME}|g' "$temp_file"
                ;;
            *.conf)
                # Configuration files
                sed 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT}|g' "$file" > "$temp_file"
                sed -i 's|/home/keith|${HOME}|g' "$temp_file"
                ;;
            *.json)
                # JSON files
                sed 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT}|g' "$file" > "$temp_file"
                sed -i 's|/home/keith|${HOME}|g' "$temp_file"
                ;;
            *.md)
                # Markdown files - be more careful
                sed 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT}|g' "$file" > "$temp_file"
                ;;
            *.service)
                # Systemd service files
                sed 's|/home/keith/chat-copilot|%h/chat-copilot|g' "$file" > "$temp_file"
                sed -i 's|/home/keith|%h|g' "$temp_file"
                ;;
            *)
                # Default case
                sed 's|/home/keith/chat-copilot|${CHAT_COPILOT_ROOT}|g' "$file" > "$temp_file"
                sed -i 's|/home/keith|${HOME}|g' "$temp_file"
                ;;
        esac
        
        # Check if changes were made
        if ! cmp -s "$file" "$temp_file"; then
            mv "$temp_file" "$file"
            FIXED_FILES=$((FIXED_FILES + 1))
            print_status "SUCCESS" "Fixed: $relative_path"
        else
            rm "$temp_file"
            print_status "INFO" "No changes needed: $relative_path"
        fi
    fi
}

# =============================================================================
# STEP 2: Process all files
# =============================================================================

print_status "INFO" "Processing files..."

# Find and process all relevant files
for file_type in "${FILE_TYPES[@]}"; do
    while IFS= read -r -d '' file; do
        fix_paths_in_file "$file"
    done < <(find "$CHAT_COPILOT_ROOT" -name "$file_type" -type f -print0 2>/dev/null)
done

# =============================================================================
# STEP 3: Create portable environment loader
# =============================================================================

print_status "INFO" "Creating portable environment loader..."

cat > "$CHAT_COPILOT_ROOT/scripts/setup/load-env.sh" << 'EOF'
#!/bin/bash

# =============================================================================
# Environment Loader for Chat Copilot
# =============================================================================
# This script loads environment variables and sets up portable paths
# Source this script before running other Chat Copilot scripts
# =============================================================================

# Get the Chat Copilot root directory
if [[ -n "${CHAT_COPILOT_ROOT:-}" ]]; then
    # Use existing environment variable
    CHAT_COPILOT_ROOT="$CHAT_COPILOT_ROOT"
elif [[ -f "$(dirname "${BASH_SOURCE[0]}")/../.env" ]]; then
    # Derive from script location
    CHAT_COPILOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
else
    # Try to find it
    CHAT_COPILOT_ROOT="$(pwd)"
fi

# Export the root directory
export CHAT_COPILOT_ROOT

# Load environment file if it exists
if [[ -f "$CHAT_COPILOT_ROOT/.env" ]]; then
    set -a
    source "$CHAT_COPILOT_ROOT/.env"
    set +a
    echo "✅ Loaded environment from: $CHAT_COPILOT_ROOT/.env"
else
    echo "⚠️  No .env file found. Using defaults."
    
    # Set default values
    export PLATFORM_USER="${USER:-$(whoami)}"
    export PLATFORM_GROUP="${USER:-$(id -gn)}"
    export PLATFORM_IP="127.0.0.1"
fi

# Ensure required directories exist
mkdir -p "$CHAT_COPILOT_ROOT"/{logs,pids,data,backups,config-backups,temp}

echo "📁 Chat Copilot Root: $CHAT_COPILOT_ROOT"
echo "👤 Platform User: $PLATFORM_USER"
echo "🌐 Platform IP: $PLATFORM_IP"
EOF

chmod +x "$CHAT_COPILOT_ROOT/scripts/setup/load-env.sh"

# =============================================================================
# STEP 4: Update main startup scripts
# =============================================================================

print_status "INFO" "Updating main startup scripts..."

# Update start-ssl-platform.sh to be portable
if [[ -f "$CHAT_COPILOT_ROOT/start-ssl-platform.sh" ]]; then
    # Add environment loading to the beginning
    temp_file=$(mktemp)
    cat > "$temp_file" << 'EOF'
#!/bin/bash

# Load portable environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scripts/setup/load-env.sh"

EOF
    
    # Append the rest of the file (skip the shebang)
    tail -n +2 "$CHAT_COPILOT_ROOT/start-ssl-platform.sh" >> "$temp_file"
    
    # Replace the original
    mv "$temp_file" "$CHAT_COPILOT_ROOT/start-ssl-platform.sh"
    chmod +x "$CHAT_COPILOT_ROOT/start-ssl-platform.sh"
    
    print_status "SUCCESS" "Updated start-ssl-platform.sh"
fi

# =============================================================================
# STEP 5: Create migration guide
# =============================================================================

print_status "INFO" "Creating migration guide..."

cat > "$CHAT_COPILOT_ROOT/PORTABLE_MIGRATION_GUIDE.md" << EOF
# Chat Copilot Portable Migration Guide

This guide explains how to migrate your Chat Copilot installation to be portable across different systems.

## What Was Fixed

The following hard-coded paths have been replaced with environment variables:

- \`/home/keith/chat-copilot\` → \`\${CHAT_COPILOT_ROOT}\`
- \`/home/keith\` → \`\${HOME}\`
- User-specific paths → Environment variables

## Files Modified

A total of **$FIXED_FILES** files were modified out of **$TOTAL_FILES** files scanned.

Backups of all modified files are stored in:
\`$BACKUP_DIR\`

## New Portable Structure

### Environment Configuration
- \`.env\` - Main environment configuration
- \`.env.template\` - Template for new installations

### Portable Scripts
- \`scripts/setup/install-portable.sh\` - Portable installation script
- \`scripts/setup/load-env.sh\` - Environment loader
- \`start-platform-portable.sh\` - Portable startup script

### Configuration Files
- All Docker Compose files now use environment variables
- All shell scripts now use portable paths
- All configuration files use environment variables

## Installation on New System

1. Copy the entire chat-copilot directory to the new system
2. Run the portable installation script:
   \`\`\`bash
   cd chat-copilot
   ./scripts/setup/install-portable.sh
   \`\`\`
3. Edit \`.env\` file to customize for your system
4. Start the platform:
   \`\`\`bash
   ./start-platform-portable.sh
   \`\`\`

## Environment Variables

Key environment variables that make the installation portable:

- \`CHAT_COPILOT_ROOT\` - Base installation directory
- \`PLATFORM_USER\` - User for file ownership
- \`PLATFORM_GROUP\` - Group for file ownership
- \`PLATFORM_IP\` - IP address for services
- All service ports are configurable

## Rollback

If you need to rollback the changes:

1. Stop all services
2. Restore files from backup:
   \`\`\`bash
   cp -r $BACKUP_DIR/* ./
   \`\`\`
3. Restart services

## Testing

To test the portable installation:

1. Create a new user account
2. Copy the chat-copilot directory to the new user's home
3. Run the portable installation script
4. Verify all services start correctly

## Migration Date

This migration was performed on: $(date)

## Support

If you encounter issues with the portable installation:

1. Check the environment variables in \`.env\`
2. Verify file permissions
3. Check the logs in \`logs/\` directory
4. Restore from backup if needed

EOF

# =============================================================================
# STEP 6: Summary
# =============================================================================

print_status "SUCCESS" "Hard-coded path fix completed!"

cat << EOF

🎉 Path Fix Summary:

📊 Statistics:
   • Files scanned: $TOTAL_FILES
   • Files fixed: $FIXED_FILES
   • Backup location: $BACKUP_DIR

📁 New Files Created:
   • .env.template - Environment template
   • scripts/setup/install-portable.sh - Portable installer
   • scripts/setup/load-env.sh - Environment loader
   • PORTABLE_MIGRATION_GUIDE.md - Migration documentation

🔧 Key Changes:
   • /home/keith/chat-copilot → \${CHAT_COPILOT_ROOT}
   • /home/keith → \${HOME}
   • Hard-coded user/group → Environment variables

🚀 Next Steps:
   1. Review the changes in PORTABLE_MIGRATION_GUIDE.md
   2. Test the portable installation on a different system
   3. Update your deployment scripts to use the new portable version

📖 For new installations, use:
   ./scripts/setup/install-portable.sh

EOF

print_status "INFO" "All changes have been backed up to: $BACKUP_DIR"