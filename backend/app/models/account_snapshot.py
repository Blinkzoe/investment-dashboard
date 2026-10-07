from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AccountSnapshot(Base):
    __tablename__ = "account_snapshots"

    __table_args__ = (
        Index(
            "ix_account_snapshots_snapshot_at",
            "snapshot_at",
        ),
        UniqueConstraint(
            "account_id",
            "snapshot_at",
            "source",
            name="uq_account_snapshots_account_date_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
    )

    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    total_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    cash_value: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    interest_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal("0"),
    )

    contribution_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal("0"),
    )

    withdrawal_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal("0"),
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    account = relationship(
        "Account",
        back_populates="snapshots",
    )
