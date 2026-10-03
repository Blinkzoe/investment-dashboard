from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.import_batch import ImportBatch


class ImportBatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(
        self,
        import_batch_id: int,
    ) -> ImportBatch | None:
        return self.db.get(ImportBatch, import_batch_id)

    def list_all(self) -> list[ImportBatch]:
        statement = select(ImportBatch).order_by(
            ImportBatch.started_at.desc(),
            ImportBatch.id.desc(),
        )

        return list(self.db.scalars(statement).all())
