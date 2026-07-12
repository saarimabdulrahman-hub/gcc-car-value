# GCC Car Value — Admin Authentication & RBAC

**Date:** 2026-07-12  
**Files:** `src/auth/`, `src/models/user_account.py`, `src/api/routes/admin.py`

---

## 1. Architecture

```
Request with Authorization: Bearer <JWT>
    │
    ├── HTTPBearer extracts token
    ├── verify_token() validates JWT signature + expiry
    ├── get_user_role() resolves role from DB (authoritative)
    │       └── Falls back to JWT claim if DB unavailable
    │
    ├── Route declares: Depends(require_permission(Permission.ADMIN_METRICS))
    │       ├── RBACService.has_permission() checks role → permission mapping
    │       ├── Inherits permissions from lower roles
    │       ├── If authorized → passes user dict to route handler
    │       └── If denied → HTTP 403 + audit log
    │
    └── Route handler receives: user = {"user_id": "...", "role": "admin", ...}
```

## 2. Roles

| # | Role | Privileges | Inherits From |
|---|------|-----------|---------------|
| 1 | `consumer` | Valuation read, market read | — |
| 2 | `dealer` | Consumer + valuation write, dealer manage | consumer |
| 3 | `moderator` | Dealer + admin login, view metrics/scrapers/quality | dealer |
| 4 | `admin` | Moderator + user management, audit read, model deploy, scraper manage | moderator |
| 5 | `super_admin` | Admin + audit write, system manage | admin |
| 6 | `system` | All permissions (internal services) | super_admin |

**Role source priority:** DB `user_accounts.role` column (authoritative) → JWT `role` claim → default `consumer`.

**Legacy compatibility:** Users with `tier="registered"` map to `consumer`. Users with `tier="enterprise"` map to `dealer`.

## 3. Permissions

| Permission | Description | Minimum Role |
|-----------|-------------|-------------|
| `valuation.read` | Request vehicle valuations | consumer |
| `valuation.write` | Save/bookmark valuations | dealer |
| `market.read` | Browse models, view trends | consumer |
| `dealer.manage` | Dealer-specific features | dealer |
| `users.read` | View user accounts | admin |
| `users.manage` | Create/disable/modify users | admin |
| `admin.login` | Access admin endpoints | moderator |
| `admin.metrics` | View platform stats | moderator |
| `admin.scrapers` | View scraper health | moderator |
| `admin.quality` | View quality metrics | moderator |
| `audit.read` | View audit logs | admin |
| `audit.write` | Export/manage audit logs | super_admin |
| `model.read` | View model registry | admin |
| `model.deploy` | Promote/rollback ML models | admin |
| `scraper.manage` | Trigger/stop scraper runs | admin |
| `system.manage` | Configuration, secrets, feature flags | super_admin |

## 4. Route Protection

### Admin endpoints (protected)

```python
@router.get("/admin/stats")
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_permission(Permission.ADMIN_METRICS)),
):
```

| Endpoint | Required Permission | Minimum Role |
|----------|-------------------|-------------|
| `GET /v1/admin/stats` | `admin.metrics` | moderator |
| `GET /v1/admin/scrapers` | `admin.scrapers` | moderator |
| `GET /v1/admin/quality` | `admin.quality` | moderator |

### Consumer endpoints (unchanged — no auth required)

| Endpoint | Auth |
|----------|------|
| `POST /v1/valuate` | None (anonymous allowed) |
| `POST /v1/valuate-url` | None |
| `GET /v1/models` | None |
| `GET /v1/health` | None |

## 5. Adding Protection to New Endpoints

```python
from src.auth.dependencies import require_permission, require_role
from src.auth.roles import Permission, Role

# By permission (preferred — granular)
@router.get("/admin/models")
async def list_models(
    user: dict = Depends(require_permission(Permission.MODEL_READ)),
):
    ...

# By role (when a minimum role level is sufficient)
@router.delete("/users/{id}")
async def delete_user(
    user: dict = Depends(require_role(Role.ADMIN)),
):
    ...
```

## 6. Audit Logging

Every denied authorization attempt generates a structured log:

```python
logger.warning("authorization_denied",
    user_id="uuid-or-None",
    role="consumer",
    required="admin.metrics",
    reason="insufficient_permission",   # or "unauthenticated", "insufficient_role"
    method="GET",
    path="/v1/admin/stats",
    ip="192.168.1.1")
```

**Not logged:** JWT tokens, passwords, API keys, or any other secrets.

## 7. Role Management

### Creating an admin user

```python
from src.models.user_account import UserAccount

user = UserAccount(
    email="admin@gcccarvalue.com",
    password_hash=hash,
    password_salt=salt,
    tier="enterprise",
    role="admin",
)
session.add(user)
await session.commit()
```

### Promoting an existing user

```sql
UPDATE user_accounts
SET role = 'admin'
WHERE email = 'user@example.com';
```

### Creating a system service account

```python
from src.auth.jwt import create_access_token

# System token for scraper service
token = create_access_token(
    user_id="svc-scraper",
    tier="enterprise",
    role="system",
)
```

## 8. Future Extensions

### Per-user permissions
Add a `user_permissions` JSONB column to `user_accounts` for granting specific permissions beyond role defaults. The RBAC service would check `user_permissions` as a supplement to role-based permissions.

### API key scoping
Add a `scopes` JSONB column to `user_accounts` to restrict API key permissions independently of the user's role. Enterprise API keys might have read-only access while the user retains full admin.

### Temporary role elevation
Add `elevated_until` timestamp column for time-limited admin access (e.g., support debugging). Auto-reverts to original role after expiry.

### Permission audit trail
Persist denied authorization events to a database table (in addition to structlog) for long-term audit retention and compliance reporting.

---

*RBAC documentation completed 2026-07-12.*
