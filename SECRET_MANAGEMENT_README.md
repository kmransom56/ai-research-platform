# 🔐 Secret Management System

## Overview

The AI Research Platform uses GitHub Actions for automated secret management, ensuring API keys and sensitive credentials are never hardcoded in the repository. This system provides automated detection, replacement, and secure configuration management.

## 🎯 Key Features

- **🔍 Automated Secret Detection**: Daily scans for hardcoded secrets
- **🔄 Auto-Replacement**: Converts hardcoded secrets to environment variables
- **🛡️ Security-First**: All secrets stored in GitHub repository secrets
- **📊 Comprehensive Reporting**: Detailed security reports and inventory
- **🚀 CI/CD Integration**: Seamless deployment with secure configurations
- **🔧 Multiple Environments**: Production, development, and local templates

## 📦 Components

### Scripts
- `scripts/security/secret-scanner.py` - Advanced secret detection
- `scripts/security/secret-replacer.py` - Automated secret replacement
- `scripts/security/setup-github-secrets.sh` - Interactive secrets setup

### GitHub Actions
- `.github/workflows/secret-management.yml` - Comprehensive secret management workflow

### Configuration Templates
- `configs/env-templates/.env.production.template` - Production environment
- `configs/env-templates/.env.development.template` - Development environment  
- `configs/env-templates/.env.local.template` - Quick local setup

## 🚀 Quick Start

### 1. Set Up GitHub Repository Secrets

```bash
# Interactive setup (recommended)
./scripts/security/setup-github-secrets.sh setup

# Or manually via GitHub UI:
# Go to Settings > Secrets and variables > Actions
# Add required secrets (see list below)
```

### 2. Scan for Existing Secrets

```bash
# Scan current codebase
python3 scripts/security/secret-scanner.py --format markdown --output scan-report.md

# Quick stats only
python3 scripts/security/secret-scanner.py --stats-only
```

### 3. Replace Hardcoded Secrets

```bash
# Dry run (see what would change)
python3 scripts/security/secret-replacer.py --dry-run

# Apply changes
python3 scripts/security/secret-replacer.py --apply
```

### 4. Set Up Local Environment

```bash
# Copy appropriate template
cp configs/env-templates/.env.local.template .env.local
# Edit .env.local with your development keys
```

## 🔑 Required Secrets

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `OPENAI_API_KEY` | OpenAI API key | Core AI functionality |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Advanced AI features |
| `AZURE_OPENAI_KEY` | Azure OpenAI service key | Enterprise AI |
| `GEMINI_API_KEY` | Google Gemini API key | Google AI integration |
| `GOOGLE_API_KEY` | Google Cloud API key | Google services |
| `LANGCHAIN_API_KEY` | LangChain API key | RAG and chains |
| `NEO4J_USERNAME` | Neo4j database username | Graph database |
| `NEO4J_PASSWORD` | Neo4j database password | Graph database |
| `POSTGRES_PASSWORD` | PostgreSQL password | Relational database |
| `RABBITMQ_USER` | RabbitMQ username | Message queue |
| `RABBITMQ_PASSWORD` | RabbitMQ password | Message queue |
| `OPENWEBUI_SECRET_KEY` | OpenWebUI secret | Web interface |
| `VSCODE_PASSWORD` | VS Code server password | Development |
| `GITHUB_TOKEN` | GitHub access token | Integrations |

## 🔄 GitHub Actions Workflows

### Secret Scan Workflow
**Triggers**: Push, PR, Daily at 2 AM UTC
- Scans for hardcoded secrets
- Fails PRs with hardcoded secrets
- Generates security reports

### Auto-Replacement Workflow  
**Triggers**: Manual, Found secrets on main branch
- Automatically replaces hardcoded secrets
- Creates commits with replacements
- Updates configuration files

### Secret Sync Workflow
**Triggers**: Push to main, Manual
- Generates environment files from GitHub secrets
- Updates configuration templates
- Creates secret inventory

### Security Reporting
**Triggers**: After other workflows
- Comprehensive security reports
- PR comments for violations
- Security status dashboard

## 📝 Usage Examples

### Scanning Specific Files
```bash
# Scan only Python files
python3 scripts/security/secret-scanner.py --format json --output python-secrets.json "**/*.py"

# Scan with high confidence only
python3 scripts/security/secret-scanner.py --confidence 0.8
```

