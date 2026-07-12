# =============================================================================
# GCC Car Value Platform — Root Variables
# =============================================================================

# --- AWS ---
variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "me-central-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

# --- VPC ---
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "availability_zones" {
  description = "Availability zones for subnet distribution"
  type        = list(string)
}

# --- RDS ---
variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 50
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "gcc_car_value"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "postgres"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password (override via tfvars or Secrets Manager)"
  type        = string
  sensitive   = true
  default     = null
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS (production only)"
  type        = bool
  default     = false
}

variable "db_backup_retention_days" {
  description = "Automated backup retention in days"
  type        = number
  default     = 7
}

# --- ECS ---
variable "ecs_api_cpu" {
  description = "vCPU units for the API Fargate task (1024 = 1 vCPU)"
  type        = number
}

variable "ecs_api_memory" {
  description = "Memory in MiB for the API Fargate task"
  type        = number
}

variable "ecs_api_desired_count" {
  description = "Desired number of API tasks"
  type        = number
}

variable "ecs_api_max_count" {
  description = "Maximum number of API tasks for auto-scaling"
  type        = number
}

variable "ecs_scraper_cpu" {
  description = "vCPU units for the scraper Fargate task"
  type        = number
  default     = 1024
}

variable "ecs_scraper_memory" {
  description = "Memory in MiB for the scraper Fargate task"
  type        = number
  default     = 2048
}

# --- Container Images ---
variable "api_container_image" {
  description = "Docker image for the API service (ECR repo:tag)"
  type        = string
}

variable "scraper_container_image" {
  description = "Docker image for the scraper service (ECR repo:tag)"
  type        = string
}

# --- Domain & CDN ---
variable "domain_name" {
  description = "Root domain name for the platform"
  type        = string
  default     = null
}

variable "certificate_arn" {
  description = "ACM certificate ARN for CloudFront (us-east-1)"
  type        = string
  default     = null
}

# --- Tags ---
variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}
