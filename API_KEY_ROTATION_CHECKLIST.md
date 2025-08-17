# 🚨 API KEY ROTATION CHECKLIST

**IMMEDIATE ACTION REQUIRED** - Complete this checklist to secure exposed credentials.

## ⚡ STEP 1: REVOKE EXPOSED KEYS (Do This First!)

### 🔴 OpenAI API Key
- [ ] Go to https://platform.openai.com/api-keys  
- [ ] **DELETE** key: `sk-proj-6OPuDLCF4X2Jjh...` (found in Docker containers)
- [ ] **DELETE** key: `sk-proj-LuEydlivxioCwn...` (found in .env file)

### 🔴 Anthropic API Key  
- [ ] Go to https://console.anthropic.com/settings/keys
- [ ] **REVOKE** key: `sk-ant-api03-cen99IvWlzuFOER...`

### 🔴 GitHub Personal Access Token
- [ ] Go to https://github.com/settings/tokens
- [ ] **DELETE** token: `github_pat_11AI6SDFA099k2ENBSKQBs...`

### 🔴 Azure OpenAI Key
- [ ] Go to Azure Portal → Cognitive Services → Your resource
- [ ] **REGENERATE** key: `5cg6k21wanDiscRtitQb9Rhf...`

### 🔴 Google API Keys
- [ ] Go to https://console.cloud.google.com/apis/credentials
- [ ] **DELETE** Gemini key: `AIzaSyB4fISJUpD2uqB6m1dO19tHQvV6jBieXXs`
- [ ] **DELETE** Maps key: `AIzaSyAp68fLIrmdO-SgBjTrX_kDS4cSeK2EHNo`

### 🟡 Other Service Keys (Lower Priority)
- [ ] Meraki API: `fd3b9969d25792d90f0789a7e28cc661c81e2150`
- [ ] Groq API: `gsk_vbotbYFfbPF2vjSCXGHpWGdyb3FYJqrk1R8cA6WN...`
- [ ] Hugging Face: `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`

---

## 🔑 STEP 2: GENERATE NEW KEYS

### OpenAI
- [ ] Create new key at https://platform.openai.com/api-keys
- [ ] Copy new key (starts with `sk-`)

### Anthropic  
- [ ] Create new key at https://console.anthropic.com/settings/keys
- [ ] Copy new key (starts with `sk-ant-`)

### GitHub
- [ ] Create fine-grained token at https://github.com/settings/personal-access-tokens/fine-grained
- [ ] Set permissions: Contents (read/write), Metadata (read), Actions (read)

### Azure OpenAI
- [ ] After regenerating, copy new key from Azure Portal

### Google APIs
- [ ] Create new credentials in Google Cloud Console
- [ ] Set appropriate API and application restrictions

---

## 🔧 STEP 3: UPDATE GITHUB SECRETS

**Option A: Use the automation script:**
```bash
./scripts/security/quick-secret-setup.sh
```

**Option B: Manual GitHub CLI:**
```bash
gh secret set OPENAI_API_KEY --body "your_new_openai_key"
gh secret set ANTHROPIC_API_KEY --body "your_new_anthropic_key"  
gh secret set AZURE_OPENAI_KEY --body "your_new_azure_key"
gh secret set GH_TOKEN --body "your_new_github_token"
gh secret set NEO4J_PASSWORD --body "secure_password_123"
gh secret set DB_PASSWORD --body "secure_db_password_456"
```

**Option C: GitHub Web Interface:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret" for each key
3. Add the secrets listed above

---

## 🧪 STEP 4: TEST DEPLOYMENT

### Verify Configuration
```bash
# Check Docker Compose config
docker compose -f docker-compose.portable.yml config

# Should show no warnings about missing variables
```

### Deploy and Test
```bash
# Deploy platform
docker compose -f docker-compose.portable.yml up -d

# Test health endpoints
curl -f http://localhost:11000/healthz    # Backend
curl -f http://localhost:7474            # Neo4j
curl -f http://localhost:3000            # Frontend
```

### Check Logs
```bash
# Check for authentication errors
docker compose logs | grep -i "error\|fail\|auth"
```

---

## 🔍 STEP 5: MONITORING SETUP

### Set Up Alerts
- [ ] OpenAI usage alerts: https://platform.openai.com/usage
- [ ] Azure cost alerts: Azure Portal → Cost Management  
- [ ] GitHub Actions usage: Repository → Insights → Actions

### Verify No Hardcoded Secrets Remain
```bash
python3 scripts/security/secret-scanner.py
```

---

## ✅ COMPLETION CHECKLIST

- [ ] All exposed keys revoked from service providers
- [ ] New keys generated with appropriate restrictions
- [ ] GitHub repository secrets updated
- [ ] Application successfully deployed with new keys
- [ ] Health endpoints responding correctly
- [ ] No hardcoded secrets detected in codebase
- [ ] Monitoring and alerts configured
- [ ] Team notified of security incident and resolution

---

## 🚨 EMERGENCY CONTACTS

**If you encounter issues:**

1. **Application won't start:** Check GitHub secrets are set correctly
2. **API authentication fails:** Verify new keys are properly generated  
3. **Database connection issues:** Ensure `NEO4J_PASSWORD` and `DB_PASSWORD` are set
4. **GitHub Actions failing:** Check `GITHUB_TOKEN` has correct permissions

**Get help:**
```bash
# Full rotation guidance
./scripts/security/rotate-api-keys.sh

# Quick setup
./scripts/security/quick-secret-setup.sh

# Check repository secrets
gh secret list
```

---

**⏰ ESTIMATED TIME TO COMPLETE:** 30-60 minutes

**🎯 SUCCESS CRITERIA:** Application running with new keys, all exposed keys revoked, no security warnings from scanner.