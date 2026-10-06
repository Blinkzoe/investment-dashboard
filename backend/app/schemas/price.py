from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceCreate(BaseModel):
    asset_id: int
    price_date: date
    price: Decimal
    currency: str
    source: str


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    price_date: date
    price: Decimal
    currency: str
    source: str
