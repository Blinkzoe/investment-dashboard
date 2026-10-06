from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PortfolioSummaryRead(BaseModel):
    snapshot_at: datetime | None
    total_value: Decimal | None
    contributed_capital: Decimal | None
    gain: Decimal | None
    return_percentage: Decimal | None
    currency: str | None
    source: str | None
