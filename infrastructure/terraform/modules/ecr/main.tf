# =============================================================================
# ECR Module — Docker Image Repositories
# =============================================================================

locals {
  name = "gcc-car-value-${var.environment}"
}

resource "aws_ecr_repository" "api" {
  name = "${local.name}-api"

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"

  force_delete = var.environment != "production"

  tags = merge(var.tags, {
    Name = "${local.name}-api-ecr"
  })
}

resource "aws_ecr_repository" "scraper" {
  name = "${local.name}-scraper"

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"

  force_delete = var.environment != "production"

  tags = merge(var.tags, {
    Name = "${local.name}-scraper-ecr"
  })
}

# Lifecycle policy: keep last 10 images
resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "scraper" {
  repository = aws_ecr_repository.scraper.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 10 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 10
      }
      action = {
        type = "expire"
      }
    }]
  })
}
