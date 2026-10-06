from datetime import date, datetime
from decimal import Decimal

from app.models.account_position import AccountPosition
from app.models.price import Price
from app.services.position_valuation import PositionValuationService


SNAPSHOT_AT = datetime(2026, 10, 3, 21, 0)


def make_position(
    *,
    asset_id: int,
    quantity: str,
    currency: str = "USD",
    market_price: str | None = None,
    market_value: str | None = None,
    source: str = "GBM",
) -> AccountPosition:
    return AccountPosition(
        account_id=1,
        asset_id=asset_id,
        snapshot_at=SNAPSHOT_AT,
        quantity=Decimal(quantity),
        market_price=(
            Decimal(market_price) if market_price is not None else None
        ),
        market_value=(
            Decimal(market_value) if market_value is not None else None
        ),
        currency=currency,
        source=source,
    )


def make_price(
    *,
    asset_id: int,
    price_date: str,
    price: str,
    currency: str = "USD",
    source: str = "MARKET_DATA",
) -> Price:
    return Price(
        asset_id=asset_id,
        price_date=date.fromisoformat(price_date),
        price=Decimal(price),
        currency=currency,
        source=source,
    )


class FakePriceRepository:
    def __init__(self, prices: list[Price]) -> None:
        self.prices = prices

    def get_latest_by_asset(
        self,
        *,
        asset_id: int,
        source: str,
    ) -> Price | None:
        candidates = [
            price
            for price in self.prices
            if price.asset_id == asset_id
            and price.source == source
        ]

        if not candidates:
            return None

        return max(candidates, key=lambda price: price.price_date)


def test_value_position_using_latest_price() -> None:
    repository = FakePriceRepository(
        [
            make_price(
                asset_id=16,
                price_date="2026-10-01",
                price="60.00",
            ),
            make_price(
                asset_id=16,
                price_date="2026-10-03",
                price="61.80",
            ),
        ]
    )

    service = PositionValuationService(repository)

    position = make_position(
        asset_id=16,
        quantity="9.94",
        market_price="999.00",
        market_value="9999.00",
    )

    result = service.value_position(
        position=position,
        price_source="MARKET_DATA",
    )

    assert result.asset_id == 16
    assert result.quantity == Decimal("9.94")
    assert result.price == Decimal("61.80")
    assert result.market_value == Decimal("614.2920")
    assert result.currency == "USD"
    assert result.price_date == date(2026, 10, 3)


def test_value_position_returns_none_when_price_is_missing() -> None:
    repository = FakePriceRepository([])

    service = PositionValuationService(repository)

    position = make_position(
        asset_id=16,
        quantity="9.94",
    )

    result = service.value_position(
        position=position,
        price_source="MARKET_DATA",
    )

    assert result.asset_id == 16
    assert result.quantity == Decimal("9.94")
    assert result.price is None
    assert result.market_value is None
    assert result.price_date is None
    assert result.currency == "USD"


def test_value_position_filters_price_source() -> None:
    repository = FakePriceRepository(
        [
            make_price(
                asset_id=16,
                price_date="2026-10-05",
                price="999.00",
                source="OTHER",
            ),
            make_price(
                asset_id=16,
                price_date="2026-10-03",
                price="61.80",
                source="MARKET_DATA",
            ),
        ]
    )

    service = PositionValuationService(repository)

    position = make_position(
        asset_id=16,
        quantity="9.94",
    )

    result = service.value_position(
        position=position,
        price_source="MARKET_DATA",
    )

    assert result.price == Decimal("61.80")
    assert result.market_value == Decimal("614.2920")


def test_value_position_does_not_use_historical_market_value() -> None:
    repository = FakePriceRepository(
        [
            make_price(
                asset_id=16,
                price_date="2026-10-03",
                price="61.80",
            ),
        ]
    )

    service = PositionValuationService(repository)

    position = make_position(
        asset_id=16,
        quantity="9.94",
        market_price="61.00",
        market_value="613.88",
    )

    result = service.value_position(
        position=position,
        price_source="MARKET_DATA",
    )

    assert result.price == Decimal("61.80")
    assert result.market_value == Decimal("614.2920")
    assert result.market_value != position.market_value


