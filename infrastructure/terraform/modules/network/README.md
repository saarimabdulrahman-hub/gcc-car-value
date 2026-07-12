# Network Module

**Purpose:** VPC with public/private subnets across 2 availability zones, NAT gateway for private subnet egress.

## Architecture
- 1 VPC (configurable CIDR)
- 2 AZs × 2 subnets = 4 total (2 public + 2 private)
- Internet Gateway for public ingress
- NAT Gateway in first AZ for private egress
- Separate route tables for public and private subnets

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `vpc_cidr` | `string` | CIDR block for the VPC (e.g. `10.0.0.0/16`) |
| `availability_zones` | `list(string)` | AZs for subnets (e.g. `["me-central-1a", "me-central-1b"]`) |
| `environment` | `string` | Environment name (`dev`, `staging`, `production`) |
| `tags` | `map(string)` | Additional resource tags |

## Outputs
| Name | Type | Description |
|------|------|-------------|
| `vpc_id` | `string` | VPC ID |
| `public_subnet_ids` | `list(string)` | Public subnet IDs (for ALB) |
| `private_subnet_ids` | `list(string)` | Private subnet IDs (for RDS, ECS tasks) |
| `nat_gateway_ip` | `string` | NAT Gateway public IP |

## Dependencies
- None (foundational module)
