from decimal import Decimal

from app.models.account_position import AccountPosition
from app.services.position_valuation import PositionValuation
from app.services.portfolio_valuation import PortfolioValuationService


def make_valuation(
    *,
    asset_id: int,
    quantity: str,
    price: str | None,
    market_value: str | None,
    currency: str,
) -> PositionValuation:
    return PositionValuation(
        asset_id=asset_id,
        quantity=Decimal(quantity),
        price=Decimal(price) if price is not None else None,
        market_value=(
            Decimal(market_value) if market_value is not None else None
        ),
        currency=currency,
        price_date=None,
    )


class FakePositionValuationService:
    def __init__(
        self,
        valuations: dict[int, PositionValuation],
    ) -> None:
        self.valuations = valuations

    def value_positions(
        self,
        *,
        positions: list[AccountPosition],
        price_source: str,
    ) -> list[PositionValuation]:
        return [
            self.valuations[position.asset_id]
            for position in positions
        ]


def make_position(
    *,
    asset_id: int,
    quantity: str,
    currency: str,
) -> AccountPosition:
    return AccountPosition(
        account_id=1,
        asset_id=asset_id,
        snapshot_at=None,
        quantity=Decimal(quantity),
        market_price=None,
        market_value=None,
        currency=currency,
        source="GBM",
    )


def test_value_portfolio_groups_values_by_currency() -> None:
    position_service = FakePositionValuationService(
        {
            15: make_valuation(
                asset_id=15,
                quantity="2.00",
                price="100.00",
                market_value="200.00",
                currency="USD",
            ),
            16: make_valuation(
                asset_id=16,
                quantity="3.00",
                price="50.00",
                market_value="150.00",
                currency="USD",
            ),
            17: make_valuation(
                asset_id=17,
                quantity="10.00",
                price="100.00",
                market_value="1000.00",
                currency="MXN",
            ),
        }
    )

    service = PortfolioValuationService(position_service)

    positions = [
        make_position(
            asset_id=15,
            quantity="2.00",
            currency="USD",
        ),
        make_position(
            asset_id=16,
            quantity="3.00",
            currency="USD",
        ),
        make_position(
            asset_id=17,
            quantity="10.00",
            currency="MXN",
        ),
    ]

    result = service.value_positions(
        positions=positions,
        price_source="MARKET_DATA",
    )

    assert len(result.positions) == 3
    assert result.totals_by_currency == {
        "USD": Decimal("350.00"),
        "MXN": Decimal("1000.00"),
    }


def test_value_portfolio_does_not_convert_currencies() -> None:
    position_service = FakePositionValuationService(
        {
            15: make_valuation(
                asset_id=15,
                quantity="1.00",
                price="100.00",
                market_value="100.00",
                currency="USD",
            ),
            16: make_valuation(
                asset_id=16,
                quantity="1.00",
                price="200.00",
                market_value="200.00",
                currency="MXN",
            ),
        }
    )

    service = PortfolioValuationService(position_service)

    positions = [
        make_position(
            asset_id=15,
            quantity="1.00",
            currency="USD",
        ),
        make_position(
            asset_id=16,
            quantity="1.00",
            currency="MXN",
        ),
    ]

    result = service.value_positions(
        positions=positions,
        price_source="MARKET_DATA",
    )

    assert result.totals_by_currency["USD"] == Decimal("100.00")
    assert result.totals_by_currency["MXN"] == Decimal("200.00")
    assert "EUR" not in result.totals_by_currency


def test_value_portfolio_ignores_positions_without_market_value() -> None:
    position_service = FakePositionValuationService(
        {
            15: make_valuation(
                asset_id=15,
                quantity="2.00",
                price="100.00",
                market_value="200.00",
                currency="USD",
            ),
            16: make_valuation(
                asset_id=16,
                quantity="3.00",
                price=None,
                market_value=None,
                currency="USD",
            ),
        }
    )

    service = PortfolioValuationService(position_service)

    positions = [
        make_position(
            asset_id=15,
            quantity="2.00",
            currency="USD",
        ),
        make_position(
            asset_id=16,
            quantity="3.00",
            currency="USD",
        ),
    ]

    result = service.value_positions(
        positions=positions,
        price_source="MARKET_DATA",
    )

    assert len(result.positions) == 2
    assert result.positions[0].market_value == Decimal("200.00")
    assert result.positions[1].market_value is None
    assert result.totals_by_currency == {
        "USD": Decimal("200.00"),
    }


def test_value_portfolio_uses_postgres_prices(db_session) -> None:
    from app.models.asset import Asset
    from app.models.account_position import AccountPosition
    from app.repositories.price import PriceRepository
    from app.services.position_valuation import PositionValuationService

    usd_asset = Asset(
        symbol="PORT-USD",
        name="Portfolio USD Asset",
        asset_type="STOCK",
        currency="USD",
        exchange="TEST",
    )
    mxn_asset = Asset(
        symbol="PORT-MXN",
        name="Portfolio MXN Asset",
        asset_type="STOCK",
        currency="MXN",
        exchange="TEST",
    )

    db_session.add_all([usd_asset, mxn_asset])
    db_session.commit()
    db_session.refresh(usd_asset)
    db_session.refresh(mxn_asset)

    db_session.add_all(
        [
            AccountPosition(
                account_id=1,
                asset_id=usd_asset.id,
                snapshot_at=__import__("datetime").datetime(
                    2026, 10, 3, 21, 0
                ),
                quantity=Decimal("2"),
                market_price=None,
                market_value=None,
                currency="USD",
                source="GBM",
            ),
            AccountPosition(
                account_id=1,
                asset_id=mxn_asset.id,
                snapshot_at=__import__("datetime").datetime(
                    2026, 10, 3, 21, 0
                ),
                quantity=Decimal("10"),
                market_price=None,
                market_value=None,
                currency="MXN",
                source="GBM",
            ),
        ]
    )
    db_session.commit()

    price_repository = PriceRepository(db_session)

    price_repository.create(
        asset_id=usd_asset.id,
        price_date=__import__("datetime").date(2026, 10, 3),
        price=Decimal("100"),
        currency="USD",
        source="MARKET_DATA",
    )
    price_repository.create(
        asset_id=mxn_asset.id,
        price_date=__import__("datetime").date(2026, 10, 3),
        price=Decimal("50"),
        currency="MXN",
        source="MARKET_DATA",
    )

    position_valuation_service = PositionValuationService(
        price_repository
    )
    portfolio_service = PortfolioValuationService(
        position_valuation_service
    )

    positions = list(
        db_session.query(AccountPosition)
        .filter(AccountPosition.account_id == 1)
        .all()
    )

    result = portfolio_service.value_positions(
        positions=positions,
        price_source="MARKET_DATA",
    )

    assert result.totals_by_currency == {
        "USD": Decimal("200"),
        "MXN": Decimal("500"),
    }
    assert len(result.positions) == 2
