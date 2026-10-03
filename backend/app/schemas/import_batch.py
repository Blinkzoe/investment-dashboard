from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImportBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    import_type: str
    status: str
    filename: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
