# S3 Module

**Purpose:** S3 buckets for raw scraper data and MLflow artifacts.

## Features
- **Raw data bucket:** Versioned, SSE-AES256 encrypted, public access blocked, 90-day lifecycle expiration, 7-day non-current version cleanup
- **MLflow artifacts bucket:** Versioned, SSE-AES256 encrypted, public access blocked (no expiration — models kept indefinitely)

## Inputs
| Name | Type | Description |
|------|------|-------------|
| `environment` | `string` | Environment name |
| `tags` | `map(string)` | Additional tags |

## Outputs
| Name | Description |
|------|-------------|
| `raw_data_bucket_name` | Raw data bucket name |
| `raw_data_bucket_arn` | Raw data bucket ARN |
| `mlflow_artifacts_bucket_name` | MLflow artifacts bucket name |
| `mlflow_artifacts_bucket_arn` | MLflow artifacts bucket ARN |

## Dependencies
- None (foundational module)
