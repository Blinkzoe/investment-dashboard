from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account_position import AccountPosition
from app.schemas.account_position import AccountPositionCreate


class AccountPositionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, position_id: int) -> AccountPosition | None:
        return self.db.get(AccountPosition, position_id)

    def list_by_account(
        self,
        account_id: int,
    ) -> list[AccountPosition]:
        statement = (
            select(AccountPosition)
            .where(AccountPosition.account_id == account_id)
            .order_by(AccountPosition.snapshot_at.desc())
        )

        return list(self.db.scalars(statement).all())

    def list_by_snapshot(
        self,
        snapshot_at: datetime,
    ) -> list[AccountPosition]:
        statement = (
            select(AccountPosition)
            .where(AccountPosition.snapshot_at == snapshot_at)
            .order_by(AccountPosition.account_id, AccountPosition.asset_id)
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        data: AccountPositionCreate,
    ) -> AccountPosition:
        position = AccountPosition(**data.model_dump())

        self.db.add(position)
        self.db.flush()
        self.db.refresh(position)

        return position
