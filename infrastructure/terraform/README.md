# GCC Car Value Platform — Terraform Infrastructure

Modular AWS infrastructure as code for the GCC Car Value platform.

## Architecture

```
Internet → CloudFront → ALB → ECS Fargate (API) → RDS PostgreSQL
                              ECS Fargate (Scraper) → S3 Raw Data
                              Secrets Manager
                              CloudWatch Logs
                              ECR (Docker images)
```

## Directory Structure

```
terraform/
├── versions.tf              # Terraform + provider version constraints
├── providers.tf             # AWS provider configuration
├── backend.tf               # Remote state backend (S3 + DynamoDB)
├── variables.tf             # Root-level input variables
├── outputs.tf               # Root-level output values
├── terraform.tfvars.example # Example variable values
├── README.md                # This file
│
├── modules/                 # Reusable infrastructure modules
│   ├── network/             # VPC, subnets, NAT, IGW, route tables
│   ├── rds/                 # PostgreSQL 16 RDS instance
│   ├── ecs/                 # ECS Fargate cluster, ALB, services
│   ├── ecr/                 # Docker image repositories
│   ├── s3/                  # S3 buckets (raw data, MLflow artifacts)
│   ├── cloudfront/          # CloudFront CDN distribution
│   ├── secrets/             # Secrets Manager secrets
│   └── iam/                 # IAM roles and policies
│
└── environments/            # Per-environment configurations
    ├── dev/                 # Shared sandbox (minimal resources)
    ├── staging/             # Pre-production validation
    └── production/          # Public traffic (full resources)
```

## Module Dependency Graph

```
network ─────┬── rds ────── secrets
             ├── ecs ───────┘
             │    ├── iam ──┘
             │    └── s3 ───┘
             │    └── ecr ──┘
             └── cloudfront
```

## Quick Start

### Prerequisites
- Terraform >= 1.6.0
- AWS credentials configured (`aws configure` or env vars)
- S3 bucket for remote state (create manually or use local state for now)

### Initialize

```bash
# For a specific environment
cd environments/dev
terraform init

# Or from root (using terraform workspaces)
cd ../..
terraform init
```

### Plan

```bash
cd environments/staging
terraform plan -var-file="terraform.tfvars"
```

### Apply

```bash
terraform apply -var-file="terraform.tfvars"
```

**Never commit `terraform.tfvars` with real secret values.**

## Environment Sizing

| Resource | dev | staging | production |
|----------|-----|---------|------------|
| RDS instance | db.t3.micro | db.t3.micro | db.t3.medium |
| RDS storage | 20 GB | 20 GB | 50 GB |
| Multi-AZ | No | No | No (V2) |
| API CPU | 256 (0.25 vCPU) | 512 (0.5 vCPU) | 512 (0.5 vCPU) |
| API memory | 512 MB | 1024 MB | 1024 MB |
| API instances | 1-2 | 1-2 | 1-4 |
| Scraper CPU | 512 (0.5 vCPU) | 1024 (1 vCPU) | 1024 (1 vCPU) |
| Scraper memory | 1024 MB | 2048 MB | 2048 MB |
| CloudFront price class | 200 | 200 | 100 |
| Geo restriction | None | None | GCC only |
| Deletion protection | No | No | Yes |

## Variables

See `variables.tf` and per-environment `variables.tf` for all available inputs.  
See `terraform.tfvars.example` for example values.

**Sensitive variables (set via environment):**
- `TF_VAR_db_password` — RDS master password
- `TF_VAR_jwt_secret` — JWT signing key
- `TF_VAR_claude_api_key` — Anthropic API key

## Outputs

See `outputs.tf` and per-environment `outputs.tf` for all exported values.

Key outputs:
- `rds_endpoint` — Database hostname:port
- `alb_dns_name` — Load balancer URL
- `cloudfront_domain` — CDN URL
- `ecr_api_repo` — API container registry URL
- `ecr_scraper_repo` — Scraper container registry URL

## Remote State

Uncomment and configure the `backend "s3"` block in each environment's `main.tf` after creating:
1. An S3 bucket for state files
2. A DynamoDB table for state locking

```hcl
terraform {
  backend "s3" {
    bucket         = "gcc-car-value-tfstate"
    key            = "environments/staging/terraform.tfstate"
    region         = "me-central-1"
    dynamodb_table = "gcc-car-value-tfstate-lock"
    encrypt        = true
  }
}
```

## Validation

```bash
# Format all files
terraform fmt -recursive

# Validate each environment
cd environments/dev    && terraform init -backend=false && terraform validate
cd environments/staging && terraform init -backend=false && terraform validate
cd environments/production && terraform init -backend=false && terraform validate
```

## Notes

- This is the **infrastructure foundation only**. Application deployment, CI/CD, and scheduler configuration belong to later prompts.
- All modules are designed to be composable — each environment uses the same modules with different sizing.
- Secrets Manager secrets are created empty and must be populated with real values before ECS services can start.
- CloudFront geo-restriction is production-only and whitelists GCC countries.
