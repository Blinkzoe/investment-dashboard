from dataclasses import dataclass
from decimal import Decimal

from app.models.account_position import AccountPosition
from app.services.position_valuation import (
    PositionValuation,
    PositionValuationService,
)


@dataclass(frozen=True)
class PortfolioValuation:
    positions: list[PositionValuation]
    totals_by_currency: dict[str, Decimal]


class PortfolioValuationService:
    def __init__(
        self,
        position_valuation_service: PositionValuationService,
    ) -> None:
        self.position_valuation_service = position_valuation_service

    def value_positions(
        self,
        *,
        positions: list[AccountPosition],
        price_source: str,
    ) -> PortfolioValuation:
        valuations = self.position_valuation_service.value_positions(
            positions=positions,
            price_source=price_source,
        )

        totals_by_currency: dict[str, Decimal] = {}

        for valuation in valuations:
            if valuation.market_value is None:
                continue

            totals_by_currency[valuation.currency] = (
                totals_by_currency.get(
                    valuation.currency,
                    Decimal("0"),
                )
                + valuation.market_value
            )

        return PortfolioValuation(
            positions=valuations,
            totals_by_currency=totals_by_currency,
        )
