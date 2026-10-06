from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account import AccountCreate, AccountRead
from app.services.account import AccountService


router = APIRouter(
    prefix="/api/v1/accounts",
    tags=["accounts"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=list[AccountRead],
)
def list_accounts(
    db: DbSession,
) -> list[AccountRead]:
    service = AccountService(db)
    return service.list_all()


@router.get(
    "/{account_id}",
    response_model=AccountRead,
)
def get_account(
    account_id: int,
    db: DbSession,
) -> AccountRead:
    service = AccountService(db)
    account = service.get_by_id(account_id)

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return account


@router.post(
    "",
    response_model=AccountRead,
    status_code=201,
)
def create_account(
    data: AccountCreate,
    db: DbSession,
) -> AccountRead:
    service = AccountService(db)
    account = service.create(data)
    db.commit()
    db.refresh(account)
    return account
