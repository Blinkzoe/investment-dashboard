from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account_snapshot import (
    AccountSnapshotCreate,
    AccountSnapshotRead,
)
from app.schemas.account_snapshot_summary import AccountSnapshotMonthlySummaryRead
from app.services.account_snapshot import AccountSnapshotService
from app.services.account_snapshot_summary import AccountSnapshotSummaryService


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


@router.get(
    "/accounts/monthly-summary",
    response_model=list[AccountSnapshotMonthlySummaryRead],
)
def get_account_snapshots_monthly_summary(
    db: DbSession,
    source: str | None = Query(default=None),
) -> list[AccountSnapshotMonthlySummaryRead]:
    service = AccountSnapshotSummaryService(db)
    return service.get_monthly_summary(source=source)


@router.post(
    "/accounts",
    response_model=AccountSnapshotRead,
    status_code=201,
)
def create_account_snapshot(
    data: AccountSnapshotCreate,
    db: DbSession,
) -> AccountSnapshotRead:
    service = AccountSnapshotService(db)
    return service.create(data)
