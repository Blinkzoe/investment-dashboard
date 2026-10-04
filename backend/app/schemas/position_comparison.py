from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PositionComparisonCreate(BaseModel):
    account_id: int
    official_snapshot_at: datetime
    reconstructed_snapshot_at: datetime


class PositionComparisonItem(BaseModel):
    asset_id: int
    official_quantity: Decimal | None
    reconstructed_quantity: Decimal | None
    difference: Decimal | None
    status: str


class PositionComparisonResponse(BaseModel):
    account_id: int
    official_snapshot_at: datetime
    reconstructed_snapshot_at: datetime
    comparisons: list[PositionComparisonItem]
