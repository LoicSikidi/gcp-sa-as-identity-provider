output "authorization_server_url" {
  description = "Endpoint of the simple authorization server"
  value       = google_cloud_run_service.simple_authz_server.status[0].url
}

output "api_url" {
  description = "Endpoint of the simple api"
  value       = google_cloud_run_service.simple_api.status[0].url
}
