from datetime import date
from decimal import Decimal

import pytest

from app.adapters.gbm.schemas import GBMTransactionInput
from app.services.gbm_import_service import GBMImportService


def make_transaction(
    *,
    account_id: int,
    asset_id: int,
    external_id: str = "TEST-VALIDATION-001",
) -> GBMTransactionInput:
    return GBMTransactionInput(
        external_id=external_id,
        account_id=account_id,
        asset_id=asset_id,
        transaction_type="BUY",
        status="FILLED",
        quantity=Decimal("1"),
        unit_price=Decimal("100"),
        gross_amount=Decimal("100"),
        commission=Decimal("1"),
        taxes=Decimal("0"),
        other_fees=Decimal("0"),
        total_amount=Decimal("101"),
        currency="MXN",
        trade_date=date(2026, 10, 3),
    )


def test_gbm_import_rejects_unknown_account(db_session):
    service = GBMImportService(db_session)

    transaction = make_transaction(
        account_id=999999,
        asset_id=1,
    )

    with pytest.raises(ValueError, match="Account 999999 not found"):
        service.import_transactions(
            transactions=[transaction],
            import_type="VALIDATION_TEST",
        )


def test_gbm_import_rejects_unknown_asset(db_session):
    service = GBMImportService(db_session)

    transaction = make_transaction(
        account_id=1,
        asset_id=999999,
    )

    with pytest.raises(ValueError, match="Asset 999999 not found"):
        service.import_transactions(
            transactions=[transaction],
            import_type="VALIDATION_TEST",
        )


def test_gbm_import_rejects_batch_when_any_reference_is_invalid(db_session):
    service = GBMImportService(db_session)

    valid_transaction = make_transaction(
        account_id=1,
        asset_id=1,
        external_id="TEST-ATOMIC-001",
    )

    invalid_transaction = make_transaction(
        account_id=1,
        asset_id=999999,
        external_id="TEST-ATOMIC-002",
    )

    with pytest.raises(ValueError, match="Asset 999999 not found"):
        service.import_transactions(
            transactions=[valid_transaction, invalid_transaction],
            import_type="ATOMICITY_TEST",
        )

    from sqlalchemy import select

    from app.models.import_batch import ImportBatch
    from app.models.transaction import Transaction

    transactions = list(
        db_session.scalars(
            select(Transaction).where(
                Transaction.external_id.in_(
                    ["TEST-ATOMIC-001", "TEST-ATOMIC-002"]
                )
            )
        ).all()
    )

    batches = list(
        db_session.scalars(
            select(ImportBatch).where(
                ImportBatch.import_type == "ATOMICITY_TEST"
            )
        ).all()
    )

    assert transactions == []
    assert batches == []
