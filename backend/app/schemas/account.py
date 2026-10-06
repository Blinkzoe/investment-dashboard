from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    institution: str
    name: str
    account_type: str
    base_currency: str
    external_id: str | None = None


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    institution: str
    name: str
    account_type: str
    base_currency: str
    external_id: str | None = None
