from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.account_snapshot import AccountSnapshot
from app.schemas.account_snapshot import AccountSnapshotCreate


class AccountSnapshotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_account(
        self,
        account_id: int,
        *,
        source: str | None = None,
    ) -> list[AccountSnapshot]:
        statement = (
            select(AccountSnapshot)
            .where(AccountSnapshot.account_id == account_id)
            .order_by(AccountSnapshot.snapshot_at.desc())
        )

        if source is not None:
            statement = statement.where(AccountSnapshot.source == source)

        return list(self.db.scalars(statement).all())

    def get_latest_by_account(
        self,
        account_id: int,
        *,
        source: str | None = None,
    ) -> AccountSnapshot | None:
        statement = (
            select(AccountSnapshot)
            .where(AccountSnapshot.account_id == account_id)
            .order_by(AccountSnapshot.snapshot_at.desc())
        )

        if source is not None:
            statement = statement.where(AccountSnapshot.source == source)

        return self.db.scalars(statement).first()

    def list_latest(self) -> list[AccountSnapshot]:
        latest_snapshot = (
            select(
                AccountSnapshot.account_id,
                func.max(AccountSnapshot.snapshot_at).label("max_snapshot_at"),
            )
            .group_by(AccountSnapshot.account_id)
            .subquery()
        )

        statement = (
            select(AccountSnapshot)
            .join(
                latest_snapshot,
                (AccountSnapshot.account_id == latest_snapshot.c.account_id)
                & (
                    AccountSnapshot.snapshot_at
                    == latest_snapshot.c.max_snapshot_at
                ),
            )
            .order_by(AccountSnapshot.account_id)
        )

        return list(self.db.scalars(statement).all())

    def list_monthly_summary(
        self,
        *,
        source: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        month = func.date_trunc("month", AccountSnapshot.snapshot_at)

        statement = (
            select(
                month.label("month"),
                func.sum(AccountSnapshot.total_value).label("total_value"),
                func.sum(AccountSnapshot.interest_value).label("interest_value"),
                func.sum(AccountSnapshot.contribution_value).label(
                    "contribution_value"
                ),
                func.sum(AccountSnapshot.withdrawal_value).label(
                    "withdrawal_value"
                ),
                func.count(AccountSnapshot.id).label("account_count"),
            )
            .group_by(month)
            .order_by(month)
        )

        if source is not None:
            statement = statement.where(AccountSnapshot.source == source)

        if start_date is not None:
            statement = statement.where(
                AccountSnapshot.snapshot_at >= start_date
            )

        if end_date is not None:
            statement = statement.where(
                AccountSnapshot.snapshot_at < end_date
            )

        return list(self.db.execute(statement).all())

    def create(self, data: AccountSnapshotCreate) -> AccountSnapshot:
        snapshot = AccountSnapshot(**data.model_dump())
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot
