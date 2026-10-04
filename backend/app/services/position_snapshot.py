from datetime import datetime

from sqlalchemy.orm import Session

from app.models.account_position import AccountPosition
from app.repositories.account_position import AccountPositionRepository
from app.repositories.transaction import TransactionRepository
from app.services.position_reconstruction import PositionReconstructionService


class PositionSnapshotService:
    SOURCE = "RECONSTRUCTED"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.position_repository = AccountPositionRepository(db)
        self.transaction_repository = TransactionRepository(db)
        self.reconstruction_service = PositionReconstructionService()

    def create_snapshot(
        self,
        *,
        account_id: int,
        snapshot_at: datetime,
    ) -> list[AccountPosition]:
        existing_positions = self.position_repository.list_by_account(account_id)

        if any(
            position.snapshot_at == snapshot_at
            and position.source == self.SOURCE
            for position in existing_positions
        ):
            raise ValueError(
                f"Reconstructed snapshot already exists for account "
                f"{account_id} at {snapshot_at}"
            )

        transactions = self.transaction_repository.list_by_account(account_id)

        reconstructed = self.reconstruction_service.reconstruct(transactions)

        positions: list[AccountPosition] = []

        for (position_account_id, asset_id), quantity in reconstructed.items():
            if position_account_id != account_id:
                continue

            source_transaction = next(
                transaction
                for transaction in transactions
                if transaction.account_id == account_id
                and transaction.asset_id == asset_id
                and transaction.currency is not None
            )

            position = AccountPosition(
                account_id=account_id,
                asset_id=asset_id,
                snapshot_at=snapshot_at,
                quantity=quantity,
                market_price=None,
                market_value=None,
                currency=source_transaction.currency,
                source=self.SOURCE,
                notes="Position reconstructed from transaction history",
            )

            self.db.add(position)
            positions.append(position)

        self.db.commit()

        for position in positions:
            self.db.refresh(position)

        return positions
