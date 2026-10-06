from sqlalchemy.orm import Session

from app.repositories.portfolio_snapshot import PortfolioSnapshotRepository
from app.schemas.portfolio_summary import PortfolioSummaryRead


class PortfolioSummaryService:
    def __init__(self, db: Session) -> None:
        self.repository = PortfolioSnapshotRepository(db)

    def get_latest(
        self,
        *,
        currency: str | None = None,
        source: str | None = None,
    ) -> PortfolioSummaryRead:
        snapshots = self.repository.list_all()

        for snapshot in snapshots:
            if currency is not None and snapshot.currency != currency:
                continue

            if source is not None and snapshot.source != source:
                continue

            return PortfolioSummaryRead(
                snapshot_at=snapshot.snapshot_at,
                total_value=snapshot.total_value,
                contributed_capital=snapshot.contributed_capital,
                gain=snapshot.gain,
                return_percentage=snapshot.return_percentage,
                currency=snapshot.currency,
                source=snapshot.source,
            )

        return PortfolioSummaryRead(
            snapshot_at=None,
            total_value=None,
            contributed_capital=None,
            gain=None,
            return_percentage=None,
            currency=None,
            source=None,
        )
