from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.account_snapshot import AccountSnapshot


def test_account_summary_returns_account_and_reconciliation(
    db_session,
) -> None:
    db_session.add(
        AccountSnapshot(
            account_id=1,
            snapshot_at=datetime(2026, 10, 3, tzinfo=timezone.utc),
            total_value=Decimal("1000.00"),
            currency="MXN",
            source="GBM",
        )
    )
    db_session.flush()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/account-summary/1",
            params={"source": "GBM"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["account_id"] == 1
        assert data["institution"] == "TEST"
        assert data["name"] == "TEST GBM Trading MX"
        assert data["account_type"] == "TRADING"
        assert data["base_currency"] == "MXN"
        assert Decimal(data["official_value"]) == Decimal("1000.00000000")
        assert Decimal(data["positions_value"]) == Decimal("0")
        assert Decimal(data["difference"]) == Decimal("-1000.00000000")
        assert data["currency"] == "MXN"
        assert data["reconciliation_status"] == "NO_POSITION_DETAIL"
    finally:
        app.dependency_overrides.clear()


def test_account_summary_without_snapshot_returns_account_only(
    db_session,
) -> None:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get("/api/v1/account-summary/1")

        assert response.status_code == 200

        data = response.json()

        assert data["account_id"] == 1
        assert data["name"] == "TEST GBM Trading MX"
        assert data["snapshot_at"] is None
        assert data["official_value"] is None
        assert data["positions_value"] is None
        assert data["difference"] is None
        assert data["currency"] is None
        assert data["reconciliation_status"] is None
    finally:
        app.dependency_overrides.clear()


def test_account_summary_returns_404_for_unknown_account(
    db_session,
) -> None:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get("/api/v1/account-summary/999999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"
    finally:
        app.dependency_overrides.clear()
