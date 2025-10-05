# tofu-aicl Bootstrap - Service Connections

This directory contains Terraform configuration to create Azure DevOps service connections for the tofu-aicl project.

## What This Creates

- **ACR Service Connection** (`tofu-aicl-acr-connection`) - For pushing Docker images to ancerallc ACR
- **Service Principal** - With AcrPush permissions

## Prerequisites

1. **Azure CLI** - Authenticated to Azure subscription
2. **Azure DevOps PAT** - With permissions:
   - Service Connections: Read, query, & manage
   - Project and Team: Read, write, & manage

## Usage

### First Time Setup

```bash
# Set your Azure subscription ID
export TF_VAR_subscription_id="your-subscription-id"

# Set Azure DevOps PAT for authentication
export AZDO_PERSONAL_ACCESS_TOKEN="your-pat-token"

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

### Outputs

After applying, you'll get:
```
acr_connection_id = "..."
acr_connection_name = "tofu-aicl-acr-connection"
service_principal_id = "..."
```

### Verify in Azure DevOps

1. Navigate to **Project Settings** → **Service connections**
2. You should see: `tofu-aicl-acr-connection` (Docker Registry)

## Update Pipeline

After bootstrap completes, update `azure-pipelines.yml`:

```yaml
variables:
  dockerRegistryServiceConnection: 'tofu-aicl-acr-connection'  # Updated from 'ancera'
  containerRegistry: 'ancerallc.azurecr.io'
```

## Troubleshooting

### Error: "Permission denied"

**Solution:** Ensure your Azure DevOps PAT has correct permissions

### Error: "Project not found"

**Solution:** Check `project_name` in variables.tf matches your Azure DevOps project name (should be "tofu-aicl")

### Error: "Subscription not found"

**Solution:** Verify your Azure CLI is authenticated to the correct subscription:
```bash
az account show
az account set --subscription "your-subscription-id"
```

## Notes

- Service connection credentials are stored in Azure DevOps (encrypted)
- Terraform state contains sensitive data - protect accordingly
- Service Principal has 1-year expiration (renewable via `terraform apply`)

---

**Standard:** Terraform IaC approach  
**Module Source:** `ancera-iac/modules/azure_devops_service_connection`
