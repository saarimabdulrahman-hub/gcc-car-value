"""Authentication & Authorization — JWT, API Keys, RBAC."""
from src.auth.dependencies import get_current_user, require_permission, require_role
from src.auth.jwt import create_access_token, create_api_key, verify_api_key, verify_token
from src.auth.rbac import RBACService, get_user_role, rbac
from src.auth.roles import ROLE_PERMISSIONS, Permission, Role

__all__ = [
    "create_access_token", "verify_token", "create_api_key", "verify_api_key",
    "Role", "Permission", "ROLE_PERMISSIONS",
    "RBACService", "rbac", "get_user_role",
    "get_current_user", "require_permission", "require_role",
]
