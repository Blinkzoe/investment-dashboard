from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.transaction import TransactionRepository


class TransactionService:
    def __init__(self, db: Session) -> None:
        self.repository = TransactionRepository(db)


    def get_by_source_and_external_id(
        self,
        source: str,
        external_id: str,
    ) -> Transaction | None:
        return self.repository.get_by_source_and_external_id(
            source,
            external_id,
        )


    def find_existing_by_external_id(
        self,
        source: str,
        external_id: str | None,
    ) -> Transaction | None:
        if not external_id:
            return None

        return self.repository.get_by_source_and_external_id(
            source,
            external_id,
        )

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
