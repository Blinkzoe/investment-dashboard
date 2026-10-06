from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PositionReconstructionCreate(BaseModel):
    account_id: int
    snapshot_at: datetime


class PositionReconstructionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    snapshot_at: datetime
    positions_created: int
