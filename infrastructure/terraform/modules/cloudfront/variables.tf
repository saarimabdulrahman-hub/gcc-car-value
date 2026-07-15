variable "environment" {
  description = "Environment name"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name (API origin)"
  type        = string
}

variable "frontend_s3_domain" {
  description = "S3 bucket regional domain name for static frontend hosting"
  type        = string
  default     = null
}

variable "domain_name" {
  description = "Custom domain name (optional)"
  type        = string
  default     = null
}

variable "certificate_arn" {
  description = "ACM certificate ARN in us-east-1 (required if domain_name is set)"
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}
