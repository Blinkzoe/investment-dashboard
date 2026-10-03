from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class GBMTransactionInput(BaseModel):
    external_id: str
    account_id: int
    asset_id: int
    transaction_type: str
    status: str = "FILLED"

    quantity: Decimal
    unit_price: Decimal
    gross_amount: Decimal
    commission: Decimal = Decimal("0")
    taxes: Decimal = Decimal("0")
    other_fees: Decimal = Decimal("0")
    total_amount: Decimal

    currency: str
    trade_date: date
    settlement_date: date | None = None

    notes: str | None = None
    metadata_json: dict | None = None
