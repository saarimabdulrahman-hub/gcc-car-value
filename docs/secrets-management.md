# GCC Car Value — Secrets Management

**Date:** 2026-07-12  
**Blueprint Reference:** §10.4 (Secret Management)  
**Files:** `src/config/secrets.py`, `src/config/startup.py`, `src/config/settings.py`

---

## 1. Architecture

```
Application code (jwt.py, config, etc.)
    │
    ▼
SecretProvider.get("JWT_SECRET")    ← single abstraction for all secrets
    │
    ├── EnvironmentProvider          ← os.getenv() (local dev, Docker)
    └── AwsSecretsManagerProvider    ← boto3 → AWS Secrets Manager (production)
```

No application code calls `os.getenv()` directly for sensitive values. All secret access flows through `SecretProvider.get()`.

## 2. Providers

### EnvironmentProvider

Reads secrets from environment variables. Used in development and staging.

```python
provider = EnvironmentProvider()
jwt_secret = await provider.get("JWT_SECRET")
```

- Always ready (no network dependency)
- Reads from `os.environ` directly
- Returns `None` for missing secrets (no automatic fallback)

### AwsSecretsManagerProvider

Reads secrets from AWS Secrets Manager. Used in production.

```python
provider = AwsSecretsManagerProvider(
    environment="production",
    region="me-central-1",
)
jwt_secret = await provider.get("JWT_SECRET")
```

- Lazy client initialization (boto3)
- In-memory cache with `invalidate_cache()` for rotation
- Secret naming: `gcc-car-value-{env}-{secret-name-lower-kebab}`
- Falls back to `default` parameter if AWS is unreachable
- Logs warnings (not errors) on read failures

### Provider Selection

```python
from src.config.secrets import get_secret_provider

provider = get_secret_provider()
# Returns AwsSecretsManagerProvider if environment == "production"
# Returns EnvironmentProvider otherwise
```

The provider is a **singleton** — created once and reused. Call `reset_secret_provider()` to force re-creation (for testing or secret rotation).

## 3. Required Secrets

| Secret | Min Length | Policy | Default Rejected? |
|--------|-----------|--------|-------------------|
| `JWT_SECRET` | 32 chars | Must have ≥2 character categories. Must not contain common weak patterns (secret, password, 1234, abcd, test, dev, admin). | ✅ Rejects known default values (dev-secret, change-in-production, etc.) |
| `DATABASE_PASSWORD` | 8 chars | Standard password policy | Optional |
| `S3_SECRET_KEY` | 8 chars | Standard key policy | Optional |
| `CLAUDE_API_KEY` | 16 chars | API key format | Optional |
| `VIN_API_KEY` | — | Optional | Optional |
| `DATABASE_URL` | — | Must start with `postgresql://`, `postgresql+asyncpg://`, or `sqlite://` | Optional |

## 4. Startup Validation

The application refuses to start with insecure configuration. `validate_startup()` checks:

1. **JWT_SECRET is set** — fails if empty or missing
2. **JWT_SECRET is not a default** — fails if it contains "dev-secret", "change-in-production", "change-me", etc.
3. **JWT_SECRET meets minimum length** — fails if < 32 chars
4. **JWT_SECRET has sufficient complexity** — fails if only 1 character category (all-lowercase, all-digits, etc.)
5. **DATABASE_URL is valid format** — fails if URL scheme is unexpected

```python
# In main.py, before creating the FastAPI app:
from src.config.startup import validate_startup
import asyncio

asyncio.run(validate_startup())
# Raises StartupError with clear error messages if insecure
```

### Error Examples

```
Startup validation failed:
  - JWT_SECRET: REQUIRED but not found. Set via environment. Description: JWT HS256 signing key

Startup validation failed:
  - JWT_SECRET: appears to be a default/example value (contains 'dev-secret'). Replace with a strong generated secret.
  - JWT_SECRET: too short (28 chars, minimum 32). Generate with: python -c "import secrets; print(secrets.token_hex(32))"
```

## 5. Secret Rotation

### JWT Secret Rotation

1. Generate new secret: `python -c "from src.config.startup import generate_secure_jwt_secret; print(generate_secure_jwt_secret())"`
2. Add to secrets provider (env var or AWS Secrets Manager) as `JWT_SECRET_NEW`
3. Deploy — application loads both secrets, verifies with old, signs with new
4. After all tokens issued with old secret have expired (24h max), remove `JWT_SECRET`
5. Rename `JWT_SECRET_NEW` → `JWT_SECRET`

### AWS Secrets Manager Rotation

Call `provider.invalidate_cache()` after updating a secret in AWS. The next `provider.get()` call will fetch the new value. No application restart required.

### Environment Variable Rotation

Update `.env` or Docker environment and restart the application. EnvironmentProvider reads fresh on each `get()` call (no caching).

## 6. Logging Security

Secrets are **never logged in plain text**.

```python
from src.config.secrets import mask_sensitive_value

# Safe logging
logger.info("secret_loaded",
    name="JWT_SECRET",
    value=mask_sensitive_value("JWT_SECRET", actual_value))
# Output: value=***MASKED***

# Non-sensitive values pass through unchanged
logger.info("config", environment="production")
# Output: environment="production"
```

**Masking rules:**
- Keys containing `secret`, `password`, `token`, `key`, `api_key`, or `credential` (case-insensitive) → value masked
- Values matching known API key patterns (`sk-`, `gccv_`, `AKIA`) → value masked
- `DATABASE_URL` is NOT masked by key (for debugging) — but the inline password within it is not explicitly stripped (consider using `DATABASE_PASSWORD` as a separate secret in production)

## 7. Local Development

```bash
# Generate a secure JWT secret for local development
python -c "from src.config.startup import generate_secure_jwt_secret; print(generate_secure_jwt_secret())"

# Add to .env
echo "JWT_SECRET=<generated-value>" >> .env
```

The `.env.example` file includes a placeholder with generation instructions. Developers must generate their own secret before starting the application.

## 8. Docker

In `docker-compose.yml`, set `JWT_SECRET` as an environment variable:

```yaml
services:
  api:
    environment:
      - JWT_SECRET=${JWT_SECRET}
```

Use a `.env` file in the project root (not committed) to provide the value:

```
JWT_SECRET=a1b2c3d4e5f6...  # generated by secrets.token_hex(32)
```

## 9. Adding a New Secret

1. Add the secret name to `SecretName` enum in `secrets.py`
2. Add a policy entry in `SECRET_POLICIES` if it has minimum requirements
3. Add the field to `Settings` in `settings.py` (with no default, or `None` for optional)
4. Access via provider: `await provider.get(SecretName.NEW_SECRET.value)`
5. Update `.env.example` with a placeholder

## 10. Adding a New Provider

Implement the `SecretProvider` ABC:

```python
class VaultProvider(SecretProvider):
    source_name = "hashicorp-vault"

    async def get(self, name: str, default=None) -> str | None:
        # Call Vault API
        ...

    async def ready(self) -> bool:
        # Check Vault connectivity
        ...
```

Then update `get_secret_provider()` to select the new provider based on a configuration flag.

---

*Secrets management documented 2026-07-12.*
