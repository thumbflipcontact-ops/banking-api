from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import TransferRequest, TransferResponse

from services.transfer_service import (
    transfer_money,
    SenderNotFoundError,
    ReceiverNotFoundError,
    SelfTransferError,
    InvalidTransferAmountError,
    InsufficientFundsError
)

from dependencies import get_db, get_current_user


router = APIRouter()


@router.post(
    "/transfer",
    response_model=TransferResponse
)
def transfer(
    request: TransferRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return transfer_money(
            receiver=request.receiver,
            amount=request.amount,
            current_user=current_user,
            db=db
        )

    except SenderNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ReceiverNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except SelfTransferError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except InvalidTransferAmountError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except InsufficientFundsError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )