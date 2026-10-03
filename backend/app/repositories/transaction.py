from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Transaction]:
        statement = select(Transaction).order_by(
            Transaction.trade_date.desc(),
            Transaction.id.desc(),
        )

        return list(self.db.scalars(statement).all())

    def list_by_account(
        self,
        account_id: int,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(
                Transaction.trade_date.desc(),
                Transaction.id.desc(),
            )
        )

        return list(self.db.scalars(statement).all())

    def list_by_asset(
        self,
        asset_id: int,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .where(Transaction.asset_id == asset_id)
            .order_by(
                Transaction.trade_date.desc(),
                Transaction.id.desc(),
            )
        )

        return list(self.db.scalars(statement).all())
