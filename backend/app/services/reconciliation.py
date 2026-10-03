from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.account_position import AccountPositionRepository
from app.repositories.account_snapshot import AccountSnapshotRepository
from app.schemas.reconciliation import AccountReconciliationRead


ROUNDING_TOLERANCE = Decimal("0.02")


class ReconciliationService:
    def __init__(self, db: Session) -> None:
        self.position_repository = AccountPositionRepository(db)
        self.snapshot_repository = AccountSnapshotRepository(db)

    def reconcile_account(
        self,
        account_id: int,
    ) -> AccountReconciliationRead:
        snapshots = self.snapshot_repository.list_by_account(account_id)

        if not snapshots:
            raise ValueError("No account snapshot found")

        snapshot = snapshots[0]

        positions = self.position_repository.list_by_account(account_id)

        snapshot_positions = [
            position
            for position in positions
            if position.snapshot_at == snapshot.snapshot_at
            and position.source == snapshot.source
        ]

        positions_value = sum(
            (
                position.market_value
                for position in snapshot_positions
                if position.market_value is not None
            ),
            Decimal("0"),
        )

        official_value = snapshot.total_value
        difference = positions_value - official_value

        if not snapshot_positions:
            status = "NO_POSITION_DETAIL"
        elif difference == Decimal("0"):
            status = "RECONCILED"
        elif abs(difference) <= ROUNDING_TOLERANCE:
            status = "RECONCILED_WITH_ROUNDING"
        else:
            status = "DIFFERENCE"

        return AccountReconciliationRead(
            account_id=account_id,
            snapshot_at=snapshot.snapshot_at,
            official_value=official_value,
            positions_value=positions_value,
            difference=difference,
            currency=snapshot.currency,
            status=status,
        )
