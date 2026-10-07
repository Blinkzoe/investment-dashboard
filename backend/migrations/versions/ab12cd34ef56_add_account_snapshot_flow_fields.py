"""add account snapshot flow fields

Revision ID: ab12cd34ef56
Revises: 9c1f4b8d2e7a
"""

from alembic import op
import sqlalchemy as sa


revision = "ab12cd34ef56"
down_revision = "9c1f4b8d2e7a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "account_snapshots",
        sa.Column(
            "interest_value",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "account_snapshots",
        sa.Column(
            "contribution_value",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "account_snapshots",
        sa.Column(
            "withdrawal_value",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade():
    op.drop_column("account_snapshots", "withdrawal_value")
    op.drop_column("account_snapshots", "contribution_value")
    op.drop_column("account_snapshots", "interest_value")
