from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account_summary import AccountSummaryRead
from app.services.account_summary import AccountSummaryService

router = APIRouter(
    prefix="/api/v1/account-summary",
    tags=["account-summary"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/{account_id}",
    response_model=AccountSummaryRead,
)
def get_account_summary(
    account_id: int,
    db: DbSession,
    source: str | None = None,
) -> AccountSummaryRead:
    service = AccountSummaryService(db)
    summary = service.get_summary(
        account_id=account_id,
        source=source,
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return summary
