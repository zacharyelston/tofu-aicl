# Bootstrap Instructions for tofu-aicl

## Overview

Before the Azure DevOps pipeline can run, we need to create the service connection for pushing Docker images to Azure Container Registry (ACR).

## What Needs to Be Done

The pipeline currently fails with:
```
Job PushContainers: Step Docker input containerRegistry references service connection 
tofu-aicl-acr-connection which could not be found.
```

This is because the service connection doesn't exist yet. We need to create it using Terraform.

## Prerequisites

1. **Azure CLI** - Authenticated to the Ancera subscription
2. **Azure DevOps PAT** - With permissions:
   - Service Connections: Read, query, & manage
   - Project and Team: Read, write, & manage
3. **Terraform** - Installed locally

## Step-by-Step Instructions

### Option 1: Automated Bootstrap (Recommended)

Run the bootstrap pipeline in Azure DevOps:

1. Go to Azure DevOps: https://dev.azure.com/ancerallc/tofu-aicl/_build
2. Click "New pipeline" or "Run pipeline"
3. Select `azure-pipelines-bootstrap.yml`
4. Click "Run"

The pipeline will:
- ✅ Install Terraform
- ✅ Get Azure subscription ID automatically
- ✅ Use System.AccessToken for authentication
- ✅ Create the service connection
- ✅ Show outputs

**Prerequisites for automated bootstrap**:
- Existing service connection `ancera-service-connection` (for running Terraform)
- Pipeline must have permission to create service connections

### Option 2: Manual Bootstrap

If you prefer to run locally:

#### 1. Get Azure Subscription ID

```bash
az account show --query id -o tsv
```

#### 2. Set Environment Variables

```bash
# Set your Azure subscription ID (from step 1)
export TF_VAR_subscription_id="your-subscription-id-here"

# Set Azure DevOps PAT
export AZDO_PERSONAL_ACCESS_TOKEN="your-pat-token-here"
```

#### 3. Run Terraform Bootstrap

```bash
cd /Users/zacelston/code/tofu-aicl/bootstrap

# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Create the service connection
terraform apply
```

### 4. Verify Service Connection

After `terraform apply` completes:

1. Go to Azure DevOps: https://dev.azure.com/ancerallc/tofu-aicl
2. Navigate to **Project Settings** → **Service connections**
3. Verify you see: `tofu-aicl-acr-connection` (Docker Registry type)

### 5. Re-run Pipeline

Once the service connection exists, the pipeline will be able to:
- Build provider containers
- Push containers to `ancerallc.azurecr.io`

## What Gets Created

The bootstrap creates:

1. **Service Principal**: `tofu-aicl-acr-sp`
   - Scoped to: `ancerallc` ACR
   - Role: `AcrPush`
   - Expiration: 1 year

2. **Service Connection**: `tofu-aicl-acr-connection`
   - Type: Docker Registry
   - Authentication: Service Principal
   - Registry: `ancerallc.azurecr.io`

## Terraform Outputs

After successful apply:
```
acr_connection_id = "guid-here"
acr_connection_name = "tofu-aicl-acr-connection"
service_principal_id = "guid-here"
```

## Troubleshooting

### Error: "Permission denied"

**Cause**: Azure DevOps PAT doesn't have sufficient permissions

**Solution**: 
1. Go to https://dev.azure.com/ancerallc/_usersSettings/tokens
2. Create new PAT with:
   - Service Connections: Read, query, & manage
   - Project and Team: Read, write, & manage

### Error: "Project not found"

**Cause**: Project name mismatch

**Solution**: Verify project name in `bootstrap/variables.tf` is `tofu-aicl`

### Error: "Subscription not found"

**Cause**: Azure CLI not authenticated to correct subscription

**Solution**:
```bash
az account list -o table
az account set --subscription "your-subscription-id"
```

## Alternative: Manual Creation

If Terraform fails, you can create the service connection manually:

1. Go to Azure DevOps → Project Settings → Service connections
2. Click "New service connection"
3. Select "Docker Registry"
4. Choose "Azure Container Registry"
5. Select subscription and `ancerallc` registry
6. Name it: `tofu-aicl-acr-connection`
7. Grant access to all pipelines

## Next Steps

After bootstrap completes:
1. ✅ Service connection exists
2. ✅ Pipeline can push to ACR
3. ✅ PR #9210 pipeline will pass
4. → Merge PR to main
5. → Deploy provider containers

## Related Files

- `bootstrap/main.tf` - Terraform configuration
- `bootstrap/variables.tf` - Input variables
- `bootstrap/outputs.tf` - Output values
- `bootstrap/README.md` - Detailed bootstrap documentation
- `azure-pipelines.yml` - Pipeline using the service connection

---

**Pattern Source**: YTBD project bootstrap  
**Module**: `ancera-iac/modules/azure_devops_service_connection`  
**Last Updated**: 2025-10-05
