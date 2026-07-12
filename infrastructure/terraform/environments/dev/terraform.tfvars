# Dev environment — minimal resources, no production data
# Copy and customize before applying

aws_region          = "me-central-1"
vpc_cidr            = "10.0.0.0/16"
availability_zones  = ["me-central-1a", "me-central-1b"]

db_instance_class       = "db.t3.micro"
db_allocated_storage    = 20
db_name                 = "gcc_car_value"
db_username             = "postgres"
db_password             = null  # Set via TF_VAR_db_password
db_multi_az             = false
db_backup_retention_days = 1

ecs_api_cpu             = 256
ecs_api_memory          = 512
ecs_api_desired_count   = 1
ecs_api_max_count       = 2

# Secrets (set via env vars, never commit real values)
jwt_secret     = null  # TF_VAR_jwt_secret
claude_api_key = null  # TF_VAR_claude_api_key

domain_name    = null
certificate_arn = null

tags = {
  Environment = "dev"
  CostCenter  = "engineering"
}
