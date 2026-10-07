from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AccountSnapshotMonthlySummaryRead(BaseModel):
    month: datetime
    total_value: Decimal
    interest_value: Decimal
    contribution_value: Decimal
    withdrawal_value: Decimal
    account_count: int
