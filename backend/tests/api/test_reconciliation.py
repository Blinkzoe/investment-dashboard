from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.account_snapshot import AccountSnapshot


def test_reconciliation_api_accepts_source_filter(db_session) -> None:
    db_session.add_all(
        [
            AccountSnapshot(
                account_id=1,
                snapshot_at=datetime(
                    2026,
                    10,
                    3,
                    tzinfo=timezone.utc,
                ),
                total_value=Decimal("1000.00"),
                currency="MXN",
                source="GBM",
            ),
            AccountSnapshot(
                account_id=1,
                snapshot_at=datetime(
                    2026,
                    10,
                    4,
                    tzinfo=timezone.utc,
                ),
                total_value=Decimal("2000.00"),
                currency="MXN",
                source="FINTUAL",
            ),
        ]
    )
    db_session.flush()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/reconciliation/accounts/1",
            params={"source": "GBM"},
        )

        assert response.status_code == 200

        data = response.json()

        assert Decimal(data["official_value"]) == Decimal("1000.00000000")
        assert data["currency"] == "MXN"
        assert data["snapshot_at"] == "2026-10-03T00:00:00Z"
        assert data["status"] == "NO_POSITION_DETAIL"
    finally:
        app.dependency_overrides.clear()
