from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.portfolio_snapshot import PortfolioSnapshot


def test_portfolio_summary_returns_latest_matching_snapshot(
    db_session,
) -> None:
    db_session.add_all(
        [
            PortfolioSnapshot(
                snapshot_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
                total_value=Decimal("1000.00"),
                contributed_capital=Decimal("900.00"),
                gain=Decimal("100.00"),
                return_percentage=Decimal("11.11"),
                currency="MXN",
                source="GBM",
            ),
            PortfolioSnapshot(
                snapshot_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
                total_value=Decimal("1200.00"),
                contributed_capital=Decimal("1000.00"),
                gain=Decimal("200.00"),
                return_percentage=Decimal("20.00"),
                currency="MXN",
                source="GBM",
            ),
            PortfolioSnapshot(
                snapshot_at=datetime(2026, 10, 6, tzinfo=timezone.utc),
                total_value=Decimal("500.00"),
                currency="USD",
                source="GBM",
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
            "/api/v1/portfolio-summary",
            params={"currency": "MXN", "source": "GBM"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["snapshot_at"] == "2026-10-05T00:00:00Z"
        assert Decimal(data["total_value"]) == Decimal("1200.00000000")
        assert Decimal(data["contributed_capital"]) == Decimal("1000.00000000")
        assert Decimal(data["gain"]) == Decimal("200.00000000")
        assert Decimal(data["return_percentage"]) == Decimal("20.00000000")
        assert data["currency"] == "MXN"
        assert data["source"] == "GBM"
    finally:
        app.dependency_overrides.clear()


def test_portfolio_summary_without_match_returns_empty_summary(
    db_session,
) -> None:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/portfolio-summary",
            params={"currency": "USD", "source": "FINTUAL"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["snapshot_at"] is None
        assert data["total_value"] is None
        assert data["contributed_capital"] is None
        assert data["gain"] is None
        assert data["return_percentage"] is None
        assert data["currency"] is None
        assert data["source"] is None
    finally:
        app.dependency_overrides.clear()


def test_portfolio_summary_filters_by_source(
    db_session,
) -> None:
    db_session.add_all(
        [
            PortfolioSnapshot(
                snapshot_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
                total_value=Decimal("1200.00"),
                currency="MXN",
                source="GBM",
            ),
            PortfolioSnapshot(
                snapshot_at=datetime(2026, 10, 6, tzinfo=timezone.utc),
                total_value=Decimal("1500.00"),
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
            "/api/v1/portfolio-summary",
            params={"currency": "MXN", "source": "GBM"},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["source"] == "GBM"
        assert Decimal(data["total_value"]) == Decimal("1200.00000000")
    finally:
        app.dependency_overrides.clear()
