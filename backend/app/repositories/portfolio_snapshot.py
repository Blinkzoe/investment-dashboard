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
