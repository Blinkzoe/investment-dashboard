from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountPositionCreate(BaseModel):
    account_id: int
    asset_id: int
    snapshot_at: datetime
    quantity: Decimal
    market_price: Decimal | None = None
    market_value: Decimal | None = None
    currency: str
    source: str
    notes: str | None = None


class AccountPositionRead(AccountPositionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
