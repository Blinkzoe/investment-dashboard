from datetime import date
from decimal import Decimal

import pytest

from app.models.transaction import Transaction
from app.services.position_reconstruction import PositionReconstructionService


def make_transaction(
    *,
    account_id: int = 1,
    asset_id: int = 1,
    transaction_type: str = "BUY",
    quantity: str = "10",
    trade_date: date = date(2026, 1, 1),
    status: str = "FILLED",
    transaction_id: int = 1,
) -> Transaction:
    return Transaction(
        id=transaction_id,
        account_id=account_id,
        asset_id=asset_id,
        transaction_type=transaction_type,
        status=status,
        quantity=Decimal(quantity),
        currency="MXN",
        trade_date=trade_date,
        source="GBM",
    )


def test_reconstructs_buy_quantity():
    transactions = [
        make_transaction(quantity="10", transaction_id=1),
        make_transaction(
            quantity="5.5",
            trade_date=date(2026, 2, 1),
            transaction_id=2,
        ),
    ]

    result = PositionReconstructionService().reconstruct(transactions)

    assert result == {(1, 1): Decimal("15.5")}


def test_ignores_non_completed_transactions():
    transactions = [
        make_transaction(quantity="10", transaction_id=1),
        make_transaction(
            quantity="20",
            status="PENDING",
            transaction_id=2,
        ),
    ]

    result = PositionReconstructionService().reconstruct(transactions)

    assert result == {(1, 1): Decimal("10")}


def test_reconstructs_multiple_accounts_and_assets():
    transactions = [
        make_transaction(
            account_id=1,
            asset_id=1,
            quantity="10",
            transaction_id=1,
        ),
        make_transaction(
            account_id=1,
            asset_id=2,
            quantity="20",
            transaction_id=2,
        ),
        make_transaction(
            account_id=2,
            asset_id=1,
            quantity="30",
            transaction_id=3,
        ),
    ]

    result = PositionReconstructionService().reconstruct(transactions)

    assert result == {
        (1, 1): Decimal("10"),
        (1, 2): Decimal("20"),
        (2, 1): Decimal("30"),
    }


def test_rejects_unsupported_transaction_type():
    transactions = [
        make_transaction(
            transaction_type="SELL",
            quantity="10",
            transaction_id=1,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Unsupported transaction type: SELL",
    ):
        PositionReconstructionService().reconstruct(transactions)


def test_rejects_missing_quantity():
    transaction = make_transaction(transaction_id=1)
    transaction.quantity = None

    with pytest.raises(
        ValueError,
        match="Transaction 1 has no quantity",
    ):
        PositionReconstructionService().reconstruct([transaction])
