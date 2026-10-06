from sqlalchemy.orm import Session

from app.repositories.account import AccountRepository
from app.schemas.account_summary import AccountSummaryRead
from app.services.reconciliation import ReconciliationService


class AccountSummaryService:
    def __init__(self, db: Session) -> None:
        self.account_repository = AccountRepository(db)
        self.reconciliation_service = ReconciliationService(db)

    def get_summary(
        self,
        *,
        account_id: int,
        source: str | None = None,
    ) -> AccountSummaryRead | None:
        account = self.account_repository.get_by_id(account_id)

        if account is None:
            return None

        try:
            reconciliation = self.reconciliation_service.reconcile_account(
                account_id=account_id,
                source=source,
            )
        except ValueError:
            return AccountSummaryRead(
                account_id=account.id,
                institution=account.institution,
                name=account.name,
                account_type=account.account_type,
                base_currency=account.base_currency,
                snapshot_at=None,
                official_value=None,
                positions_value=None,
                difference=None,
                currency=None,
                reconciliation_status=None,
            )

        return AccountSummaryRead(
            account_id=account.id,
            institution=account.institution,
            name=account.name,
            account_type=account.account_type,
            base_currency=account.base_currency,
            snapshot_at=reconciliation.snapshot_at,
            official_value=reconciliation.official_value,
            positions_value=reconciliation.positions_value,
            difference=reconciliation.difference,
            currency=reconciliation.currency,
            reconciliation_status=reconciliation.status,
        )
