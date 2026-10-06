from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.account import AccountRepository
from app.schemas.account import AccountCreate


class AccountService:
    def __init__(self, db: Session) -> None:
        self.repository = AccountRepository(db)

    def get_by_id(self, account_id: int) -> Account | None:
        return self.repository.get_by_id(account_id)

    def list_all(self) -> list[Account]:
        return self.repository.list_all()

    def create(self, data: AccountCreate) -> Account:
        return self.repository.create(data)
