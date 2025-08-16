# 🏢 Multi-Repository Secret Management System

## Overview

The Multi-Repository Secret Management System extends your single-repository secret management to cover **all repositories** in your organization or personal account. This enterprise-grade solution provides centralized secret management, automated deployment, and organization-wide security compliance.

## 🎯 Key Features

### **🔍 Repository Discovery**
- **Automatic Detection**: Discovers all repositories in your organization/account
- **Smart Filtering**: Excludes forks, applies star count filters
- **Language Detection**: Identifies repositories that need API key management
- **Secret Inventory**: Tracks existing secrets across all repositories

### **🚀 Bulk Secret Deployment**
- **Mass Deployment**: Deploy 31+ secrets to multiple repositories simultaneously
- **Parallel Processing**: Efficient deployment with configurable worker threads
- **Conflict Resolution**: Handle existing secrets with overwrite options
- **Progress Tracking**: Real-time deployment status for each repository

### **📊 Organization-Wide Management**
- **Centralized Control**: Manage secrets across all repositories from one place
- **Security Compliance**: Organization-wide secret scanning and reporting
- **Workflow Deployment**: Add secret management workflows to all repositories
- **Inventory Reports**: Comprehensive security posture reports

### **🔄 Automated Workflows**
- **GitHub Actions Integration**: Organization-wide workflows for automated management
- **Scheduled Audits**: Weekly security scans across all repositories
- **Compliance Monitoring**: Continuous monitoring for hardcoded secrets
- **Automated Remediation**: Auto-replacement of detected secrets

## 🚀 Quick Start

### **1. Interactive Setup (Recommended)**
```bash
# Complete organization setup with guided prompts
./scripts/security/setup-multi-repo-secrets.sh
```

### **2. Discover Your Repositories**
```bash
# Discover all repositories
python3 scripts/security/multi-repo-secret-manager.py discover

# Discover with filters
python3 scripts/security/multi-repo-secret-manager.py discover --include-forks --min-stars 5
```

### **3. Deploy Secrets to All Repositories**
```bash
# Deploy all 31 secrets to all repositories
python3 scripts/security/multi-repo-secret-manager.py \
  --secrets-file github_secrets.txt.converted \
  deploy --overwrite

# Deploy specific secrets to specific repositories
python3 scripts/security/multi-repo-secret-manager.py \
  --secrets-file github_secrets.txt.converted \
  deploy --repos repo1 repo2 --secrets OPENAI_API_KEY GITHUB_TOKEN
```

### **4. Deploy Workflows Organization-Wide**
```bash
# Add secret management workflows to all repositories
python3 scripts/security/multi-repo-secret-manager.py deploy-workflow
```

## 📋 Available Commands

### **Repository Discovery**
```bash
# Basic discovery
python3 scripts/security/multi-repo-secret-manager.py discover

# Advanced discovery with filters
python3 scripts/security/multi-repo-secret-manager.py discover \
  --include-forks --min-stars 10

# Organization discovery
python3 scripts/security/multi-repo-secret-manager.py \
  --owner-type org --owner MyOrg discover
```

### **Secret Scanning**
```bash
# Scan all repositories for hardcoded secrets
python3 scripts/security/multi-repo-secret-manager.py scan

# Scan specific repositories
python3 scripts/security/multi-repo-secret-manager.py scan \
  --repos user/repo1 user/repo2
```

### **Bulk Secret Deployment**
```bash
# Deploy to all repositories
python3 scripts/security/multi-repo-secret-manager.py \
  --secrets-file my-secrets.txt deploy

# Deploy with options
python3 scripts/security/multi-repo-secret-manager.py \
  --secrets-file my-secrets.txt deploy \
  --repos repo1 repo2 \
  --secrets OPENAI_API_KEY GITHUB_TOKEN \
  --overwrite \
  --max-workers 10
```

### **Secret Synchronization**
```bash
# Sync secrets from master repository to others
python3 scripts/security/multi-repo-secret-manager.py sync \
  --source master-repo \
  --targets repo1 repo2 repo3
```

### **Organization Inventory**
```bash
# Generate comprehensive inventory report
python3 scripts/security/multi-repo-secret-manager.py inventory \
  --output org-inventory-$(date +%Y%m%d).json
```

