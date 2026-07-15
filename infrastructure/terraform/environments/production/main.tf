# =============================================================================
# Production Environment — Public traffic, full resources
# =============================================================================

terraform {
  required_version = ">= 1.6.0"
}

module "network" {
  source              = "../../modules/network"
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  environment         = var.environment
  tags                = var.tags
}

module "s3" {
  source      = "../../modules/s3"
  environment = var.environment
  tags        = var.tags
}

module "ecr" {
  source      = "../../modules/ecr"
  environment = var.environment
  tags        = var.tags
}

module "iam" {
  source                     = "../../modules/iam"
  environment                = var.environment
  raw_data_bucket_arn        = module.s3.raw_data_bucket_arn
  mlflow_artifacts_bucket_arn = module.s3.mlflow_artifacts_bucket_arn
  tags                       = var.tags
}

module "rds" {
  source                    = "../../modules/rds"
  environment               = var.environment
  vpc_id                    = module.network.vpc_id
  private_subnet_ids        = module.network.private_subnet_ids
  instance_class            = var.db_instance_class
  allocated_storage         = var.db_allocated_storage
  db_name                   = var.db_name
  db_username               = var.db_username
  db_password               = var.db_password
  multi_az                  = var.db_multi_az
  backup_retention_days     = var.db_backup_retention_days
  allowed_security_group_ids = [module.ecs.ecs_task_security_group_id]
  tags                      = var.tags
}

module "secrets" {
  source          = "../../modules/secrets"
  environment     = var.environment
  database_url    = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${module.rds.address}:${module.rds.port}/${var.db_name}"
  jwt_secret      = var.jwt_secret
  claude_api_key  = var.claude_api_key
  tags            = var.tags
}

module "ecs" {
  source                  = "../../modules/ecs"
  environment             = var.environment
  vpc_id                  = module.network.vpc_id
  public_subnet_ids       = module.network.public_subnet_ids
  private_subnet_ids      = module.network.private_subnet_ids
  api_cpu                 = var.ecs_api_cpu
  api_memory              = var.ecs_api_memory
  api_desired_count       = var.ecs_api_desired_count
  api_max_count           = var.ecs_api_max_count
  scraper_cpu             = var.ecs_scraper_cpu
  scraper_memory          = var.ecs_scraper_memory
  api_container_image     = "${module.ecr.api_repository_url}:production"
  scraper_container_image = "${module.ecr.scraper_repository_url}:production"
  database_url_secret_arn = module.secrets.database_url_secret_arn
  jwt_secret_arn          = module.secrets.jwt_secret_arn
  s3_bucket_name          = module.s3.raw_data_bucket_name
  execution_role_arn      = module.iam.ecs_execution_role_arn
  task_role_arn           = module.iam.ecs_task_role_arn
  certificate_arn         = var.certificate_arn
  tags                    = var.tags
}

module "cloudfront" {
  source               = "../../modules/cloudfront"
  environment          = var.environment
  alb_dns_name         = module.ecs.alb_dns_name
  frontend_s3_domain   = module.s3.frontend_bucket_regional_domain_name
  domain_name          = var.domain_name
  certificate_arn      = var.certificate_arn
  tags                 = var.tags
}
