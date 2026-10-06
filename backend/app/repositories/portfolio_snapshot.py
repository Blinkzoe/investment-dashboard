from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot


class PortfolioSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[PortfolioSnapshot]:
        statement = select(PortfolioSnapshot).order_by(
            PortfolioSnapshot.snapshot_at.desc()
        )

        return list(self.db.scalars(statement).all())

    def get_by_snapshot_source_currency(
        self,
        *,
        snapshot_at: datetime,
        source: str,
        currency: str,
    ) -> PortfolioSnapshot | None:
        statement = select(PortfolioSnapshot).where(
            PortfolioSnapshot.snapshot_at == snapshot_at,
            PortfolioSnapshot.source == source,
            PortfolioSnapshot.currency == currency,
        )

        return self.db.scalars(statement).first()

    def create(
        self,
        *,
        snapshot_at: datetime,
        total_value: Decimal,
        contributed_capital: Decimal | None,
        gain: Decimal | None,
        return_percentage: Decimal | None,
        currency: str,
        source: str,
        notes: str | None,
    ) -> PortfolioSnapshot:
        snapshot = PortfolioSnapshot(
            snapshot_at=snapshot_at,
            total_value=total_value,
            contributed_capital=contributed_capital,
            gain=gain,
            return_percentage=return_percentage,
            currency=currency,
            source=source,
            notes=notes,
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot
