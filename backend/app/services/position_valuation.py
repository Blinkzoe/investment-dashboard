from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.models.account_position import AccountPosition
from app.repositories.price import PriceRepository


@dataclass(frozen=True)
class PositionValuation:
    asset_id: int
    quantity: Decimal
    price: Decimal | None
    market_value: Decimal | None
    currency: str
    price_date: date | None


class PositionValuationService:
    def __init__(self, price_repository: PriceRepository) -> None:
        self.price_repository = price_repository

    def value_positions(
        self,
        *,
        positions: list[AccountPosition],
        price_source: str,
    ) -> list[PositionValuation]:
        return [
            self.value_position(
                position=position,
                price_source=price_source,
            )
            for position in positions
        ]

    def value_position(
        self,
        *,
        position: AccountPosition,
        price_source: str,
    ) -> PositionValuation:
        price_record = self.price_repository.get_latest_by_asset(
            asset_id=position.asset_id,
            source=price_source,
        )

        if price_record is None:
            return PositionValuation(
                asset_id=position.asset_id,
                quantity=position.quantity,
                price=None,
                market_value=None,
                currency=position.currency,
                price_date=None,
            )

        market_value = position.quantity * price_record.price

        return PositionValuation(
            asset_id=position.asset_id,
            quantity=position.quantity,
            price=price_record.price,
            market_value=market_value,
            currency=position.currency,
            price_date=price_record.price_date,
        )
