#!/usr/bin/env python3
"""
Debug Configuration Tool
Diagnoses and fixes configuration issues
"""

import json
import sys
from pathlib import Path

def debug_config():
    """Debug and fix configuration issues"""
    platform_dir = Path("/home/keith/chat-copilot")
    config_file = platform_dir / "config" / "cleanup_config.json"
    
    print("🔍 Debugging Configuration Issues")
    print(f"Platform Directory: {platform_dir}")
    print(f"Config File: {config_file}")
    
    # Check if config file exists
    if config_file.exists():
        print(f"✅ Config file exists: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            print(f"✅ Config file is valid JSON")
            print(f"Config structure: {type(config_data)}")
            print(f"Config keys: {list(config_data.keys()) if isinstance(config_data, dict) else 'Not a dictionary!'}")
            
            # Check if this is old format (no 'directories' section)
            if 'directories' not in config_data:
                print("🔄 Found old config format, migrating to new format...")
                migrate_old_config(config_data, config_file)
            else:
                # Check directories section
                directories = config_data['directories']
                print(f"Directories section type: {type(directories)}")
                
                if isinstance(directories, dict):
                    print(f"Directory names: {list(directories.keys())}")
                    
                    for name, config in directories.items():
                        print(f"  {name}: {type(config)} - {config}")
                        if not isinstance(config, dict):
                            print(f"    ❌ ERROR: {name} config is {type(config)}, should be dict!")
                else:
                    print(f"❌ ERROR: 'directories' is {type(directories)}, should be dict!")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Config file has invalid JSON: {e}")
            backup_and_create_new()
        except Exception as e:
            print(f"❌ Error reading config: {e}")
            backup_and_create_new()
    else:
        print(f"ℹ️  Config file doesn't exist, will create new one")
        create_fresh_config()

def migrate_old_config(old_config, config_file):
    """Migrate old flat config format to new nested format"""
    platform_dir = Path("/home/keith/chat-copilot")
    
    print("🔄 Migrating old configuration format...")
    
    # Create backup
    backup_file = config_file.with_suffix('.json.old')
    with open(backup_file, 'w') as f:
        json.dump(old_config, f, indent=2)
    print(f"✅ Backed up old config to: {backup_file}")
    
    # Convert old format to new format
    new_config = {
        "directories": {},
        "logging": {
            "level": "INFO",
            "file": str(platform_dir / "logs" / "cleanup.log")
        }
    }
    
    # Migrate each directory config
    for dir_name, dir_config in old_config.items():
        if isinstance(dir_config, dict):
            # Ensure path is correct (under platform directory)
            if 'path' in dir_config:
                old_path = dir_config['path']
                if not old_path.startswith(str(platform_dir)):
                    # Update path to be under platform directory
                    new_path = str(platform_dir / dir_name)
                    print(f"  🔄 Updating path for {dir_name}: {old_path} → {new_path}")
                    dir_config['path'] = new_path
            else:
                # Add missing path
                dir_config['path'] = str(platform_dir / dir_name)
                print(f"  ➕ Added missing path for {dir_name}: {dir_config['path']}")
            
            # Ensure required fields exist
            if 'enabled' not in dir_config:
                dir_config['enabled'] = True
            if 'max_age_days' not in dir_config:
                dir_config['max_age_days'] = 30
            if 'max_files' not in dir_config:
                dir_config['max_files'] = 100
                
            new_config['directories'][dir_name] = dir_config
            print(f"  ✅ Migrated {dir_name}: {dir_config}")
        else:
            print(f"  ⚠️  Skipping {dir_name}: invalid config type {type(dir_config)}")
    
    # Write new config
    with open(config_file, 'w') as f:
        json.dump(new_config, f, indent=2)
    
    print(f"✅ Migration complete! New config saved to: {config_file}")
    return new_config

def backup_and_create_new():
    """Backup corrupted config and create fresh one"""
    platform_dir = Path("/home/keith/chat-copilot")
    config_file = platform_dir / "config" / "cleanup_config.json"
    
    # Create backup
    backup_file = config_file.with_suffix('.json.backup')
    if config_file.exists():
        config_file.rename(backup_file)
        print(f"✅ Backed up corrupted config to: {backup_file}")
    
    create_fresh_config()

def create_fresh_config():
    """Create a fresh, clean configuration"""
    platform_dir = Path("/home/keith/chat-copilot")
    config_file = platform_dir / "config" / "cleanup_config.json"
    
    # Ensure directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create fresh config
    fresh_config = {
        "directories": {
            "config-backups": {
                "path": str(platform_dir / "config-backups"),
                "enabled": True,
                "max_age_days": 30,
                "max_files": 100
            },
            "config-backups-auto": {
                "path": str(platform_dir / "config-backups-auto"),
                "enabled": True,
                "max_age_days": 7,
                "max_files": 50
            },
            "config-snapshots": {
                "path": str(platform_dir / "config-snapshots"),
                "enabled": True,
                "max_age_days": 14,
                "max_files": 20
            },
            "platform-logs": {
                "path": str(platform_dir / "logs"),
                "enabled": True,
                "max_age_days": 30,
                "max_files": 100
            }
        },
        "logging": {
            "level": "INFO",
            "file": str(platform_dir / "logs" / "cleanup.log")
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(fresh_config, f, indent=2)
    
    print(f"✅ Created fresh config file: {config_file}")
    
    # Verify the new config
    with open(config_file, 'r') as f:
        verify_config = json.load(f)
    
    print(f"✅ Verified new config structure")
    for name, config in verify_config['directories'].items():
        print(f"  {name}: {config['path']} (enabled: {config['enabled']})")

def test_cleanup():
    """Test the cleanup utility with fresh config"""
    print("\n🧪 Testing Cleanup Utility")
    
    try:
        from config_cleanup_utility import ConfigCleanupUtility
        cleanup = ConfigCleanupUtility()
        
        # Test loading config
        config = cleanup.load_config()
        print(f"✅ Config loaded successfully")
        print(f"Directories configured: {len(config.get('directories', {}))}")
        
        # Check available methods
        available_methods = [method for method in dir(cleanup) if not method.startswith('_')]
        print(f"Available methods: {available_methods}")
        
        # Test cleanup using the correct method
        if hasattr(cleanup, 'cleanup_directories'):
            print("\n🧪 Testing directory cleanup...")
            total_files, total_size = cleanup.cleanup_directories()
            print(f"✅ Cleanup test successful: {total_files} files, {total_size:.2f} MB")
        elif hasattr(cleanup, 'cleanup_directory'):
            print("\n🧪 Testing individual directory cleanup...")
            total_files = 0
            total_size = 0.0
            directories = config.get('directories', {})
            
            for dir_name, dir_config in directories.items():
                if dir_config.get('enabled', True):
                    files, size = cleanup.cleanup_directory(dir_name, dir_config)
                    total_files += files
                    total_size += size
            
            print(f"✅ Manual cleanup test successful: {total_files} files, {total_size:.2f} MB")
        else:
            print("❌ No cleanup method found")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("ℹ️  Make sure config_cleanup_utility.py exists in the current directory")
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_config()
    test_cleanup()
