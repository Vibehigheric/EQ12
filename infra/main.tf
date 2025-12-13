# EQ12 Sports Betting Analytics - Google Cloud Infrastructure
# Implements Jump Start Solutions: Data Warehouse, Generative AI RAG, Knowledge Base, Web Application
# Focus: Monetization-first architecture with cost controls and security

# ================================
# API ENABLEMENT
# ================================

resource "google_project_service" "required_apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "storage-component.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudscheduler.googleapis.com",
    "pubsub.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudfunctions.googleapis.com",
    "eventarc.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "documentai.googleapis.com"
  ])

  service                    = each.key
  disable_dependent_services = false
  disable_on_destroy        = false
}

# ================================
# BIGQUERY DATA WAREHOUSE (Jump Start: Data Warehouse)
# ================================

resource "google_bigquery_dataset" "eq12_dw" {
  dataset_id  = "eq12_dw"
  location    = var.bq_location
  description = "EQ12 Sports Betting Analytics Data Warehouse - Production Dataset"

  access {
    role          = "OWNER"
    user_by_email = google_service_account.eq12_runner.email
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  labels = {
    environment = var.environment
    purpose     = "sports_betting_analytics"
    cost_center = "monetization"
  }

  depends_on = [google_project_service.required_apis]
}

# Partitioned tables for performance and cost control
resource "google_bigquery_table" "odds" {
  dataset_id = google_bigquery_dataset.eq12_dw.dataset_id
  table_id   = "odds"

  time_partitioning {
    type  = "DAY"
    field = "ts"
  }

  clustering = ["sport", "event_id"]

  schema = jsonencode([
    {
      name = "ts"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "event_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "sport"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "market"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "selection"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "book"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "odds"
      type = "INTEGER"
      mode = "REQUIRED"
    }
  ])

  labels = {
    table_type = "transactional"
    retention  = "1year"
  }
}

resource "google_bigquery_table" "arb_opportunities" {
  dataset_id = google_bigquery_dataset.eq12_dw.dataset_id
  table_id   = "arb_opportunities"

  time_partitioning {
    type  = "DAY"
    field = "ts"
  }

  clustering = ["event_id", "arb_pct"]

  schema = jsonencode([
    {
      name = "ts"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "event_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "sideA"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "bookA"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "oddsA"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "sideB"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "bookB"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "oddsB"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "arb_pct"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "bankroll"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "lock_profit"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "mode"
      type = "STRING"
      mode = "REQUIRED"
    }
  ])
}

# ================================
# CLOUD STORAGE (Deliverables & Assets)
# ================================

resource "google_storage_bucket" "eq12_deliverables" {
  name     = var.bucket_name
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  labels = {
    purpose     = "monetization_deliverables"
    environment = var.environment
  }

  depends_on = [google_project_service.required_apis]
}

# ================================
# CLOUD SQL (RAG Knowledge Base - Jump Start: RAG with Cloud SQL)
# ================================

resource "google_sql_database_instance" "eq12_rag" {
  name             = "eq12-rag-${var.environment}"
  database_version = "POSTGRES_15"
  region          = var.sql_region

  settings {
    tier              = "db-f1-micro"  # Cost-optimized for development
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 20
    disk_autoresize   = true

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.eq12_vpc.id
      require_ssl     = true
    }

    database_flags {
      name  = "shared_preload_libraries"
      value = "vector"
    }
  }

  deletion_protection = true
  depends_on         = [google_project_service.required_apis]
}

resource "google_sql_database" "rag_knowledge" {
  name     = "rag_knowledge"
  instance = google_sql_database_instance.eq12_rag.name
}

resource "google_sql_user" "rag_user" {
  name     = "eq12_rag_user"
  instance = google_sql_database_instance.eq12_rag.name
  password = random_password.rag_password.result
}

resource "random_password" "rag_password" {
  length  = 16
  special = true
}

# ================================
# VPC AND NETWORKING
# ================================

resource "google_compute_network" "eq12_vpc" {
  name                    = "eq12-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "eq12_subnet" {
  name          = "eq12-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.eq12_vpc.id

  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "10.1.0.0/24"
  }
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "eq12-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.eq12_vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.eq12_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

