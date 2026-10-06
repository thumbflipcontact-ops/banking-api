from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from schemas import TransactionResponse

from services.transaction_service import (
    get_user_transactions,
    TransactionUserNotFoundError
)

from dependencies import get_db, get_current_user


router = APIRouter()


@router.get(
    "/transactions",
    response_model=list[TransactionResponse]
)
def transactions(
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    offset: int = Query(
        default=0,
        ge=0
    ),
    transaction_type: Literal[
        "deposit",
        "transfer"
    ] | None = Query(
        default=None
    ),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return get_user_transactions(
            current_user=current_user,
            limit=limit,
            offset=offset,
            transaction_type=transaction_type,
            db=db
        )

    except TransactionUserNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )