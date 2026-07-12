output "vpc_id"              { value = module.network.vpc_id }
output "rds_endpoint"        { value = module.rds.endpoint }
output "alb_dns_name"        { value = module.ecs.alb_dns_name }
output "cloudfront_domain"   { value = module.cloudfront.domain_name }
output "ecr_api_repo"        { value = module.ecr.api_repository_url }
output "ecr_scraper_repo"    { value = module.ecr.scraper_repository_url }
output "raw_data_bucket"     { value = module.s3.raw_data_bucket_name }
