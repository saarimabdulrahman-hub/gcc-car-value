# ECR Module

**Purpose:** Elastic Container Registry repositories for API and scraper Docker images.

## Features
- Separate repositories for API and scraper
- Image scanning on push (vulnerability detection)
- Lifecycle policy: retain last 10 images, auto-expire older
- Force delete enabled for non-production environments

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `api_repository_url` | ECR URL for API image |
| `scraper_repository_url` | ECR URL for scraper image |
| `api_repository_name` | API repository name |
| `scraper_repository_name` | Scraper repository name |

## Dependencies
- None (foundational module)
