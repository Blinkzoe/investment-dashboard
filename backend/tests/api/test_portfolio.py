from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.services.portfolio_snapshot import PortfolioSnapshotService


def test_list_portfolio_snapshots_exposes_contributed_capital(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        service = PortfolioSnapshotService(db_session)

        service.create(
            snapshot_at=datetime(
                2026,
                10,
                3,
                21,
                0,
                tzinfo=timezone.utc,
            ),
            total_value=Decimal("100000"),
            contributed_capital=Decimal("90000"),
            gain=Decimal("10000"),
            return_percentage=Decimal("11.111111"),
            currency="MXN",
            source="GBM",
            notes="Test snapshot",
        )

        client = TestClient(app)

        response = client.get("/api/v1/portfolio/snapshots")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert Decimal(data[0]["total_value"]) == Decimal("100000.00000000")
        assert Decimal(data[0]["contributed_capital"]) == Decimal("90000.00000000")
        assert Decimal(data[0]["gain"]) == Decimal("10000.00000000")
        assert Decimal(data[0]["return_percentage"]) == Decimal("11.111111")
        assert data[0]["currency"] == "MXN"
        assert data[0]["source"] == "GBM"
    finally:
        app.dependency_overrides.clear()
