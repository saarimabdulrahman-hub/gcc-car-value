"""Role and Permission definitions for RBAC.

Roles are hierarchical — higher roles inherit all permissions from lower roles.
Permissions are granular actions on resources. Routes declare which permission
they require via FastAPI dependencies; no permission checks are hardcoded.
"""

from enum import StrEnum


# ---------------------------------------------------------------------------
# Roles (hierarchical — each role inherits from those below it)
# ---------------------------------------------------------------------------

class Role(StrEnum):
    """User roles in ascending privilege order."""
    CONSUMER    = "consumer"     # Can use public valuation API
    DEALER      = "dealer"       # Consumer + dealer-specific features
    MODERATOR   = "moderator"    # Dealer + content moderation
    ADMIN       = "admin"        # Moderator + platform administration
    SUPER_ADMIN = "super_admin"  # Admin + system configuration
    SYSTEM      = "system"       # Internal service accounts (full access)

    @classmethod
    def hierarchy(cls) -> dict["Role", list["Role"]]:
        """Roles at each level inherit all permissions from roles below."""
        return {
            cls.CONSUMER:    [],
            cls.DEALER:      [cls.CONSUMER],
            cls.MODERATOR:   [cls.CONSUMER, cls.DEALER],
            cls.ADMIN:       [cls.CONSUMER, cls.DEALER, cls.MODERATOR],
            cls.SUPER_ADMIN: [cls.CONSUMER, cls.DEALER, cls.MODERATOR, cls.ADMIN],
            cls.SYSTEM:      [cls.CONSUMER, cls.DEALER, cls.MODERATOR, cls.ADMIN,
                             cls.SUPER_ADMIN],
        }

    def inherits_from(self) -> list["Role"]:
        return self.hierarchy().get(self, [])


# ---------------------------------------------------------------------------
# Permissions (granular actions on resources)
# ---------------------------------------------------------------------------

class Permission(StrEnum):
    """Granular permissions for platform resources."""

    # Valuation
    VALUATION_READ   = "valuation.read"    # Request a valuation
    VALUATION_WRITE  = "valuation.write"   # Save/bookmark valuations

    # Market
    MARKET_READ      = "market.read"       # Browse models, view trends

    # Dealer
    DEALER_MANAGE    = "dealer.manage"     # Dealer-only features

    # Users
    USERS_READ       = "users.read"        # View user accounts
    USERS_MANAGE     = "users.manage"      # Create/disable/modify users

    # Admin
    ADMIN_LOGIN      = "admin.login"       # Access admin endpoints
    ADMIN_METRICS    = "admin.metrics"     # View platform stats
    ADMIN_SCRAPERS   = "admin.scrapers"    # View scraper health
    ADMIN_QUALITY    = "admin.quality"     # View quality metrics

    # Audit
    AUDIT_READ       = "audit.read"        # View audit logs
    AUDIT_WRITE       = "audit.write"      # Export/manage audit logs

    # ML
    MODEL_DEPLOY     = "model.deploy"      # Promote/rollback ML models
    MODEL_READ       = "model.read"        # View model registry

    # Scraper
    SCRAPER_MANAGE   = "scraper.manage"    # Trigger/stop scraper runs

    # System
    SYSTEM_MANAGE    = "system.manage"     # Configuration, secrets, feature flags


# ---------------------------------------------------------------------------
# Role → Permission mapping
# ---------------------------------------------------------------------------

ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.CONSUMER: [
        Permission.VALUATION_READ,
        Permission.MARKET_READ,
    ],
    Role.DEALER: [
        Permission.VALUATION_READ,
        Permission.VALUATION_WRITE,
        Permission.MARKET_READ,
        Permission.DEALER_MANAGE,
    ],
    Role.MODERATOR: [
        Permission.VALUATION_READ,
        Permission.VALUATION_WRITE,
        Permission.MARKET_READ,
        Permission.DEALER_MANAGE,
        Permission.ADMIN_LOGIN,
        Permission.ADMIN_METRICS,
        Permission.ADMIN_SCRAPERS,
        Permission.ADMIN_QUALITY,
    ],
    Role.ADMIN: [
        Permission.VALUATION_READ,
        Permission.VALUATION_WRITE,
        Permission.MARKET_READ,
        Permission.DEALER_MANAGE,
        Permission.USERS_READ,
        Permission.USERS_MANAGE,
        Permission.ADMIN_LOGIN,
        Permission.ADMIN_METRICS,
        Permission.ADMIN_SCRAPERS,
        Permission.ADMIN_QUALITY,
        Permission.AUDIT_READ,
        Permission.MODEL_READ,
        Permission.MODEL_DEPLOY,
        Permission.SCRAPER_MANAGE,
    ],
    Role.SUPER_ADMIN: [
        # All permissions
        Permission.VALUATION_READ,
        Permission.VALUATION_WRITE,
        Permission.MARKET_READ,
        Permission.DEALER_MANAGE,
        Permission.USERS_READ,
        Permission.USERS_MANAGE,
        Permission.ADMIN_LOGIN,
        Permission.ADMIN_METRICS,
        Permission.ADMIN_SCRAPERS,
        Permission.ADMIN_QUALITY,
        Permission.AUDIT_READ,
        Permission.AUDIT_WRITE,
        Permission.MODEL_READ,
        Permission.MODEL_DEPLOY,
        Permission.SCRAPER_MANAGE,
        Permission.SYSTEM_MANAGE,
    ],
    Role.SYSTEM: [
        # All permissions (internal services)
        Permission.VALUATION_READ,
        Permission.VALUATION_WRITE,
        Permission.MARKET_READ,
        Permission.DEALER_MANAGE,
        Permission.USERS_READ,
        Permission.USERS_MANAGE,
        Permission.ADMIN_LOGIN,
        Permission.ADMIN_METRICS,
        Permission.ADMIN_SCRAPERS,
        Permission.ADMIN_QUALITY,
        Permission.AUDIT_READ,
        Permission.AUDIT_WRITE,
        Permission.MODEL_READ,
        Permission.MODEL_DEPLOY,
        Permission.SCRAPER_MANAGE,
        Permission.SYSTEM_MANAGE,
    ],
}
