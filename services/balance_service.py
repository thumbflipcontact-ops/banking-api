from sqlalchemy.orm import Session

from models import User


class BalanceServiceError(Exception):
    """Base exception for balance-related errors."""


class BalanceUserNotFoundError(BalanceServiceError):
    pass


def get_user_balance(
    current_user: str,
    db: Session
):
    user = db.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise BalanceUserNotFoundError(
            "User not found"
        )

    return {
        "username": user.username,
        "balance": user.balance
    }