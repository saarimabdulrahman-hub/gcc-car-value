output "database_url_secret_arn" {
  description = "Secrets Manager secret ARN for DATABASE_URL"
  value       = aws_secretsmanager_secret.database_url.arn
}

output "jwt_secret_arn" {
  description = "Secrets Manager secret ARN for JWT_SECRET"
  value       = aws_secretsmanager_secret.jwt_secret.arn
}

output "claude_api_key_arn" {
  description = "Secrets Manager secret ARN for CLAUDE_API_KEY"
  value       = var.claude_api_key != null ? aws_secretsmanager_secret.claude_api_key[0].arn : null
}
