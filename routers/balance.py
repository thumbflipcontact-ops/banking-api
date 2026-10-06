from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import BalanceResponse

from services.balance_service import (
    get_user_balance,
    BalanceUserNotFoundError
)

from dependencies import get_db, get_current_user


router = APIRouter()


@router.get("/balance", response_model=BalanceResponse)
def check_balance(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return get_user_balance(
            current_user=current_user,
            db=db
        )

    except BalanceUserNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )