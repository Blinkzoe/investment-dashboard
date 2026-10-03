from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_import_token
from app.core.database import get_db
from app.schemas.import_request import ImportTransactionsRequest
from app.schemas.import_result import ImportResult
from app.services.import_service import ImportService


router = APIRouter(
    prefix="/api/v1/imports",
    tags=["imports"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/transactions",
    response_model=ImportResult,
    status_code=201,
)
def import_transactions(
    data: ImportTransactionsRequest,
    db: DbSession,
    _: Annotated[None, Depends(require_import_token)],
) -> ImportResult:
    service = ImportService(db)

    return service.import_transactions(
        source=data.source,
        import_type=data.import_type,
        transactions=data.transactions,
        filename=data.filename,
        notes=data.notes,
    )
