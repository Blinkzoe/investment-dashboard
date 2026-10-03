from decimal import Decimal

from app.adapters.gbm.json_parser import GBMJsonParser
from app.adapters.gbm.parser import GBMParser


def test_json_parser_implements_gbm_parser_contract():
    parser = GBMJsonParser()

    assert isinstance(parser, GBMParser)


def test_json_parser_parses_transactions():
    payload = """
    [
      {
        "external_id": "TEST-PARSER-001",
        "account_id": 1,
        "asset_id": 7,
        "transaction_type": "BUY",
        "status": "FILLED",
        "quantity": "10",
        "unit_price": "29.95",
        "gross_amount": "299.50",
        "commission": "0.75",
        "taxes": "0",
        "total_amount": "300.25",
        "currency": "MXN",
        "trade_date": "2026-10-02"
      }
    ]
    """

    result = GBMJsonParser().parse(payload)

    assert len(result) == 1

    transaction = result[0]

    assert transaction.external_id == "TEST-PARSER-001"
    assert transaction.account_id == 1
    assert transaction.asset_id == 7
    assert transaction.transaction_type == "BUY"
    assert transaction.quantity == Decimal("10")
    assert transaction.unit_price == Decimal("29.95")
    assert transaction.gross_amount == Decimal("299.50")
    assert transaction.commission == Decimal("0.75")
    assert transaction.total_amount == Decimal("300.25")
    assert transaction.currency == "MXN"


def test_json_parser_rejects_non_list_payload():
    payload = """
    {
      "external_id": "INVALID"
    }
    """

    try:
        GBMJsonParser().parse(payload)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "GBM JSON payload must be a list"
