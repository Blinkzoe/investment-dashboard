from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account_snapshot import AccountSnapshotRead
from app.services.account_snapshot import AccountSnapshotService


router = APIRouter(
    prefix="/api/v1/snapshots",
    tags=["snapshots"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/accounts",
    response_model=list[AccountSnapshotRead],
)
def list_account_snapshots(
    db: DbSession,
    account_id: int | None = Query(default=None, ge=1),
) -> list[AccountSnapshotRead]:
    service = AccountSnapshotService(db)

    if account_id is not None:
        return service.list_by_account(account_id)

    return service.list_latest()
