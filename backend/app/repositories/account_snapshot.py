
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
    ) -> list[AccountSnapshot]:
        statement = (
            select(AccountSnapshot)
            .where(AccountSnapshot.account_id == account_id)
            .order_by(AccountSnapshot.snapshot_at.desc())
        )
        return list(self.db.scalars(statement).all())

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

    def create(
        self,
        data: AccountSnapshotCreate,
    ) -> AccountSnapshot:
        snapshot = AccountSnapshot(**data.model_dump())
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot
