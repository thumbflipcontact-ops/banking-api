from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database import SessionLocal

from services.auth_service import (
    register_user,
    login_user,
    UserAlreadyExistsError,
    InvalidCredentialsError
)


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
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


@router.post("/login")
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