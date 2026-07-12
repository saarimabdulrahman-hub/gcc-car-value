# ECS Module

**Purpose:** ECS Fargate cluster with ALB, API service (auto-scaled), and scraper task definition.

## Architecture
- ECS Fargate cluster with Container Insights enabled
- Application Load Balancer (public subnets, HTTP→HTTPS redirect)
- API service: Fargate launch type, auto-scaled 1-4 by CPU at 70%
- Scraper task definition: scheduled via EventBridge (not auto-scaled)
- CloudWatch log groups (30-day retention)
- Secrets injected from Secrets Manager

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `vpc_id` | `string` | VPC ID |
| `public_subnet_ids` | `list(string)` | Public subnets for ALB |
| `private_subnet_ids` | `list(string)` | Private subnets for tasks |
| `api_cpu` | `number` | vCPU for API (512 = 0.5 vCPU) |
| `api_memory` | `number` | MiB for API (1024 = 1 GB) |
| `api_desired_count` | `number` | Base task count |
| `api_max_count` | `number` | Max auto-scale count |
| `api_container_image` | `string` | ECR image for API |
| `scraper_cpu` | `number` | vCPU for scraper |
| `scraper_memory` | `number` | MiB for scraper |
| `scraper_container_image` | `string` | ECR image for scraper |
| `database_url_secret_arn` | `string` | Secrets Manager ARN |
| `jwt_secret_arn` | `string` | Secrets Manager ARN |
| `s3_bucket_name` | `string` | Raw data bucket |
| `execution_role_arn` | `string` | Task execution IAM role |
| `task_role_arn` | `string` | Task IAM role |
| `certificate_arn` | `string` | ACM cert ARN (optional) |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `cluster_name` | ECS cluster name |
| `api_service_name` | API service name |
| `alb_dns_name` | ALB DNS name |
| `alb_arn` | ALB ARN |
| `ecs_task_security_group_id` | Tasks SG ID |
| `alb_security_group_id` | ALB SG ID |

## Dependencies
- `network` module (VPC, subnets)
- `rds` module (security group for DB access)
- `iam` module (execution + task roles)
- `secrets` module (database URL, JWT secret)
- `s3` module (bucket name)
- `ecr` module (container images)
