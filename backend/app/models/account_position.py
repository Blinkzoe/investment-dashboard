from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AccountPosition(Base):
    __tablename__ = "account_positions"

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "asset_id",
            "snapshot_at",
            "source",
            name="uq_account_positions_snapshot",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 10),
        nullable=False,
    )

    market_price: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 10),
        nullable=True,
    )

    market_value: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 10),
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
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
