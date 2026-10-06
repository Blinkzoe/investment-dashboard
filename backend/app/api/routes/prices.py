from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.price import PriceCreate, PriceRead
from app.services.price import PriceService


router = APIRouter(
    prefix="/api/v1/prices",
    tags=["prices"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=list[PriceRead],
)
def list_prices(
    db: DbSession,
    asset_id: int = Query(..., ge=1),
) -> list[PriceRead]:
    service = PriceService(db)

    return service.list_by_asset(asset_id)


@router.get(
    "/{asset_id}/latest",
    response_model=PriceRead,
)
def get_latest_price(
    asset_id: int,
    db: DbSession,
    source: str = Query(..., min_length=1),
) -> PriceRead:
    service = PriceService(db)
    price = service.get_latest_by_asset(
        asset_id=asset_id,
        source=source,
    )

    if price is None:
        raise HTTPException(
            status_code=404,
            detail="Latest price not found",
        )

    return price


@router.get(
    "/{asset_id}/{price_date}",
    response_model=PriceRead,
)
def get_price(
    asset_id: int,
    price_date: date,
    db: DbSession,
    source: str = Query(..., min_length=1),
) -> PriceRead:
    service = PriceService(db)

    price = service.get_by_asset_date_source(
        asset_id=asset_id,
        price_date=price_date,
        source=source,
    )

    if price is None:
        raise HTTPException(
            status_code=404,
            detail="Price not found",
        )

    return price


@router.post(
    "",
    response_model=PriceRead,
    status_code=201,
)
def create_price(
    data: PriceCreate,
    db: DbSession,
) -> PriceRead:
    service = PriceService(db)

    return service.create(
        asset_id=data.asset_id,
        price_date=data.price_date,
        price=data.price,
        currency=data.currency,
        source=data.source,
    )
