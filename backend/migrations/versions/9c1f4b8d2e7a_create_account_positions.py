"""create account positions

Revision ID: 9c1f4b8d2e7a
Revises: 747fcf8a991e
Create Date: 2026-10-02 21:25:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c1f4b8d2e7a"
down_revision: Union[str, Sequence[str], None] = "747fcf8a991e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "account_positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "account_id",
            sa.Integer(),
            sa.ForeignKey("accounts.id"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id"),
            nullable=False,
        ),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 10), nullable=False),
        sa.Column("market_price", sa.Numeric(20, 10), nullable=True),
        sa.Column("market_value", sa.Numeric(20, 10), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "account_id",
            "asset_id",
            "snapshot_at",
            "source",
            name="uq_account_positions_snapshot",
        ),
    )

    op.create_index(
        "ix_account_positions_account_snapshot",
        "account_positions",
        ["account_id", "snapshot_at"],
    )

    op.create_index(
        "ix_account_positions_asset_snapshot",
        "account_positions",
        ["asset_id", "snapshot_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_account_positions_asset_snapshot",
        table_name="account_positions",
    )

    op.drop_index(
        "ix_account_positions_account_snapshot",
        table_name="account_positions",
    )

    op.drop_table("account_positions")
