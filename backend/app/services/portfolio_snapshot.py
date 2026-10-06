from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.repositories.portfolio_snapshot import PortfolioSnapshotRepository


class PortfolioSnapshotService:
    def __init__(self, db: Session) -> None:
        self.repository = PortfolioSnapshotRepository(db)

    def list_all(self) -> list[PortfolioSnapshot]:
        return self.repository.list_all()

    def get_by_snapshot_source_currency(
        self,
        *,
        snapshot_at: datetime,
        source: str,
        currency: str,
    ) -> PortfolioSnapshot | None:
        return self.repository.get_by_snapshot_source_currency(
            snapshot_at=snapshot_at,
            source=source,
            currency=currency,
        )

    def create(
        self,
        *,
        snapshot_at: datetime,
        total_value: Decimal,
        contributed_capital: Decimal | None = None,
        gain: Decimal | None = None,
        return_percentage: Decimal | None = None,
        currency: str,
        source: str,
        notes: str | None = None,
    ) -> PortfolioSnapshot:
        return self.repository.create(
            snapshot_at=snapshot_at,
            total_value=total_value,
            contributed_capital=contributed_capital,
            gain=gain,
            return_percentage=return_percentage,
            currency=currency,
            source=source,
            notes=notes,
        )
