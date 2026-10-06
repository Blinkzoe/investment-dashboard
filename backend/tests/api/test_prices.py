from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.asset import Asset


def create_asset(db_session) -> Asset:
    asset = Asset(
        symbol="PRICE-TEST",
        name="Price Test Asset",
        asset_type="STOCK",
        currency="USD",
        exchange="TEST",
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def test_create_price_endpoint(db_session):
    asset = create_asset(db_session)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-01",
                "price": "123.456789",
                "currency": "USD",
                "source": "TEST",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["asset_id"] == asset.id
        assert data["price_date"] == "2026-10-01"
        assert Decimal(data["price"]) == Decimal("123.456789")
        assert data["currency"] == "USD"
        assert data["source"] == "TEST"
    finally:
        app.dependency_overrides.clear()


def test_list_prices_endpoint(db_session):
    asset = create_asset(db_session)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        first = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-01",
                "price": "100",
                "currency": "USD",
                "source": "TEST",
            },
        )

        second = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-02",
                "price": "110",
                "currency": "USD",
                "source": "TEST",
            },
        )

        assert first.status_code == 201
        assert second.status_code == 201

        response = client.get(
            "/api/v1/prices",
            params={"asset_id": asset.id},
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2
        assert data[0]["price_date"] == "2026-10-02"
        assert data[1]["price_date"] == "2026-10-01"
    finally:
        app.dependency_overrides.clear()


def test_get_price_endpoint(db_session):
    asset = create_asset(db_session)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        create_response = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-03",
                "price": "125.50",
                "currency": "USD",
                "source": "TEST",
            },
        )

        assert create_response.status_code == 201

        response = client.get(
            f"/api/v1/prices/{asset.id}/2026-10-03",
            params={"source": "TEST"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["asset_id"] == asset.id
        assert data["price_date"] == "2026-10-03"
        assert Decimal(data["price"]) == Decimal("125.50")
        assert data["currency"] == "USD"
        assert data["source"] == "TEST"
    finally:
        app.dependency_overrides.clear()


def test_get_price_endpoint_returns_404_when_not_found(db_session):
    asset = create_asset(db_session)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/api/v1/prices/{asset.id}/2026-10-03",
            params={"source": "TEST"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Price not found"
    finally:
        app.dependency_overrides.clear()


def test_get_latest_price_endpoint(db_session):
    asset = create_asset(db_session)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        first = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-01",
                "price": "100",
                "currency": "USD",
                "source": "TEST",
            },
        )

        second = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-03",
                "price": "125",
                "currency": "USD",
                "source": "TEST",
            },
        )

        other_source = client.post(
            "/api/v1/prices",
            json={
                "asset_id": asset.id,
                "price_date": "2026-10-05",
                "price": "999",
                "currency": "USD",
                "source": "OTHER",
            },
        )

        assert first.status_code == 201
        assert second.status_code == 201
        assert other_source.status_code == 201

        response = client.get(
            f"/api/v1/prices/{asset.id}/latest",
            params={"source": "TEST"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["asset_id"] == asset.id
        assert data["price_date"] == "2026-10-03"
        assert Decimal(data["price"]) == Decimal("125")
        assert data["currency"] == "USD"
        assert data["source"] == "TEST"
    finally:
        app.dependency_overrides.clear()


def test_get_latest_price_endpoint_returns_404_when_not_found(db_session):
    asset = create_asset(db_session)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/api/v1/prices/{asset.id}/latest",
            params={"source": "TEST"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Latest price not found"
    finally:
        app.dependency_overrides.clear()
