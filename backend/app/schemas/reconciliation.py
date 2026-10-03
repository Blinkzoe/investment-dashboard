from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AccountReconciliationRead(BaseModel):
    account_id: int
    snapshot_at: datetime
    official_value: Decimal
    positions_value: Decimal
    difference: Decimal
    currency: str
    status: str
