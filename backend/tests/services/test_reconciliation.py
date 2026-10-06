from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models.account_position import AccountPosition
from app.models.account_snapshot import AccountSnapshot
from app.services.reconciliation import ReconciliationService


def test_reconcile_account_requires_snapshot(db_session):
    service = ReconciliationService(db_session)

    with pytest.raises(ValueError, match="No account snapshot found"):
        service.reconcile_account(999999)


def test_reconcile_account_without_positions(db_session):
    snapshot = AccountSnapshot(
        account_id=1,
        snapshot_at=datetime(2026, 10, 3, tzinfo=timezone.utc),
        total_value=Decimal("1000.00"),
        currency="MXN",
        source="GBM",
    )

    db_session.add(snapshot)
    db_session.flush()

    result = ReconciliationService(db_session).reconcile_account(1)

    assert result.official_value == Decimal("1000.00")
    assert result.positions_value == Decimal("0")
    assert result.difference == Decimal("-1000.00")
    assert result.status == "NO_POSITION_DETAIL"


def test_reconcile_account_with_rounding_difference(db_session):
    snapshot_at = datetime(2026, 10, 3, tzinfo=timezone.utc)

    snapshot = AccountSnapshot(
        account_id=1,
        snapshot_at=snapshot_at,
        total_value=Decimal("1000.00"),
        currency="USD",
        source="GBM",
    )

    position = AccountPosition(
        account_id=1,
        asset_id=1,
        snapshot_at=snapshot_at,
        quantity=Decimal("10"),
        market_price=Decimal("100.0005"),
        market_value=Decimal("1000.005"),
        currency="USD",
        source="GBM",
    )

    db_session.add_all([snapshot, position])
    db_session.flush()

    result = ReconciliationService(db_session).reconcile_account(1)

    assert result.official_value == Decimal("1000.00")
    assert result.positions_value == Decimal("1000.005")
    assert result.difference == Decimal("0.005")
    assert result.status == "RECONCILED_WITH_ROUNDING"

def test_reconcile_account_can_filter_latest_snapshot_by_source(
    db_session,
):
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

    result = ReconciliationService(db_session).reconcile_account(
        1,
        source="GBM",
    )

    assert result.official_value == Decimal("1000.00")
    assert result.currency == "MXN"
    assert result.snapshot_at == datetime(
        2026,
        10,
        3,
        tzinfo=timezone.utc,
    )

