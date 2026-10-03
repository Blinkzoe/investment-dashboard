from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FxRate(Base):
    __tablename__ = "fx_rates"

    __table_args__ = (
        UniqueConstraint(
            "base_currency",
            "quote_currency",
            "rate_date",
            "source",
            name="uq_fx_rates_pair_date_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    base_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    quote_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    rate_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    rate: Mapped[Decimal] = mapped_column(
        Numeric(24, 10),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
