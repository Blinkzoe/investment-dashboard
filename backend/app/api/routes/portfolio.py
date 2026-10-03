from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.portfolio_snapshot import PortfolioSnapshotRead
from app.services.portfolio_snapshot import PortfolioSnapshotService


router = APIRouter(
    prefix="/api/v1/portfolio",
    tags=["portfolio"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/snapshots",
    response_model=list[PortfolioSnapshotRead],
)
def list_portfolio_snapshots(
    db: DbSession,
) -> list[PortfolioSnapshotRead]:
    service = PortfolioSnapshotService(db)

    return service.list_all()
