from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class NormalizedTransaction(BaseModel):
    account_id: int
    asset_id: int

    transaction_type: str
    status: str = "FILLED"

    quantity: Decimal | None = None
    unit_price: Decimal | None = None

    gross_amount: Decimal | None = None
    commission: Decimal = Field(default=Decimal("0"))
    taxes: Decimal = Field(default=Decimal("0"))
    other_fees: Decimal = Field(default=Decimal("0"))
    total_amount: Decimal | None = None

    currency: str

    trade_date: date | None = None
    settlement_date: date | None = None

    source: str
    external_id: str | None = None
    notes: str | None = None
    metadata_json: dict | None = None