def test_value_positions_returns_valuation_for_each_position() -> None:
    repository = FakePriceRepository(
        [
            make_price(
                asset_id=15,
                price_date="2026-10-03",
                price="100.00",
            ),
            make_price(
                asset_id=16,
                price_date="2026-10-03",
                price="61.80",
            ),
        ]
    )

    service = PositionValuationService(repository)

    positions = [
        make_position(
            asset_id=15,
            quantity="2.00",
        ),
        make_position(
            asset_id=16,
            quantity="9.94",
        ),
    ]

    result = service.value_positions(
        positions=positions,
        price_source="MARKET_DATA",
    )

    assert len(result) == 2

    assert result[0].asset_id == 15
    assert result[0].quantity == Decimal("2.00")
    assert result[0].price == Decimal("100.00")
    assert result[0].market_value == Decimal("200.0000")

    assert result[1].asset_id == 16
    assert result[1].quantity == Decimal("9.94")
    assert result[1].price == Decimal("61.80")
    assert result[1].market_value == Decimal("614.2920")


def test_value_positions_keeps_positions_without_price() -> None:
    repository = FakePriceRepository(
        [
            make_price(
                asset_id=15,
                price_date="2026-10-03",
                price="100.00",
            ),
        ]
    )

    service = PositionValuationService(repository)

    positions = [
        make_position(
            asset_id=15,
            quantity="2.00",
        ),
        make_position(
            asset_id=16,
            quantity="9.94",
        ),
    ]

    result = service.value_positions(
        positions=positions,
        price_source="MARKET_DATA",
    )

    assert len(result) == 2

    assert result[0].asset_id == 15
    assert result[0].market_value == Decimal("200.0000")

    assert result[1].asset_id == 16
    assert result[1].price is None
    assert result[1].market_value is None
    assert result[1].price_date is None


def test_value_position_uses_real_price_repository(db_session) -> None:
    from app.models.asset import Asset
    from app.repositories.price import PriceRepository

    asset = Asset(
        symbol="INTEGRATION",
        name="Integration Asset",
        asset_type="STOCK",
        currency="USD",
        exchange="TEST",
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    repository = PriceRepository(db_session)

    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 1),
        price=Decimal("60.00"),
        currency="USD",
        source="MARKET_DATA",
    )
    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        price=Decimal("61.80"),
        currency="USD",
        source="MARKET_DATA",
    )

    service = PositionValuationService(repository)

    position = make_position(
        asset_id=asset.id,
        quantity="9.94",
    )

    result = service.value_position(
        position=position,
        price_source="MARKET_DATA",
    )

    assert result.asset_id == asset.id
    assert result.price == Decimal("61.80")
    assert result.market_value == Decimal("614.2920")
    assert result.price_date == date(2026, 10, 3)


def test_value_position_with_real_repository_respects_source(
    db_session,
) -> None:
    from app.models.asset import Asset
    from app.repositories.price import PriceRepository

    asset = Asset(
        symbol="SOURCE-TEST",
        name="Source Test Asset",
        asset_type="STOCK",
        currency="USD",
        exchange="TEST",
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    repository = PriceRepository(db_session)

    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 5),
        price=Decimal("999.00"),
        currency="USD",
        source="OTHER",
    )
    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        price=Decimal("61.80"),
        currency="USD",
        source="MARKET_DATA",
    )

    service = PositionValuationService(repository)

    position = make_position(
        asset_id=asset.id,
        quantity="9.94",
    )

    result = service.value_position(
        position=position,
        price_source="MARKET_DATA",
    )

    assert result.price == Decimal("61.80")
    assert result.market_value == Decimal("614.2920")
    assert result.price_date == date(2026, 10, 3)
