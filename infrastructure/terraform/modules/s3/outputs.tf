output "raw_data_bucket_name" {
  description = "Raw data S3 bucket name"
  value       = aws_s3_bucket.raw_data.id
}

output "raw_data_bucket_arn" {
  description = "Raw data S3 bucket ARN"
  value       = aws_s3_bucket.raw_data.arn
}

output "mlflow_artifacts_bucket_name" {
  description = "MLflow artifacts S3 bucket name"
  value       = aws_s3_bucket.mlflow_artifacts.id
}

output "mlflow_artifacts_bucket_arn" {
  description = "MLflow artifacts S3 bucket ARN"
  value       = aws_s3_bucket.mlflow_artifacts.arn
}

output "frontend_bucket_name" {
  description = "Static frontend S3 bucket name"
  value       = aws_s3_bucket.frontend.id
}

output "frontend_bucket_arn" {
  description = "Static frontend S3 bucket ARN"
  value       = aws_s3_bucket.frontend.arn
}

output "frontend_bucket_regional_domain_name" {
  description = "Frontend S3 bucket regional domain name"
  value       = aws_s3_bucket.frontend.bucket_regional_domain_name
}
