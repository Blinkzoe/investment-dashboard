from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.transaction import TransactionRepository


class TransactionService:
    def __init__(self, db: Session) -> None:
        self.repository = TransactionRepository(db)

    def list_all(self) -> list[Transaction]:
        return self.repository.list_all()

    def list_by_account(
        self,
        account_id: int,
    ) -> list[Transaction]:
        return self.repository.list_by_account(account_id)

    def list_by_asset(
        self,
        asset_id: int,
    ) -> list[Transaction]:
        return self.repository.list_by_asset(asset_id)
