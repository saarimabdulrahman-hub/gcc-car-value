# RDS Module

**Purpose:** PostgreSQL 16 RDS instance with encryption, automated backups, and pgvector support.

## Features
- PostgreSQL 16.3 (configurable)
- gp3 storage with KMS encryption
- Automated backups with configurable retention
- Deletion protection in production
- CloudWatch log exports for PostgreSQL logs
- Security group allowing access only from ECS tasks

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `vpc_id` | `string` | VPC ID |
| `private_subnet_ids` | `list(string)` | Private subnets for subnet group |
| `instance_class` | `string` | RDS instance type |
| `allocated_storage` | `number` | Storage in GB |
| `db_name` | `string` | Database name |
| `db_username` | `string` | Master username |
| `db_password` | `string` | Master password (sensitive) |
| `multi_az` | `bool` | Multi-AZ (default `false`) |
| `backup_retention_days` | `number` | Backup retention (default `7`) |
| `allowed_security_group_ids` | `list(string)` | SGs allowed to connect |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `endpoint` | Full endpoint (hostname:port) |
| `address` | Hostname only |
| `port` | Port number |
| `database_name` | Database name |
| `security_group_id` | RDS SG ID |
| `instance_id` | RDS instance identifier |

## Dependencies
- `network` module (VPC, private subnets)
