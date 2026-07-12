# Remote state backend.
# Uncomment and configure after creating the S3 bucket + DynamoDB table.
#
# terraform {
#   backend "s3" {
#     bucket         = "gcc-car-value-tfstate"
#     key            = "environments/${var.environment}/terraform.tfstate"
#     region         = var.aws_region
#     dynamodb_table = "gcc-car-value-tfstate-lock"
#     encrypt        = true
#   }
# }
