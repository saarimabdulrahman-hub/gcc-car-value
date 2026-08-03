"""Index dead_letter for token-revocation lookups."""
from collections.abc import Sequence

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | Sequence[str] | None = "d4e5f6a7b8c9"   # G1's new id
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # if_not_exists: the initial-schema migration builds tables from
    # Base.metadata.create_all(), which already creates this index because the
    # DeadLetter model declares it in __table_args__. A fresh DB therefore has
    # the index before this migration runs; skip instead of failing.
    op.create_index(
        "ix_dead_letter_source_external_id",
        "dead_letter",
        ["source", "external_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_dead_letter_source_external_id", table_name="dead_letter")
