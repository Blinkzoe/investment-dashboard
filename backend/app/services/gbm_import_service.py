from app.adapters.gbm.adapter import GBMAdapter
from app.adapters.gbm.schemas import GBMTransactionInput
from app.schemas.import_result import ImportResult
from app.services.import_service import ImportService
from sqlalchemy.orm import Session


class GBMImportService:
    SOURCE = "GBM"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.import_service = ImportService(db)
        self.adapter = GBMAdapter()

    def import_transactions(
        self,
        *,
        transactions: list[GBMTransactionInput],
        import_type: str,
        filename: str | None = None,
        notes: str | None = None,
    ) -> ImportResult:
        normalized = self.adapter.normalize_transactions(transactions)

        return self.import_service.import_transactions(
            source=self.SOURCE,
            import_type=import_type,
            transactions=normalized,
            filename=filename,
            notes=notes,
        )
