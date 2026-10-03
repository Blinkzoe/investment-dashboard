from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.transaction import TransactionRead
from app.services.transaction import TransactionService


router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["transactions"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=list[TransactionRead],
)
def list_transactions(
    db: DbSession,
    account_id: int | None = Query(default=None, ge=1),
    asset_id: int | None = Query(default=None, ge=1),
) -> list[TransactionRead]:
    service = TransactionService(db)

    if account_id is not None:
        return service.list_by_account(account_id)

    if asset_id is not None:
        return service.list_by_asset(asset_id)

    return service.list_all()
