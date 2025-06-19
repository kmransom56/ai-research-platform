#!/usr/bin/env python3
"""
Config Backup Directory Cleanup Utility
Standalone utility for cleaning up FortiGate/FortiManager config backups
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import shutil


class ConfigCleanupUtility:
    """Utility for cleaning up config backup directories"""
    
    def __init__(self):
        # Use the platform directory for config storage
        self.platform_dir = Path("/home/keith/chat-copilot")
        self.config_file = self.platform_dir / "config" / "cleanup_config.json"
        self.default_configs = {
            "config-backups": {
                "path": "/home/keith/config-backups",
                "retention_days": 90,
                "size_limit_mb": 500,
                "file_patterns": ["*.conf", "*.cfg", "*.backup", "*.json"],
                "enabled": True,
                "description": "Main FortiGate configuration backups"
            },
            "config-backups-auto": {
                "path": "/home/keith/config-backups-auto",
                "retention_days": 30,
                "size_limit_mb": 200,
                "file_patterns": ["*.conf", "*.cfg", "*.backup"],
                "enabled": True,
                "description": "Automated FortiGate backups"
            },
            "config-snapshots": {
                "path": "/home/keith/config-snapshots",
                "retention_days": 60,
                "size_limit_mb": 300,
                "file_patterns": ["*.snapshot", "*.json", "*.xml"],
                "enabled": True,
                "description": "Configuration snapshots and comparisons"
            },
            "fortimanager-backups": {
                "path": "/home/keith/fortimanager-backups",
                "retention_days": 120,
                "size_limit_mb": 1000,
                "file_patterns": ["*.backup", "*.json", "*.conf"],
                "enabled": True,
                "description": "FortiManager database backups"
            },
            "network-configs": {
                "path": "/home/keith/network-device-configs",
                "retention_days": 45,
                "size_limit_mb": 100,
                "file_patterns": ["*.conf", "*.cfg", "*.running", "*.startup"],
                "enabled": True,
                "description": "General network device configurations"
            },
            "temp-configs": {
                "path": "/tmp/config-temp",
                "retention_days": 7,
                "size_limit_mb": 50,
                "file_patterns": ["*.tmp", "*.temp", "*.conf"],
                "enabled": True,
                "description": "Temporary configuration files"
            }
        }
    
    def create_config_file(self):
        """Create default configuration file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(self.default_configs, f, indent=2)
        
        print(f"✅ Created configuration file: {self.config_file}")
        print("📝 Edit this file to customize cleanup settings")
    
    def load_config(self) -> Dict[str, Any]:
        """Load cleanup configuration"""
        if not self.config_file.exists():
            print("⚠️  Configuration file not found, creating default...")
            self.create_config_file()
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def analyze_directory(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze directory without making changes"""
        directory = Path(config['path'])
        
        if not directory.exists():
            return {
                "name": name,
                "path": str(directory),
                "exists": False,
                "error": "Directory does not exist"
            }
        
        try:
            # Get all files matching patterns
            all_files = []
            for pattern in config['file_patterns']:
                all_files.extend(directory.rglob(pattern))
            
            # Calculate statistics
            total_files = len(all_files)
            total_size_mb = sum(f.stat().st_size for f in all_files if f.is_file()) / (1024 * 1024)
            
            # Analyze by age
            cutoff_date = datetime.now() - timedelta(days=config['retention_days'])
            old_files = [f for f in all_files if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff_date]
            old_files_size_mb = sum(f.stat().st_size for f in old_files) / (1024 * 1024)
            
            # Files to delete due to size limit
            size_limited_files = []
            if config.get('size_limit_mb') and total_size_mb > config['size_limit_mb']:
                # Sort by modification time (oldest first)
                sorted_files = sorted(all_files, key=lambda f: f.stat().st_mtime)
                current_size = total_size_mb
                
                for f in sorted_files:
                    if current_size <= config['size_limit_mb']:
                        break
                    if f not in old_files:  # Don't double-count
                        size_limited_files.append(f)
                        current_size -= f.stat().st_size / (1024 * 1024)
            
            # Oldest and newest files
            if all_files:
                all_files_with_time = [(f, f.stat().st_mtime) for f in all_files if f.is_file()]
                all_files_with_time.sort(key=lambda x: x[1])
                oldest_file = all_files_with_time[0] if all_files_with_time else None
                newest_file = all_files_with_time[-1] if all_files_with_time else None
            else:
                oldest_file = newest_file = None
            
            return {
                "name": name,
                "path": str(directory),
                "description": config.get('description', ''),
                "exists": True,
                "enabled": config.get('enabled', True),
                "retention_days": config['retention_days'],
                "size_limit_mb": config.get('size_limit_mb'),
                "file_patterns": config['file_patterns'],
                "statistics": {
                    "total_files": total_files,
                    "total_size_mb": round(total_size_mb, 2),
                    "old_files_count": len(old_files),
                    "old_files_size_mb": round(old_files_size_mb, 2),
                    "size_limited_files_count": len(size_limited_files),
                    "oldest_file": {
                        "name": oldest_file[0].name if oldest_file else None,
                        "age_days": (datetime.now() - datetime.fromtimestamp(oldest_file[1])).days if oldest_file else None
                    } if oldest_file else None,
                    "newest_file": {
                        "name": newest_file[0].name if newest_file else None,
                        "age_days": (datetime.now() - datetime.fromtimestamp(newest_file[1])).days if newest_file else None
                    } if newest_file else None
                },
                "cleanup_estimate": {
                    "files_to_delete": len(old_files) + len(size_limited_files),
                    "space_to_free_mb": round(old_files_size_mb + sum(f.stat().st_size for f in size_limited_files) / (1024 * 1024), 2)
                }
            }
        
        except Exception as e:
            return {
                "name": name,
                "path": str(directory),
                "exists": True,
                "error": str(e)
            }
    
    def cleanup_directory(self, name: str, config: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Clean up a specific directory"""
        directory = Path(config['path'])
        
        if not directory.exists():
            return {
                "name": name,
                "success": False,
                "error": "Directory does not exist",
                "files_processed": 0,
                "space_freed_mb": 0
            }
        
        if not config.get('enabled', True):
            return {
                "name": name,
                "success": False,
                "error": "Cleanup disabled in configuration",
                "files_processed": 0,
                "space_freed_mb": 0
            }
        
        try:
            cutoff_date = datetime.now() - timedelta(days=config['retention_days'])
            files_processed = 0
            space_freed = 0
            errors = []
            
            # Get all files matching patterns
            all_files = []
            for pattern in config['file_patterns']:
                all_files.extend(directory.rglob(pattern))
            
            # Sort by modification time (oldest first)
            all_files.sort(key=lambda f: f.stat().st_mtime)
            
            # Calculate current directory size
            current_size_mb = sum(f.stat().st_size for f in all_files if f.is_file()) / (1024 * 1024)
            
            for file_path in all_files:
                try:
                    if not file_path.is_file():
                        continue
                    
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    should_delete = False
                    reason = ""
                    
                    # Check age-based deletion
                    if file_mtime < cutoff_date:
                        should_delete = True
                        reason = f"older than {config['retention_days']} days"
                    
                    # Check size-based deletion
                    elif config.get('size_limit_mb') and current_size_mb > config['size_limit_mb']:
                        should_delete = True
                        reason = f"directory exceeds {config['size_limit_mb']} MB limit"
                    
                    if should_delete:
                        if dry_run:
                            print(f"[DRY RUN] Would delete: {file_path.name} ({reason})")
                        else:
                            file_path.unlink()
                            print(f"Deleted: {file_path.name} ({reason})")
                        
                        files_processed += 1
                        space_freed += file_size_mb
                        current_size_mb -= file_size_mb
                        
                        # Stop if we're under the size limit
                        if config.get('size_limit_mb') and current_size_mb <= config['size_limit_mb']:
                            break
                
                except Exception as e:
                    errors.append(f"Error processing {file_path}: {e}")
            
            # Remove empty directories (only if not dry run)
            if not dry_run:
                self._remove_empty_directories(directory)
            
            return {
                "name": name,
                "success": True,
                "files_processed": files_processed,
                "space_freed_mb": round(space_freed, 2),
                "directory_size_after_mb": round(current_size_mb, 2),
                "errors": errors,
                "dry_run": dry_run
            }
        
        except Exception as e:
            return {
                "name": name,
                "success": False,
                "error": str(e),
                "files_processed": 0,
                "space_freed_mb": 0
            }
    
    def _remove_empty_directories(self, directory: Path):
        """Remove empty subdirectories"""
        for dirpath in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if dirpath.is_dir() and dirpath != directory:
                try:
                    if not any(dirpath.iterdir()):
                        dirpath.rmdir()
                        print(f"Removed empty directory: {dirpath}")
                except OSError:
                    pass  # Directory not empty or other error
    
    def run_analysis(self, directories: List[str] = None):
        """Run analysis on specified directories or all"""
        config = self.load_config()
        
        print("🔍 DIRECTORY ANALYSIS REPORT")
        print("=" * 60)
        
        total_files = 0
        total_size_mb = 0
        total_cleanup_files = 0
        total_cleanup_size_mb = 0
        
        for name, dir_config in config.items():
            if directories and name not in directories:
                continue
            
            analysis = self.analyze_directory(name, dir_config)
            
            print(f"\n📁 {analysis['name'].upper()}")
            print(f"   Path: {analysis['path']}")
            print(f"   Description: {analysis.get('description', 'N/A')}")
            
            if not analysis.get('exists', False):
                print(f"   ❌ {analysis.get('error', 'Unknown error')}")
                continue
            
            if 'error' in analysis:
                print(f"   ❌ Error: {analysis['error']}")
                continue
            
            stats = analysis['statistics']
            cleanup = analysis['cleanup_estimate']
            
            print(f"   Status: {'✅ Enabled' if analysis['enabled'] else '❌ Disabled'}")
            print(f"   Files: {stats['total_files']} ({stats['total_size_mb']} MB)")
            print(f"   Retention: {analysis['retention_days']} days")
            if analysis['size_limit_mb']:
                print(f"   Size Limit: {analysis['size_limit_mb']} MB")
            print(f"   Patterns: {', '.join(analysis['file_patterns'])}")
            
            if stats['oldest_file']:
                print(f"   Oldest: {stats['oldest_file']['name']} ({stats['oldest_file']['age_days']} days)")
            
            if stats['newest_file']:
                print(f"   Newest: {stats['newest_file']['name']} ({stats['newest_file']['age_days']} days)")
            
            print(f"   🧹 Cleanup Estimate: {cleanup['files_to_delete']} files, {cleanup['space_to_free_mb']} MB")
            
            total_files += stats['total_files']
            total_size_mb += stats['total_size_mb']
            total_cleanup_files += cleanup['files_to_delete']
            total_cleanup_size_mb += cleanup['space_to_free_mb']
        
        print("\n" + "=" * 60)
        print(f"📊 SUMMARY")
        print(f"   Total Files: {total_files} ({total_size_mb:.2f} MB)")
        print(f"   Cleanup Potential: {total_cleanup_files} files ({total_cleanup_size_mb:.2f} MB)")
        print(f"   Space Savings: {(total_cleanup_size_mb / total_size_mb * 100):.1f}%" if total_size_mb > 0 else "   Space Savings: N/A")
    
    def run_cleanup(self, directories: List[str] = None, dry_run: bool = False):
        """Run cleanup on specified directories or all"""
        config = self.load_config()
        
        mode = "DRY RUN" if dry_run else "CLEANUP"
        print(f"🧹 {mode} OPERATION")
        print("=" * 60)
        
        total_files_processed = 0
        total_space_freed = 0
        
        for name, dir_config in config.items():
            if directories and name not in directories:
                continue
            
            print(f"\n📁 Processing: {name}")
            result = self.cleanup_directory(name, dir_config, dry_run)
            
            if result['success']:
                print(f"   ✅ {result['files_processed']} files, {result['space_freed_mb']} MB freed")
                if 'directory_size_after_mb' in result:
                    print(f"   📊 Directory size after: {result['directory_size_after_mb']} MB")
                
                if result.get('errors'):
                    print(f"   ⚠️  {len(result['errors'])} errors occurred")
                    for error in result['errors'][:3]:  # Show first 3 errors
                        print(f"      • {error}")
                    if len(result['errors']) > 3:
                        print(f"      • ... and {len(result['errors']) - 3} more")
                
                total_files_processed += result['files_processed']
                total_space_freed += result['space_freed_mb']
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        print(f"\n{'=' * 60}")
        print(f"📊 {mode} SUMMARY")
        print(f"   Files Processed: {total_files_processed}")
        print(f"   Space Freed: {total_space_freed:.2f} MB")
        
        if not dry_run and total_files_processed > 0:
            print(f"   🎉 Cleanup completed successfully!")
        elif dry_run:
            print(f"   💡 Run without --dry-run to execute cleanup")


def main():
    parser = argparse.ArgumentParser(description="Config Backup Directory Cleanup Utility")
    parser.add_argument('--analyze', action='store_true', help='Analyze directories without cleaning')
    parser.add_argument('--cleanup', action='store_true', help='Perform cleanup operation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    parser.add_argument('--directories', nargs='+', help='Specific directories to process')
    parser.add_argument('--create-config', action='store_true', help='Create default configuration file')
    parser.add_argument('--list-config', action='store_true', help='List current configuration')
    
    args = parser.parse_args()
    
    utility = ConfigCleanupUtility()
    
    if args.create_config:
        utility.create_config_file()
        return
    
    if args.list_config:
        config = utility.load_config()
        print("📋 CURRENT CONFIGURATION")
        print("=" * 60)
        for name, dir_config in config.items():
            print(f"\n{name}:")
            for key, value in dir_config.items():
                print(f"  {key}: {value}")
        return
    
    if args.analyze:
        utility.run_analysis(args.directories)
    elif args.cleanup or args.dry_run:
        utility.run_cleanup(args.directories, args.dry_run)
    else:
        # Default to analysis
        print("💡 No action specified, running analysis...")
        print("💡 Use --cleanup to perform cleanup, --dry-run to simulate")
        print()
        utility.run_analysis(args.directories)


if __name__ == "__main__":
    main()
