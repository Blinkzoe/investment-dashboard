from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate


class AccountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, account_id: int) -> Account | None:
        return self.db.get(Account, account_id)

    def list_all(self) -> list[Account]:
        statement = select(Account).order_by(Account.id)

        return list(self.db.scalars(statement).all())

    def create(self, data: AccountCreate) -> Account:
        account = Account(**data.model_dump())

        self.db.add(account)
        self.db.flush()
        self.db.refresh(account)

        return account
