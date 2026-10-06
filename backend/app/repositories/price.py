from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price import Price


class PriceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_asset_date_source(
        self,
        *,
        asset_id: int,
        price_date: date,
        source: str,
    ) -> Price | None:
        statement = select(Price).where(
            Price.asset_id == asset_id,
            Price.price_date == price_date,
            Price.source == source,
        )

        return self.db.scalars(statement).first()

    def list_by_asset(
        self,
        asset_id: int,
    ) -> list[Price]:
        statement = (
            select(Price)
            .where(Price.asset_id == asset_id)
            .order_by(Price.price_date.desc())
        )

        return list(self.db.scalars(statement).all())

    def get_latest_by_asset(
        self,
        *,
        asset_id: int,
        source: str,
    ) -> Price | None:
        statement = (
            select(Price)
            .where(
                Price.asset_id == asset_id,
                Price.source == source,
            )
            .order_by(Price.price_date.desc())
        )
        return self.db.scalars(statement).first()

    def create(
        self,
        *,
        asset_id: int,
        price_date: date,
        price,
        currency: str,
        source: str,
    ) -> Price:
        price_record = Price(
            asset_id=asset_id,
            price_date=price_date,
            price=price,
            currency=currency,
            source=source,
        )

        self.db.add(price_record)
        self.db.commit()
        self.db.refresh(price_record)

        return price_record
