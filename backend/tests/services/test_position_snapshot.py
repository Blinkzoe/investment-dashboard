from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.models.transaction import Transaction
from app.models.account_position import AccountPosition
from app.services.position_snapshot import PositionSnapshotService


def make_transaction(
    *,
    account_id: int,
    asset_id: int,
    quantity: str,
    trade_date: date,
    transaction_type: str = "BUY",
    status: str = "FILLED",
    currency: str = "MXN",
) -> Transaction:
    return Transaction(
        account_id=account_id,
        asset_id=asset_id,
        transaction_type=transaction_type,
        status=status,
        quantity=Decimal(quantity),
        unit_price=Decimal("100"),
        gross_amount=Decimal(quantity) * Decimal("100"),
        commission=Decimal("0"),
        taxes=Decimal("0"),
        other_fees=Decimal("0"),
        total_amount=Decimal(quantity) * Decimal("100"),
        currency=currency,
        trade_date=trade_date,
        source="TEST",
    )


def test_create_reconstructed_snapshot(db_session):
    transaction = make_transaction(
        account_id=1,
        asset_id=1,
        quantity="10",
        trade_date=date(2026, 1, 10),
    )
    db_session.add(transaction)
    db_session.commit()

    snapshot_at = datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc)

    service = PositionSnapshotService(db_session)

    positions = service.create_snapshot(
        account_id=1,
        snapshot_at=snapshot_at,
    )

    assert len(positions) == 1
    assert positions[0].account_id == 1
    assert positions[0].asset_id == 1
    assert positions[0].quantity == Decimal("10")
    assert positions[0].snapshot_at == snapshot_at
    assert positions[0].currency == "MXN"
    assert positions[0].source == "RECONSTRUCTED"
    assert positions[0].market_price is None
    assert positions[0].market_value is None


def test_create_snapshot_aggregates_transactions(db_session):
    db_session.add_all(
        [
            make_transaction(
                account_id=1,
                asset_id=1,
                quantity="10",
                trade_date=date(2026, 1, 10),
            ),
            make_transaction(
                account_id=1,
                asset_id=1,
                quantity="5",
                trade_date=date(2026, 2, 10),
            ),
        ]
    )
    db_session.commit()

    service = PositionSnapshotService(db_session)

    positions = service.create_snapshot(
        account_id=1,
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
    )

    assert len(positions) == 1
    assert positions[0].quantity == Decimal("15")


def test_create_snapshot_ignores_transactions_without_completed_status(
    db_session,
):
    db_session.add(
        make_transaction(
            account_id=1,
            asset_id=1,
            quantity="10",
            trade_date=date(2026, 1, 10),
            status="PENDING",
        )
    )
    db_session.commit()

    service = PositionSnapshotService(db_session)

    positions = service.create_snapshot(
        account_id=1,
        snapshot_at=datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc),
    )

    assert positions == []


def test_create_snapshot_rejects_duplicate_snapshot(db_session):
    transaction = make_transaction(
        account_id=1,
        asset_id=1,
        quantity="10",
        trade_date=date(2026, 1, 10),
    )
    db_session.add(transaction)
    db_session.commit()

    snapshot_at = datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc)

    service = PositionSnapshotService(db_session)

    service.create_snapshot(
        account_id=1,
        snapshot_at=snapshot_at,
    )

    with pytest.raises(ValueError, match="already exists"):
        service.create_snapshot(
            account_id=1,
            snapshot_at=snapshot_at,
        )
