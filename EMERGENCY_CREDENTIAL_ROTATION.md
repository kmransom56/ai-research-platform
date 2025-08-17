# 🚨 EMERGENCY CREDENTIAL ROTATION GUIDE

**SECURITY INCIDENT:** Multiple API keys and credentials were found exposed in the repository.

## ⚡ IMMEDIATE ACTIONS TAKEN

✅ **Files Removed from Repository:**
- `.env` file containing live API keys
- `github_secrets.txt` and `github_secrets.txt.converted` 
- Docker environment files secured
- Enhanced `.gitignore` to prevent future exposure

✅ **Hardcoded Secrets Replaced:**
- Docker WebAPI OpenAI key → `${OPENAI_API_KEY}`
- Docker MemoryPipeline OpenAI key → `${OPENAI_API_KEY}`
- All database passwords → environment variables

## 🔐 KEYS REQUIRING IMMEDIATE ROTATION

### **OpenAI API Keys** 
**Status:** 🔴 ROTATE IMMEDIATELY
- **Exposed Key Pattern:** `sk-proj-6OPuDLCF4X2Jjh...` (truncated for security)
- **Found In:** Docker containers, main .env file
- **Action:** 
  1. Go to https://platform.openai.com/api-keys
  2. Revoke the exposed key immediately
  3. Generate new API key
  4. Update GitHub repository secrets: `OPENAI_API_KEY`

### **Azure OpenAI** 
**Status:** 🔴 ROTATE IMMEDIATELY  
- **Exposed Key Pattern:** `5cg6k21wanDiscRtit...` (truncated)
- **Action:**
  1. Access Azure Portal → Cognitive Services
  2. Regenerate access keys
  3. Update `AZURE_OPENAI_KEY` in repository secrets

### **Anthropic API Keys**
**Status:** 🔴 ROTATE IMMEDIATELY
- **Exposed Key Pattern:** `sk-ant-api03-cen99Iv...` (truncated)
- **Action:**
  1. Go to https://console.anthropic.com/
  2. Revoke exposed key
  3. Generate new API key
  4. Update `ANTHROPIC_API_KEY` in repository secrets

### **Google API Keys** 
**Status:** 🔴 ROTATE IMMEDIATELY
- **Gemini Key:** `AIzaSyB4fISJUpD2uq...` (truncated)
- **Maps Key:** `AIzaSyAp68fLIrmdO-...` (truncated)
- **Action:**
  1. Go to https://console.cloud.google.com/apis/credentials
  2. Delete exposed keys
  3. Create new API keys with appropriate restrictions
  4. Update `GEMINI_API_KEY` and `GOOGLE_MAPS_API` secrets

### **GitHub Personal Access Tokens**
**Status:** 🔴 ROTATE IMMEDIATELY  
- **Exposed Token:** `github_pat_11AI6SDFA0...` (truncated)
- **Action:**
  1. Go to https://github.com/settings/tokens
  2. Revoke the exposed token immediately
  3. Generate new fine-grained personal access token
  4. Update `GITHUB_TOKEN` in repository secrets

### **Additional Service Keys Requiring Rotation:**
- **Meraki API:** `fd3b9969d25792d90f...` → Rotate in Meraki Dashboard
- **Brave Search:** `BSAraRLiwdxjg43P7u...` → Rotate at Brave API portal  
- **Groq API:** `gsk_vbotbYFfbPF2vjS...` → Rotate at Groq console
- **Hugging Face:** `hf_DRpJKiiBbTQmHdq...` → Rotate at HF settings
- **Fortinet API:** `HbsysGgkc7wd1pp3x...` → Rotate in FortiManager

## 🛡️ SECURE DEPLOYMENT PROCESS

### **Step 1: Set Up Environment Variables**
```bash
# Copy the template
cp .env.template .env

# Edit .env with your NEW rotated keys (do not commit this file)
nano .env
```

### **Step 2: Use GitHub Secrets (Recommended)**
```bash
# Set secrets via GitHub CLI
gh secret set OPENAI_API_KEY --body "your_new_openai_key"
gh secret set ANTHROPIC_API_KEY --body "your_new_anthropic_key"  
gh secret set AZURE_OPENAI_KEY --body "your_new_azure_key"
gh secret set GEMINI_API_KEY --body "your_new_gemini_key"
gh secret set GH_TOKEN --body "your_new_github_token"
```

