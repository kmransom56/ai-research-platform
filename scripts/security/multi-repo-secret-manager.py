#!/usr/bin/env python3
"""
Multi-Repository Secret Management System
Manages secrets across all repositories in an organization or user account

Features:
- Discover repositories with API keys
- Deploy secrets to multiple repositories
- Sync secrets across repositories
- Organization-wide secret inventory
- Bulk repository configuration
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

@dataclass
class Repository:
    name: str
    full_name: str
    owner: str
    private: bool
    has_secrets: bool
    secrets_count: int
    languages: List[str]
    default_branch: str
    last_push: str

@dataclass
class SecretDeployment:
    secret_name: str
    repositories: List[str]
    deployment_status: Dict[str, bool]
    last_deployed: str

class MultiRepoSecretManager:
    """Multi-repository secret management system"""
    
    def __init__(self, owner_type: str = "user", owner_name: str = None):
        self.owner_type = owner_type  # "user" or "org"
        self.owner_name = owner_name or self.get_current_user()
        self.repositories: List[Repository] = []
        self.master_secrets: Dict[str, str] = {}
        
    def get_current_user(self) -> str:
        """Get current GitHub user"""
        try:
            result = subprocess.run(['gh', 'api', 'user'], 
                                 capture_output=True, text=True, check=True)
            user_data = json.loads(result.stdout)
            return user_data['login']
        except Exception:
            return ""
    
    def discover_repositories(self, include_forks: bool = False, 
                            min_stars: int = 0) -> List[Repository]:
        """Discover all repositories for the owner"""
        print(f"🔍 Discovering repositories for {self.owner_type}: {self.owner_name}")
        
        try:
            # Get repositories
            if self.owner_type == "org":
                cmd = ['gh', 'api', f'orgs/{self.owner_name}/repos', 
                       '--paginate', '-q', '.[]']
            else:
                cmd = ['gh', 'api', 'user/repos', '--paginate', '-q', '.[]']
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            repo_data = [json.loads(line) for line in result.stdout.strip().split('\n') if line.strip()]
            
            repositories = []
            for repo in repo_data:
                # Apply filters
                if not include_forks and repo.get('fork', False):
                    continue
                if repo.get('stargazers_count', 0) < min_stars:
                    continue
                
                # Check for existing secrets
                secrets_count = self.get_repo_secrets_count(repo['full_name'])
                
                repositories.append(Repository(
                    name=repo['name'],
                    full_name=repo['full_name'],
                    owner=repo['owner']['login'],
                    private=repo['private'],
                    has_secrets=secrets_count > 0,
                    secrets_count=secrets_count,
                    languages=self.get_repo_languages(repo['full_name']),
                    default_branch=repo['default_branch'],
                    last_push=repo['pushed_at']
                ))
            
            self.repositories = repositories
            print(f"📊 Found {len(repositories)} repositories")
            return repositories
            
        except Exception as e:
            print(f"❌ Failed to discover repositories: {e}")
            return []
    
    def get_repo_secrets_count(self, full_name: str) -> int:
        """Get count of secrets for a repository"""
        try:
            result = subprocess.run([
                'gh', 'api', f'repos/{full_name}/actions/secrets'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('total_count', 0)
            return 0
        except Exception:
            return 0
    
    def get_repo_languages(self, full_name: str) -> List[str]:
        """Get programming languages used in repository"""
        try:
            result = subprocess.run([
                'gh', 'api', f'repos/{full_name}/languages'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                languages = json.loads(result.stdout)
                return list(languages.keys())
            return []
        except Exception:
            return []
    
    def scan_repository_for_secrets(self, repo_full_name: str) -> List[Dict]:
        """Scan a repository for hardcoded secrets"""
        print(f"🔍 Scanning {repo_full_name} for secrets...")
        
        # Clone repository to temp directory
        temp_dir = f"/tmp/secret-scan-{repo_full_name.replace('/', '-')}"
        
        try:
            # Clone repository
            subprocess.run([
                'gh', 'repo', 'clone', repo_full_name, temp_dir
            ], check=True, capture_output=True)
            
            # Run secret scanner
            scanner_path = Path(__file__).parent / "secret-scanner.py"
            result = subprocess.run([
                'python3', str(scanner_path), temp_dir, 
                '--format', 'json', '--quiet'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                scan_data = json.loads(result.stdout)
                return scan_data.get('matches', [])
            
            return []
            
        except Exception as e:
            print(f"❌ Failed to scan {repo_full_name}: {e}")
            return []
        
        finally:
            # Cleanup temp directory
            subprocess.run(['rm', '-rf', temp_dir], capture_output=True)
    
    def load_master_secrets(self, secrets_file: str):
        """Load master secrets from file"""
        try:
            with open(secrets_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        name, value = line.split('=', 1)
                        self.master_secrets[name.strip()] = value.strip()
            
            print(f"📋 Loaded {len(self.master_secrets)} master secrets")
            
        except Exception as e:
            print(f"❌ Failed to load secrets file: {e}")
    
    def deploy_secrets_to_repo(self, repo_full_name: str, secrets: Dict[str, str], 
                             overwrite: bool = False) -> Dict[str, bool]:
        """Deploy secrets to a single repository"""
        results = {}
        
        # Get existing secrets if not overwriting
        existing_secrets = set()
        if not overwrite:
            existing_secrets = self.get_existing_repo_secrets(repo_full_name)
        
        for secret_name, secret_value in secrets.items():
            if not overwrite and secret_name in existing_secrets:
                print(f"⏭️  Skipping {secret_name} in {repo_full_name} (already exists)")
                results[secret_name] = True  # Consider as success
                continue
            
            try:
                process = subprocess.Popen([
                    'gh', 'secret', 'set', secret_name, '--repo', repo_full_name
                ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                   stderr=subprocess.PIPE, text=True)
                
                stdout, stderr = process.communicate(input=secret_value)
                results[secret_name] = process.returncode == 0
                
                if process.returncode == 0:
                    print(f"✅ Deployed {secret_name} to {repo_full_name}")
                else:
                    print(f"❌ Failed to deploy {secret_name} to {repo_full_name}: {stderr}")
                    
            except Exception as e:
                print(f"❌ Error deploying {secret_name} to {repo_full_name}: {e}")
                results[secret_name] = False
        
        return results
    
    def get_existing_repo_secrets(self, repo_full_name: str) -> Set[str]:
        """Get list of existing secrets in a repository"""
        try:
            result = subprocess.run([
                'gh', 'secret', 'list', '--repo', repo_full_name,
                '--json', 'name', '-q', '.[].name'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return set(line.strip() for line in result.stdout.strip().split('\n') if line.strip())
            return set()
        except Exception:
            return set()
    
    def deploy_secrets_bulk(self, target_repos: List[str] = None, 
                           secrets_filter: List[str] = None,
                           overwrite: bool = False, max_workers: int = 5) -> Dict[str, Dict[str, bool]]:
        """Deploy secrets to multiple repositories in parallel"""
        if not self.master_secrets:
            print("❌ No master secrets loaded. Use load_master_secrets() first.")
            return {}
        
        # Filter repositories
        if target_repos:
            repos_to_process = [r for r in self.repositories if r.full_name in target_repos]
        else:
            repos_to_process = self.repositories
        
        # Filter secrets
        secrets_to_deploy = self.master_secrets
        if secrets_filter:
            secrets_to_deploy = {k: v for k, v in self.master_secrets.items() if k in secrets_filter}
        
        print(f"🚀 Deploying {len(secrets_to_deploy)} secrets to {len(repos_to_process)} repositories")
        
        results = {}
        
        # Use thread pool for parallel deployment
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(
                    self.deploy_secrets_to_repo, 
                    repo.full_name, 
                    secrets_to_deploy, 
                    overwrite
                ): repo.full_name for repo in repos_to_process
            }
            
            for future in as_completed(future_to_repo):
                repo_name = future_to_repo[future]
                try:
                    result = future.result()
                    results[repo_name] = result
                except Exception as e:
                    print(f"❌ Failed to deploy to {repo_name}: {e}")
                    results[repo_name] = {secret: False for secret in secrets_to_deploy}
        
        return results
    
    def sync_secrets_across_repos(self, source_repo: str, target_repos: List[str]) -> Dict[str, bool]:
        """Sync secrets from one repository to others"""
        print(f"🔄 Syncing secrets from {source_repo} to {len(target_repos)} repositories")
        
        # Get secrets from source repository
        source_secrets = self.get_existing_repo_secrets(source_repo)
        
        if not source_secrets:
            print(f"❌ No secrets found in source repository: {source_repo}")
            return {}
        
        # Note: We can't actually read secret values, so we'll use master secrets
        secrets_to_sync = {name: value for name, value in self.master_secrets.items() 
                          if name in source_secrets}
        
        if not secrets_to_sync:
            print("❌ No matching secrets found in master secrets file")
            return {}
        
        results = {}
        for repo in target_repos:
            repo_results = self.deploy_secrets_to_repo(repo, secrets_to_sync, overwrite=True)
            results[repo] = all(repo_results.values())
        
        return results
    
    def generate_organization_inventory(self) -> Dict:
        """Generate comprehensive organization-wide secret inventory"""
        print("📊 Generating organization-wide secret inventory...")
        
        inventory = {
            "organization": self.owner_name,
            "scan_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "total_repositories": len(self.repositories),
            "repositories_with_secrets": len([r for r in self.repositories if r.has_secrets]),
            "total_secrets_deployed": sum(r.secrets_count for r in self.repositories),
            "master_secrets_available": len(self.master_secrets),
            "repositories": [],
            "secret_usage_summary": {},
            "recommendations": []
        }
        
        # Repository details
        for repo in self.repositories:
            repo_secrets = self.get_existing_repo_secrets(repo.full_name)
            
            inventory["repositories"].append({
                "name": repo.name,
                "full_name": repo.full_name,
                "private": repo.private,
                "languages": repo.languages,
                "secrets_count": repo.secrets_count,
                "secrets": list(repo_secrets),
                "last_push": repo.last_push,
                "needs_attention": repo.secrets_count == 0 and any(
                    lang in ["JavaScript", "Python", "Go", "Java", "C#"] 
                    for lang in repo.languages
                )
            })
        
        # Secret usage summary
        all_secret_names = set()
        for repo in self.repositories:
            repo_secrets = self.get_existing_repo_secrets(repo.full_name)
            all_secret_names.update(repo_secrets)
        
        for secret_name in all_secret_names:
            repos_using_secret = []
            for repo in self.repositories:
                repo_secrets = self.get_existing_repo_secrets(repo.full_name)
                if secret_name in repo_secrets:
                    repos_using_secret.append(repo.full_name)
            
            inventory["secret_usage_summary"][secret_name] = {
                "used_in_repos": len(repos_using_secret),
                "repositories": repos_using_secret,
                "coverage": len(repos_using_secret) / len(self.repositories) * 100
            }
        
        # Recommendations
        repos_without_secrets = [r for r in self.repositories 
                               if not r.has_secrets and any(
                                   lang in ["JavaScript", "Python", "Go", "Java", "C#"] 
                                   for lang in r.languages
                               )]
        
        if repos_without_secrets:
            inventory["recommendations"].append({
                "type": "missing_secrets",
                "description": f"{len(repos_without_secrets)} repositories may need secret management",
                "repositories": [r.full_name for r in repos_without_secrets]
            })
        
        # Inconsistent secret usage
        common_secrets = {name: data for name, data in inventory["secret_usage_summary"].items() 
                         if data["coverage"] > 50}
        
        for secret_name, data in common_secrets.items():
            if data["coverage"] < 80:
                inventory["recommendations"].append({
                    "type": "inconsistent_usage",
                    "description": f"{secret_name} is used in {data['coverage']:.1f}% of repositories",
                    "suggestion": f"Consider deploying {secret_name} to all repositories"
                })
        
        return inventory
    
    def deploy_secret_management_workflow(self, target_repos: List[str] = None):
        """Deploy secret management GitHub Actions workflow to repositories"""
        workflow_path = Path(__file__).parent.parent.parent / ".github/workflows/secret-management.yml"
        
        if not workflow_path.exists():
            print("❌ Secret management workflow not found")
            return
        
        repos_to_process = target_repos or [r.full_name for r in self.repositories]
        
        print(f"🚀 Deploying secret management workflow to {len(repos_to_process)} repositories")
        
        for repo_name in repos_to_process:
            try:
                # Create .github/workflows directory in repository
                subprocess.run([
                    'gh', 'api', f'repos/{repo_name}/contents/.github/workflows/secret-management.yml',
                    '--method', 'PUT',
                    '--field', f'message=Add secret management workflow',
                    '--field', f'content=@{workflow_path}'
                ], check=True, capture_output=True)
                
                print(f"✅ Deployed workflow to {repo_name}")
                
            except Exception as e:
                print(f"❌ Failed to deploy workflow to {repo_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Multi-Repository Secret Management System')
    parser.add_argument('--owner', help='GitHub username or organization name')
    parser.add_argument('--owner-type', choices=['user', 'org'], default='user',
                       help='Owner type (user or org)')
    parser.add_argument('--secrets-file', help='Path to master secrets file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover repositories')
    discover_parser.add_argument('--include-forks', action='store_true',
                                help='Include forked repositories')
    discover_parser.add_argument('--min-stars', type=int, default=0,
                                help='Minimum stars filter')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan repositories for secrets')
    scan_parser.add_argument('--repos', nargs='+', help='Specific repositories to scan')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy secrets to repositories')
    deploy_parser.add_argument('--repos', nargs='+', help='Target repositories')
    deploy_parser.add_argument('--secrets', nargs='+', help='Specific secrets to deploy')
    deploy_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing secrets')
    deploy_parser.add_argument('--max-workers', type=int, default=5, help='Parallel workers')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync secrets between repositories')
    sync_parser.add_argument('--source', required=True, help='Source repository')
    sync_parser.add_argument('--targets', nargs='+', required=True, help='Target repositories')
    
    # Inventory command
    inventory_parser = subparsers.add_parser('inventory', help='Generate organization inventory')
    inventory_parser.add_argument('--output', help='Output file (JSON format)')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('deploy-workflow', help='Deploy secret management workflow')
    workflow_parser.add_argument('--repos', nargs='+', help='Target repositories')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize manager
    manager = MultiRepoSecretManager(args.owner_type, args.owner)
    
    # Load secrets if provided
    if args.secrets_file:
        manager.load_master_secrets(args.secrets_file)
    
    # Execute command
    if args.command == 'discover':
        repos = manager.discover_repositories(args.include_forks, args.min_stars)
        
        print(f"\n📊 Repository Summary:")
        print(f"  Total: {len(repos)}")
        print(f"  With secrets: {len([r for r in repos if r.has_secrets])}")
        print(f"  Private: {len([r for r in repos if r.private])}")
        
        # Group by language
        languages = {}
        for repo in repos:
            for lang in repo.languages:
                languages[lang] = languages.get(lang, 0) + 1
        
        print(f"\n🔤 Top Languages:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {lang}: {count} repositories")
    
    elif args.command == 'scan':
        manager.discover_repositories()
        target_repos = args.repos or [r.full_name for r in manager.repositories]
        
        for repo in target_repos[:5]:  # Limit to first 5 for demo
            secrets = manager.scan_repository_for_secrets(repo)
            print(f"\n📋 {repo}: {len(secrets)} potential secrets found")
    
    elif args.command == 'deploy':
        if not args.secrets_file:
            print("❌ --secrets-file is required for deployment")
            sys.exit(1)
        
        manager.discover_repositories()
        results = manager.deploy_secrets_bulk(
            args.repos, args.secrets, args.overwrite, args.max_workers
        )
        
        # Summary
        total_deployments = sum(len(repo_results) for repo_results in results.values())
        successful_deployments = sum(
            sum(1 for success in repo_results.values() if success) 
            for repo_results in results.values()
        )
        
        print(f"\n📊 Deployment Summary:")
        print(f"  Total deployments: {total_deployments}")
        print(f"  Successful: {successful_deployments}")
        print(f"  Failed: {total_deployments - successful_deployments}")
    
    elif args.command == 'sync':
        manager.discover_repositories()
        results = manager.sync_secrets_across_repos(args.source, args.targets)
        
        successful_syncs = sum(1 for success in results.values() if success)
        print(f"\n📊 Sync Summary:")
        print(f"  Repositories synced: {successful_syncs}/{len(results)}")
    
    elif args.command == 'inventory':
        manager.discover_repositories()
        inventory = manager.generate_organization_inventory()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(inventory, f, indent=2)
            print(f"📄 Inventory saved to {args.output}")
        else:
            print(json.dumps(inventory, indent=2))
    
    elif args.command == 'deploy-workflow':
        manager.discover_repositories()
        manager.deploy_secret_management_workflow(args.repos)

if __name__ == '__main__':
    main()