resource "google_vpc_access_connector" "eq12_connector" {
  name          = "eq12-connector"
  subnet {
    name = google_compute_subnetwork.eq12_subnet.name
  }
  machine_type   = "f1-micro"
  min_instances  = 2
  max_instances  = 3
  region         = var.region
}

# ================================
# ARTIFACT REGISTRY
# ================================

resource "google_artifact_registry_repository" "eq12_docker" {
  location      = var.region
  repository_id = "eq12-docker"
  description   = "EQ12 Docker images repository"
  format        = "DOCKER"

  labels = {
    environment = var.environment
    purpose     = "microservices"
  }

  depends_on = [google_project_service.required_apis]
}

# ================================
# SECRET MANAGER
# ================================

resource "google_secret_manager_secret" "bitly_token" {
  secret_id = "BITLY_TOKEN"

  replication {
    auto {}
  }

  labels = {
    service = "monetization"
  }
}

resource "google_secret_manager_secret" "telegram_bot_token" {
  secret_id = "TG_TOKEN"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "telegram_chat_id" {
  secret_id = "TG_CHAT"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "GEMINI_API_KEY"

  replication {
    auto {}
  }

  labels = {
    service = "ai_analytics"
  }
}

resource "google_secret_manager_secret" "rag_db_password" {
  secret_id = "RAG_DB_PASSWORD"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "rag_db_password_version" {
  secret      = google_secret_manager_secret.rag_db_password.id
  secret_data = random_password.rag_password.result
}

# ================================
# SERVICE ACCOUNTS AND IAM
# ================================

resource "google_service_account" "eq12_runner" {
  account_id   = "eq12-runner"
  display_name = "EQ12 Analytics Runner Service Account"
  description  = "Service account for EQ12 sports betting analytics operations"
}

resource "google_service_account" "eq12_deployer" {
  account_id   = "eq12-deployer"
  display_name = "EQ12 CI/CD Deployer Service Account"
  description  = "Service account for Cloud Build deployments"
}

# IAM bindings for eq12_runner (least privilege)
resource "google_project_iam_binding" "eq12_runner_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  members = [
    "serviceAccount:${google_service_account.eq12_runner.email}"
  ]
}

resource "google_project_iam_binding" "eq12_runner_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  members = [
    "serviceAccount:${google_service_account.eq12_runner.email}"
  ]
}

resource "google_project_iam_binding" "eq12_runner_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${google_service_account.eq12_runner.email}"
  ]
}

resource "google_project_iam_binding" "eq12_runner_vertex_ai" {
  count   = var.enable_vertex_ai ? 1 : 0
  project = var.project_id
  role    = "roles/aiplatform.user"
  members = [
    "serviceAccount:${google_service_account.eq12_runner.email}"
  ]
}

# ================================
# CLOUD RUN SERVICES
# ================================

# API Service (Jump Start: Dynamic Web Application)
resource "google_cloud_run_service" "eq12_api" {
  name     = "eq12-api"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.eq12_runner.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/eq12-docker/eq12-api:latest"

        ports {
          container_port = 8080
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "DATASET_ID"
          value = google_bigquery_dataset.eq12_dw.dataset_id
        }

        env {
          name  = "BUCKET_NAME"
          value = google_storage_bucket.eq12_deliverables.name
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }

      container_concurrency = 80
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = tostring(var.max_instances)
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.eq12_connector.name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis]
}

# Scheduler Service
resource "google_cloud_run_service" "eq12_scheduler" {
  name     = "eq12-scheduler"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.eq12_runner.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/eq12-docker/eq12-scheduler:latest"

        ports {
          container_port = 8080
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "1"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.eq12_connector.name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# RAG Service (Jump Start: Generative AI RAG)
resource "google_cloud_run_service" "eq12_rag" {
  name     = "eq12-rag"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.eq12_runner.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/eq12-docker/eq12-rag:latest"

        env {
          name  = "DB_HOST"
          value = google_sql_database_instance.eq12_rag.private_ip_address
        }

        env {
          name  = "DB_NAME"
          value = google_sql_database.rag_knowledge.name
        }

        env {
          name  = "DB_USER"
          value = google_sql_user.rag_user.name
        }

        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.rag_db_password.secret_id
              key  = "latest"
            }
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "2"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.eq12_connector.name
      }
    }
  }
}

