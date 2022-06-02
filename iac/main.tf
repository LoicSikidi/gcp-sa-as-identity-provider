resource "random_id" "random_suffix" {
  byte_length = 4
}

resource "google_service_account" "authz_server_dedicated_sa" {
  account_id  = "authz-srv-runtime-sa-${random_id.random_suffix.hex}"
  description = "Runtime Service Account dedicated to the simple authorization server (least privilege principle)"
}

resource "google_service_account" "api_dedicated_sa" {
  account_id  = "api-runtime-sa-${random_id.random_suffix.hex}"
  description = "Runtime Service Account dedicated to the simple api server (least privilege principle)"
}

resource "google_service_account_key" "user_managed" {
  count = var.use_user_managed_key == true ? 1 : 0

  service_account_id = google_service_account.authz_server_dedicated_sa.name
}

# When user-managed key is used, we store the private key in secret manager because is the simplest way to mount the file in the container's filesystem
resource "google_secret_manager_secret" "signing_key" {
  count = var.use_user_managed_key == true ? 1 : 0

  secret_id = "authz-server-siging-key-${random_id.random_suffix.hex}"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "signing_key_v1" {
  count = var.use_user_managed_key == true ? 1 : 0

  secret      = google_secret_manager_secret.signing_key[0].id
  secret_data = base64decode(google_service_account_key.user_managed[0].private_key)
}

resource "google_secret_manager_secret_iam_member" "authz_server_dedicated_sa_secret_accessor" {
  count = var.use_user_managed_key == true ? 1 : 0

  secret_id = google_secret_manager_secret.signing_key[0].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.authz_server_dedicated_sa.email}"
}

# When signing process is delegated to Google-managed key, authz server dedicated SA must have the permission to this sign JWT on GCP api
resource "google_service_account_iam_member" "authz_server_dedicated_sa_token_creator" {
  count = var.use_user_managed_key == false ? 1 : 0

  service_account_id = google_service_account.authz_server_dedicated_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.authz_server_dedicated_sa.email}"
}

resource "google_cloud_run_service" "simple_authz_server" {
  depends_on = [
    google_secret_manager_secret_iam_member.authz_server_dedicated_sa_secret_accessor,
    google_service_account_iam_member.authz_server_dedicated_sa_token_creator
  ]

  name     = "simple-authorization-server-${random_id.random_suffix.hex}"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.registry_name}/simple-authz-server:latest"

        dynamic "env" {
          for_each = var.use_user_managed_key == true ? [true] : []
          content {
            name  = "SIGNING_SERVICE_ACCOUNT_KEY_PATH"
            value = "/secrets/sa_key.json"
          }
        }

        # When user-managed key is used, the latter is mounted as a file in the container
        dynamic "volume_mounts" {
          for_each = var.use_user_managed_key == true ? [true] : []
          content {
            name       = "secret_manager_volume"
            mount_path = "/secrets"
          }
        }
      }
      service_account_name = google_service_account.authz_server_dedicated_sa.email

      dynamic "volumes" {
        for_each = var.use_user_managed_key == true ? [true] : []
        content {
          name = "secret_manager_volume"
          secret {
            secret_name  = google_secret_manager_secret.signing_key[0].secret_id
            default_mode = 0440
            items {
              key  = "latest"
              path = "sa_key.json"
            }
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "1"
        "run.googleapis.com/client-name"   = "terraform"
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "simple_authz_server_public_invoker" {
  location = google_cloud_run_service.simple_authz_server.location
  service  = google_cloud_run_service.simple_authz_server.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service" "simple_api" {
  name     = "simple-api-${random_id.random_suffix.hex}"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.registry_name}/simple-api:latest"

        env {
          name  = "SERVICE_ACCOUNT_ISSUER"
          value = google_service_account.authz_server_dedicated_sa.email
        }
      }
      service_account_name = google_service_account.api_dedicated_sa.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "1"
        "run.googleapis.com/client-name"   = "terraform"
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "simple_api_public_invoker" {
  location = google_cloud_run_service.simple_api.location
  service  = google_cloud_run_service.simple_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}