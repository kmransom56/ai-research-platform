#!/usr/bin/env python3
"""
Automated Secret Replacer for AI Research Platform
Replaces hardcoded secrets with environment variable references
"""

import re
import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import shutil
import difflib

@dataclass
class ReplacementRule:
    name: str
    pattern: str
    replacement: str
    file_types: List[str]
    description: str
    confidence: float
    test_examples: List[str]

class SecretReplacer:
    """Automated secret replacement with safety checks"""
    
    def __init__(self):
        self.replacement_rules = [
            ReplacementRule(
                name="openai_api_key",
                pattern=r'"(apiKey|APIKey|api_key)":\s*"sk-[a-zA-Z0-9]{48,}"',
                replacement=r'"\1": "${OPENAI_API_KEY}"',
                file_types=['.json'],
                description="OpenAI API Key in JSON",
                confidence=0.95,
                test_examples=[
                    '"apiKey": "sk-abc123..."',
                    '"APIKey": "sk-xyz789..."'
                ]
            ),
            ReplacementRule(
                name="openai_raw_key",
                pattern=r'sk-[a-zA-Z0-9]{48,}',
                replacement='${OPENAI_API_KEY}',
                file_types=['.py', '.js', '.ts', '.env'],
                description="Raw OpenAI API Key",
                confidence=0.9,
                test_examples=['sk-abc123def456...']
            ),
            ReplacementRule(
                name="anthropic_api_key",
                pattern=r'"(apiKey|APIKey|api_key)":\s*"sk-ant-api03-[a-zA-Z0-9\-_]{95}"',
                replacement=r'"\1": "${ANTHROPIC_API_KEY}"',
                file_types=['.json'],
                description="Anthropic API Key in JSON",
                confidence=0.95,
                test_examples=['"apiKey": "sk-ant-api03-..."']
            ),
            ReplacementRule(
                name="github_token_json",
                pattern=r'"(token|githubToken|github_token)":\s*"gh[pousr]_[A-Za-z0-9]{36}"',
                replacement=r'"\1": "${GITHUB_TOKEN}"',
                file_types=['.json'],
                description="GitHub Token in JSON",
                confidence=0.9,
                test_examples=['"token": "ghp_abc123..."']
            ),
            ReplacementRule(
                name="github_token_raw",
                pattern=r'gh[pousr]_[A-Za-z0-9]{36}',
                replacement='${GITHUB_TOKEN}',
                file_types=['.py', '.js', '.ts', '.env'],
                description="Raw GitHub Token",
                confidence=0.85,
                test_examples=['ghp_abc123def456...']
            ),
            ReplacementRule(
                name="google_api_key_json",
                pattern=r'"(apiKey|APIKey|api_key|googleApiKey)":\s*"AIza[0-9A-Za-z\\-_]{35}"',
                replacement=r'"\1": "${GOOGLE_API_KEY}"',
                file_types=['.json'],
                description="Google API Key in JSON",
                confidence=0.8,
                test_examples=['"apiKey": "AIza..."']
            ),
            ReplacementRule(
                name="password_json",
                pattern=r'"(password|Password)":\s*"[^"]{8,}"',
                replacement=r'"\1": "${DATABASE_PASSWORD}"',
                file_types=['.json'],
                description="Password in JSON (generic)",
                confidence=0.6,
                test_examples=['"password": "secretpass123"']
            ),
            ReplacementRule(
                name="neo4j_auth",
                pattern=r'NEO4J_AUTH=neo4j/[^\s\'"]+',
                replacement='NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}',
                file_types=['.yml', '.yaml', '.env'],
                description="Neo4j Authentication",
                confidence=0.9,
                test_examples=['NEO4J_AUTH=neo4j/password123']
            ),
            ReplacementRule(
                name="connection_string",
                pattern=r'(mongodb|postgresql|mysql)://([^:]+):([^@]+)@([^/\s]+)',
                replacement=r'\1://${DB_USER}:${DB_PASSWORD}@\4',
                file_types=['.py', '.js', '.ts', '.json', '.env'],
                description="Database Connection String",
                confidence=0.8,
                test_examples=['postgresql://user:pass@localhost:5432/db']
            ),
            ReplacementRule(
                name="env_assignment",
                pattern=r'(API_KEY|APIKEY|SECRET_KEY|PASSWORD)\s*=\s*["\']?([a-zA-Z0-9\-_]{15,})["\']?',
                replacement=r'\1=${SECRET_VALUE}',
                file_types=['.env'],
                description="Environment Variable Assignment",
                confidence=0.5,
                test_examples=['API_KEY=abc123def456']
            )
        ]
        
        self.exclude_patterns = [
            r'example\.com',
            r'placeholder',
            r'your[_-]?key[_-]?here',
            r'insert[_-]?key',
            r'test[_-]?key',
            r'demo[_-]?key',
            r'sample[_-]?key',
            r'fake[_-]?key',
            r'\$\{[^}]+\}',  # Already environment variable
            r'process\.env\.',  # Node.js env access
            r'os\.environ',     # Python env access
        ]
        
        self.exclude_dirs = {
            '.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv',
            'build', 'dist', '.next', 'coverage', '.pytest_cache', '.tox',
            'vendor', 'Pods', '.DS_Store', 'data/openwebui/cache'
        }

    def should_exclude_match(self, match_text: str, full_line: str) -> bool:
        """Check if match should be excluded"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, full_line, re.IGNORECASE):
                return True
        return False

    def create_backup(self, file_path: Path) -> Path:
        """Create backup of file before modification"""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        shutil.copy2(file_path, backup_path)
        return backup_path

    def replace_in_file(self, file_path: Path, dry_run: bool = True) -> Tuple[bool, List[str]]:
        """Replace secrets in a single file"""
        changes = []
        modified = False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                original_content = content
            
            applicable_rules = [
                rule for rule in self.replacement_rules 
                if file_path.suffix in rule.file_types or 
                   any(file_path.name.startswith(ft.lstrip('.')) for ft in rule.file_types if ft.startswith('.env'))
            ]
            
            for rule in applicable_rules:
                matches = list(re.finditer(rule.pattern, content))
                
                for match in matches:
                    match_text = match.group()
                    full_line = content.split('\n')[content[:match.start()].count('\n')]
                    
                    if self.should_exclude_match(match_text, full_line):
                        continue
                    
                    # Apply replacement
                    new_content = re.sub(rule.pattern, rule.replacement, content)
                    
                    if new_content != content:
                        line_num = content[:match.start()].count('\n') + 1
                        changes.append(f"Line {line_num}: {rule.description}")
                        changes.append(f"  Before: {match_text}")
                        changes.append(f"  After:  {rule.replacement}")
                        content = new_content
                        modified = True
            
            # Write changes if not dry run
            if modified and not dry_run:
                # Create backup first
                backup_path = self.create_backup(file_path)
                changes.append(f"Backup created: {backup_path}")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            changes.append(f"Error processing file: {e}")
            
        return modified, changes

    def scan_and_replace(self, directory: Path, dry_run: bool = True, 
                        file_pattern: Optional[str] = None) -> Dict:
        """Scan directory and replace secrets"""
        results = {
            'total_files_scanned': 0,
            'total_files_modified': 0,
            'files_with_changes': [],
            'summary': {},
            'errors': []
        }
        
        # Find files to process
        if file_pattern:
            files_to_process = list(directory.glob(file_pattern))
        else:
            files_to_process = []
            for rule in self.replacement_rules:
                for file_type in rule.file_types:
                    if file_type.startswith('.env'):
                        files_to_process.extend(directory.rglob('.env*'))
                    else:
                        files_to_process.extend(directory.rglob(f'*{file_type}'))
        
        # Remove duplicates and filter
        files_to_process = list(set(files_to_process))
        files_to_process = [
            f for f in files_to_process 
            if f.is_file() and not any(exc_dir in f.parts for exc_dir in self.exclude_dirs)
        ]
        
        results['total_files_scanned'] = len(files_to_process)
        
        for file_path in files_to_process:
            try:
                modified, changes = self.replace_in_file(file_path, dry_run)
                
                if modified:
                    results['total_files_modified'] += 1
                    results['files_with_changes'].append({
                        'file': str(file_path.relative_to(directory)),
                        'changes': changes
                    })
                    
            except Exception as e:
                results['errors'].append(f"Error processing {file_path}: {e}")
        
        # Generate summary
        rule_usage = {}
        for file_info in results['files_with_changes']:
            for change in file_info['changes']:
                if 'Line' in change and ':' in change:
                    rule_desc = change.split(': ', 1)[1]
                    rule_usage[rule_desc] = rule_usage.get(rule_desc, 0) + 1
        
        results['summary'] = {
            'dry_run': dry_run,
            'replacements_by_type': rule_usage,
            'files_modified': results['total_files_modified'],
            'files_scanned': results['total_files_scanned']
        }
        
        return results

    def generate_diff_report(self, file_path: Path) -> str:
        """Generate diff report for a file"""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        
        if not backup_path.exists():
            return f"No backup found for {file_path}"
        
        try:
            with open(backup_path, 'r') as f:
                original_lines = f.readlines()
            with open(file_path, 'r') as f:
                modified_lines = f.readlines()
            
            diff = difflib.unified_diff(
                original_lines,
                modified_lines,
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (modified)",
                lineterm=''
            )
            
            return '\n'.join(diff)
            
        except Exception as e:
            return f"Error generating diff: {e}"

    def restore_from_backup(self, file_path: Path) -> bool:
        """Restore file from backup"""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        
        if not backup_path.exists():
            print(f"No backup found for {file_path}")
            return False
        
        try:
            shutil.copy2(backup_path, file_path)
            print(f"Restored {file_path} from backup")
            return True
        except Exception as e:
            print(f"Error restoring {file_path}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Automated Secret Replacer for AI Research Platform')
    parser.add_argument('path', nargs='?', default='.', help='Path to process (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--apply', action='store_true', help='Actually apply the changes (opposite of dry-run)')
    parser.add_argument('--pattern', help='File pattern to process (e.g., "*.json")')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--diff', help='Generate diff report for specific file')
    parser.add_argument('--restore', help='Restore file from backup')
    parser.add_argument('--cleanup-backups', action='store_true', help='Remove all backup files')
    
    args = parser.parse_args()
    
    replacer = SecretReplacer()
    process_path = Path(args.path)
    
    # Handle special operations
    if args.diff:
        diff_file = Path(args.diff)
        diff_report = replacer.generate_diff_report(diff_file)
        print(diff_report)
        return
    
    if args.restore:
        restore_file = Path(args.restore)
        replacer.restore_from_backup(restore_file)
        return
    
    if args.cleanup_backups:
        backup_files = list(process_path.rglob('*.backup'))
        for backup in backup_files:
            backup.unlink()
            print(f"Removed backup: {backup}")
        print(f"Cleaned up {len(backup_files)} backup files")
        return
    
    # Determine if this is a dry run
    dry_run = not args.apply
    if args.dry_run:
        dry_run = True
    
    # Process files
    print(f"🔄 {'Dry run - analyzing' if dry_run else 'Applying'} secret replacements...")
    print(f"📂 Processing: {process_path}")
    
    results = replacer.scan_and_replace(process_path, dry_run, args.pattern)
    
    # Generate report
    report = f"""
