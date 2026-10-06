from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.account import Account


def test_create_account_snapshot_exposes_cash_value(db_session) -> None:
    account = db_session.get(Account, 1)
    if account is None:
        account = db_session.query(Account).first()
    assert account is not None

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/snapshots/accounts",
            json={
                "account_id": account.id,
                "snapshot_at": datetime(
                    2026,
                    10,
                    3,
                    21,
                    0,
                    tzinfo=timezone.utc,
                ).isoformat(),
                "total_value": "150000",
                "cash_value": "12500",
                "currency": "MXN",
                "source": "GBM",
                "notes": "API test snapshot",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["account_id"] == account.id
        assert Decimal(data["total_value"]) == Decimal("150000.00000000")
        assert Decimal(data["cash_value"]) == Decimal("12500.00000000")
        assert data["currency"] == "MXN"
        assert data["source"] == "GBM"
        assert data["notes"] == "API test snapshot"
    finally:
        app.dependency_overrides.clear()
