# =============================================================================
# GCC Car Value Platform — Root Outputs
# =============================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.network.private_subnet_ids
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_api_service_name" {
  description = "ECS API service name"
  value       = module.ecs.api_service_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint (hostname:port)"
  value       = module.rds.endpoint
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.rds.database_name
}

output "database_url_secret_arn" {
  description = "Secrets Manager secret ARN for DATABASE_URL"
  value       = module.secrets.database_url_secret_arn
}

output "s3_raw_data_bucket" {
  description = "S3 bucket name for raw scraper data"
  value       = module.s3.raw_data_bucket_name
}

output "s3_mlflow_artifacts_bucket" {
  description = "S3 bucket name for MLflow artifacts"
  value       = module.s3.mlflow_artifacts_bucket_name
}

output "ecr_api_repository_url" {
  description = "ECR repository URL for the API image"
  value       = module.ecr.api_repository_url
}

output "ecr_scraper_repository_url" {
  description = "ECR repository URL for the scraper image"
  value       = module.ecr.scraper_repository_url
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.cloudfront.domain_name
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.ecs.alb_dns_name
}

output "environment" {
  description = "Current environment name"
  value       = var.environment
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}
