from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.price import Price
from app.repositories.price import PriceRepository


class PriceService:
    def __init__(self, db: Session) -> None:
        self.repository = PriceRepository(db)

    def get_by_asset_date_source(
        self,
        *,
        asset_id: int,
        price_date: date,
        source: str,
    ) -> Price | None:
        return self.repository.get_by_asset_date_source(
            asset_id=asset_id,
            price_date=price_date,
            source=source,
        )

    def list_by_asset(
        self,
        asset_id: int,
    ) -> list[Price]:
        return self.repository.list_by_asset(asset_id)

    def get_latest_by_asset(
        self,
        *,
        asset_id: int,
        source: str,
    ) -> Price | None:
        return self.repository.get_latest_by_asset(
            asset_id=asset_id,
            source=source,
        )

    def create(
        self,
        *,
        asset_id: int,
        price_date: date,
        price: Decimal,
        currency: str,
        source: str,
    ) -> Price:
        return self.repository.create(
            asset_id=asset_id,
            price_date=price_date,
            price=price,
            currency=currency,
            source=source,
        )
