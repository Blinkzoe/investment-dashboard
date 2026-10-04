from datetime import datetime

from sqlalchemy.orm import Session

from app.models.account_position import AccountPosition
from app.repositories.account_position import AccountPositionRepository
from app.schemas.account_position import AccountPositionCreate


class AccountPositionService:
    def __init__(self, db: Session) -> None:
        self.repository = AccountPositionRepository(db)

    def get_by_id(self, position_id: int) -> AccountPosition | None:
        return self.repository.get_by_id(position_id)

    def list_by_account(
        self,
        account_id: int,
        source: str | None = None,
    ) -> list[AccountPosition]:
        return self.repository.list_by_account(
            account_id,
            source=source,
        )

    def list_by_snapshot(
        self,
        snapshot_at: datetime,
    ) -> list[AccountPosition]:
        return self.repository.list_by_snapshot(snapshot_at)

    def list_by_snapshot_and_source(
        self,
        *,
        account_id: int,
        snapshot_at: datetime,
        source: str,
    ) -> list[AccountPosition]:
        return self.repository.list_by_snapshot_and_source(
            account_id=account_id,
            snapshot_at=snapshot_at,
            source=source,
        )

    def create(
        self,
        data: AccountPositionCreate,
    ) -> AccountPosition:
        return self.repository.create(data)
