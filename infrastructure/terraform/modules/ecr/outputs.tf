output "api_repository_url" {
  description = "ECR repository URL for the API image"
  value       = aws_ecr_repository.api.repository_url
}

output "scraper_repository_url" {
  description = "ECR repository URL for the scraper image"
  value       = aws_ecr_repository.scraper.repository_url
}

output "api_repository_name" {
  description = "API repository name"
  value       = aws_ecr_repository.api.name
}

output "scraper_repository_name" {
  description = "Scraper repository name"
  value       = aws_ecr_repository.scraper.name
}
