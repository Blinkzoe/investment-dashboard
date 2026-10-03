from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    __table_args__ = (
        Index(
            "ix_portfolio_snapshots_snapshot_at",
            "snapshot_at",
        ),
        UniqueConstraint(
            "snapshot_at",
            "source",
            "currency",
            name="uq_portfolio_snapshots_date_source_currency",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    total_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    contributed_capital: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    gain: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    return_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6),
        nullable=True,
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
