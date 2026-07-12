variable "environment" {
  description = "Environment name"
  type        = string
}

variable "raw_data_bucket_arn" {
  description = "S3 raw data bucket ARN"
  type        = string
}

variable "mlflow_artifacts_bucket_arn" {
  description = "S3 MLflow artifacts bucket ARN"
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional resource tags"
  type        = map(string)
  default     = {}
}
