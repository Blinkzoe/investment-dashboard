from datetime import datetime

from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    __table_args__ = (
        Index("ix_assets_symbol", "symbol"),
        Index("ix_assets_asset_type", "asset_type"),
        UniqueConstraint(
            "symbol",
            "exchange",
            name="uq_assets_symbol_exchange",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    symbol: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    exchange: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    isin: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    transactions = relationship(
        "Transaction",
        back_populates="asset",
    )

    prices = relationship(
        "Price",
        back_populates="asset",
    )
