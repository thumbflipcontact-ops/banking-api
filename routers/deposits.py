from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import DepositRequest, DepositResponse

from services.deposit_service import (
    deposit_money,
    DepositUserNotFoundError,
    InvalidDepositAmountError
)

from dependencies import get_db, get_current_user


router = APIRouter()


@router.post("/deposit", response_model=DepositResponse)
def deposit(
    request: DepositRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return deposit_money(
            amount=request.amount,
            current_user=current_user,
            db=db
        )

    except DepositUserNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except InvalidDepositAmountError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )