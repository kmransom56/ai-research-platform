# 💰 API Billing Alerts Setup Guide

This guide helps you set up billing alerts for all API services to monitor costs following the credential rotation.

## 🚨 Priority: Set These Up IMMEDIATELY

After rotating your API keys, it's critical to monitor for unexpected usage that could indicate:
- Unauthorized access to your new keys
- Application misconfigurations causing excessive API calls
- Billing fraud or account compromise

---

## 🔥 OpenAI Billing Alerts

### **Step 1: Access OpenAI Usage Dashboard**
1. Go to: https://platform.openai.com/usage
2. Login with your OpenAI account

### **Step 2: Set Up Usage Alerts**
1. Click on **"Settings"** → **"Billing"**
2. Go to **"Usage limits"** section
3. Set up alerts:
   - **Hard limit**: $50/month (adjust based on your budget)
   - **Soft limit**: $30/month (80% warning)
   - **Email notifications**: Enable for both limits

### **Step 3: Monitor Usage Patterns**
```bash
# Check usage every few hours for first 48 hours
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/dashboard/billing/usage \
  -G -d "start_date=2025-08-16" -d "end_date=2025-08-17"
```

**🚨 Red Flags:**
- Usage spikes immediately after key rotation
- Calls from unexpected IP addresses
- Unusual model usage patterns

---

## 🔷 Azure OpenAI Cost Alerts

### **Step 1: Access Azure Cost Management**
1. Go to: https://portal.azure.com/#view/Microsoft_Azure_CostManagement
2. Select your subscription containing OpenAI resources

### **Step 2: Create Budget Alerts**
1. Click **"Budgets"** → **"Add"**
2. Configure budget:
   - **Name**: "OpenAI API Usage Alert"
   - **Amount**: $100/month (adjust for your needs)
   - **Time grain**: Monthly
   - **Start date**: Current month

3. Set up alert conditions:
   - **Alert condition 1**: 80% of budget ($80)
   - **Alert condition 2**: 100% of budget ($100)
   - **Alert condition 3**: 120% of budget ($120) - CRITICAL

### **Step 3: Configure Notifications**
- **Email recipients**: Your primary email + team
- **Language**: English
- **Enable**: Azure portal notifications

**🚨 Monitor For:**
- Sudden cost increases
- Resource usage in unexpected regions
- New service deployments

---

## 💎 Anthropic Billing Monitoring

### **Step 1: Access Anthropic Console**
1. Go to: https://console.anthropic.com/
2. Navigate to **"Billing & Usage"**

### **Step 2: Set Usage Monitoring**
1. Check **"Usage"** section regularly
2. Set up email notifications (if available)
3. Monitor token usage patterns

### **Step 3: API Usage Tracking**
```bash
# Anthropic doesn't provide usage API, monitor via application logs
tail -f logs/monitoring/usage_report_*.json | grep anthropic
```

**🚨 Watch For:**
- Unexpected API call volumes
- Usage outside normal business hours
- Long conversation threads (token usage)

---

## 🔍 Google Cloud (Gemini) Billing Alerts

### **Step 1: Access Google Cloud Console**
1. Go to: https://console.cloud.google.com/billing
2. Select the project with your API keys

### **Step 2: Create Budget Alerts**
1. Click **"Budgets & alerts"** → **"Create budget"**
2. Configure:
   - **Name**: "Gemini API Usage Alert"
   - **Budget type**: Specified amount
   - **Target amount**: $50/month
   - **Include credits**: No

### **Step 3: Set Alert Thresholds**
- **50%** threshold → Email notification
- **90%** threshold → Email + SMS notification  
- **100%** threshold → CRITICAL alert

### **Step 4: API Quotas**
1. Go to **"APIs & Services"** → **"Quotas"**
2. Find "Generative Language API"
3. Set reasonable daily/monthly limits

---

## 🐙 GitHub API Rate Limiting

### **Step 1: Monitor Rate Limits**
```bash
# Check current rate limit status
curl -H "Authorization: token $GH_TOKEN" https://api.github.com/rate_limit
```

### **Step 2: Set Up Monitoring**
```bash
# Add this to your monitoring script
gh api rate_limit --jq '.resources.core | "Used: \(.used)/\(.limit) Reset: \(.reset | todateiso8601)"'
```

