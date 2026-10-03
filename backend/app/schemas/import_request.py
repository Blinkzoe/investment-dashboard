from pydantic import BaseModel, Field

from app.schemas.import_transaction import NormalizedTransaction


class ImportTransactionsRequest(BaseModel):
    source: str = Field(min_length=1, max_length=50)
    import_type: str = Field(min_length=1, max_length=50)

    filename: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None

    transactions: list[NormalizedTransaction]
