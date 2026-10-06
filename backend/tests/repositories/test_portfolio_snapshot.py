from datetime import datetime, timezone
from decimal import Decimal

from app.repositories.portfolio_snapshot import PortfolioSnapshotRepository


def test_create_and_get_snapshot(db_session) -> None:
    repository = PortfolioSnapshotRepository(db_session)

    snapshot_at = datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc)

    created = repository.create(
        snapshot_at=snapshot_at,
        total_value=Decimal("100000"),
        contributed_capital=Decimal("90000"),
        gain=Decimal("10000"),
        return_percentage=Decimal("11.111111"),
        currency="MXN",
        source="GBM",
        notes="Test snapshot",
    )

    assert created.id is not None
    assert created.total_value == Decimal("100000.00000000")

    found = repository.get_by_snapshot_source_currency(
        snapshot_at=snapshot_at,
        source="GBM",
        currency="MXN",
    )

    assert found is not None
    assert found.id == created.id
    assert found.total_value == Decimal("100000.00000000")


def test_list_all_orders_newest_first(db_session) -> None:
    repository = PortfolioSnapshotRepository(db_session)

    older = datetime(2026, 10, 1, 21, 0, tzinfo=timezone.utc)
    newer = datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc)

    repository.create(
        snapshot_at=older,
        total_value=Decimal("100000"),
        contributed_capital=None,
        gain=None,
        return_percentage=None,
        currency="MXN",
        source="GBM",
        notes=None,
    )

    repository.create(
        snapshot_at=newer,
        total_value=Decimal("105000"),
        contributed_capital=None,
        gain=None,
        return_percentage=None,
        currency="MXN",
        source="GBM",
        notes=None,
    )

    snapshots = repository.list_all()

    assert len(snapshots) == 2
    assert snapshots[0].snapshot_at == newer
    assert snapshots[1].snapshot_at == older


def test_get_snapshot_returns_none_when_not_found(db_session) -> None:
    repository = PortfolioSnapshotRepository(db_session)

    result = repository.get_by_snapshot_source_currency(
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
        source="GBM",
        currency="MXN",
    )

    assert result is None
