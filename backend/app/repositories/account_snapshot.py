from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account_snapshot import AccountSnapshot


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
        statement = select(AccountSnapshot).order_by(
            AccountSnapshot.account_id,
            AccountSnapshot.snapshot_at.desc(),
        )

        return list(self.db.scalars(statement).all())
