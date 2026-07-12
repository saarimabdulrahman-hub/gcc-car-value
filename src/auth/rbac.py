"""RBAC service — role lookup, permission validation, role inheritance.

All authorization decisions flow through this module. Routes never check
roles directly — they declare required permissions via FastAPI dependencies.
"""

from src.auth.roles import Role, Permission, ROLE_PERMISSIONS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


class RBACService:
    """Stateless RBAC service. All methods are pure functions of role + permission.

    Usage:
        svc = RBACService()
        if svc.has_permission(role, Permission.ADMIN_METRICS):
            ...
    """

    def has_permission(self, role: Role | str, permission: Permission | str) -> bool:
        """Check if a role has a specific permission.

        Handles role inheritance: if role='admin', also checks moderator,
        dealer, and consumer permissions.
        """
        role = Role(role) if isinstance(role, str) else role
        permission = Permission(permission) if isinstance(permission, str) else permission

        # Direct permissions for this role
        direct = permission in ROLE_PERMISSIONS.get(role, [])

        # Inherited permissions from lower roles
        inherited = any(
            permission in ROLE_PERMISSIONS.get(inherited_role, [])
            for inherited_role in role.inherits_from()
        )

        return direct or inherited

    def has_role(self, user_role: Role | str,
                 required_role: Role | str) -> bool:
        """Check if user_role is at least as privileged as required_role.

        Uses numeric ordering from the Role enum definition order.
        """
        user_role = Role(user_role) if isinstance(user_role, str) else user_role
        required_role = (Role(required_role) if isinstance(required_role, str)
                        else required_role)

        role_order = list(Role)
        user_idx = role_order.index(user_role)
        required_idx = role_order.index(required_role)
        return user_idx >= required_idx

    def get_permissions(self, role: Role | str) -> list[Permission]:
        """Get all permissions for a role (including inherited)."""
        role = Role(role) if isinstance(role, str) else role
        perms: set[Permission] = set(ROLE_PERMISSIONS.get(role, []))

        for inherited_role in role.inherits_from():
            perms.update(ROLE_PERMISSIONS.get(inherited_role, []))

        return sorted(perms, key=lambda p: p.value)


# Singleton instance
rbac = RBACService()


async def get_user_role(
    session: AsyncSession,
    user_id: str,
) -> Role:
    """Look up a user's role from the database.

    Returns Role.CONSUMER as default if user not found or role is unset.
    """
    from src.models.user_account import UserAccount

    stmt = select(UserAccount).where(UserAccount.id == user_id).limit(1)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return Role.CONSUMER

    # Check the role column first, fall back to tier mapping
    raw_role = getattr(user, 'role', None)
    if raw_role and raw_role in Role.__members__.values():
        return Role(raw_role)

    # Map legacy tier values to roles
    tier = getattr(user, 'tier', 'registered')
    tier_role_map = {
        "registered": Role.CONSUMER,
        "enterprise": Role.DEALER,
    }
    return tier_role_map.get(tier, Role.CONSUMER)
