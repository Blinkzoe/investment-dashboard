from datetime import date
from decimal import Decimal

from app.adapters.gbm.adapter import GBMAdapter
from app.adapters.gbm.schemas import GBMTransactionInput


def make_transaction(
    external_id: str = "TEST-ADAPTER-001",
) -> GBMTransactionInput:
    return GBMTransactionInput(
        external_id=external_id,
        account_id=1,
        asset_id=7,
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


def test_adapter_normalizes_transaction():
    transaction = make_transaction()

    result = GBMAdapter().normalize_transaction(transaction)

    assert result.account_id == 1
    assert result.asset_id == 7
    assert result.transaction_type == "BUY"
    assert result.status == "FILLED"

    assert result.quantity == Decimal("10")
    assert result.unit_price == Decimal("29.95")
    assert result.gross_amount == Decimal("299.50")
    assert result.commission == Decimal("0.75")
    assert result.taxes == Decimal("0")
    assert result.other_fees == Decimal("0")
    assert result.total_amount == Decimal("300.25")

    assert result.currency == "MXN"
    assert result.trade_date == date(2026, 10, 2)

    assert result.source == "GBM"
    assert result.external_id == "TEST-ADAPTER-001"


def test_adapter_normalizes_multiple_transactions():
    transactions = [
        make_transaction("TEST-ADAPTER-001"),
        make_transaction("TEST-ADAPTER-002"),
    ]

    result = GBMAdapter().normalize_transactions(transactions)

    assert len(result) == 2
    assert [item.external_id for item in result] == [
        "TEST-ADAPTER-001",
        "TEST-ADAPTER-002",
    ]

    assert all(item.source == "GBM" for item in result)
