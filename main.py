from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import SessionLocal
from models import User, Transaction
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 JWT CONFIG
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    return SessionLocal()


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------- AUTH ----------------

@app.post("/register")
def register(username: str, password: str):
    db = get_db()

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(username=username, password=hash_password(password))
    db.add(user)
    db.commit()

    return {"message": "User registered"}


@app.post("/login")
def login(username: str, password: str):
    db = get_db()

    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": username})

    return {"access_token": token, "token_type": "bearer"}


# ---------------- BALANCE ----------------

@app.get("/balance")
def check_balance(current_user: str = Depends(get_current_user)):
    db = get_db()

    user = db.query(User).filter(User.username == current_user).first()

    return {
        "username": current_user,
        "balance": user.balance
    }


@app.post("/deposit")
def deposit(amount: float, current_user: str = Depends(get_current_user)):
    db = get_db()

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    user = db.query(User).filter(User.username == current_user).first()

    user.balance += amount
    db.commit()

    return {"balance": user.balance}


# ---------------- TRANSFER ----------------

@app.post("/transfer")
def transfer(receiver: str, amount: float, current_user: str = Depends(get_current_user)):
    db = get_db()

    sender_user = db.query(User).filter(User.username == current_user).first()
    receiver_user = db.query(User).filter(User.username == receiver).first()

    if not receiver_user:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if current_user == receiver:
        raise HTTPException(status_code=400, detail="Cannot send to yourself")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    if sender_user.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

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

    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed")


# ---------------- TRANSACTIONS ----------------

@app.get("/transactions")
def get_transactions(current_user: str = Depends(get_current_user)):
    db = get_db()

    user = db.query(User).filter(User.username == current_user).first()

    txns = db.query(Transaction).filter(
        (Transaction.sender_id == user.id) |
        (Transaction.receiver_id == user.id)
    ).all()

    return txns