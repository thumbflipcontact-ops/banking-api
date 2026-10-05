from typing import Literal

from sqlalchemy.orm import Session, joinedload

from models import User, Transaction


class TransactionServiceError(Exception):
    """Base exception for transaction-related errors."""


class TransactionUserNotFoundError(TransactionServiceError):
    pass

def get_user_transactions(
    current_user: str,
    limit: int,
    offset: int,
    transaction_type: Literal["deposit", "transfer"] | None,
    db: Session
):
    user = db.query(User).filter(
        User.username == current_user
    ).first()

    if not user:
        raise TransactionUserNotFoundError(
    "User not found"
)

    query = (
        db.query(Transaction)
        .options(
            joinedload(Transaction.sender),
            joinedload(Transaction.receiver)
        )
        .filter(
            (Transaction.sender_id == user.id) |
            (Transaction.receiver_id == user.id)
        )
    )

    if transaction_type == "deposit":
        query = query.filter(
            Transaction.sender_id.is_(None)
        )

    elif transaction_type == "transfer":
        query = query.filter(
            Transaction.sender_id.isnot(None)
        )

    txns = (
        query
        .order_by(Transaction.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": txn.id,
            "sender_id": txn.sender_id,
            "receiver_id": txn.receiver_id,
            "sender_username": (
                txn.sender.username
                if txn.sender
                else None
            ),
            "receiver_username": txn.receiver.username,
            "amount": txn.amount,
            "timestamp": txn.timestamp
        }
        for txn in txns
    ]