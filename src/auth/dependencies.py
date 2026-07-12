"""FastAPI dependencies for authentication and authorization.

Routes declare what they need via Depends():
    @router.get("/admin/stats")
    async def stats(
        db: AsyncSession = Depends(get_db),
        user: dict = Depends(require_permission(Permission.ADMIN_METRICS)),
    ):
        ...

Consumer endpoints remain unchanged — no auth dependency required.
"""

from typing import Callable
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db
from src.auth.jwt import verify_token
from src.auth.roles import Role, Permission
from src.auth.rbac import rbac, get_user_role
import structlog

logger = structlog.get_logger()

bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Core auth dependency — extracts and validates the current user
# ---------------------------------------------------------------------------

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict | None:
    """Extract and validate the current user from JWT Bearer token.

    Returns a dict with user_id, role, and tier, or None if unauthenticated.
    Consumer endpoints can call this optionally; admin endpoints require it.
    """
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    # Resolve role from DB (authoritative source) with JWT claim as fallback
    role_str = payload.get("role")
    tier_str = payload.get("tier", "registered")

    try:
        db_role = await get_user_role(db, user_id)
    except Exception:
        db_role = None

    resolved_role = db_role.value if db_role else (role_str or "consumer")

    return {
        "user_id": user_id,
        "role": resolved_role,
        "tier": tier_str,
        "is_authenticated": True,
    }


# ---------------------------------------------------------------------------
# Authorization dependencies — declarative permission/role requirements
# ---------------------------------------------------------------------------

def require_permission(
    permission: Permission | str,
) -> Callable:
    """FastAPI dependency: require a specific permission.

    Usage:
        @router.get("/admin/stats")
        async def stats(
            user: dict = Depends(require_permission(Permission.ADMIN_METRICS)),
        ):
            ...

    Returns the user dict if authorized.
    Raises HTTPException(403) if denied, HTTPException(401) if unauthenticated.
    """
    permission = Permission(permission) if isinstance(permission, str) else permission

    async def _check(
        request: Request,
        user: dict | None = Depends(get_current_user),
    ) -> dict:
        if user is None:
            _log_denied(request, None, permission, "unauthenticated")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_role = Role(user["role"]) if user["role"] in Role.__members__.values() else Role.CONSUMER

        if not rbac.has_permission(user_role, permission):
            _log_denied(request, user, permission, "insufficient_permission")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required.",
            )

        return user

    return _check


def require_role(
    role: Role | str,
) -> Callable:
    """FastAPI dependency: require a minimum role level.

    Usage:
        @router.delete("/users/{id}")
        async def delete_user(
            user: dict = Depends(require_role(Role.ADMIN)),
        ):
            ...
    """
    role = Role(role) if isinstance(role, str) else role

    async def _check(
        request: Request,
        user: dict | None = Depends(get_current_user),
    ) -> dict:
        if user is None:
            _log_denied(request, None, f"role:{role.value}", "unauthenticated")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_role = Role(user["role"]) if user["role"] in Role.__members__.values() else Role.CONSUMER

        if not rbac.has_role(user_role, role):
            _log_denied(request, user, f"role:{role.value}",
                       "insufficient_role")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role.value}' or higher required.",
            )

        return user

    return _check


# ---------------------------------------------------------------------------
# Audit logging for denied requests
# ---------------------------------------------------------------------------

def _log_denied(
    request: Request,
    user: dict | None,
    required: Permission | str | None,
    reason: str,
) -> None:
    """Log denied authorization attempts for audit trail."""
    perm_str = (required.value if isinstance(required, Permission)
               else str(required) if required else "unknown")

    logger.warning(
        "authorization_denied",
        user_id=user.get("user_id") if user else None,
        role=user.get("role") if user else None,
        required=perm_str,
        reason=reason,
        method=request.method,
        path=request.url.path,
        ip=request.client.host if request.client else None,
    )
