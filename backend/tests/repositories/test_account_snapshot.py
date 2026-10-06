from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select

from app.models.account import Account
from app.repositories.account_snapshot import AccountSnapshotRepository
from app.schemas.account_snapshot import AccountSnapshotCreate


def test_repository_creates_account_snapshot(db_session) -> None:
    account = db_session.scalars(select(Account)).first()
    assert account is not None

    repository = AccountSnapshotRepository(db_session)

    snapshot = repository.create(
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
            total_value=Decimal("100000"),
            cash_value=Decimal("5000"),
            currency="MXN",
            source="GBM",
            notes="Test account snapshot",
        )
    )

    assert snapshot.id is not None
    assert snapshot.account_id == account.id
    assert snapshot.total_value == Decimal("100000.00000000")
    assert snapshot.cash_value == Decimal("5000.00000000")
    assert snapshot.currency == "MXN"
    assert snapshot.source == "GBM"


def test_repository_list_latest_returns_latest_snapshot_per_account(
    db_session,
) -> None:
    account = db_session.scalars(select(Account)).first()
    assert account is not None

    repository = AccountSnapshotRepository(db_session)

    repository.create(
        AccountSnapshotCreate(
            account_id=account.id,
            snapshot_at=datetime(
                2026,
                10,
                2,
                21,
                0,
                tzinfo=timezone.utc,
            ),
            total_value=Decimal("100000"),
            currency="MXN",
            source="GBM",
        )
    )

    latest = repository.create(
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
            total_value=Decimal("110000"),
            currency="MXN",
            source="GBM",
        )
    )

    snapshots = repository.list_latest()

    assert len(snapshots) == 1
    assert snapshots[0].id == latest.id
    assert snapshots[0].total_value == Decimal("110000.00000000")
