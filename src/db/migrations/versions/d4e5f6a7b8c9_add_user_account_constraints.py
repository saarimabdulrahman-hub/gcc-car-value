"""Add unique email + non-empty password hash to user_accounts."""

from collections.abc import Sequence

from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "1cbe748cf623"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Existing duplicates must be purged before the constraint can apply.
    op.execute(
        "DELETE FROM user_accounts a USING user_accounts b "
        "WHERE a.id > b.id AND a.email = b.email"
    )
    op.create_unique_constraint("uq_user_accounts_email", "user_accounts", ["email"])
    op.create_check_constraint(
        "ck_user_accounts_password_hash_not_empty",
        "user_accounts",
        "password_hash IS NOT NULL AND length(password_hash) > 0",
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_accounts_email", "user_accounts", type_="unique")
    op.drop_constraint(
        "ck_user_accounts_password_hash_not_empty", "user_accounts", type_="check"
    )
