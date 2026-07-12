# =============================================================================
# Secrets Manager Module — Database URL, JWT Secret, API Keys
# =============================================================================

locals {
  name = "gcc-car-value-${var.environment}"
}

resource "aws_secretsmanager_secret" "database_url" {
  name        = "${local.name}-database-url"
  description = "Async database URL for ${var.environment}"

  tags = merge(var.tags, {
    Name = "${local.name}-database-url"
  })
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id

  secret_string = jsonencode({
    DATABASE_URL = var.database_url
  })
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "${local.name}-jwt-secret"
  description = "JWT signing secret for ${var.environment}"

  tags = merge(var.tags, {
    Name = "${local.name}-jwt-secret"
  })
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id = aws_secretsmanager_secret.jwt_secret.id

  secret_string = jsonencode({
    JWT_SECRET = var.jwt_secret
  })
}

resource "aws_secretsmanager_secret" "claude_api_key" {
  count = var.claude_api_key != null ? 1 : 0

  name        = "${local.name}-claude-api-key"
  description = "Anthropic Claude API key for ${var.environment}"

  tags = merge(var.tags, {
    Name = "${local.name}-claude-api-key"
  })
}

resource "aws_secretsmanager_secret_version" "claude_api_key" {
  count = var.claude_api_key != null ? 1 : 0

  secret_id = aws_secretsmanager_secret.claude_api_key[0].id

  secret_string = jsonencode({
    CLAUDE_API_KEY = var.claude_api_key
  })
}
