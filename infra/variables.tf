# EQ12 GCP Infrastructure Variables
# Monetization-first configuration for sports betting analytics platform

variable "project_id" {
  description = "Google Cloud Project ID for EQ12 deployment"
  type        = string
  default     = "clear-region-421121"
}

variable "region" {
  description = "Primary GCP region for services deployment"
  type        = string
  default     = "us-central1"
}

variable "bq_location" {
  description = "BigQuery dataset location for data warehouse"
  type        = string
  default     = "US"
}

variable "bucket_name" {
  description = "Cloud Storage bucket for deliverables and monetization assets"
  type        = string
  default     = "eq12-deliverables"
}

variable "sql_region" {
  description = "Cloud SQL region for RAG knowledge base"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "domain_name" {
  description = "Domain name for EQ12 web application (optional)"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "Enable advanced monitoring and logging"
  type        = bool
  default     = true
}

variable "enable_vertex_ai" {
  description = "Enable Vertex AI for advanced analytics"
  type        = bool
  default     = true
}

variable "max_instances" {
  description = "Maximum Cloud Run instances per service"
  type        = number
  default     = 3
}

variable "scheduler_timezone" {
  description = "Timezone for Cloud Scheduler jobs"
  type        = string
  default     = "America/New_York"
}
