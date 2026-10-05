from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Literal
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal, engine, Base
from models import User, Transaction
from jose import jwt, JWTError
from config import (
    SECRET_KEY,
    JWT_ALGORITHM
)
from schemas import (
    BalanceResponse,
    DepositRequest,
    DepositResponse,
    TransferRequest,
    TransferResponse,
    TransactionResponse
)

from services.transfer_service import (
    transfer_money,
    SenderNotFoundError,
    ReceiverNotFoundError,
    SelfTransferError,
    InvalidTransferAmountError,
    InsufficientFundsError
)

from services.deposit_service import (
    deposit_money,
    DepositUserNotFoundError,
    InvalidDepositAmountError
)

from services.transaction_service import (
    get_user_transactions,
    TransactionUserNotFoundError
)

from services.balance_service import (
    get_user_balance,
    BalanceUserNotFoundError
)

from services.auth_service import (
    register_user,
    login_user,
    UserAlreadyExistsError,
    InvalidCredentialsError
)

from config import (
    SECRET_KEY,
    JWT_ALGORITHM
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------- DATABASE ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- PASSWORD FUNCTIONS ----------------



# ---------------- JWT FUNCTIONS ----------------
def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

# ---------------- AUTH ----------------
@app.post("/register")
def register(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    try:
        return register_user(
            username=username,
            password=password,
            db=db
        )

    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        return login_user(
            username=form_data.username,
            password=form_data.password,
            db=db
        )

    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error)
        )

# ---------------- BALANCE ----------------

@app.get("/balance", response_model=BalanceResponse)
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

@app.post("/deposit", response_model=DepositResponse)
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

# ---------------- TRANSFER ----------------

@app.post("/transfer", response_model=TransferResponse)
def transfer(
    receiver: str,
    amount: float,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return transfer_money(
            receiver=receiver,
            amount=amount,
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


# ---------------- TRANSACTIONS ----------------

@app.get(
    "/transactions",
    response_model=list[TransactionResponse]
)
def get_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    transaction_type: Literal["deposit", "transfer"] | None = Query(
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