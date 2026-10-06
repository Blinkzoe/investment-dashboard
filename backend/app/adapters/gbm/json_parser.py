import json

from app.adapters.gbm.parser import GBMParser
from app.adapters.gbm.schemas import GBMTransactionInput


class GBMJsonParser(GBMParser):
    def parse(self, payload: str) -> list[GBMTransactionInput]:
        data = json.loads(payload)

        if not isinstance(data, list):
            raise ValueError("GBM JSON payload must be a list")

        return [
            GBMTransactionInput.model_validate(item)
            for item in data
        ]
