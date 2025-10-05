output "acr_connection_id" {
  description = "ACR service connection ID"
  value       = module.acr_connection.connection_id
}

output "acr_connection_name" {
  description = "ACR service connection name"
  value       = module.acr_connection.connection_name
}

output "service_principal_id" {
  description = "Service Principal ID for ACR"
  value       = module.acr_connection.service_principal_id
}
