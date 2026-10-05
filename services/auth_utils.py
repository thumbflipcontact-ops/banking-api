from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from config import (
    SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(
        plain,
        hashed
    )


def create_token(data: dict):
    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )