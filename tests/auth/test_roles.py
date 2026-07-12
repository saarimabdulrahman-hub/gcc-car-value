"""Test role/permission definitions and RBAC service."""
import pytest
from src.auth.roles import Role, Permission, ROLE_PERMISSIONS
from src.auth.rbac import RBACService


@pytest.fixture
def svc():
    return RBACService()


class TestRoleHierarchy:
    def test_consumer_is_lowest(self):
        order = list(Role)
        assert order[0] == Role.CONSUMER

    def test_system_is_highest(self):
        order = list(Role)
        assert order[-1] == Role.SYSTEM

    def test_admin_is_above_moderator(self, svc):
        assert svc.has_role(Role.ADMIN, Role.MODERATOR)
        assert not svc.has_role(Role.MODERATOR, Role.ADMIN)

    def test_super_admin_is_above_admin(self, svc):
        assert svc.has_role(Role.SUPER_ADMIN, Role.ADMIN)
        assert not svc.has_role(Role.ADMIN, Role.SUPER_ADMIN)

    def test_same_role_passes(self, svc):
        for role in Role:
            assert svc.has_role(role, role)


class TestPermissions:
    def test_consumer_has_valuation_read(self, svc):
        assert svc.has_permission(Role.CONSUMER, Permission.VALUATION_READ)

    def test_consumer_does_not_have_admin(self, svc):
        assert not svc.has_permission(Role.CONSUMER, Permission.ADMIN_METRICS)
        assert not svc.has_permission(Role.CONSUMER, Permission.ADMIN_LOGIN)

    def test_admin_has_all_admin_permissions(self, svc):
        for perm in [Permission.ADMIN_LOGIN, Permission.ADMIN_METRICS,
                     Permission.ADMIN_SCRAPERS, Permission.ADMIN_QUALITY]:
            assert svc.has_permission(Role.ADMIN, perm)

    def test_admin_does_not_have_system_manage(self, svc):
        assert not svc.has_permission(Role.ADMIN, Permission.SYSTEM_MANAGE)

    def test_super_admin_has_system_manage(self, svc):
        assert svc.has_permission(Role.SUPER_ADMIN, Permission.SYSTEM_MANAGE)

    def test_system_has_everything(self, svc):
        for perm in Permission:
            assert svc.has_permission(Role.SYSTEM, perm)

    def test_dealer_has_consumer_permissions_via_inheritance(self, svc):
        assert svc.has_permission(Role.DEALER, Permission.VALUATION_READ)
        assert svc.has_permission(Role.DEALER, Permission.MARKET_READ)

    def test_moderator_has_dealer_permissions_via_inheritance(self, svc):
        assert svc.has_permission(Role.MODERATOR, Permission.DEALER_MANAGE)

    def test_string_roles_work(self, svc):
        assert svc.has_permission("admin", "admin.metrics")
        assert not svc.has_permission("consumer", "admin.metrics")

    def test_get_permissions_returns_all_with_inheritance(self, svc):
        perms = svc.get_permissions(Role.ADMIN)
        perm_values = [p.value for p in perms]
        assert "valuation.read" in perm_values
        assert "dealer.manage" in perm_values
        assert "admin.metrics" in perm_values


class TestPermissionMapping:
    def test_every_role_has_permissions(self):
        for role in Role:
            assert role in ROLE_PERMISSIONS
            assert len(ROLE_PERMISSIONS[role]) > 0

    def test_higher_roles_have_more_permissions(self):
        consumer_count = len(ROLE_PERMISSIONS[Role.CONSUMER])
        admin_count = len(ROLE_PERMISSIONS[Role.ADMIN])
        super_admin_count = len(ROLE_PERMISSIONS[Role.SUPER_ADMIN])
        assert admin_count > consumer_count
        assert super_admin_count >= admin_count
