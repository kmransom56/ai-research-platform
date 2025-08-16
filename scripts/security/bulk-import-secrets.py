#!/usr/bin/env python3
"""
Bulk Secret Import Script for AI Research Platform
Python version with enhanced parsing and validation

Usage:
  python3 bulk-import-secrets.py [secrets_file] [options]
"""

import os
import re
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

@dataclass
class SecretEntry:
    name: str
    value: str
    line_number: int
    description: str = ""

class SecretImporter:
    """Bulk secret importer with validation and GitHub integration"""
    
    def __init__(self):
        self.repo_owner = self.get_repo_info()[0]
        self.repo_name = self.get_repo_info()[1]
        self.existing_secrets: Set[str] = set()
    
    def get_repo_info(self) -> Tuple[str, str]:
        """Get repository owner and name from git config"""
        try:
            # Try environment variables first
            owner = os.getenv('GITHUB_REPOSITORY_OWNER', '')
            name = os.getenv('GITHUB_REPOSITORY_NAME', '')
            
            if owner and name:
                return owner, name
            
            # Fall back to git config
            origin_url = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Parse GitHub URL
            if 'github.com' in origin_url:
                if origin_url.startswith('git@'):
                    # SSH format: git@github.com:owner/repo.git
                    parts = origin_url.split(':')[1].replace('.git', '').split('/')
                elif origin_url.startswith('https://'):
                    # HTTPS format: https://github.com/owner/repo.git
                    parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                else:
                    return '', ''
                
                if len(parts) >= 2:
                    return parts[0], parts[1]
            
            return '', ''
        except Exception:
            return '', ''
    
    def check_gh_cli(self) -> bool:
        """Check if GitHub CLI is available and authenticated"""
        try:
            subprocess.run(['gh', '--version'], 
                         capture_output=True, check=True)
            subprocess.run(['gh', 'auth', 'status'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_existing_secrets(self) -> Set[str]:
        """Get list of existing repository secrets"""
        try:
            result = subprocess.run([
                'gh', 'secret', 'list', 
                '--repo', f'{self.repo_owner}/{self.repo_name}',
                '--json', 'name', '-q', '.[].name'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return set(line.strip() for line in result.stdout.strip().split('\n') if line.strip())
            return set()
        except Exception:
            return set()
    
    def parse_secrets_file(self, file_path: str) -> Tuple[List[SecretEntry], List[str]]:
        """Parse secrets file and return secrets and validation errors"""
        secrets = []
        errors = []
        seen_names = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            errors.append(f"Failed to read file: {e}")
            return secrets, errors
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse SECRET_NAME=value format
            if '=' not in line:
                errors.append(f"Line {line_num}: No '=' found - {line}")
                continue
            
            name, value = line.split('=', 1)
            name = name.strip()
            value = value.strip()
            
            # Validate secret name format
            if not re.match(r'^[A-Z_][A-Z0-9_]*$', name):
                errors.append(f"Line {line_num}: Invalid secret name format - {name}")
                continue
            
            # Check for empty values
            if not value:
                errors.append(f"Line {line_num}: Empty value for {name}")
                continue
            
            # Check for duplicates
            if name in seen_names:
                errors.append(f"Line {line_num}: Duplicate secret name - {name}")
                continue
            
            seen_names.add(name)
            
            # Extract description from value if it contains it
            description = ""
            if ' # ' in value:
                value, description = value.split(' # ', 1)
                value = value.strip()
                description = description.strip()
            
            secrets.append(SecretEntry(
                name=name,
                value=value,
                line_number=line_num,
                description=description
            ))
        
        return secrets, errors
    
    def validate_secret_value(self, secret: SecretEntry) -> List[str]:
        """Validate individual secret values and provide warnings"""
        warnings = []
        
        # Check for common test/placeholder values
        test_patterns = [
            'your_.*_here',
            'test_.*',
            'example_.*',
            'placeholder',
            'sample_.*',
            'demo_.*'
        ]
        
        for pattern in test_patterns:
            if re.match(pattern, secret.value, re.IGNORECASE):
                warnings.append(f"{secret.name}: Appears to be a placeholder value")
                break
        
        # Check for suspicious patterns
        if len(secret.value) < 8:
            warnings.append(f"{secret.name}: Value seems too short for a secure secret")
        
        # Validate specific secret types
        if 'OPENAI' in secret.name and not secret.value.startswith('sk-'):
            warnings.append(f"{secret.name}: OpenAI keys should start with 'sk-'")
        
        if 'GITHUB' in secret.name and not secret.value.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
            warnings.append(f"{secret.name}: GitHub tokens should start with 'gh*_'")
        
        if 'ANTHROPIC' in secret.name and not secret.value.startswith('sk-ant-'):
            warnings.append(f"{secret.name}: Anthropic keys should start with 'sk-ant-'")
        
        return warnings
    
    def import_secret(self, secret: SecretEntry, dry_run: bool = False) -> bool:
        """Import a single secret to GitHub"""
        if dry_run:
            return True
        
        try:
            process = subprocess.Popen([
                'gh', 'secret', 'set', secret.name,
                '--repo', f'{self.repo_owner}/{self.repo_name}'
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
               stderr=subprocess.PIPE, text=True)
            
            stdout, stderr = process.communicate(input=secret.value)
            return process.returncode == 0
            
        except Exception:
            return False
    
    def create_secrets_template(self, output_file: str):
        """Create a comprehensive secrets template file"""
        template_content = '''# Secret Import File for AI Research Platform
# Format: SECRET_NAME=secret_value
# Lines starting with # are comments and will be ignored
# Empty lines are also ignored

# =============================================================================
# AI SERVICE API KEYS
# =============================================================================

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_ORG_ID=org-your_org_id_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-api03-your_anthropic_key_here

# Azure OpenAI
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Google AI
GEMINI_API_KEY=AIza_your_gemini_key_here
GOOGLE_API_KEY=AIza_your_google_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path_to_service_account_json

# Other AI Services
LANGCHAIN_API_KEY=your_langchain_key_here
COHERE_API_KEY=your_cohere_key_here
HUGGINGFACE_API_KEY=hf_your_huggingface_key_here
REPLICATE_API_TOKEN=r8_your_replicate_token_here

# =============================================================================
# DATABASE CREDENTIALS
# =============================================================================

# Neo4j
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# PostgreSQL
POSTGRES_PASSWORD=your_postgres_password_here
POSTGRES_USER=postgres
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# MongoDB
MONGODB_CONNECTION_STRING=mongodb://user:pass@localhost:27017/db
MONGODB_PASSWORD=your_mongodb_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here
REDIS_URL=redis://localhost:6379

# =============================================================================
# MESSAGE QUEUE & CACHE
# =============================================================================

# RabbitMQ
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=your_rabbitmq_password_here
RABBITMQ_DEFAULT_VHOST=/

# Apache Kafka
KAFKA_PASSWORD=your_kafka_password_here
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# =============================================================================
# APPLICATION SECRETS
# =============================================================================

# JWT & Session
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# Application Services
OPENWEBUI_SECRET_KEY=your_openwebui_secret_here
VSCODE_PASSWORD=your_vscode_password_here
NEXTAUTH_SECRET=your_nextauth_secret_here

# =============================================================================
# EXTERNAL SERVICE API KEYS
# =============================================================================

# GitHub
GITHUB_TOKEN=ghp_your_github_token_here
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# Communication Services
SLACK_BOT_TOKEN=xoxb-your_slack_bot_token_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
DISCORD_BOT_TOKEN=your_discord_bot_token_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Email Services
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
MAILGUN_API_KEY=key-your_mailgun_api_key_here
SMTP_PASSWORD=your_smtp_password_here

# =============================================================================
# CLOUD SERVICE KEYS
# =============================================================================

# AWS
AWS_ACCESS_KEY_ID=AKIA_your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-west-2

# Azure
AZURE_CLIENT_ID=your_azure_client_id_here
AZURE_CLIENT_SECRET=your_azure_client_secret_here
AZURE_TENANT_ID=your_azure_tenant_id_here

# Google Cloud Platform
GCP_SERVICE_ACCOUNT_KEY=your_gcp_service_account_key_here
GOOGLE_CLOUD_PROJECT=your_project_id_here

# =============================================================================
# MONITORING & ANALYTICS
# =============================================================================

# Application Monitoring
SENTRY_DSN=your_sentry_dsn_here
DATADOG_API_KEY=your_datadog_api_key_here
NEW_RELIC_LICENSE_KEY=your_newrelic_license_key_here

# Analytics
GOOGLE_ANALYTICS_ID=GA-your_analytics_id_here
MIXPANEL_TOKEN=your_mixpanel_token_here

# =============================================================================
# CUSTOM APPLICATION KEYS
# =============================================================================

# Add your additional 31 keys here following the same format
# CUSTOM_API_KEY_1=your_custom_key_1_here
# CUSTOM_SERVICE_TOKEN=your_service_token_here
# THIRD_PARTY_API_KEY=your_third_party_key_here

# Example additional keys:
# WEATHER_API_KEY=your_weather_api_key_here
# PAYMENT_GATEWAY_SECRET=your_payment_secret_here
# CDN_ACCESS_KEY=your_cdn_access_key_here
'''

        try:
            with open(output_file, 'w') as f:
                f.write(template_content)
            return True
        except Exception as e:
            print(f"❌ Failed to create template: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Bulk Secret Import for AI Research Platform')
    parser.add_argument('secrets_file', nargs='?', 
                       default='configs/secrets-import.txt',
                       help='Path to secrets file (default: configs/secrets-import.txt)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be imported without doing it')
    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite existing secrets')
    parser.add_argument('--validate', action='store_true',
                       help='Only validate file format')
    parser.add_argument('--create-template', metavar='FILE',
                       help='Create a secrets template file')
    parser.add_argument('--format', choices=['table', 'json'], default='table',
                       help='Output format for validation results')
    
    args = parser.parse_args()
    
    importer = SecretImporter()
    
    print("🔐 Bulk Secret Import for AI Research Platform")
    print("===============================================")
    print()
    
    # Handle template creation
    if args.create_template:
        print(f"📝 Creating secrets template: {args.create_template}")
        if importer.create_secrets_template(args.create_template):
            print(f"✅ Template created successfully!")
            print(f"📝 Edit {args.create_template} with your actual secrets")
        sys.exit(0)
    
    # Check if secrets file exists
    if not os.path.exists(args.secrets_file):
        print(f"❌ Secrets file not found: {args.secrets_file}")
        print()
        print("Create a secrets file using:")
        print(f"python3 {sys.argv[0]} --create-template {args.secrets_file}")
        sys.exit(1)
    
    print(f"📁 Secrets file: {args.secrets_file}")
    if importer.repo_owner and importer.repo_name:
        print(f"🏢 Repository: {importer.repo_owner}/{importer.repo_name}")
    else:
        print("⚠️  Could not determine repository info")
    print()
    
    # Parse and validate secrets file
    secrets, errors = importer.parse_secrets_file(args.secrets_file)
    
    print(f"🔍 Validation Results:")
    print(f"  Total secrets found: {len(secrets)}")
    print(f"  Validation errors: {len(errors)}")
    
    if errors:
        print("\n❌ Validation Errors:")
        for error in errors:
            print(f"  {error}")
        if not args.validate:
            print("\nFix validation errors before importing.")
            sys.exit(1)
    
    if args.validate:
        if not errors:
            print("✅ File format is valid!")
        sys.exit(0 if not errors else 1)
    
    if not secrets:
        print("❌ No valid secrets found to import")
        sys.exit(1)
    
    # Check GitHub CLI
    if not args.dry_run and not importer.check_gh_cli():
        print("❌ GitHub CLI not available or not authenticated")
        print("Please install and authenticate GitHub CLI:")
        print("  https://cli.github.com/")
        print("  gh auth login")
        sys.exit(1)
    
    # Get existing secrets for conflict detection
    if not args.overwrite and not args.dry_run:
        importer.existing_secrets = importer.get_existing_secrets()
        if importer.existing_secrets:
            print(f"📋 Found {len(importer.existing_secrets)} existing secrets")
    
    # Validate secret values and show warnings
    all_warnings = []
    for secret in secrets:
        warnings = importer.validate_secret_value(secret)
        all_warnings.extend(warnings)
    
    if all_warnings:
        print(f"\n⚠️  Security Warnings:")
        for warning in all_warnings:
            print(f"  {warning}")
        print()
    
    # Import secrets
    print(f"🔄 {'[DRY RUN] ' if args.dry_run else ''}Importing secrets...")
    print()
    
    imported = 0
    skipped = 0
    failed = 0
    
    for secret in secrets:
        # Check if exists and not overwriting
        if not args.overwrite and secret.name in importer.existing_secrets:
            print(f"⏭️  Skipped: {secret.name} (already exists)")
            skipped += 1
            continue
        
        # Import the secret
        if importer.import_secret(secret, args.dry_run):
            status = "Would import" if args.dry_run else "Imported"
            print(f"✅ {status}: {secret.name}")
            imported += 1
        else:
            print(f"❌ Failed: {secret.name}")
            failed += 1
    
    # Summary
    print()
    print("📊 Import Summary:")
    print(f"  Imported: {imported}")
    if skipped > 0:
        print(f"  Skipped: {skipped}")
    if failed > 0:
        print(f"  Failed: {failed}")
    
    if args.dry_run:
        print()
        print("🎉 Dry run completed successfully!")
        print()
        print("To actually import the secrets, run:")
        print(f"python3 {sys.argv[0]} {args.secrets_file}")
    elif failed == 0:
        print()
        print("🎉 All secrets imported successfully!")
        print()
        print("Next steps:")
        print(f"1. Verify: gh secret list --repo {importer.repo_owner}/{importer.repo_name}")
        print("2. Test: python3 scripts/security/secret-scanner.py --stats-only")
        print("3. Replace: python3 scripts/security/secret-replacer.py --dry-run")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()