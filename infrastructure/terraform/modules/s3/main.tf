# =============================================================================
# S3 Module — Raw Data Storage, MLflow Artifacts
# =============================================================================

locals {
  name = "gcc-car-value-${var.environment}"
}

# --- Raw Data Bucket (scraper HTML/JSON) ---
resource "aws_s3_bucket" "raw_data" {
  bucket = "${local.name}-raw-data"

  tags = merge(var.tags, {
    Name = "${local.name}-raw-data"
  })
}

resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    id     = "expire-raw-data"
    status = "Enabled"

    expiration {
      days = 90
    }

    # Also clean up old non-current versions
    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# --- MLflow Artifacts Bucket ---
resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = "${local.name}-mlflow-artifacts"

  tags = merge(var.tags, {
    Name = "${local.name}-mlflow-artifacts"
  })
}

resource "aws_s3_bucket_versioning" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Static Frontend Bucket ---
resource "aws_s3_bucket" "frontend" {
  bucket = "${local.name}-frontend"

  tags = merge(var.tags, {
    Name = "${local.name}-frontend"
  })
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}