### **Workflow Deployment**
```bash
# Deploy secret management workflows to all repositories
python3 scripts/security/multi-repo-secret-manager.py deploy-workflow

# Deploy to specific repositories
python3 scripts/security/multi-repo-secret-manager.py deploy-workflow \
  --repos repo1 repo2
```

## 🏢 Organization-Wide GitHub Actions Workflow

The system includes a powerful organization-wide GitHub Actions workflow that can manage secrets across all repositories.

### **Workflow Features:**
- **🔍 Repository Discovery**: Automatically finds all repositories
- **🔍 Organization-Wide Scanning**: Scans all repositories for hardcoded secrets
- **🚀 Bulk Deployment**: Deploys secrets to all repositories simultaneously
- **📋 Workflow Deployment**: Adds secret management workflows to all repositories
- **📊 Inventory Generation**: Creates comprehensive organization reports
- **🛡️ Security Compliance**: Generates security compliance reports

### **Manual Trigger Options:**
```yaml
# Available actions in GitHub Actions UI:
actions:
  - scan                # Scan all repositories for secrets
  - deploy-to-all       # Deploy master secrets to all repositories
  - sync-from-master    # Sync secrets from master repository
  - generate-inventory  # Create organization inventory report
  - deploy-workflows    # Deploy workflows to all repositories
```

### **Scheduled Operations:**
- **Weekly Security Scan**: Every Monday at 2 AM UTC
- **Monthly Inventory**: Generate organization inventory reports
- **Quarterly Compliance**: Comprehensive security compliance reviews

## 📊 Organization Inventory Reports

### **Report Contents:**
```json
{
  "organization": "your-org",
  "scan_date": "2025-08-16 23:15:00 UTC",
  "total_repositories": 25,
  "repositories_with_secrets": 18,
  "total_secrets_deployed": 450,
  "master_secrets_available": 31,
  "repositories": [
    {
      "name": "repo-name",
      "full_name": "org/repo-name",
      "private": true,
      "languages": ["JavaScript", "Python"],
      "secrets_count": 15,
      "secrets": ["OPENAI_API_KEY", "GITHUB_TOKEN", "..."],
      "needs_attention": false
    }
  ],
  "secret_usage_summary": {
    "OPENAI_API_KEY": {
      "used_in_repos": 20,
      "repositories": ["org/repo1", "org/repo2", "..."],
      "coverage": 80.0
    }
  },
  "recommendations": [
    {
      "type": "missing_secrets",
      "description": "5 repositories may need secret management",
      "repositories": ["org/repo-x", "org/repo-y"]
    }
  ]
}
```

### **Report Usage:**
- **Security Audits**: Identify repositories missing secret management
- **Compliance Reviews**: Track secret coverage across organization
- **Risk Assessment**: Find repositories with hardcoded secrets
- **Planning**: Understand organization-wide secret deployment needs

## 🛡️ Security Best Practices

### **✅ Deployment Best Practices**
1. **Test First**: Always run with `--dry-run` or small repository sets first
2. **Staged Rollout**: Deploy to a few repositories, then scale up
3. **Monitor Results**: Check deployment status and fix failures
4. **Backup Strategies**: Maintain master secrets file in secure location

### **🔐 Secret Management Best Practices**
1. **Consistent Naming**: Use standardized secret names across all repositories
2. **Least Privilege**: Only deploy secrets that repositories actually need
3. **Regular Rotation**: Rotate secrets quarterly across all repositories
4. **Monitor Usage**: Track which repositories use which secrets

### **📋 Workflow Best Practices**
1. **Regular Scans**: Run organization-wide scans weekly
2. **Automated Remediation**: Use auto-replacement workflows
3. **Compliance Monitoring**: Review security reports monthly
4. **Incident Response**: Have procedures for detected secret leaks

## 🔧 Advanced Configuration

### **Organization Types**
```bash
# Personal repositories
python3 scripts/security/multi-repo-secret-manager.py \
  --owner-type user --owner username discover

# Organization repositories  
python3 scripts/security/multi-repo-secret-manager.py \
  --owner-type org --owner orgname discover
```