### **Step 3: Deploy with Environment Variables**
```bash
# Option 1: Docker Compose with environment file
docker compose -f docker-compose.portable.yml up -d

# Option 2: Set environment variables directly
export OPENAI_API_KEY="your_new_key"
export NEO4J_PASSWORD="secure_password"
docker compose -f docker-compose.simple.yml up -d
```

## 📋 ROTATION CHECKLIST

### **Immediate (0-2 hours):**
- [ ] Revoke OpenAI API key: `sk-proj-6OPuDLCF4X2Jjh...`
- [ ] Revoke Anthropic API key: `sk-ant-api03-cen99Iv...`
- [ ] Revoke GitHub PAT: `github_pat_11AI6SDFA0...`
- [ ] Revoke Azure OpenAI key: `5cg6k21wanDiscRtit...`
- [ ] Revoke Google API keys: `AIzaSyB4fISJUpD2uq...`
- [ ] Monitor access logs for unauthorized usage

### **Short-term (2-24 hours):**
- [ ] Generate new API keys for all services
- [ ] Update GitHub repository secrets
- [ ] Test application functionality with new keys
- [ ] Update any external integrations using these keys

### **Medium-term (1-7 days):**
- [ ] Audit API usage logs for suspicious activity
- [ ] Review billing for unexpected charges
- [ ] Implement automated secret scanning in CI/CD
- [ ] Create security incident report

## 🔍 MONITORING & DETECTION

### **Check for Unauthorized Usage:**
```bash
# Monitor OpenAI usage
curl -H "Authorization: Bearer new_key" https://api.openai.com/v1/usage

# Check GitHub API rate limits
curl -H "Authorization: token new_token" https://api.github.com/rate_limit
```

### **Set Up Alerts:**
- Configure usage alerts for all API services
- Enable security notifications in service dashboards
- Monitor repository access logs

## 🚫 PREVENTING FUTURE INCIDENTS

### **Enforcement Rules:**
1. **Never commit .env files** - Already added to .gitignore
2. **Use environment variables only** - Templates provided
3. **Regular secret scans** - Scanner script available
4. **Team training** - Security best practices

### **Automated Protection:**
```bash
# Run secret scanner before commits
python3 scripts/security/secret-scanner.py

# Use pre-commit hooks
git config core.hooksPath scripts/git-hooks/
```

## ⚠️ BUSINESS IMPACT ASSESSMENT

### **Services at Risk:**
- **AI/ML Operations:** OpenAI, Anthropic, Google AI services
- **Development Workflow:** GitHub automation and deployments  
- **Infrastructure:** Azure cloud resources
- **Network Management:** Meraki and Fortinet systems

### **Potential Damages:**
- Unauthorized API usage charges
- Data access and manipulation
- Service disruption
- Compliance violations

## 📞 INCIDENT RESPONSE CONTACTS

### **Technical Team:**
- **Security Team:** Immediate key rotation
- **DevOps Team:** Environment variable deployment
- **API Administrators:** Service-specific key management

### **Monitoring Dashboards:**
- **OpenAI Usage:** https://platform.openai.com/usage
- **Azure Costs:** https://portal.azure.com/#view/Microsoft_Azure_CostManagement
- **GitHub Actions:** Repository settings → Secrets and variables

## ✅ VERIFICATION STEPS

After rotation, verify:

1. **Application Functionality:**
   ```bash
   curl -f http://localhost:11000/healthz
   curl -f http://localhost:7474  # Neo4j
   ```

2. **Secret Scanner Clean:**
   ```bash
   python3 scripts/security/secret-scanner.py
   ```

3. **Service Authentication:**
   - Test OpenAI API calls
   - Verify Azure OpenAI connectivity  
   - Check Anthropic API access
   - Validate GitHub API operations

## 🎯 SUCCESS CRITERIA

✅ All exposed keys revoked and replaced  
✅ Application running with new credentials  
✅ No hardcoded secrets in codebase  
✅ Monitoring and alerts configured  
✅ Team trained on secure practices  

---

**⚡ This incident demonstrates the critical importance of proper secret management. The infrastructure exists - execution is key to security.**