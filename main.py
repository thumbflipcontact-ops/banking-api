import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import SessionLocal
from models import User, Transaction
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception("Unexpected error occurred")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred"
        }
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT CONFIG
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------- DATABASE ----------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------- SECURITY ----------------

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
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
    existing = db.query(User).filter(
        User.username == username
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = User(
        username=username,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return {"message": "User registered"}


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token({
        "sub": form_data.username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ---------------- BALANCE ----------------

@app.get("/balance")
def check_balance(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "username": current_user,
        "balance": user.balance
    }


@app.post("/deposit")
def deposit(
    amount: float,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    user = db.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.balance += amount
    db.commit()

    logger.info(
        "Deposit completed: user_id=%s amount=%s",
        user.id,
        amount
    )

    return {"balance": user.balance}

# ---------------- TRANSFER ----------------

@app.post("/transfer")
def transfer(
    receiver: str,
    amount: float,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sender_user = db.query(User).filter(
        User.username == current_user
    ).first()

    receiver_user = db.query(User).filter(
        User.username == receiver
    ).first()

    if not sender_user:
        raise HTTPException(
            status_code=404,
            detail="Sender not found"
        )

    if not receiver_user:
        raise HTTPException(
            status_code=404,
            detail="Receiver not found"
        )

    if current_user == receiver:
        raise HTTPException(
            status_code=400,
            detail="Cannot send to yourself"
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    if sender_user.balance < amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    try:
        sender_user.balance -= amount
        receiver_user.balance += amount

        txn = Transaction(
            sender_id=sender_user.id,
            receiver_id=receiver_user.id,
            amount=amount
        )

        db.add(txn)
        db.commit()

        return {"message": "Transfer successful"}

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Transaction failed"
        )


# ---------------- TRANSACTIONS ----------------

@app.get("/transactions")
def get_transactions(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    txns = db.query(Transaction).filter(
        (Transaction.sender_id == user.id) |
        (Transaction.receiver_id == user.id)
    ).all()

    return txns