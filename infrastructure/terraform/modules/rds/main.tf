# =============================================================================
# RDS Module — PostgreSQL 16 with pgvector
# =============================================================================

locals {
  name = "gcc-car-value-${var.environment}"
}

# --- Security Group ---
resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "Allow PostgreSQL inbound from ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${local.name}-rds-sg"
  })
}

# --- Subnet Group ---
resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnet"
  subnet_ids = var.private_subnet_ids
  description = "Subnet group for ${local.name} RDS"

  tags = merge(var.tags, {
    Name = "${local.name}-db-subnet"
  })
}

# --- Parameter Group (enable pgvector) ---
resource "aws_db_parameter_group" "main" {
  name   = "${local.name}-pg16-params"
  family = "postgres16"
  description = "PostgreSQL 16 parameter group for ${local.name}"

  tags = merge(var.tags, {
    Name = "${local.name}-pg16-params"
  })
}

# --- RDS Instance ---
resource "aws_db_instance" "main" {
  identifier = "${local.name}-db"

  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  allocated_storage     = var.allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  multi_az               = var.multi_az
  backup_retention_period = var.backup_retention_days
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${local.name}-final-snapshot" : null

  enabled_cloudwatch_logs_exports = ["postgresql"]
  parameter_group_name            = aws_db_parameter_group.main.name

  tags = merge(var.tags, {
    Name = "${local.name}-db"
  })
}