**🚨 Rate Limit Warnings:**
- 5000 requests/hour for authenticated requests
- Monitor for unusual spikes
- Set alerts at 80% usage (4000 requests)

---

## 🛡️ Security-Focused Monitoring

### **Immediate Red Flags (0-48 Hours)**
Monitor these indicators during the critical post-rotation period:

#### **🚨 CRITICAL INDICATORS:**
- **Billing spikes** within hours of key rotation
- **API calls from unknown IP addresses**
- **Usage patterns outside normal hours**
- **New resource deployments** in cloud accounts
- **Unusual API endpoint usage**

#### **⚠️ WARNING INDICATORS:**
- **Gradual usage increases** over 24-48 hours
- **Changes in API call patterns**
- **New user agents or client identifiers**
- **Errors or failed authentication attempts**

---

## 🔔 Alert Configuration Examples

### **Email Alert Template**
```
Subject: 🚨 API Usage Alert - [SERVICE] 

ALERT: API usage threshold exceeded
Service: [OpenAI/Azure/Google/etc.]
Current Usage: $X.XX / $Y.XX budget
Time: [Timestamp]
Duration since key rotation: [Hours]

IMMEDIATE ACTIONS:
1. Check usage dashboard
2. Review application logs  
3. Verify no unauthorized access
4. Consider temporarily revoking keys if suspicious

Dashboard: [Service URL]
```

### **Slack/Discord Webhook (Optional)**
```bash
# Example webhook for critical alerts
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🚨 CRITICAL: API usage spike detected after key rotation!"}' \
  YOUR_WEBHOOK_URL
```

---

## 📊 Monitoring Dashboard Setup

### **Daily Monitoring Checklist (Next 7 Days)**

**Morning Check (9 AM):**
- [ ] OpenAI usage dashboard
- [ ] Azure cost management
- [ ] Google Cloud billing
- [ ] GitHub API rate limits
- [ ] Application error logs

**Evening Check (6 PM):**
- [ ] Compare usage vs. previous day
- [ ] Check for new billing alerts
- [ ] Review monitoring logs
- [ ] Verify application performance

### **Weekly Review (Next 4 Weeks)**
- [ ] Usage trend analysis
- [ ] Cost optimization opportunities  
- [ ] Security incident review
- [ ] Update billing thresholds if needed

---

## 🎯 Target Alert Thresholds

Based on typical AI Research Platform usage:

| Service | Monthly Budget | Alert Thresholds |
|---------|----------------|------------------|
| **OpenAI** | $100 | $50 (50%), $80 (80%), $100 (100%) |
| **Azure OpenAI** | $150 | $75 (50%), $120 (80%), $150 (100%) |
| **Anthropic** | $75 | Monitor manually, no direct API |
| **Google Gemini** | $50 | $25 (50%), $40 (80%), $50 (100%) |
| **GitHub** | Free tier | Rate limit: 4000/5000 requests |

---

## 🚀 Quick Setup Commands

```bash
# 1. Set up monitoring system
./scripts/monitoring/setup-api-monitoring.sh

# 2. Start 48-hour monitoring
./scripts/monitoring/start-monitoring.sh

# 3. Check current status
python3 scripts/monitoring/dashboard.py

# 4. Manual usage check
python3 scripts/monitoring/track-api-usage.py
```

---

## ⚠️ EMERGENCY RESPONSE

If you detect suspicious activity:

### **IMMEDIATE (0-15 minutes):**
1. **Revoke compromised API keys** in service dashboards
2. **Document the incident** (time, usage, indicators)
3. **Stop application** if necessary: `docker compose down`

### **SHORT-TERM (15-60 minutes):**
1. **Generate new API keys** following rotation guide
2. **Update GitHub repository secrets**
3. **Deploy with new keys**
4. **Verify normal operation**

### **FOLLOW-UP (1-24 hours):**
1. **Review logs** for compromise indicators
2. **Contact service providers** if fraud suspected
3. **Update security measures** based on lessons learned
4. **Document incident** for future prevention

---

**🔥 REMEMBER: The first 48 hours after key rotation are critical for detecting unauthorized access. Monitor actively!**