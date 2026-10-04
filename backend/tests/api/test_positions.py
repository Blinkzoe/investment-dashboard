from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.database import get_db
from app.main import app
from app.models.account_position import AccountPosition
from app.models.transaction import Transaction


def test_reconstruct_positions_endpoint(db_session):
    transactions = [
        Transaction(
            account_id=1,
            asset_id=1,
            transaction_type="BUY",
            status="FILLED",
            quantity=Decimal("5"),
            unit_price=Decimal("100"),
            gross_amount=Decimal("500"),
            total_amount=Decimal("500"),
            currency="MXN",
            trade_date=datetime(2026, 9, 1, tzinfo=timezone.utc),
            source="GBM",
            external_id="TEST-RECON-001",
        ),
        Transaction(
            account_id=1,
            asset_id=1,
            transaction_type="BUY",
            status="FILLED",
            quantity=Decimal("2.5"),
            unit_price=Decimal("110"),
            gross_amount=Decimal("275"),
            total_amount=Decimal("275"),
            currency="MXN",
            trade_date=datetime(2026, 9, 2, tzinfo=timezone.utc),
            source="GBM",
            external_id="TEST-RECON-002",
        ),
    ]

    for transaction in transactions:
        db_session.add(transaction)

    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/positions/reconstruct",
            json={
                "account_id": 1,
                "snapshot_at": "2026-10-03T21:00:00+00:00",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["account_id"] == 1
        assert data["snapshot_at"] == "2026-10-03T21:00:00Z"
        assert data["positions_created"] == 1

        positions = db_session.scalars(
            select(AccountPosition).where(
                AccountPosition.account_id == 1,
                AccountPosition.source == "RECONSTRUCTED",
            )
        ).all()

        assert len(positions) == 1
        assert positions[0].quantity == Decimal("7.5")
        assert positions[0].currency == "MXN"
        assert positions[0].market_price is None
        assert positions[0].market_value is None

    finally:
        app.dependency_overrides.clear()


def test_reconstruct_positions_endpoint_rejects_duplicate_snapshot(db_session):
    transaction = Transaction(
        account_id=1,
        asset_id=1,
        transaction_type="BUY",
        status="FILLED",
        quantity=Decimal("3"),
        unit_price=Decimal("100"),
        gross_amount=Decimal("300"),
        total_amount=Decimal("300"),
        currency="MXN",
        trade_date=datetime(2026, 9, 1, tzinfo=timezone.utc),
        source="GBM",
        external_id="TEST-RECON-DUPLICATE-001",
    )

    db_session.add(transaction)
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        payload = {
            "account_id": 1,
            "snapshot_at": "2026-10-03T21:00:00+00:00",
        }

        first = client.post(
            "/api/v1/positions/reconstruct",
            json=payload,
        )

        second = client.post(
            "/api/v1/positions/reconstruct",
            json=payload,
        )

        assert first.status_code == 201
        assert first.json()["positions_created"] == 1

        assert second.status_code == 409
        assert (
            second.json()["detail"]
            == "Reconstructed snapshot already exists for account "
            "1 at 2026-10-03 21:00:00+00:00"
        )

    finally:
        app.dependency_overrides.clear()


def test_list_positions_filters_by_source(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        base_payload = {
            "account_id": 1,
            "asset_id": 1,
            "snapshot_at": "2026-10-03T21:00:00+00:00",
            "quantity": "5",
            "currency": "MXN",
        }

        gbm_response = client.post(
            "/api/v1/positions",
            json={
                **base_payload,
                "market_price": "100",
                "market_value": "500",
                "source": "GBM",
            },
        )

        reconstructed_response = client.post(
            "/api/v1/positions",
            json={
                **base_payload,
                "snapshot_at": "2026-10-04T21:00:00+00:00",
                "market_price": None,
                "market_value": None,
                "source": "RECONSTRUCTED",
            },
        )

        assert gbm_response.status_code == 201
        assert reconstructed_response.status_code == 201

        all_positions = client.get(
            "/api/v1/positions",
            params={"account_id": 1},
        )

        reconstructed_positions = client.get(
            "/api/v1/positions",
            params={
                "account_id": 1,
                "source": "RECONSTRUCTED",
            },
        )

        gbm_positions = client.get(
            "/api/v1/positions",
            params={
                "account_id": 1,
                "source": "GBM",
            },
        )

        assert all_positions.status_code == 200
        assert reconstructed_positions.status_code == 200
        assert gbm_positions.status_code == 200

        assert len(all_positions.json()) == 2
        assert len(reconstructed_positions.json()) == 1
        assert reconstructed_positions.json()[0]["source"] == "RECONSTRUCTED"
        assert len(gbm_positions.json()) == 1
        assert gbm_positions.json()[0]["source"] == "GBM"

    finally:
        app.dependency_overrides.clear()


def test_compare_positions_endpoint(db_session):
    official = AccountPosition(
        account_id=1,
        asset_id=1,
        snapshot_at=datetime(2026, 10, 3, 20, 0, tzinfo=timezone.utc),
        quantity=Decimal("9.94"),
        market_price=Decimal("61.80"),
        market_value=Decimal("613.88"),
        currency="USD",
        source="GBM",
    )

    reconstructed = AccountPosition(
        account_id=1,
        asset_id=1,
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
        quantity=Decimal("10.00"),
        market_price=None,
        market_value=None,
        currency="USD",
        source="RECONSTRUCTED",
    )

    db_session.add_all([official, reconstructed])
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/positions/compare",
            json={
                "account_id": 1,
                "official_snapshot_at": "2026-10-03T20:00:00+00:00",
                "reconstructed_snapshot_at": "2026-10-03T21:00:00+00:00",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["account_id"] == 1
        assert data["official_snapshot_at"] == "2026-10-03T20:00:00Z"
        assert data["reconstructed_snapshot_at"] == "2026-10-03T21:00:00Z"

        assert len(data["comparisons"]) == 1

        comparison = data["comparisons"][0]

        assert comparison["asset_id"] == 1
        assert comparison["official_quantity"] == "9.9400000000"
        assert comparison["reconstructed_quantity"] == "10.0000000000"
        assert comparison["difference"] == "0.0600000000"
        assert comparison["status"] == "DIFFERENCE"

    finally:
        app.dependency_overrides.clear()


def test_compare_positions_endpoint_detects_missing_reconstructed(
    db_session,
):
    official = AccountPosition(
        account_id=1,
        asset_id=1,
        snapshot_at=datetime(2026, 10, 3, 20, 0, tzinfo=timezone.utc),
        quantity=Decimal("9.94"),
        market_price=Decimal("61.80"),
        market_value=Decimal("613.88"),
        currency="USD",
        source="GBM",
    )

    db_session.add(official)
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/positions/compare",
            json={
                "account_id": 1,
                "official_snapshot_at": "2026-10-03T20:00:00+00:00",
                "reconstructed_snapshot_at": "2026-10-03T21:00:00+00:00",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["comparisons"]) == 1

        comparison = data["comparisons"][0]

        assert comparison["asset_id"] == 1
        assert comparison["official_quantity"] == "9.9400000000"
        assert comparison["reconstructed_quantity"] is None
        assert comparison["difference"] is None
        assert comparison["status"] == "MISSING_RECONSTRUCTED"

    finally:
        app.dependency_overrides.clear()
