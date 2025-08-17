# 🔧 GitHub Secret Naming Fix

## ❌ Issue Encountered
The GitHub API returned an error when trying to set `GITHUB_TOKEN` as a repository secret:

```
HTTP 422: Secret names must not start with GITHUB_.
```

## ✅ Solution
GitHub Actions restricts secret names starting with "GITHUB_" to prevent conflicts with built-in environment variables.

### **Corrected Secret Name:**
- **OLD:** `GITHUB_TOKEN` ❌
- **NEW:** `GH_TOKEN` ✅

## 🔧 How to Fix

### **Option 1: Use the Updated Script**
The automation script has been fixed. Run it again:
```bash
./scripts/security/rotate-api-keys.sh
```

### **Option 2: Set Manually with GitHub CLI**
```bash
gh secret set GH_TOKEN --body "your_new_github_personal_access_token"
```

### **Option 3: GitHub Web Interface**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GH_TOKEN` (not GITHUB_TOKEN)
4. Value: Your new GitHub personal access token

## 📝 Files Updated
The following files have been corrected to use `GH_TOKEN`:
- ✅ `scripts/security/rotate-api-keys.sh`
- ✅ `API_KEY_ROTATION_CHECKLIST.md`
- ✅ `EMERGENCY_CREDENTIAL_ROTATION.md`
- ✅ `configs/env-templates/.env.production.template`

## 🧪 Verify the Fix
After setting the secret, verify it exists:
```bash
gh secret list | grep GH_TOKEN
```

Should show:
```
GH_TOKEN    Updated YYYY-MM-DD
```

## 📋 Complete Your Rotation
Continue with the other secrets:
- `OPENAI_API_KEY` ✅ (No naming restrictions)
- `ANTHROPIC_API_KEY` ✅ (No naming restrictions)
- `AZURE_OPENAI_KEY` ✅ (No naming restrictions)
- `NEO4J_PASSWORD` ✅ (No naming restrictions)
- `DB_PASSWORD` ✅ (No naming restrictions)

The platform is configured to use `GH_TOKEN` instead of `GITHUB_TOKEN` for GitHub integration.