🔐 Secret Replacement Report
{'=' * 50}

📊 Summary:
  Files Scanned: {results['total_files_scanned']}
  Files Modified: {results['total_files_modified']}
  Mode: {'DRY RUN' if dry_run else 'APPLIED CHANGES'}

📋 Replacements by Type:
"""
    
    for rule_type, count in results['summary']['replacements_by_type'].items():
        report += f"  {rule_type}: {count}\n"
    
    report += "\n📁 Files with Changes:\n"
    for file_info in results['files_with_changes']:
        report += f"\n  📄 {file_info['file']}\n"
        for change in file_info['changes']:
            report += f"    {change}\n"
    
    if results['errors']:
        report += "\n❌ Errors:\n"
        for error in results['errors']:
            report += f"  {error}\n"
    
    if dry_run and results['total_files_modified'] > 0:
        report += f"""
🚀 Next Steps:
  To apply these changes, run:
  python {sys.argv[0]} {args.path} --apply
  
  To see specific diffs:
  python {sys.argv[0]} --diff <filename>
  
  To restore from backup:
  python {sys.argv[0]} --restore <filename>
"""
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"📄 Report saved to {args.output}")
    else:
        print(report)
    
    # Exit codes
    if results['errors']:
        sys.exit(1)
    elif results['total_files_modified'] > 0:
        print("✅ Secret replacement completed successfully!")
    else:
        print("ℹ️  No secrets found to replace")

if __name__ == '__main__':
    main()