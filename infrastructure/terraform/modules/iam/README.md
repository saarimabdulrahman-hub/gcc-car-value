# IAM Module

**Purpose:** IAM roles and policies for ECS task execution and application-level permissions.

## Roles

### ECS Task Execution Role
- Pulls images from ECR
- Reads secrets from Secrets Manager
- Writes logs to CloudWatch

### ECS Task Role (application)
- Read/write raw data in S3
- Read/write MLflow artifacts in S3
- Write CloudWatch metrics

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `raw_data_bucket_arn` | `string` | S3 raw data bucket ARN |
| `mlflow_artifacts_bucket_arn` | `string` | S3 MLflow bucket ARN (optional) |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `ecs_execution_role_arn` | Execution role ARN |
| `ecs_task_role_arn` | Task role ARN |
| `ecs_execution_role_name` | Execution role name |
| `ecs_task_role_name` | Task role name |

## Dependencies
- `s3` module (bucket ARNs for policy scoping)
