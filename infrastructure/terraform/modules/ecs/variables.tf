variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for the ALB"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for ECS tasks"
  type        = list(string)
}

variable "api_cpu" {
  description = "vCPU units for API task (1024 = 1 vCPU)"
  type        = number
}

variable "api_memory" {
  description = "Memory MiB for API task"
  type        = number
}

variable "api_desired_count" {
  description = "Desired number of API tasks"
  type        = number
}

variable "api_max_count" {
  description = "Maximum number of API tasks"
  type        = number
}

variable "scraper_cpu" {
  description = "vCPU units for scraper task"
  type        = number
}

variable "scraper_memory" {
  description = "Memory MiB for scraper task"
  type        = number
}

variable "api_container_image" {
  description = "Docker image for API service"
  type        = string
}

variable "scraper_container_image" {
  description = "Docker image for scraper service"
  type        = string
}

variable "database_url_secret_arn" {
  description = "Secrets Manager ARN for DATABASE_URL"
  type        = string
}

variable "jwt_secret_arn" {
  description = "Secrets Manager ARN for JWT secret"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for raw data"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS (optional)"
  type        = string
  default     = null
}

variable "execution_role_arn" {
  description = "IAM role ARN for ECS task execution"
  type        = string
}

variable "task_role_arn" {
  description = "IAM role ARN for ECS tasks"
  type        = string
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}
