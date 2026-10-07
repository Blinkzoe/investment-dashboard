from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PortfolioEvolutionPoint(BaseModel):
    date: date
    buys: Decimal
    sells: Decimal
    net_invested: Decimal
    currency: str
    source: str
