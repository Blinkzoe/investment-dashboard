from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Price(Base):
    __tablename__ = "prices"

    __table_args__ = (
        UniqueConstraint(
            "asset_id",
            "price_date",
            "source",
            name="uq_prices_asset_date_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
    )

    price_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(24, 10),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
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

    asset = relationship(
        "Asset",
        back_populates="prices",
    )
