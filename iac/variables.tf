variable "project_id" {
  description = "Project ID where resources are created"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "registry_name" {
  description = "Name of the artifact registry"
  type        = string
  default     = "sa-as-identity-provider"
}

variable "use_user_managed_key" {
  description = "Flag indicating if a user-managed service account key must be used"
  type        = bool
  default     = false
}