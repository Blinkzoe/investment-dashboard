from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select

from app.models.account import Account
from app.schemas.account_snapshot import AccountSnapshotCreate
from app.services.account_snapshot import AccountSnapshotService


def test_service_creates_account_snapshot(db_session) -> None:
    account = db_session.scalars(select(Account)).first()
    assert account is not None

    service = AccountSnapshotService(db_session)

    snapshot = service.create(
        AccountSnapshotCreate(
            account_id=account.id,
            snapshot_at=datetime(
                2026,
                10,
                3,
                21,
                0,
                tzinfo=timezone.utc,
            ),
            total_value=Decimal("120000"),
            cash_value=Decimal("7500"),
            currency="MXN",
            source="GBM",
            notes="Test service snapshot",
        )
    )

    assert snapshot.id is not None
    assert snapshot.account_id == account.id
    assert snapshot.total_value == Decimal("120000.00000000")
    assert snapshot.cash_value == Decimal("7500.00000000")
