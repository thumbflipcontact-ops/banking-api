from sqlalchemy.orm import Session

from models import User
from services.auth_utils import (
    hash_password,
    verify_password,
    create_token
)


class AuthServiceError(Exception):
    """Base exception for authentication-related errors."""


class UserAlreadyExistsError(AuthServiceError):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


def register_user(
    username: str,
    password: str,
    db: Session
):
    existing = db.query(User).filter(
        User.username == username
    ).first()

    if existing:
        raise UserAlreadyExistsError(
            "User already exists"
        )

    user = User(
        username=username,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return {
        "message": "User registered"
    }


def login_user(
    username: str,
    password: str,
    db: Session
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(
        password,
        user.password
    ):
        raise InvalidCredentialsError(
            "Invalid credentials"
        )

    token = create_token({
        "sub": username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }