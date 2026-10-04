from sqlalchemy.orm import Session

from models import User, Transaction


class TransferError(Exception):
    """Base exception for transfer-related errors."""


class SenderNotFoundError(TransferError):
    pass


class ReceiverNotFoundError(TransferError):
    pass


class SelfTransferError(TransferError):
    pass


class InvalidTransferAmountError(TransferError):
    pass


class InsufficientFundsError(TransferError):
    pass


def transfer_money(
    receiver: str,
    amount: float,
    current_user: str,
    db: Session
):
    sender_user = db.query(User).filter(
        User.username == current_user
    ).first()

    receiver_user = db.query(User).filter(
        User.username == receiver
    ).first()

    if not sender_user:
        raise SenderNotFoundError(
            "Sender not found"
        )

    if not receiver_user:
        raise ReceiverNotFoundError(
            "Receiver not found"
        )

    if current_user == receiver:
        raise SelfTransferError(
            "Cannot send to yourself"
        )

    if amount <= 0:
        raise InvalidTransferAmountError(
            "Invalid amount"
        )

    try:
        # Lock both users in a consistent ID order.
        # This reduces the risk of deadlocks when
        # transfers happen in opposite directions.

        if sender_user.id < receiver_user.id:
            first_user_id = sender_user.id
            second_user_id = receiver_user.id
        else:
            first_user_id = receiver_user.id
            second_user_id = sender_user.id

        first_user = (
            db.query(User)
            .filter(User.id == first_user_id)
            .with_for_update()
            .one()
        )

        second_user = (
            db.query(User)
            .filter(User.id == second_user_id)
            .with_for_update()
            .one()
        )

        # Re-identify sender and receiver after acquiring locks.
        if first_user.id == sender_user.id:
            sender_user = first_user
            receiver_user = second_user
        else:
            receiver_user = first_user
            sender_user = second_user

        # Check the current balance AFTER acquiring the lock.
        if sender_user.balance < amount:
            raise InsufficientFundsError(
                "Insufficient balance"
            )

        # Update balances
        sender_user.balance -= amount
        receiver_user.balance += amount

        # Create transaction record
        txn = Transaction(
            sender_id=sender_user.id,
            receiver_id=receiver_user.id,
            amount=amount
        )

        db.add(txn)
        db.commit()

        return {
            "message": "Transfer successful"
        }

    except TransferError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise