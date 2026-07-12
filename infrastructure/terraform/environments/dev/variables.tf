# =============================================================================
# Dev Environment — Local Docker Compose equivalent
# =============================================================================
# Note: Dev uses Docker Compose locally, not AWS.
# This environment file is a placeholder for when dev moves to AWS shared sandbox.

variable "aws_region" {
  default = "me-central-1"
}

variable "environment" {
  default = "dev"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "availability_zones" {
  default = ["me-central-1a", "me-central-1b"]
}

variable "db_instance_class" {
  default = "db.t3.micro"
}

variable "db_allocated_storage" {
  default = 20
}

variable "db_multi_az" {
  default = false
}

variable "db_backup_retention_days" {
  default = 1
}

variable "ecs_api_cpu" {
  default = 256 # 0.25 vCPU
}

variable "ecs_api_memory" {
  default = 512 # 512 MB
}

variable "ecs_api_desired_count" {
  default = 1
}

variable "ecs_api_max_count" {
  default = 2
}

variable "ecs_scraper_cpu" {
  default = 512
}

variable "ecs_scraper_memory" {
  default = 1024
}
