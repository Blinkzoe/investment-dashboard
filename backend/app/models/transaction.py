from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Date,
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


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_transactions_source_external_id",
        ),
        Index(
            "ix_transactions_account_trade_date",
            "account_id",
            "trade_date",
        ),
        Index(
            "ix_transactions_asset_trade_date",
            "asset_id",
            "trade_date",
        ),
        Index(
            "ix_transactions_source",
            "source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
    )

    asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("assets.id"),
        nullable=True,
    )

    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id"),
        nullable=True,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="COMPLETED",
    )

    quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 10),
        nullable=True,
    )

    unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 10),
        nullable=True,
    )

    gross_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    commission: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal(0),
    )

    taxes: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal(0),
    )

    other_fees: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
        default=Decimal(0),
    )

    total_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    trade_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    settlement_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    account = relationship(
        "Account",
        back_populates="transactions",
    )

    asset = relationship(
        "Asset",
        back_populates="transactions",
    )

    import_batch = relationship(
        "ImportBatch",
    )
