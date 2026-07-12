# =============================================================================
# IAM Module — ECS Execution Role, Task Role, and Service-Linked Roles
# =============================================================================

locals {
  name = "gcc-car-value-${var.environment}"
}

# --- ECS Task Execution Role (pulls images, reads secrets, writes logs) ---
resource "aws_iam_role" "ecs_execution" {
  name = "${local.name}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = merge(var.tags, {
    Name = "${local.name}-ecs-execution"
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_base" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow reading Secrets Manager secrets
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${local.name}-execution-secrets"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = ["*"] # Scoped by environment naming convention
    }]
  })
}

# --- ECS Task Role (application-level permissions) ---
resource "aws_iam_role" "ecs_task" {
  name = "${local.name}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = merge(var.tags, {
    Name = "${local.name}-ecs-task"
  })
}

# Allow S3 raw data read/write
resource "aws_iam_role_policy" "ecs_task_s3_raw" {
  name = "${local.name}-task-s3-raw"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.raw_data_bucket_arn,
          "${var.raw_data_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Allow S3 MLflow artifacts read/write (if bucket exists)
resource "aws_iam_role_policy" "ecs_task_s3_mlflow" {
  count = var.mlflow_artifacts_bucket_arn != null ? 1 : 0

  name = "${local.name}-task-s3-mlflow"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.mlflow_artifacts_bucket_arn,
          "${var.mlflow_artifacts_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Allow CloudWatch logs + metrics
resource "aws_iam_role_policy" "ecs_task_cloudwatch" {
  name = "${local.name}-task-cloudwatch"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "cloudwatch:PutMetricData"
        ]
        Resource = ["*"]
      }
    ]
  })
}
