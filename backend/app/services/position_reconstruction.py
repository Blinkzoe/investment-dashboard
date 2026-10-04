from collections import defaultdict
from decimal import Decimal

from app.models.transaction import Transaction


class PositionReconstructionService:
    SUPPORTED_TRANSACTION_TYPES = {
        "BUY": Decimal("1"),
    }

    def reconstruct(
        self,
        transactions: list[Transaction],
    ) -> dict[tuple[int, int], Decimal]:
        positions: dict[tuple[int, int], Decimal] = defaultdict(
            lambda: Decimal("0")
        )

        ordered_transactions = sorted(
            transactions,
            key=lambda transaction: (
                transaction.trade_date,
                transaction.id,
            ),
        )

        for transaction in ordered_transactions:
            if transaction.status not in {"FILLED", "COMPLETED"}:
                continue

            if transaction.asset_id is None:
                continue

            if transaction.transaction_type not in self.SUPPORTED_TRANSACTION_TYPES:
                raise ValueError(
                    f"Unsupported transaction type: "
                    f"{transaction.transaction_type}"
                )

            if transaction.quantity is None:
                raise ValueError(
                    f"Transaction {transaction.id} has no quantity"
                )

            key = (transaction.account_id, transaction.asset_id)

            positions[key] += (
                transaction.quantity
                * self.SUPPORTED_TRANSACTION_TYPES[
                    transaction.transaction_type
                ]
            )

        return dict(positions)
