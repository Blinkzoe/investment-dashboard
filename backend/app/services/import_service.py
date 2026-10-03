from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.adapters.gbm.adapter import GBMAdapter
from app.adapters.gbm.schemas import GBMTransactionInput
from app.models.import_batch import ImportBatch
from app.models.transaction import Transaction
from app.repositories.transaction import TransactionRepository
from app.schemas.import_result import ImportResult
from app.schemas.import_transaction import NormalizedTransaction


class ImportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.transaction_repository = TransactionRepository(db)

    def import_transactions(
        self,
        *,
        source: str,
        import_type: str,
        transactions: list[NormalizedTransaction],
        filename: str | None = None,
        notes: str | None = None,
    ) -> ImportResult:
        received = len(transactions)
        imported = 0
        skipped_duplicates = 0

        batch = ImportBatch(
            source=source,
            import_type=import_type,
            status="RUNNING",
            filename=filename,
            notes=notes,
        )

        self.db.add(batch)
        self.db.flush()

        try:
            for item in transactions:
                existing = (
                    self.transaction_repository
                    .get_by_source_and_external_id(
                        item.source,
                        item.external_id,
                    )
                    if item.external_id
                    else None
                )

                if existing is not None:
                    skipped_duplicates += 1
                    continue

                transaction = Transaction(
                    **item.model_dump(),
                    import_batch_id=batch.id,
                )

                self.db.add(transaction)
                imported += 1

            batch.status = "COMPLETED"
            batch.completed_at = datetime.now(timezone.utc)

            self.db.commit()

            return ImportResult(
                import_batch_id=batch.id,
                received=received,
                imported=imported,
                skipped_duplicates=skipped_duplicates,
            )

        except Exception:
            self.db.rollback()
            raise

    def import_gbm_transactions(
        self,
        *,
        transactions: list[GBMTransactionInput],
        import_type: str,
        filename: str | None = None,
        notes: str | None = None,
    ) -> ImportResult:
        adapter = GBMAdapter()

        normalized = adapter.normalize_transactions(transactions)

        return self.import_transactions(
            source=GBMAdapter.SOURCE,
            import_type=import_type,
            transactions=normalized,
            filename=filename,
            notes=notes,
        )
