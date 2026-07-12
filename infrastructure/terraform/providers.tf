provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "gcc-car-value"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
