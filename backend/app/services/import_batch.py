from sqlalchemy.orm import Session

from app.models.import_batch import ImportBatch
from app.repositories.import_batch import ImportBatchRepository


class ImportBatchService:
    def __init__(self, db: Session) -> None:
        self.repository = ImportBatchRepository(db)

    def get_by_id(
        self,
        import_batch_id: int,
    ) -> ImportBatch | None:
        return self.repository.get_by_id(import_batch_id)

    def list_all(self) -> list[ImportBatch]:
        return self.repository.list_all()
