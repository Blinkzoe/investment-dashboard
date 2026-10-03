from sqlalchemy.orm import Session

from app.models.account_snapshot import AccountSnapshot
from app.repositories.account_snapshot import AccountSnapshotRepository


class AccountSnapshotService:
    def __init__(self, db: Session) -> None:
        self.repository = AccountSnapshotRepository(db)

    def list_by_account(
        self,
        account_id: int,
    ) -> list[AccountSnapshot]:
        return self.repository.list_by_account(account_id)

    def list_latest(self) -> list[AccountSnapshot]:
        return self.repository.list_latest()
