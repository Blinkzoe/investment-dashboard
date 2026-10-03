from app.adapters.gbm.schemas import GBMTransactionInput
from app.adapters.gbm.transaction_mapper import GBMTransactionMapper
from app.schemas.import_transaction import NormalizedTransaction


class GBMAdapter:
    SOURCE = "GBM"

    def normalize_transaction(
        self,
        transaction: GBMTransactionInput,
    ) -> NormalizedTransaction:
        return GBMTransactionMapper.to_normalized(transaction)

    def normalize_transactions(
        self,
        transactions: list[GBMTransactionInput],
    ) -> list[NormalizedTransaction]:
        return GBMTransactionMapper.to_normalized_many(transactions)
