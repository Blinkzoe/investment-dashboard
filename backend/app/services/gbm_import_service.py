from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.gbm.adapter import GBMAdapter
from app.adapters.gbm.schemas import GBMTransactionInput
from app.models.account import Account
from app.models.asset import Asset
from app.schemas.import_result import ImportResult
from app.services.import_service import ImportService


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
        self._validate_references(transactions)

        normalized = self.adapter.normalize_transactions(transactions)

        return self.import_service.import_transactions(
            source=self.SOURCE,
            import_type=import_type,
            transactions=normalized,
            filename=filename,
            notes=notes,
        )

    def _validate_references(
        self,
        transactions: list[GBMTransactionInput],
    ) -> None:
        account_ids = {transaction.account_id for transaction in transactions}
        asset_ids = {transaction.asset_id for transaction in transactions}

        existing_account_ids = set(
            self.db.scalars(
                select(Account.id).where(Account.id.in_(account_ids))
            ).all()
        )

        for account_id in account_ids:
            if account_id not in existing_account_ids:
                raise ValueError(f"Account {account_id} not found")

        existing_asset_ids = set(
            self.db.scalars(
                select(Asset.id).where(Asset.id.in_(asset_ids))
            ).all()
        )

        for asset_id in asset_ids:
            if asset_id not in existing_asset_ids:
                raise ValueError(f"Asset {asset_id} not found")
