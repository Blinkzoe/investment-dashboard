from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountSnapshotCreate(BaseModel):
    account_id: int
    snapshot_at: datetime
    total_value: Decimal
    cash_value: Decimal | None = None
    currency: str
    source: str
    notes: str | None = None


class AccountSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    snapshot_at: datetime
    total_value: Decimal
    cash_value: Decimal | None = None
    currency: str
    source: str
    notes: str | None = None
    created_at: datetime
