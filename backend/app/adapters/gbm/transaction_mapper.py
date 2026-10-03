from app.adapters.gbm.schemas import GBMTransactionInput
from app.schemas.import_transaction import NormalizedTransaction


class GBMTransactionMapper:
    SOURCE = "GBM"

    @classmethod
    def to_normalized(
        cls,
        transaction: GBMTransactionInput,
    ) -> NormalizedTransaction:
        return NormalizedTransaction(
            account_id=transaction.account_id,
            asset_id=transaction.asset_id,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            quantity=transaction.quantity,
            unit_price=transaction.unit_price,
            gross_amount=transaction.gross_amount,
            commission=transaction.commission,
            taxes=transaction.taxes,
            other_fees=transaction.other_fees,
            total_amount=transaction.total_amount,
            currency=transaction.currency,
            trade_date=transaction.trade_date,
            settlement_date=transaction.settlement_date,
            source=cls.SOURCE,
            external_id=transaction.external_id,
            notes=transaction.notes,
            metadata_json=transaction.metadata_json,
        )

    @classmethod
    def to_normalized_many(
        cls,
        transactions: list[GBMTransactionInput],
    ) -> list[NormalizedTransaction]:
        return [
            cls.to_normalized(transaction)
            for transaction in transactions
        ]
