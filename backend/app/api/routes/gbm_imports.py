from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.adapters.gbm.json_parser import GBMJsonParser
from app.api.dependencies import require_import_token
from app.core.database import get_db
from app.schemas.import_result import ImportResult
from app.services.gbm_import_service import GBMImportService

router = APIRouter(
    prefix="/api/v1/imports/gbm",
    tags=["gbm-imports"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/json",
    response_model=ImportResult,
    status_code=201,
)
def import_gbm_json(
    data: dict,
    db: DbSession,
    _: Annotated[None, Depends(require_import_token)],
) -> ImportResult:
    payload = data.get("payload")

    if payload is None:
        raise HTTPException(
            status_code=422,
            detail="Field 'payload' is required",
        )

    try:
        import json

        transactions = GBMJsonParser().parse(
            json.dumps(payload)
        )
    except (ValueError, ValidationError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid GBM JSON payload: {exc}",
        ) from exc

    service = GBMImportService(db)

    return service.import_transactions(
        transactions=transactions,
        import_type=str(data.get("import_type", "JSON")),
        filename=data.get("filename"),
        notes=data.get("notes"),
    )
