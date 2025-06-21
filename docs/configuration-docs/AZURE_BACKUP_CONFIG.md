# Azure OpenAI Backup Configuration

This document provides instructions for configuring Azure OpenAI as a backup service for the AI Research Platform.

## Overview

The platform is configured with OpenAI as the primary service, with Azure OpenAI available as a backup option. This provides redundancy and ensures continued operation if the primary service experiences issues.

## Configuration Files

### Primary Configuration
- `appsettings.Development.json` - Uses OpenAI (currently active)
- `appsettings.json` - Uses OpenAI (currently active)

### Backup Configuration
- `appsettings.Azure.json` - Ready for Azure OpenAI configuration

## Environment Configuration

### 1. Create Local Environment File

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Update .bashrc (Optional)

For system-wide access, uncomment and configure the Azure OpenAI variables in `/home/keith/.bashrc`:

```bash
# Azure OpenAI Configuration (Backup) - Configure when needed
export AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
export AZURE_OPENAI_DEPLOYMENT="gpt-4o"
export AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002"
```

### 2. Update Configuration Files

Replace the OpenAI configuration in `appsettings.Development.json` and `appsettings.json` with:

```json
{
  "KernelMemory": {
    "TextGeneratorType": "AzureOpenAI",
    "DataIngestion": {
      "EmbeddingGeneratorTypes": ["AzureOpenAI"]
    },
    "Retrieval": {
      "EmbeddingGeneratorType": "AzureOpenAI"
    },
    "Services": {
      "AzureOpenAI": {
        "APIKey": "your-azure-openai-api-key",
        "Endpoint": "https://your-resource-name.openai.azure.com/",
        "Deployment": "gpt-4o",
        "EmbeddingDeployment": "text-embedding-ada-002",
        "APIType": "AzureOpenAI",
        "APIVersion": "2024-02-15-preview"
      }
    }
  },
  "SemanticKernel": {
    "Services": [
      {
        "Type": "AzureOpenAI",
        "Models": [
          {
            "DeploymentOrModelId": "gpt-4o",
            "ModelId": "gpt-4o",
            "AIServiceType": "ChatCompletion"
          }
        ],
        "Endpoint": "https://your-resource-name.openai.azure.com/",
        "APIKey": "your-azure-openai-api-key",
        "APIVersion": "2024-02-15-preview"
      }
    ]
  }
}
```

### 3. Required Azure Resources

Ensure you have the following Azure OpenAI deployments:
- **Text Generation**: `gpt-4o` (or `gpt-4`, `gpt-35-turbo`)
- **Embeddings**: `text-embedding-ada-002`

### 4. Restart Services

After configuration changes:

```bash
# Restart Chat Copilot backend
cd /home/keith/chat-copilot/webapi
dotnet run --urls "https://100.123.10.72:40443"

# Restart frontend
cd /home/keith/chat-copilot/webapp
yarn start
```

## Quick Switch Script

You can create a quick switch script for easy switching between providers:

```bash
#!/bin/bash
# switch-to-azure.sh

echo "Switching to Azure OpenAI..."

# Backup current config
cp webapi/appsettings.json webapi/appsettings.json.openai.backup

# Copy Azure config
cp webapi/appsettings.Azure.json webapi/appsettings.json

echo "Configuration switched to Azure OpenAI"
echo "Remember to restart the backend service"
```

## Monitoring

Both configurations support the same health check endpoint:
- Health Check: `https://100.123.10.72:40443/healthz`

## Benefits of Dual Configuration

1. **Redundancy**: If OpenAI experiences outages, switch to Azure OpenAI
2. **Cost Optimization**: Compare costs between providers
3. **Regional Compliance**: Use Azure for data residency requirements
4. **Performance Testing**: Compare response times and quality

## Notes

- Both services support the same GPT-4 models
- Embedding models are compatible
- No changes required to frontend applications
- All Tailscale network access remains the same