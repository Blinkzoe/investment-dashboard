from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.adapters.gbm.schemas import GBMTransactionInput
from app.models.account import Account
from app.models.asset import Asset
from app.models.import_batch import ImportBatch
from app.models.transaction import Transaction
from app.services.gbm_import_service import GBMImportService


def make_transaction(
    account_id: int,
    asset_id: int,
    external_id: str,
) -> GBMTransactionInput:
    return GBMTransactionInput(
        external_id=external_id,
        account_id=account_id,
        asset_id=asset_id,
        transaction_type="BUY",
        status="FILLED",
        quantity=Decimal("10"),
        unit_price=Decimal("29.95"),
        gross_amount=Decimal("299.50"),
        commission=Decimal("0.75"),
        taxes=Decimal("0"),
        other_fees=Decimal("0"),
        total_amount=Decimal("300.25"),
        currency="MXN",
        trade_date=date(2026, 10, 2),
    )


def test_gbm_import_service_imports_transactions(db_session):
    account = db_session.scalars(
        select(Account).where(Account.institution == "TEST")
    ).one()

    asset = db_session.scalars(
        select(Asset).where(Asset.symbol == "TEST-ASSET")
    ).one()

    service = GBMImportService(db_session)

    result = service.import_transactions(
        transactions=[
            make_transaction(account.id, asset.id, "TEST-SERVICE-001"),
            make_transaction(account.id, asset.id, "TEST-SERVICE-002"),
        ],
        import_type="TEST",
        filename="test_gbm.json",
    )

    assert result.received == 2
    assert result.imported == 2
    assert result.skipped_duplicates == 0
    assert result.import_batch_id is not None

    batch = db_session.get(ImportBatch, result.import_batch_id)

    assert batch is not None
    assert batch.source == "GBM"
    assert batch.import_type == "TEST"
    assert batch.status == "COMPLETED"

    transactions = db_session.scalars(
        select(Transaction).where(
            Transaction.import_batch_id == result.import_batch_id
        )
    ).all()

    assert len(transactions) == 2
    assert {item.external_id for item in transactions} == {
        "TEST-SERVICE-001",
        "TEST-SERVICE-002",
    }
    assert all(item.source == "GBM" for item in transactions)
    assert all(item.account_id == account.id for item in transactions)
    assert all(item.asset_id == asset.id for item in transactions)


def test_gbm_import_service_skips_duplicate_transactions(db_session):
    account = db_session.scalars(
        select(Account).where(Account.institution == "TEST")
    ).one()

    asset = db_session.scalars(
        select(Asset).where(Asset.symbol == "TEST-ASSET")
    ).one()

    service = GBMImportService(db_session)

    transactions = [
        make_transaction(account.id, asset.id, "TEST-DUP-001"),
        make_transaction(account.id, asset.id, "TEST-DUP-002"),
    ]

    first_result = service.import_transactions(
        transactions=transactions,
        import_type="TEST",
        filename="test_gbm.json",
    )

    assert first_result.received == 2
    assert first_result.imported == 2
    assert first_result.skipped_duplicates == 0

    second_result = service.import_transactions(
        transactions=transactions,
        import_type="TEST",
        filename="test_gbm.json",
    )

    assert second_result.received == 2
    assert second_result.imported == 0
    assert second_result.skipped_duplicates == 2

    stored_transactions = db_session.scalars(
        select(Transaction).where(
            Transaction.external_id.in_(
                ["TEST-DUP-001", "TEST-DUP-002"]
            )
        )
    ).all()

    assert len(stored_transactions) == 2


def test_gbm_import_service_skips_duplicate_external_ids_within_same_payload(
    db_session,
):
    account = db_session.scalars(
        select(Account).where(Account.institution == "TEST")
    ).one()

    asset = db_session.scalars(
        select(Asset).where(Asset.symbol == "TEST-ASSET")
    ).one()

    service = GBMImportService(db_session)

    transactions = [
        make_transaction(
            account.id,
            asset.id,
            "TEST-INTERNAL-DUP-001",
        ),
        make_transaction(
            account.id,
            asset.id,
            "TEST-INTERNAL-DUP-001",
        ),
    ]

    result = service.import_transactions(
        transactions=transactions,
        import_type="TEST_INTERNAL_DUPLICATE",
        filename="test_gbm.json",
    )

    assert result.received == 2
    assert result.imported == 1
    assert result.skipped_duplicates == 1

    stored_transactions = db_session.scalars(
        select(Transaction).where(
            Transaction.external_id == "TEST-INTERNAL-DUP-001"
        )
    ).all()

    assert len(stored_transactions) == 1
