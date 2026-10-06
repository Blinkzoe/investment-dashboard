from datetime import date
from decimal import Decimal

from app.models.asset import Asset
from app.services.price import PriceService


def create_asset(db_session) -> Asset:
    asset = Asset(
        symbol="TEST",
        name="Test Asset",
        asset_type="STOCK",
        currency="USD",
        exchange="TEST",
    )

    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    return asset


def test_create_price(db_session):
    asset = create_asset(db_session)
    service = PriceService(db_session)

    price = service.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 1),
        price=Decimal("123.456789"),
        currency="USD",
        source="TEST",
    )

    assert price.id is not None
    assert price.asset_id == asset.id
    assert price.price_date == date(2026, 10, 1)
    assert price.price == Decimal("123.456789")
    assert price.currency == "USD"
    assert price.source == "TEST"


def test_list_prices_by_asset(db_session):
    asset = create_asset(db_session)
    service = PriceService(db_session)

    service.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 1),
        price=Decimal("100"),
        currency="USD",
        source="TEST",
    )

    service.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 2),
        price=Decimal("110"),
        currency="USD",
        source="TEST",
    )

    prices = service.list_by_asset(asset.id)

    assert len(prices) == 2
    assert prices[0].price_date == date(2026, 10, 2)
    assert prices[1].price_date == date(2026, 10, 1)


def test_get_latest_price_by_asset_filters_source(db_session):
    asset = create_asset(db_session)
    service = PriceService(db_session)

    service.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 1),
        price=Decimal("100"),
        currency="USD",
        source="TEST",
    )

    service.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        price=Decimal("125"),
        currency="USD",
        source="TEST",
    )

    service.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 5),
        price=Decimal("999"),
        currency="USD",
        source="OTHER",
    )

    latest = service.get_latest_by_asset(
        asset_id=asset.id,
        source="TEST",
    )

    assert latest is not None
    assert latest.price_date == date(2026, 10, 3)
    assert latest.price == Decimal("125")
    assert latest.source == "TEST"
