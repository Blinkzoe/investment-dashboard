from datetime import datetime

from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        Index("ix_accounts_institution", "institution"),
        UniqueConstraint(
            "institution",
            "name",
            name="uq_accounts_institution_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    institution: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    account_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    base_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    transactions = relationship(
        "Transaction",
        back_populates="account",
    )

    snapshots = relationship(
        "AccountSnapshot",
        back_populates="account",
    )
