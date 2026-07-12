# CloudFront Module

**Purpose:** CloudFront CDN distribution for API with TLS termination, GCC geo-restriction, and static asset caching.

## Features
- HTTP/2 and HTTP/3 support
- Redirect HTTP → HTTPS
- API responses: no cache (min/default/max TTL = 0)
- Static assets (`/static/*`): 24h default TTL, 1 week max
- Health check: no cache
- Production: geo-restricted to GCC countries (AE, SA, QA, KW, BH, OM)
- Optional custom domain with ACM certificate

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `alb_dns_name` | `string` | ALB origin DNS name |
| `domain_name` | `string` | Custom domain (optional) |
| `certificate_arn` | `string` | ACM cert in us-east-1 (optional) |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `domain_name` | CloudFront distribution domain |
| `hosted_zone_id` | Route53 alias hosted zone ID |
| `distribution_id` | Distribution ID |

## Dependencies
- `ecs` module (ALB DNS name)
