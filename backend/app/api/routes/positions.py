from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account_position import AccountPositionCreate, AccountPositionRead
from app.services.account_position import AccountPositionService


router = APIRouter(
    prefix="/api/v1/positions",
    tags=["positions"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[AccountPositionRead])
def list_positions(
    db: DbSession,
    account_id: int | None = Query(default=None, ge=1),
    snapshot_at: datetime | None = None,
) -> list[AccountPositionRead]:
    service = AccountPositionService(db)

    if account_id is not None:
        return service.list_by_account(account_id)

    if snapshot_at is not None:
        return service.list_by_snapshot(snapshot_at)

    raise HTTPException(
        status_code=400,
        detail="Provide account_id or snapshot_at",
    )


@router.get("/{position_id}", response_model=AccountPositionRead)
def get_position(
    position_id: int,
    db: DbSession,
) -> AccountPositionRead:
    service = AccountPositionService(db)

    position = service.get_by_id(position_id)

    if position is None:
        raise HTTPException(
            status_code=404,
            detail="Position not found",
        )

    return position


@router.post(
    "",
    response_model=AccountPositionRead,
    status_code=201,
)
def create_position(
    data: AccountPositionCreate,
    db: DbSession,
) -> AccountPositionRead:
    service = AccountPositionService(db)

    return service.create(data)
