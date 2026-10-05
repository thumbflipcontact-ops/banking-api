from sqlalchemy.orm import Session

from models import User, Transaction


class DepositError(Exception):
    """Base exception for deposit-related errors."""


class DepositUserNotFoundError(DepositError):
    pass

class InvalidDepositAmountError(DepositError):
    pass


def deposit_money(
    amount: float,
    current_user: str,
    db: Session
):
    if amount <= 0:
        raise InvalidDepositAmountError(
            "Invalid amount"
        )

    try:
        # Lock the user row so concurrent deposits
        # cannot update the same balance unsafely.

        user = (
            db.query(User)
            .filter(User.username == current_user)
            .with_for_update()
            .first()
        )

        if not user:
            raise DepositUserNotFoundError(
                "User not found"
            )

        user.balance += amount

        transaction = Transaction(
            sender_id=None,
            receiver_id=user.id,
            amount=amount
        )

        db.add(transaction)
        db.commit()

        return {
            "balance": user.balance
        }

    except DepositError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise