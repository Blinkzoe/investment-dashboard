from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.portfolio_summary import PortfolioSummaryRead
from app.services.portfolio_summary import PortfolioSummaryService


router = APIRouter(
    prefix="/api/v1/portfolio-summary",
    tags=["portfolio-summary"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=PortfolioSummaryRead,
)
def get_portfolio_summary(
    db: DbSession,
    currency: str | None = None,
    source: str | None = None,
) -> PortfolioSummaryRead:
    service = PortfolioSummaryService(db)
    return service.get_latest(
        currency=currency,
        source=source,
    )
