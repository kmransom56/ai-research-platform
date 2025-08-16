#!/usr/bin/env python3
"""
Advanced Secret Scanner for AI Research Platform
Detects hardcoded API keys, passwords, and sensitive data
"""

import re
import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SecretMatch:
    file_path: str
    line_number: int
    secret_type: str
    pattern_name: str
    match_text: str
    context_before: str
    context_after: str
    severity: str
    confidence: float

class SecretScanner:
    """Advanced secret scanner with multiple detection patterns"""
    
    def __init__(self):
        self.patterns = {
            # API Keys
            'openai_api_key': {
                'pattern': r'sk-[a-zA-Z0-9]{48,}',
                'severity': 'critical',
                'confidence': 0.95,
                'description': 'OpenAI API Key'
            },
            'anthropic_api_key': {
                'pattern': r'sk-ant-api03-[a-zA-Z0-9\-_]{95}',
                'severity': 'critical', 
                'confidence': 0.95,
                'description': 'Anthropic API Key'
            },
            'github_token': {
                'pattern': r'gh[pousr]_[A-Za-z0-9]{36}',
                'severity': 'critical',
                'confidence': 0.9,
                'description': 'GitHub Personal Access Token'
            },
            'slack_token': {
                'pattern': r'xoxb-[0-9]+-[0-9]+-[0-9]+-[a-zA-Z0-9]+',
                'severity': 'high',
                'confidence': 0.85,
                'description': 'Slack Bot Token'
            },
            'google_api_key': {
                'pattern': r'AIza[0-9A-Za-z\\-_]{35}',
                'severity': 'high',
                'confidence': 0.8,
                'description': 'Google API Key'
            },
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'severity': 'critical',
                'confidence': 0.9,
                'description': 'AWS Access Key ID'
            },
            'azure_key': {
                'pattern': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                'severity': 'medium',
                'confidence': 0.6,
                'description': 'Azure Key (UUID format)'
            },
            
            # JSON/YAML patterns
            'json_api_key': {
                'pattern': r'"(apiKey|api_key|APIKey)":\s*"[a-zA-Z0-9\-_]{20,}"',
                'severity': 'high',
                'confidence': 0.7,
                'description': 'JSON API Key field'
            },
            'json_secret': {
                'pattern': r'"(secret|secretKey|secret_key)":\s*"[a-zA-Z0-9\-_]{15,}"',
                'severity': 'high',
                'confidence': 0.7,
                'description': 'JSON Secret field'
            },
            'json_password': {
                'pattern': r'"(password|Password)":\s*"[^"]{8,}"',
                'severity': 'medium',
                'confidence': 0.6,
                'description': 'JSON Password field'
            },
            
            # Environment variable assignments
            'env_api_key': {
                'pattern': r'(API_KEY|APIKEY|SECRET_KEY|PASSWORD)\s*=\s*["\']?[a-zA-Z0-9\-_]{15,}["\']?',
                'severity': 'medium',
                'confidence': 0.5,
                'description': 'Environment Variable Assignment'
            },
            
            # Connection strings
            'connection_string': {
                'pattern': r'(mongodb|postgresql|mysql)://[^:\s]+:[^@\s]+@[^/\s]+',
                'severity': 'high',
                'confidence': 0.8,
                'description': 'Database Connection String with Credentials'
            },
            
            # Generic high-entropy strings
            'high_entropy': {
                'pattern': r'[a-zA-Z0-9+/]{40,}={0,2}',
                'severity': 'low',
                'confidence': 0.3,
                'description': 'High-entropy string (possible encoded secret)'
            }
        }
        
        self.exclude_patterns = [
            r'example\.com',
            r'placeholder',
            r'your[_-]?key[_-]?here',
            r'insert[_-]?key',
            r'test[_-]?key',
            r'demo[_-]?key',
            r'sample[_-]?key',
            r'fake[_-]?key',
            r'dummy[_-]?data',
            r'lorem[_-]?ipsum',
            r'XXXXXXX',
            r'0{10,}',
            r'1{10,}',
        ]
        
        self.exclude_dirs = {
            '.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv',
            'build', 'dist', '.next', 'coverage', '.pytest_cache', '.tox',
            'vendor', 'Pods', '.DS_Store', 'data/openwebui/cache'
        }
        
        self.include_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yml', '.yaml',
            '.env', '.conf', '.config', '.ini', '.toml', '.xml', '.sh', '.bash'
        }

    def should_exclude_match(self, match_text: str) -> bool:
        """Check if match should be excluded based on common false positives"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, match_text, re.IGNORECASE):
                return True
        return False

    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        import math
        if not text:
            return 0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        entropy = 0
        text_len = len(text)
        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)
        
        return entropy

    def scan_file(self, file_path: Path) -> List[SecretMatch]:
        """Scan a single file for secrets"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                for pattern_name, pattern_info in self.patterns.items():
                    pattern = pattern_info['pattern']
                    
                    for match in re.finditer(pattern, line, re.IGNORECASE):
                        match_text = match.group()
                        
                        # Skip excluded matches
                        if self.should_exclude_match(match_text):
                            continue
                        
                        # Additional entropy check for high-entropy patterns
                        if pattern_name == 'high_entropy':
                            entropy = self.calculate_entropy(match_text)
                            if entropy < 4.5:  # Threshold for likely secrets
                                continue
                        
                        # Get context
                        context_before = lines[max(0, line_num-2):line_num-1]
                        context_after = lines[line_num:min(len(lines), line_num+2)]
                        
                        matches.append(SecretMatch(
                            file_path=str(file_path.relative_to(Path.cwd())),
                            line_number=line_num,
                            secret_type=pattern_info['description'],
                            pattern_name=pattern_name,
                            match_text=match_text[:50] + '...' if len(match_text) > 50 else match_text,
                            context_before=''.join(context_before).strip(),
                            context_after=''.join(context_after).strip(),
                            severity=pattern_info['severity'],
                            confidence=pattern_info['confidence']
                        ))
                        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            
        return matches

    def scan_directory(self, directory: Path) -> List[SecretMatch]:
        """Scan entire directory tree for secrets"""
        all_matches = []
        
        for file_path in directory.rglob('*'):
            # Skip directories and excluded directories
            if file_path.is_dir():
                continue
            
            if any(exc_dir in file_path.parts for exc_dir in self.exclude_dirs):
                continue
            
            # Check file extension
            if file_path.suffix not in self.include_extensions and not file_path.name.startswith('.env'):
                continue
            
            # Skip large files (>10MB)
            try:
                if file_path.stat().st_size > 10 * 1024 * 1024:
                    continue
            except:
                continue
            
            matches = self.scan_file(file_path)
            all_matches.extend(matches)
            
        return all_matches

    def generate_report(self, matches: List[SecretMatch], output_format: str = 'json') -> str:
        """Generate report in specified format"""
        
        if output_format == 'json':
            report = {
                'scan_timestamp': datetime.now().isoformat(),
                'total_matches': len(matches),
                'severity_breakdown': self._get_severity_breakdown(matches),
                'matches': [asdict(match) for match in matches]
            }
            return json.dumps(report, indent=2)
        
        elif output_format == 'markdown':
            return self._generate_markdown_report(matches)
        
        elif output_format == 'text':
            return self._generate_text_report(matches)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _get_severity_breakdown(self, matches: List[SecretMatch]) -> Dict[str, int]:
        """Get count of matches by severity"""
        breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for match in matches:
            breakdown[match.severity] += 1
        return breakdown

    def _generate_markdown_report(self, matches: List[SecretMatch]) -> str:
        """Generate markdown report"""
        severity_breakdown = self._get_severity_breakdown(matches)
        
        report = f"""# 🔐 Secret Scan Report

**Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Secrets Found**: {len(matches)}

## 📊 Severity Breakdown

| Severity | Count |
|----------|-------|
| 🔴 Critical | {severity_breakdown['critical']} |
| 🟠 High | {severity_breakdown['high']} |
| 🟡 Medium | {severity_breakdown['medium']} |
| 🟢 Low | {severity_breakdown['low']} |

## 📋 Detailed Findings

"""
        
        for match in sorted(matches, key=lambda x: (x.severity, x.file_path)):
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🟢'
            }[match.severity]
            
            report += f"""
### {severity_emoji} {match.secret_type}

- **File**: `{match.file_path}:{match.line_number}`
- **Pattern**: {match.pattern_name}
- **Confidence**: {match.confidence:.0%}
- **Match**: `{match.match_text}`

"""
        
        return report

    def _generate_text_report(self, matches: List[SecretMatch]) -> str:
        """Generate plain text report"""
        report = f"SECRET SCAN REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        severity_breakdown = self._get_severity_breakdown(matches)
        report += f"TOTAL SECRETS FOUND: {len(matches)}\n\n"
        
        report += "SEVERITY BREAKDOWN:\n"
        for severity, count in severity_breakdown.items():
            report += f"  {severity.upper()}: {count}\n"
        
        report += "\nDETAILED FINDINGS:\n"
        report += "-" * 40 + "\n"
        
        for i, match in enumerate(matches, 1):
            report += f"\n{i}. [{match.severity.upper()}] {match.secret_type}\n"
            report += f"   File: {match.file_path}:{match.line_number}\n"
            report += f"   Match: {match.match_text}\n"
            report += f"   Confidence: {match.confidence:.0%}\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Advanced Secret Scanner for AI Research Platform')
    parser.add_argument('path', nargs='?', default='.', help='Path to scan (default: current directory)')
    parser.add_argument('--format', choices=['json', 'markdown', 'text'], default='text', 
                       help='Output format (default: text)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'], 
                       help='Filter by minimum severity')
    parser.add_argument('--confidence', type=float, default=0.0, 
                       help='Filter by minimum confidence (0.0-1.0)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    parser.add_argument('--stats-only', action='store_true', help='Show only statistics')
    
    args = parser.parse_args()
    
    scanner = SecretScanner()
    scan_path = Path(args.path)
    
    if not args.quiet:
        print(f"🔍 Scanning {scan_path} for secrets...")
    
    # Perform scan
    if scan_path.is_file():
        matches = scanner.scan_file(scan_path)
    else:
        matches = scanner.scan_directory(scan_path)
    
    # Apply filters
    if args.severity:
        severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        min_severity = severity_order[args.severity]
        matches = [m for m in matches if severity_order[m.severity] >= min_severity]
    
    if args.confidence > 0:
        matches = [m for m in matches if m.confidence >= args.confidence]
    
    # Generate report
    if args.stats_only:
        severity_breakdown = scanner._get_severity_breakdown(matches)
        print(f"Total secrets found: {len(matches)}")
        for severity, count in severity_breakdown.items():
            if count > 0:
                print(f"  {severity.capitalize()}: {count}")
    else:
        report = scanner.generate_report(matches, args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            if not args.quiet:
                print(f"📄 Report saved to {args.output}")
        else:
            print(report)
    
    # Exit with error code if secrets found
    if matches:
        severity_breakdown = scanner._get_severity_breakdown(matches)
        if severity_breakdown['critical'] > 0 or severity_breakdown['high'] > 0:
            sys.exit(1)  # Exit with error for critical/high severity secrets
    
    sys.exit(0)

if __name__ == '__main__':
    main()