### **Filtering Options**
```bash
# Include forked repositories
--include-forks

# Minimum star count filter
--min-stars 10

# Specific repository targeting
--repos repo1 repo2 repo3

# Specific secret filtering
--secrets OPENAI_API_KEY GITHUB_TOKEN
```

### **Performance Tuning**
```bash
# Parallel processing
--max-workers 10        # More workers = faster deployment

# Batch processing
--repos $(echo repo{1..20})  # Process in batches
```

## 🚨 Troubleshooting

### **Common Issues**

**Authentication Problems:**
```bash
# Check GitHub CLI authentication
gh auth status

# Re-authenticate if needed
gh auth login --scopes repo,workflow
```

**Permission Issues:**
```bash
# Ensure proper permissions for organization
# Repository admin or organization owner required
# Check token scopes include 'repo' and 'workflow'
```

**Deployment Failures:**
```bash
# Check individual repository permissions
gh repo view owner/repo

# Verify secret names don't conflict with GitHub reserved names
# (SECRET_NAME cannot start with GITHUB_)
```

**Rate Limiting:**
```bash
# Reduce worker count to avoid rate limits
--max-workers 3

# Add delays between operations
# The script automatically handles rate limiting
```

### **Recovery Procedures**

**Failed Bulk Deployment:**
1. Check deployment summary for specific failures
2. Retry failed repositories individually
3. Verify permissions and authentication
4. Check for reserved secret name conflicts

**Workflow Deployment Issues:**
1. Verify source workflow file exists
2. Check target repository permissions
3. Ensure `.github/workflows/` directory structure
4. Validate workflow YAML syntax

## 📈 Monitoring & Metrics

### **Key Metrics to Track:**
- **Repository Coverage**: Percentage of repositories with secret management
- **Secret Consistency**: Same secrets deployed across similar repositories  
- **Security Posture**: Number of repositories with hardcoded secrets
- **Deployment Success Rate**: Percentage of successful secret deployments

### **Regular Reviews:**
- **Weekly**: Security scan results and new repository detection
- **Monthly**: Organization inventory and coverage reports
- **Quarterly**: Secret rotation and access reviews
- **Annually**: Complete security architecture review

## 🔗 Integration Points

### **CI/CD Pipeline Integration**
- **Pre-commit Hooks**: Block commits with hardcoded secrets
- **Pull Request Checks**: Scan PRs for secret leaks
- **Deployment Gates**: Verify secret management before production
- **Security Notifications**: Alert on detected vulnerabilities

### **External Tools Integration**
- **Security Information and Event Management (SIEM)**: Forward security events
- **Vulnerability Scanners**: Integrate with existing security tools
- **Monitoring Systems**: Track secret management metrics
- **Identity Providers**: Integrate with organizational SSO

## 🎯 Success Metrics

After implementing the multi-repository secret management system, you should see:

✅ **100% Repository Coverage**: All repositories with API keys have proper secret management  
✅ **Zero Hardcoded Secrets**: No secrets found in code scans across organization  
✅ **Consistent Secret Usage**: Same secrets available across similar repositories  
✅ **Automated Compliance**: Regular security audits with automated reporting  
✅ **Reduced Security Risk**: Centralized secret management and rotation  
✅ **Improved Developer Experience**: Easy access to required secrets across all projects  

## 📞 Support & Maintenance

### **Regular Maintenance Tasks:**
1. **Weekly**: Review organization security scan results
2. **Monthly**: Update master secrets file with new API keys
3. **Quarterly**: Rotate all organization secrets
4. **As Needed**: Add secret management to newly created repositories

### **Getting Help:**
1. **Run Tests**: `./scripts/security/test-secret-management.sh`
2. **Check Logs**: Review GitHub Actions workflow logs
3. **Validate Setup**: Run discovery and inventory commands
4. **Documentation**: Reference this guide and individual script help

---

*This multi-repository secret management system provides enterprise-grade security and operational efficiency for organizations of any size. It scales from personal accounts with a few repositories to large enterprises with hundreds of repositories, ensuring consistent and secure API key management across your entire development ecosystem.*