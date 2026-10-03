from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.import_batch import ImportBatchRead
from app.services.import_batch import ImportBatchService


router = APIRouter(
    prefix="/api/v1/imports",
    tags=["imports"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/batches",
    response_model=list[ImportBatchRead],
)
def list_import_batches(
    db: DbSession,
) -> list[ImportBatchRead]:
    service = ImportBatchService(db)

    return service.list_all()


@router.get(
    "/batches/{import_batch_id}",
    response_model=ImportBatchRead,
)
def get_import_batch(
    import_batch_id: int,
    db: DbSession,
) -> ImportBatchRead:
    service = ImportBatchService(db)

    batch = service.get_by_id(import_batch_id)

    if batch is None:
        raise HTTPException(
            status_code=404,
            detail="Import batch not found",
        )

    return batch
