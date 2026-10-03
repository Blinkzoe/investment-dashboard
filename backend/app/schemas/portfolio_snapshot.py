from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PortfolioSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    snapshot_at: datetime
    total_value: Decimal
    gain: Decimal | None = None
    return_percentage: Decimal | None = None
    currency: str
    source: str
    notes: str | None = None
    created_at: datetime
