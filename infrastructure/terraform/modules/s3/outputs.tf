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
