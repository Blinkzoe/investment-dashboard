from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.repositories.portfolio_snapshot import PortfolioSnapshotRepository


class PortfolioSnapshotService:
    def __init__(self, db: Session) -> None:
        self.repository = PortfolioSnapshotRepository(db)

    def list_all(self) -> list[PortfolioSnapshot]:
        return self.repository.list_all()
