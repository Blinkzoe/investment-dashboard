from pydantic import BaseModel


class ImportResult(BaseModel):
    import_batch_id: int
    received: int
    imported: int
    skipped_duplicates: int
