from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db


    def get_by_source_and_external_id(
        self,
        source: str,
        external_id: str,
    ) -> Transaction | None:
        statement = (
            select(Transaction)
            .where(
                Transaction.source == source,
                Transaction.external_id == external_id,
            )
        )

        return self.db.scalars(statement).first()

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
