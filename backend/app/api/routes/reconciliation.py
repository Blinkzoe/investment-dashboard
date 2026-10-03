from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.reconciliation import AccountReconciliationRead
from app.services.reconciliation import ReconciliationService


router = APIRouter(
    prefix="/api/v1/reconciliation",
    tags=["reconciliation"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/accounts/{account_id}",
    response_model=AccountReconciliationRead,
)
def reconcile_account(
    account_id: int,
    db: DbSession,
) -> AccountReconciliationRead:
    service = ReconciliationService(db)

    try:
        return service.reconcile_account(account_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
