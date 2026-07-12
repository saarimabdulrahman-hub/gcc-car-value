variable "environment" {
  description = "Environment name"
  type        = string
}

variable "database_url" {
  description = "Full async database URL (postgresql+asyncpg://...)"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "claude_api_key" {
  description = "Anthropic Claude API key (optional)"
  type        = string
  sensitive   = true
  default     = null
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}
