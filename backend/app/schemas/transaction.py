from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    asset_id: int
    transaction_type: str
    status: str
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    gross_amount: Decimal | None = None
    commission: Decimal
    taxes: Decimal
    other_fees: Decimal
    total_amount: Decimal | None = None
    currency: str
    trade_date: date | None = None
    settlement_date: date | None = None
    source: str
    external_id: str | None = None
    import_batch_id: int | None = None
    notes: str | None = None
    metadata_json: dict | None = None
    created_at: datetime
