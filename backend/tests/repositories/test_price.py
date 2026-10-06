from datetime import date
from decimal import Decimal

from app.models.asset import Asset
from app.repositories.price import PriceRepository


def test_create_and_get_price(db_session):
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

    repository = PriceRepository(db_session)

    created = repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        price=Decimal("123.45"),
        currency="USD",
        source="TEST",
    )

    assert created.id is not None
    assert created.asset_id == asset.id
    assert created.price == Decimal("123.45")

    stored = repository.get_by_asset_date_source(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        source="TEST",
    )

    assert stored is not None
    assert stored.id == created.id


def test_list_by_asset_orders_latest_first(db_session):
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

    repository = PriceRepository(db_session)

    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 1),
        price=Decimal("100"),
        currency="USD",
        source="TEST",
    )

    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        price=Decimal("123"),
        currency="USD",
        source="TEST",
    )

    prices = repository.list_by_asset(asset.id)

    assert [price.price_date for price in prices] == [
        date(2026, 10, 3),
        date(2026, 10, 1),
    ]


def test_get_latest_by_asset_filters_source_and_returns_latest(db_session):
    asset = Asset(
        symbol="LATEST",
        name="Latest Price Test",
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
        price=Decimal("100"),
        currency="USD",
        source="TEST",
    )

    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 3),
        price=Decimal("125"),
        currency="USD",
        source="TEST",
    )

    repository.create(
        asset_id=asset.id,
        price_date=date(2026, 10, 5),
        price=Decimal("999"),
        currency="USD",
        source="OTHER",
    )

    latest = repository.get_latest_by_asset(
        asset_id=asset.id,
        source="TEST",
    )

    assert latest is not None
    assert latest.price_date == date(2026, 10, 3)
    assert latest.price == Decimal("125")
    assert latest.source == "TEST"
