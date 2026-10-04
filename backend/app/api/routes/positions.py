from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account_position import AccountPositionCreate, AccountPositionRead
from app.schemas.position_comparison import (
    PositionComparisonCreate,
    PositionComparisonItem,
    PositionComparisonResponse,
)

from app.schemas.position_reconstruction import (
    PositionReconstructionCreate,
    PositionReconstructionResponse,
)
from app.services.account_position import AccountPositionService
from app.services.position_snapshot import PositionSnapshotService
from app.services.position_comparison import PositionComparisonService


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
    source: str | None = None,
) -> list[AccountPositionRead]:
    service = AccountPositionService(db)

    if account_id is not None:
        return service.list_by_account(
            account_id,
            source=source,
        )

    if snapshot_at is not None:
        return service.list_by_snapshot(snapshot_at)

    raise HTTPException(
        status_code=400,
        detail="Provide account_id or snapshot_at",
    )


@router.post(
    "/reconstruct",
    response_model=PositionReconstructionResponse,
    status_code=201,
)
def reconstruct_positions(
    data: PositionReconstructionCreate,
    db: DbSession,
) -> PositionReconstructionResponse:
    service = PositionSnapshotService(db)

    try:
        positions = service.create_snapshot(
            account_id=data.account_id,
            snapshot_at=data.snapshot_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return PositionReconstructionResponse(
        account_id=data.account_id,
        snapshot_at=data.snapshot_at,
        positions_created=len(positions),
    )


@router.post(
    "/compare",
    response_model=PositionComparisonResponse,
)
def compare_positions(
    data: PositionComparisonCreate,
    db: DbSession,
) -> PositionComparisonResponse:
    position_service = AccountPositionService(db)
    comparison_service = PositionComparisonService()

    official_positions = position_service.list_by_snapshot_and_source(
        account_id=data.account_id,
        snapshot_at=data.official_snapshot_at,
        source="GBM",
    )

    reconstructed_positions = position_service.list_by_snapshot_and_source(
        account_id=data.account_id,
        snapshot_at=data.reconstructed_snapshot_at,
        source=PositionComparisonService.RECONSTRUCTED_SOURCE,
    )

    comparisons = comparison_service.compare(
        official_positions=official_positions,
        reconstructed_positions=reconstructed_positions,
    )

    comparison_items = [
        PositionComparisonItem(
            asset_id=comparison.asset_id,
            official_quantity=comparison.official_quantity,
            reconstructed_quantity=comparison.reconstructed_quantity,
            difference=comparison.difference,
            status=comparison.status,
        )
        for comparison in comparisons
    ]

    return PositionComparisonResponse(
        account_id=data.account_id,
        official_snapshot_at=data.official_snapshot_at,
        reconstructed_snapshot_at=data.reconstructed_snapshot_at,
        comparisons=comparison_items,
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
