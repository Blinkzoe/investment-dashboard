from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.api.dependencies import require_import_token
from app.core.database import get_db
from app.main import app
from app.models.account import Account
from app.models.asset import Asset
from app.models.transaction import Transaction


def test_import_gbm_json_endpoint(db_session):
    account = db_session.scalars(
        select(Account).where(Account.institution == "TEST")
    ).one()
    asset = db_session.scalars(
        select(Asset).where(Asset.symbol == "TEST-ASSET")
    ).one()

    def override_get_db():
        yield db_session

    def override_import_token():
        return None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_import_token] = override_import_token

    try:
        client = TestClient(app)

        payload = {
            "import_type": "JSON_TEST",
            "filename": "gbm_test.json",
            "notes": "Endpoint integration test",
            "payload": [
                {
                    "external_id": "TEST-ENDPOINT-001",
                    "account_id": account.id,
                    "asset_id": asset.id,
                    "transaction_type": "BUY",
                    "status": "FILLED",
                    "quantity": "5",
                    "unit_price": "100.00",
                    "gross_amount": "500.00",
                    "commission": "1.25",
                    "taxes": "0",
                    "other_fees": "0",
                    "total_amount": "501.25",
                    "currency": "MXN",
                    "trade_date": "2026-10-03",
                }
            ],
        }

        response = client.post(
            "/api/v1/imports/gbm/json",
            json=payload,
        )

        assert response.status_code == 201

        result = response.json()

        assert result["received"] == 1
        assert result["imported"] == 1
        assert result["skipped_duplicates"] == 0
        assert result["import_batch_id"] is not None

        transaction = db_session.scalars(
            select(Transaction).where(
                Transaction.external_id == "TEST-ENDPOINT-001"
            )
        ).one()

        assert transaction.source == "GBM"
        assert transaction.account_id == account.id
        assert transaction.asset_id == asset.id
        assert transaction.quantity == Decimal("5")
        assert transaction.unit_price == Decimal("100.00")
        assert transaction.total_amount == Decimal("501.25")
    finally:
        app.dependency_overrides.clear()


def test_import_gbm_json_endpoint_requires_authentication():
    client = TestClient(app)

    response = client.post(
        "/api/v1/imports/gbm/json",
        json={"payload": []},
    )

    assert response.status_code == 401


def test_import_gbm_json_endpoint_skips_duplicate(db_session):
    account = db_session.scalars(
        select(Account).where(Account.institution == "TEST")
    ).one()
    asset = db_session.scalars(
        select(Asset).where(Asset.symbol == "TEST-ASSET")
    ).one()

    def override_get_db():
        yield db_session

    def override_import_token():
        return None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_import_token] = override_import_token

    try:
        client = TestClient(app)

        payload = {
            "import_type": "JSON_TEST",
            "payload": [
                {
                    "external_id": "TEST-ENDPOINT-DUPLICATE-001",
                    "account_id": account.id,
                    "asset_id": asset.id,
                    "transaction_type": "BUY",
                    "status": "FILLED",
                    "quantity": "2",
                    "unit_price": "50.00",
                    "gross_amount": "100.00",
                    "commission": "0.25",
                    "taxes": "0",
                    "other_fees": "0",
                    "total_amount": "100.25",
                    "currency": "MXN",
                    "trade_date": "2026-10-03",
                }
            ],
        }

        first = client.post(
            "/api/v1/imports/gbm/json",
            json=payload,
        )

        second = client.post(
            "/api/v1/imports/gbm/json",
            json=payload,
        )

        assert first.status_code == 201
        assert second.status_code == 201

        assert first.json()["imported"] == 1
        assert first.json()["skipped_duplicates"] == 0

        assert second.json()["imported"] == 0
        assert second.json()["skipped_duplicates"] == 1

        transactions = db_session.scalars(
            select(Transaction).where(
                Transaction.external_id == "TEST-ENDPOINT-DUPLICATE-001"
            )
        ).all()

        assert len(transactions) == 1

    finally:
        app.dependency_overrides.clear()


def test_import_gbm_json_endpoint_rejects_invalid_payload():
    def override_import_token():
        return None

    app.dependency_overrides[require_import_token] = override_import_token

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/imports/gbm/json",
            json={
                "payload": {
                    "external_id": "INVALID",
                }
            },
        )

        assert response.status_code == 422
        assert "Invalid GBM JSON payload" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_import_gbm_json_endpoint_requires_payload():
    def override_import_token():
        return None

    app.dependency_overrides[require_import_token] = override_import_token

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/imports/gbm/json",
            json={},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "Field 'payload' is required"
    finally:
        app.dependency_overrides.clear()
