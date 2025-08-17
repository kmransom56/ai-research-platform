# 🚀 AI Research Platform - Deployment Guide

This guide explains how to deploy the platform after the secret management updates.

## 🔧 Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Configure required environment variables in `.env`:**
   ```bash
   # Database passwords
   NEO4J_PASSWORD=your_secure_neo4j_password
   DB_PASSWORD=your_secure_db_password
   
   # API keys (set via GitHub Secrets or manually)
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   MERAKI_API_KEY=your_meraki_key
   ```

## 🔐 Secret Management

The application now uses environment variables instead of hardcoded secrets:

### Files Updated:
- ✅ `docker-compose.simple.yml` - Neo4j authentication uses `${NEO4J_PASSWORD}`
- ✅ `docker-compose.portable.yml` - Neo4j authentication uses `${NEO4J_PASSWORD}`  
- ✅ `docker-compose.ai-stack.yml` - Neo4j authentication uses `${NEO4J_PASSWORD}`
- ✅ `python/meraki-connector/main.py` - Database URL uses `${DB_USER}:${DB_PASSWORD}`
- ✅ `.env.template` - Updated with all required variables

### Backup Files Created:
All modified files have `.backup` versions for rollback if needed.

## 🚀 Deployment Commands

### Option 1: Simple Deployment
```bash
# Set required environment variables
export NEO4J_PASSWORD=password
export DB_PASSWORD=chatcopilot-password

# Start platform
docker compose -f docker-compose.simple.yml up -d
```

### Option 2: Portable Deployment (Recommended)
```bash
# Configure .env file first
cp .env.template .env
# Edit .env with your values

# Start platform
docker compose -f docker-compose.portable.yml up -d
```

### Option 3: AI Stack Deployment
```bash
# For GPU-enabled deployment with AI stack
export NEO4J_PASSWORD=password
docker compose -f docker-compose.ai-stack.yml up -d
```

## ✅ Verification

1. **Check configuration validity:**
   ```bash
   docker compose -f docker-compose.simple.yml config --quiet
   ```

2. **Verify services are running:**
   ```bash
   docker compose -f docker-compose.simple.yml ps
   ```

3. **Test key services:**
   ```bash
   # Neo4j Browser
   curl -f http://localhost:7474

   # Backend API
   curl -f http://localhost:11000/healthz

   # Chat Copilot Frontend
   curl -f http://localhost:3000
   ```

## 🔧 Troubleshooting

### Common Issues:

1. **"NEO4J_PASSWORD variable is not set"**
   - Solution: Set `NEO4J_PASSWORD` in your `.env` file or environment

2. **Database connection issues**
   - Solution: Ensure `DB_PASSWORD` matches your PostgreSQL configuration

3. **API key not found**
   - Solution: Set API keys in environment or use GitHub Secrets workflow

### Rollback if Needed:
```bash
# Restore original files from backups
cp docker-compose.simple.yml.backup docker-compose.simple.yml
cp docker-compose.portable.yml.backup docker-compose.portable.yml
cp docker-compose.ai-stack.yml.backup docker-compose.ai-stack.yml
cp python/meraki-connector/main.py.backup python/meraki-connector/main.py
```

## 📋 Environment Variables Reference

### Required Variables:
- `NEO4J_PASSWORD` - Neo4j database password
- `DB_PASSWORD` - PostgreSQL password  
- `DB_USER` - PostgreSQL username (default: postgres)

### Optional Variables:
- `OPENAI_API_KEY` - For OpenAI integration
- `ANTHROPIC_API_KEY` - For Anthropic integration  
- `MERAKI_API_KEY` - For Meraki network connector
- `POSTGRES_PASSWORD` - Alternative to DB_PASSWORD
- `RABBITMQ_DEFAULT_PASS` - RabbitMQ password

### GitHub Secrets Integration:
If using GitHub Actions, the platform will automatically use repository secrets when available.

## 🎉 Success!

Your AI Research Platform is now deployed with secure secret management! 

Next steps:
- Access the platform at http://localhost:11000
- Configure your AI providers through the web interface
- Start building with the multi-agent AI capabilities