# Knowledge Base Service (Jump Start: Generative AI Knowledge Base)
resource "google_cloud_run_service" "eq12_kb" {
  name     = "eq12-kb"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.eq12_runner.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/eq12-docker/eq12-kb:latest"

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "2"
      }
    }
  }
}

# ================================
# CLOUD RUN IAM (Public API Access)
# ================================

resource "google_cloud_run_service_iam_binding" "eq12_api_public" {
  service  = google_cloud_run_service.eq12_api.name
  location = google_cloud_run_service.eq12_api.location
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}

# ================================
# PUB/SUB TOPICS
# ================================

resource "google_pubsub_topic" "eq12_alerts" {
  name = "eq12-alerts"

  labels = {
    environment = var.environment
    purpose     = "monetization_alerts"
  }
}

resource "google_pubsub_topic" "eq12_reports" {
  name = "eq12-reports"

  labels = {
    environment = var.environment
    purpose     = "deliverable_notifications"
  }
}

resource "google_pubsub_topic" "eq12_arb" {
  name = "eq12-arb"

  labels = {
    environment = var.environment
    purpose     = "arbitrage_opportunities"
  }
}

# ================================
# CLOUD SCHEDULER
# ================================

resource "google_cloud_scheduler_job" "eq12_daily" {
  name             = "eq12-daily"
  description      = "Daily EQ12 analytics pipeline execution"
  schedule         = "5 9 * * *"  # 09:05 daily
  time_zone        = var.scheduler_timezone
  attempt_deadline = "320s"

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "GET"
    uri         = "${google_cloud_run_service.eq12_scheduler.status[0].url}/run?job=daily"

    oidc_token {
      service_account_email = google_service_account.eq12_runner.email
    }
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloud_scheduler_job" "eq12_weekly" {
  name             = "eq12-weekly"
  description      = "Weekly EQ12 analytics and reporting"
  schedule         = "10 9 * * 1"  # 09:10 Monday
  time_zone        = var.scheduler_timezone
  attempt_deadline = "600s"

  retry_config {
    retry_count = 2
  }

  http_target {
    http_method = "GET"
    uri         = "${google_cloud_run_service.eq12_scheduler.status[0].url}/run?job=weekly"

    oidc_token {
      service_account_email = google_service_account.eq12_runner.email
    }
  }
}

# ================================
# MONITORING (Optional)
# ================================

resource "google_monitoring_alert_policy" "high_cost_alert" {
  count        = var.enable_monitoring ? 1 : 0
  display_name = "EQ12 High Cost Alert"
  combiner     = "OR"

  conditions {
    display_name = "BigQuery cost threshold"

    condition_threshold {
      filter          = "resource.type=\"bigquery_project\""
      comparison      = "COMPARISON_GT"
      threshold_value = 50.0  # $50 daily
      duration        = "300s"
    }
  }

  notification_channels = []

  alert_strategy {
    auto_close = "1800s"
  }
}

# ================================
# OUTPUTS
# ================================

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID for EQ12 data warehouse"
  value       = google_bigquery_dataset.eq12_dw.dataset_id
}

output "storage_bucket" {
  description = "Cloud Storage bucket for deliverables"
  value       = google_storage_bucket.eq12_deliverables.name
}

output "api_url" {
  description = "EQ12 API Cloud Run service URL"
  value       = google_cloud_run_service.eq12_api.status[0].url
}

output "scheduler_url" {
  description = "EQ12 Scheduler Cloud Run service URL"
  value       = google_cloud_run_service.eq12_scheduler.status[0].url
}

output "rag_url" {
  description = "EQ12 RAG service URL"
  value       = google_cloud_run_service.eq12_rag.status[0].url
}

output "kb_url" {
  description = "EQ12 Knowledge Base service URL"
  value       = google_cloud_run_service.eq12_kb.status[0].url
}

output "service_account_email" {
  description = "EQ12 runner service account email"
  value       = google_service_account.eq12_runner.email
}

output "sql_instance_connection" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.eq12_rag.connection_name
}
