variable "project_name" {
  description = "Azure DevOps project name"
  type        = string
  default     = "tofu-aicl"
}

variable "organization_url" {
  description = "Azure DevOps organization URL"
  type        = string
  default     = "https://dev.azure.com/ancerallc"
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}
