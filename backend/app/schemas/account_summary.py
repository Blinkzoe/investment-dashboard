from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AccountSummaryRead(BaseModel):
    account_id: int
    institution: str
    name: str
    account_type: str
    base_currency: str

    snapshot_at: datetime | None
    official_value: Decimal | None
    positions_value: Decimal | None
    difference: Decimal | None
    currency: str | None
    reconciliation_status: str | None
