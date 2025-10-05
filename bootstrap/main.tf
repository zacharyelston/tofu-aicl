# tofu-aicl Project Bootstrap - Service Connections
# Creates Azure DevOps service connections using Terraform

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = "~> 0.11"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

provider "azuredevops" {
  org_service_url = var.organization_url
  # Set AZDO_PERSONAL_ACCESS_TOKEN environment variable
}

# Get current Azure context
data "azurerm_client_config" "current" {}

# Get Azure DevOps project
data "azuredevops_project" "tofu_aicl" {
  name = var.project_name
}

# Create ACR Service Connection
module "acr_connection" {
  source = "git::ssh://git@ssh.dev.azure.com/v3/ancerallc/ancera-iac/ancera-iac.git//modules/azure_devops_service_connection?ref=main"

  project_name     = var.project_name
  organization_url = var.organization_url
  connection_name  = "tofu-aicl-acr-connection"
  connection_type  = "acr"

  acr_name            = "ancerallc"
  acr_resource_group  = "ancera-dev-csp-rg"
  acr_subscription_id = var.subscription_id

  sp_name = "${var.project_name}-acr-sp"
}
