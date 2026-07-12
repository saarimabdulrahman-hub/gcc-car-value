# Secrets Manager Module

**Purpose:** AWS Secrets Manager secrets for database URL, JWT signing key, and optional Claude API key.

## Features
- Secrets encrypted at rest with AWS KMS
- Automatic rotation not configured (manual rotation recommended for DB credentials)
- Secrets injected into ECS tasks via `secrets` block in task definition

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `database_url` | `string` | Full async database URL (sensitive) |
| `jwt_secret` | `string` | JWT signing secret (sensitive) |
| `claude_api_key` | `string` | Claude API key, optional (sensitive) |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `database_url_secret_arn` | DATABASE_URL secret ARN |
| `jwt_secret_arn` | JWT_SECRET secret ARN |
| `claude_api_key_arn` | CLAUDE_API_KEY secret ARN (null if not set) |

## Dependencies
- None (foundational module — requires RDS endpoint for the DATABASE_URL value)
