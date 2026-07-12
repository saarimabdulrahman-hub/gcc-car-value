# =============================================================================
# Production Environment — Public traffic
# =============================================================================

variable "aws_region"              { default = "me-central-1" }
variable "environment"             { default = "production" }
variable "vpc_cidr"                { default = "10.2.0.0/16" }
variable "availability_zones"      { default = ["me-central-1a", "me-central-1b"] }
variable "db_instance_class"       { default = "db.t3.medium" }
variable "db_allocated_storage"    { default = 50 }
variable "db_name"                 { default = "gcc_car_value" }
variable "db_username"             { default = "postgres" }
variable "db_multi_az"             { default = false }
variable "db_backup_retention_days" { default = 7 }
variable "ecs_api_cpu"             { default = 512 }
variable "ecs_api_memory"          { default = 1024 }
variable "ecs_api_desired_count"   { default = 1 }
variable "ecs_api_max_count"       { default = 4 }
variable "ecs_scraper_cpu"         { default = 1024 }
variable "ecs_scraper_memory"      { default = 2048 }
