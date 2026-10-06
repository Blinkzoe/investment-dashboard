from datetime import datetime, timezone
from decimal import Decimal

from app.services.portfolio_snapshot import PortfolioSnapshotService


def test_service_creates_snapshot(db_session) -> None:
    service = PortfolioSnapshotService(db_session)

    snapshot = service.create(
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
        total_value=Decimal("125000"),
        contributed_capital=Decimal("100000"),
        gain=Decimal("25000"),
        return_percentage=Decimal("25"),
        currency="MXN",
        source="GBM",
        notes="Service test",
    )

    assert snapshot.id is not None
    assert snapshot.total_value == Decimal("125000.00000000")
    assert snapshot.contributed_capital == Decimal("100000.00000000")
    assert snapshot.gain == Decimal("25000.00000000")


def test_service_lists_snapshots(db_session) -> None:
    service = PortfolioSnapshotService(db_session)

    service.create(
        snapshot_at=datetime(2026, 10, 1, 21, 0, tzinfo=timezone.utc),
        total_value=Decimal("100000"),
        currency="MXN",
        source="GBM",
    )

    service.create(
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
        total_value=Decimal("110000"),
        currency="MXN",
        source="GBM",
    )

    snapshots = service.list_all()

    assert len(snapshots) == 2
    assert snapshots[0].total_value == Decimal("110000.00000000")


def test_service_gets_snapshot_by_identity(db_session) -> None:
    service = PortfolioSnapshotService(db_session)

    created = service.create(
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
        total_value=Decimal("110000"),
        currency="MXN",
        source="GBM",
    )

    found = service.get_by_snapshot_source_currency(
        snapshot_at=created.snapshot_at,
        source="GBM",
        currency="MXN",
    )

    assert found is not None
    assert found.id == created.id