### Targeted Replacement
```bash
# Replace only in specific file pattern
python3 scripts/security/secret-replacer.py --pattern "*.json" --dry-run

# Generate diff report
python3 scripts/security/secret-replacer.py --diff webapi/appsettings.json
```

### Environment Setup
```bash
# Production deployment
cp configs/env-templates/.env.production.template .env.production
# Populate with actual values via deployment process

# Development setup
cp configs/env-templates/.env.development.template .env.development
# Add your development API keys
```

## 🛡️ Security Best Practices

### ✅ Do's
- Store all secrets in GitHub repository secrets
- Use environment variable references: `${SECRET_NAME}`
- Rotate secrets regularly (quarterly recommended)
- Use different secrets for different environments
- Monitor automated scan results
- Review security reports regularly

### ❌ Don'ts
- Never commit actual secret values to the repository
- Don't use production secrets in development
- Don't bypass the automated scans
- Don't share secrets in plain text
- Don't use weak or predictable passwords

## 🔧 Configuration Management

### appsettings.json Example
```json
{
  "OpenAI": {
    "APIKey": "${OPENAI_API_KEY}",
    "Model": "gpt-4"
  },
  "Neo4j": {
    "Uri": "bolt://localhost:7687",
    "Username": "${NEO4J_USERNAME}",
    "Password": "${NEO4J_PASSWORD}"
  }
}
```

### Docker Compose Example
```yaml
services:
  neo4j:
    environment:
      - NEO4J_AUTH=${NEO4J_USERNAME}/${NEO4J_PASSWORD}
  
  postgres:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

### Python Code Example
```python
import os

# Good - uses environment variables
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable required")

# Bad - hardcoded secret (will be detected and flagged)
# api_key = "sk-abc123def456..."
```

## 🚨 Troubleshooting

### Common Issues

**Secret not found in environment**
- Ensure secret is added to GitHub repository secrets
- Check spelling of secret name
- Verify environment file is loaded correctly

**Hardcoded secrets still detected**
- Run the replacement script: `python3 scripts/security/secret-replacer.py --apply`
- Check for exclude patterns in scanner configuration
- Verify secrets are properly replaced with `${SECRET_NAME}` format

**GitHub Actions failing**
- Check repository secrets are properly configured
- Verify GitHub CLI authentication: `gh auth status`
- Review workflow logs for specific errors

**Local development issues**
- Copy appropriate environment template
- Ensure local environment file is loaded (`.env.local`, `.env.development`)
- Check application startup logs for missing variables

### Getting Help

1. **Check the scan report**: `python3 scripts/security/secret-scanner.py --format markdown`
2. **Validate secrets setup**: `./scripts/security/setup-github-secrets.sh validate`
3. **Review GitHub Actions logs** in the repository
4. **Check security reports** in workflow artifacts

## 📊 Monitoring & Reporting

### Automated Reports
- **Daily Scan Reports**: Generated automatically, available as workflow artifacts
- **Security Dashboard**: View in GitHub Actions tab
- **Secret Inventory**: Updated with each workflow run

### Manual Reports
```bash
# Generate comprehensive report
python3 scripts/security/secret-scanner.py --format markdown --output security-report.md

# Check specific severity
python3 scripts/security/secret-scanner.py --severity critical

# Generate replacement preview
python3 scripts/security/secret-replacer.py --dry-run --output replacement-preview.txt
```

## 🔄 Maintenance

### Regular Tasks
- **Weekly**: Review scan reports for new secrets
- **Monthly**: Update secret replacement patterns
- **Quarterly**: Rotate critical secrets (API keys, passwords)
- **On demand**: Run secret replacement after adding new code

### Secret Rotation Process
1. Generate new secret value
2. Update GitHub repository secret
3. Deploy applications to pick up new value
4. Verify all services are working
5. Deactivate old secret

## 🔗 Related Documentation

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Docker Secrets Management](https://docs.docker.com/engine/swarm/secrets/)
- [.NET Configuration](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/)

## 📞 Support

For issues with secret management:

1. Run the validation script: `./scripts/security/setup-github-secrets.sh validate`
2. Check the troubleshooting section above
3. Review GitHub Actions workflow logs
4. Open an issue with scan results and error logs

---

*This system was designed to provide enterprise-grade secret management while maintaining developer productivity. All components work together to ensure your AI Research Platform remains secure while being easy to develop and deploy.*