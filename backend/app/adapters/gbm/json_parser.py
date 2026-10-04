import json
from datetime import date
from decimal import Decimal

from app.adapters.gbm.parser import GBMParser
from app.adapters.gbm.schemas import GBMTransactionInput


class GBMJsonParser(GBMParser):
    def parse(self, payload: str) -> list[GBMTransactionInput]:
        data = json.loads(payload)

        if not isinstance(data, list):
            raise ValueError("GBM JSON payload must be a list")

        transactions: list[GBMTransactionInput] = []

        for item in data:
            transactions.append(
                GBMTransactionInput(
                    external_id=str(item["external_id"]),
                    account_id=int(item["account_id"]),
                    asset_id=int(item["asset_id"]),
                    transaction_type=str(item["transaction_type"]),
                    status=str(item.get("status", "FILLED")),
                    quantity=Decimal(str(item["quantity"])),
                    unit_price=Decimal(str(item["unit_price"])),
                    gross_amount=Decimal(str(item["gross_amount"])),
                    commission=Decimal(str(item.get("commission", "0"))),
                    taxes=Decimal(str(item.get("taxes", "0"))),
                    other_fees=Decimal(str(item.get("other_fees", "0"))),
                    total_amount=Decimal(str(item["total_amount"])),
                    currency=str(item["currency"]),
                    trade_date=date.fromisoformat(item["trade_date"]),
                    settlement_date=(
                        date.fromisoformat(item["settlement_date"])
                        if item.get("settlement_date")
                        else None
                    ),
                    notes=item.get("notes"),
                    metadata_json=item.get("metadata_json"),
                )
            )

        return transactions
