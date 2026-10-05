from pydantic import BaseModel, ConfigDict, Field


class BalanceResponse(BaseModel):
    username: str
    balance: float


class DepositRequest(BaseModel):
    amount: float = Field(
        gt=0
    )


class DepositResponse(BaseModel):
    balance: float


class TransferRequest(BaseModel):
    receiver: str
    amount: float = Field(
        gt=0
    )


class TransferResponse(BaseModel):
    message: str


class TransactionResponse(BaseModel):
    id: int
    sender_id: int | None
    receiver_id: int
    sender_username: str | None
    receiver_username: str
    amount: float
    timestamp: str

    model_config = ConfigDict(
        from_attributes=True
    )