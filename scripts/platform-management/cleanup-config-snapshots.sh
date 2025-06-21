#!/bin/bash
# Configuration Snapshot Cleanup Script
# Manages and cleans up old configuration snapshots

set -euo pipefail

readonly SNAPSHOTS_DIR="/home/keith/chat-copilot/config-snapshots"
readonly KEEP_DAYS=7
readonly KEEP_WEEKLY=4
readonly KEEP_MONTHLY=3

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️ $message${NC}" ;;
    esac
}

analyze_snapshots() {
    print_status "INFO" "Analyzing configuration snapshots..."
    
    if [ ! -d "$SNAPSHOTS_DIR" ]; then
        print_status "ERROR" "Snapshots directory not found: $SNAPSHOTS_DIR"
        return 1
    fi
    
    local total_snapshots=$(find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "202*" | wc -l)
    local total_size=$(du -sh "$SNAPSHOTS_DIR" 2>/dev/null | cut -f1)
    
    print_status "INFO" "Found $total_snapshots configuration snapshots"
    print_status "INFO" "Total size: $total_size"
    
    echo
    echo -e "${BLUE}📊 Snapshot Analysis:${NC}"
    echo -e "   Directory: $SNAPSHOTS_DIR"
    echo -e "   Total Snapshots: $total_snapshots"
    echo -e "   Total Size: $total_size"
    echo
    
    # Show breakdown by date
    echo -e "${YELLOW}📅 Snapshots by Date:${NC}"
    find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "202*" | sort | while read snapshot_dir; do
        local snapshot_name=$(basename "$snapshot_dir")
        local snapshot_size=$(du -sh "$snapshot_dir" 2>/dev/null | cut -f1)
        local snapshot_date=$(echo "$snapshot_name" | cut -d'_' -f1)
        echo "   $snapshot_date: $snapshot_name ($snapshot_size)"
    done
}

identify_cleanup_candidates() {
    print_status "INFO" "Identifying cleanup candidates..."
    
    # Current time for calculations
    local current_time=$(date +%s)
    local keep_daily_time=$((current_time - (KEEP_DAYS * 86400)))
    local keep_weekly_time=$((current_time - (KEEP_WEEKLY * 7 * 86400)))
    local keep_monthly_time=$((current_time - (KEEP_MONTHLY * 30 * 86400)))
    
    echo
    echo -e "${YELLOW}📋 Cleanup Policy:${NC}"
    echo -e "   Keep daily snapshots: Last $KEEP_DAYS days"
    echo -e "   Keep weekly snapshots: Last $KEEP_WEEKLY weeks (oldest per week)"
    echo -e "   Keep monthly snapshots: Last $KEEP_MONTHLY months (oldest per month)"
    echo
    
    local snapshots_to_delete=()
    local snapshots_to_keep=()
    
    # Process each snapshot
    find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "202*" | sort | while read snapshot_dir; do
        local snapshot_name=$(basename "$snapshot_dir")
        local snapshot_date=$(echo "$snapshot_name" | cut -d'_' -f1)
        local snapshot_time=$(date -d "$snapshot_date" +%s 2>/dev/null || echo 0)
        
        if [ $snapshot_time -eq 0 ]; then
            echo "   ❓ Invalid date format: $snapshot_name"
            continue
        fi
        
        # Determine retention category
        if [ $snapshot_time -gt $keep_daily_time ]; then
            echo "   ✅ Keep (daily): $snapshot_name"
        elif [ $snapshot_time -gt $keep_weekly_time ]; then
            echo "   📅 Keep (weekly): $snapshot_name"
        elif [ $snapshot_time -gt $keep_monthly_time ]; then
            echo "   📆 Keep (monthly): $snapshot_name"
        else
            echo "   🗑️ Delete candidate: $snapshot_name"
        fi
    done
}

create_archive() {
    print_status "INFO" "Creating archive of snapshots before cleanup..."
    
    local archive_dir="/home/keith/chat-copilot/config-archives"
    local archive_file="$archive_dir/snapshots-archive-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    mkdir -p "$archive_dir"
    
    if tar -czf "$archive_file" -C "$(dirname "$SNAPSHOTS_DIR")" "$(basename "$SNAPSHOTS_DIR")" 2>/dev/null; then
        print_status "SUCCESS" "Archive created: $archive_file"
        local archive_size=$(du -sh "$archive_file" | cut -f1)
        print_status "INFO" "Archive size: $archive_size"
    else
        print_status "ERROR" "Failed to create archive"
        return 1
    fi
}

perform_cleanup() {
    local dry_run=${1:-true}
    
    if [ "$dry_run" = "true" ]; then
        print_status "INFO" "Performing DRY RUN cleanup (no files will be deleted)..."
    else
        print_status "WARNING" "Performing ACTUAL cleanup - files will be deleted!"
        create_archive
    fi
    
    local current_time=$(date +%s)
    local keep_daily_time=$((current_time - (KEEP_DAYS * 86400)))
    local deleted_count=0
    local deleted_size=0
    
    find "$SNAPSHOTS_DIR" -maxdepth 1 -type d -name "202*" | sort | while read snapshot_dir; do
        local snapshot_name=$(basename "$snapshot_dir")
        local snapshot_date=$(echo "$snapshot_name" | cut -d'_' -f1)
        local snapshot_time=$(date -d "$snapshot_date" +%s 2>/dev/null || echo 0)
        
        if [ $snapshot_time -eq 0 ]; then
            continue
        fi
        
        # Delete if older than keep period
        if [ $snapshot_time -lt $keep_daily_time ]; then
            local snapshot_size=$(du -sh "$snapshot_dir" 2>/dev/null | cut -f1)
            
            if [ "$dry_run" = "true" ]; then
                echo "   [DRY RUN] Would delete: $snapshot_name ($snapshot_size)"
            else
                echo "   🗑️ Deleting: $snapshot_name ($snapshot_size)"
                rm -rf "$snapshot_dir"
                ((deleted_count++))
            fi
        fi
    done
    
    if [ "$dry_run" = "false" ]; then
        print_status "SUCCESS" "Cleanup completed - deleted $deleted_count snapshots"
    fi
}

show_usage() {
    echo "Configuration Snapshot Cleanup Tool"
    echo ""
    echo "Usage: $0 {analyze|cleanup|cleanup-force|help}"
    echo ""
    echo "Commands:"
    echo "  analyze       - Analyze current snapshots and show cleanup plan"
    echo "  cleanup       - Perform dry-run cleanup (shows what would be deleted)"
    echo "  cleanup-force - Actually perform cleanup (creates archive first)"
    echo "  help          - Show this help message"
    echo ""
    echo "Retention Policy:"
    echo "  - Keep daily snapshots for last $KEEP_DAYS days"
    echo "  - Keep weekly snapshots for last $KEEP_WEEKLY weeks"
    echo "  - Keep monthly snapshots for last $KEEP_MONTHLY months"
}

main() {
    echo -e "${BLUE}🧹 Configuration Snapshot Cleanup Tool${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo
    
    case "${1:-analyze}" in
        "analyze")
            analyze_snapshots
            echo
            identify_cleanup_candidates
            ;;
        "cleanup")
            analyze_snapshots
            echo
            perform_cleanup true
            ;;
        "cleanup-force")
            read -p "Are you sure you want to delete old snapshots? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                analyze_snapshots
                echo
                perform_cleanup false
            else
                print_status "INFO" "Cleanup cancelled"
            fi
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_status "ERROR" "Unknown command: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
}

main "$@"