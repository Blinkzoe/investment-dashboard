from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.account_snapshot import AccountSnapshotRepository
from app.schemas.account_snapshot_summary import AccountSnapshotMonthlySummaryRead


class AccountSnapshotSummaryService:
    def __init__(self, db: Session) -> None:
        self.repository = AccountSnapshotRepository(db)

    def get_monthly_summary(
        self,
        *,
        source: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[AccountSnapshotMonthlySummaryRead]:
        rows = self.repository.list_monthly_summary(
            source=source,
            start_date=start_date,
            end_date=end_date,
        )

        return [
            AccountSnapshotMonthlySummaryRead(
                month=row.month,
                total_value=row.total_value or 0,
                interest_value=row.interest_value or 0,
                contribution_value=row.contribution_value or 0,
                withdrawal_value=row.withdrawal_value or 0,
                account_count=row.account_count,
            )
            for row in rows
        ]
