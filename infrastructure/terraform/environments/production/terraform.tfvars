# Production environment — public traffic, full resources
# ALL secret values MUST be set via environment variables, never committed

aws_region          = "me-central-1"
vpc_cidr            = "10.2.0.0/16"
availability_zones  = ["me-central-1a", "me-central-1b"]

db_instance_class       = "db.t3.medium"
db_allocated_storage    = 50
db_name                 = "gcc_car_value"
db_username             = "postgres"
db_password             = null  # REQUIRED: TF_VAR_db_password (generate strong password)
db_multi_az             = false
db_backup_retention_days = 7

ecs_api_cpu             = 512
ecs_api_memory          = 1024
ecs_api_desired_count   = 1
ecs_api_max_count       = 4

# REQUIRED: Set via environment variables
jwt_secret      = null  # TF_VAR_jwt_secret (min 32 chars, random)
claude_api_key  = null  # TF_VAR_claude_api_key

# Set domain and ACM certificate ARN for production
domain_name     = null  # e.g. "gcccarvalue.com"
certificate_arn = null  # ACM cert ARN in us-east-1

tags = {
  Environment = "production"
  CostCenter  = "engineering"
}
