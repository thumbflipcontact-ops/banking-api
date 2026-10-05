import sys
from pathlib import Path
import uuid

# Add project root to Python path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)


def test_api_is_running(client):
    response = client.get("/docs")

    assert response.status_code == 200


def test_balance_requires_authentication(client):
    response = client.get("/balance")

    assert response.status_code == 401


def test_login_with_invalid_password(client):
    response = client.post(
        "/login",
        data={
            "username": "nonexistent_user",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_balance_with_invalid_token(client):
    response = client.get(
        "/balance",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401


def test_nonexistent_endpoint(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404


def test_transactions_requires_authentication(client):
    response = client.get("/transactions")

    assert response.status_code == 401


def test_register_with_missing_username(client):
    response = client.post(
        "/register",
        json={
            "password": "testpassword"
        }
    )

    assert response.status_code == 422


def test_login_with_missing_password(client):
    response = client.post(
        "/login",
        data={
            "username": "testuser"
        }
    )

    assert response.status_code == 422


def test_successful_login(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"

    # Register a new user
    register_response = client.post(
        "/register",
        params={
            "username": username,
            "password": password
        }
    )

    assert register_response.status_code in [200, 201]

    # Login with the new user's credentials
    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"


def test_authenticated_balance_access(authenticated_client):
    client = authenticated_client["client"]

    response = client.get("/balance")

    assert response.status_code == 200
    assert "balance" in response.json()

def test_authenticated_deposit(authenticated_client):
    client = authenticated_client["client"]

    response = client.post(
        "/deposit",
        json={
            "amount": 100
        }
    )

    assert response.status_code == 200
    assert response.json()["balance"] == 100


def test_authenticated_transactions(authenticated_client):
    client = authenticated_client["client"]

    response = client.get("/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_new_user_has_zero_balance(authenticated_client):
    client = authenticated_client["client"]

    response = client.get("/balance")

    assert response.status_code == 200
    assert response.json()["balance"] == 0

def test_deposit_creates_transaction(authenticated_client):
    client = authenticated_client["client"]

    # Deposit money
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 100
        }
    )

    assert deposit_response.status_code == 200

    # Get transaction history
    transactions_response = client.get("/transactions")

    assert transactions_response.status_code == 200

    transactions = transactions_response.json()

    # A transaction should exist
    assert len(transactions) >= 1

    # Verify transaction amount
    assert transactions[-1]["amount"] == 100

def test_invalid_deposit_rejected(authenticated_client):
    client = authenticated_client["client"]

    # Try to deposit zero
    response = client.post(
        "/deposit",
        json={
            "amount": 0
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than"

def test_negative_deposit_rejected(authenticated_client):
    client = authenticated_client["client"]

    response = client.post(
        "/deposit",
        json={
            "amount": -50
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "greater_than"

def test_invalid_deposit_does_not_change_balance(authenticated_client):
    client = authenticated_client["client"]

    # Get initial balance
    initial_response = client.get("/balance")

    assert initial_response.status_code == 200

    initial_balance = initial_response.json()["balance"]

    # Attempt invalid deposit
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": -100
        }
    )

    assert deposit_response.status_code == 422

    # Check balance again
    final_response = client.get("/balance")

    assert final_response.status_code == 200

    final_balance = final_response.json()["balance"]

    assert final_balance == initial_balance

def test_multiple_deposits_accumulate(authenticated_client):
    client = authenticated_client["client"]

    first_deposit = client.post(
        "/deposit",
        json={"amount": 100}
    )

    assert first_deposit.status_code == 200
    assert first_deposit.json()["balance"] == 100

    second_deposit = client.post(
        "/deposit",
        json={"amount": 50}
    )

    assert second_deposit.status_code == 200
    assert second_deposit.json()["balance"] == 150

    # Verify persisted balance
    balance_response = client.get("/balance")

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 150

def test_successful_transfer(authenticated_client):
    client = authenticated_client["client"]
    sender_token = authenticated_client["token"]
    receiver_username = f"receiver_{uuid.uuid4().hex[:8]}"
    receiver_password = "TestPassword123!"

    # Register receiver
    register_response = client.post(
        "/register",
        params={
            "username": receiver_username,
            "password": receiver_password
        }
    )

    assert register_response.status_code in [200, 201]

    # Deposit money into sender account
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {sender_token}"
        }
    )

    assert deposit_response.status_code == 200
    assert deposit_response.json()["balance"] == 100

    # Transfer money to receiver
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": receiver_username,
            "amount": 40
        },
        headers={
            "Authorization": f"Bearer {sender_token}"
        }
    )

    assert transfer_response.status_code == 200
    assert transfer_response.json()["message"] == "Transfer successful"

    # Login as receiver
    receiver_login = client.post(
        "/login",
        data={
            "username": receiver_username,
            "password": receiver_password
        }
    )

    assert receiver_login.status_code == 200

    receiver_token = receiver_login.json()["access_token"]

    # Check sender balance
    sender_balance = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {sender_token}"
        }
    )

    assert sender_balance.status_code == 200
    assert sender_balance.json()["balance"] == 60

    # Check receiver balance
    receiver_balance = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {receiver_token}"
        }
    )

    assert receiver_balance.status_code == 200
    assert receiver_balance.json()["balance"] == 40

def test_transfer_insufficient_balance(authenticated_client):
    client = authenticated_client["client"]
    sender_token = authenticated_client["token"]

    receiver_username = f"receiver_{uuid.uuid4().hex[:8]}"
    receiver_password = "TestPassword123!"

    # Register receiver
    register_response = client.post(
        "/register",
        params={
            "username": receiver_username,
            "password": receiver_password
        }
    )

    assert register_response.status_code in [200, 201]

    # Sender has only $50
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 50
        },
        headers={
            "Authorization": f"Bearer {sender_token}"
        }
    )

    assert deposit_response.status_code == 200
    assert deposit_response.json()["balance"] == 50

    # Try to transfer $100
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": receiver_username,
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {sender_token}"
        }
    )

    assert transfer_response.status_code == 400
    assert transfer_response.json()["detail"] == "Insufficient balance"

    # Verify sender balance did not change
    balance_response = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {sender_token}"
        }
    )

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 50

def test_transfer_to_self_rejected(authenticated_client):
    client = authenticated_client["client"]
    username = authenticated_client["username"]
    token = authenticated_client["token"]

    # Deposit money first
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert deposit_response.status_code == 200

    # Try to transfer to yourself
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": username,
            "amount": 50
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert transfer_response.status_code == 400
    assert transfer_response.json()["detail"] == "Cannot send to yourself"

    # Verify balance did not change
    balance_response = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 100

def test_invalid_transfer_amount_rejected(authenticated_client):
    client = authenticated_client["client"]
    token = authenticated_client["token"]

    receiver_username = f"receiver_{uuid.uuid4().hex[:8]}"

    # Register receiver
    register_response = client.post(
        "/register",
        params={
            "username": receiver_username,
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code in [200, 201]

    # Deposit money into sender account
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert deposit_response.status_code == 200

    # Try to transfer zero
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": receiver_username,
            "amount": 0
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert transfer_response.status_code == 400
    assert transfer_response.json()["detail"] == "Invalid amount"

    # Verify sender balance is unchanged
    balance_response = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 100

def test_negative_transfer_amount_rejected(authenticated_client):
    client = authenticated_client["client"]
    token = authenticated_client["token"]

    receiver_username = f"receiver_{uuid.uuid4().hex[:8]}"

    # Register receiver
    register_response = client.post(
        "/register",
        params={
            "username": receiver_username,
            "password": "TestPassword123!"
        }
    )

    assert register_response.status_code in [200, 201]

    # Deposit money into sender account
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert deposit_response.status_code == 200

    # Try to transfer a negative amount
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": receiver_username,
            "amount": -50
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert transfer_response.status_code == 400
    assert transfer_response.json()["detail"] == "Invalid amount"

    # Verify sender balance is unchanged
    balance_response = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 100

def test_transfer_to_nonexistent_receiver_rejected(authenticated_client):
    client = authenticated_client["client"]
    token = authenticated_client["token"]

    # Give sender some money
    deposit_response = client.post(
        "/deposit",
        json={
            "amount": 100
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert deposit_response.status_code == 200
    assert deposit_response.json()["balance"] == 100

    # Try to transfer to a user that doesn't exist
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": f"does_not_exist_{uuid.uuid4().hex[:8]}",
            "amount": 50
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert transfer_response.status_code == 404
    assert transfer_response.json()["detail"] == "Receiver not found"

    # Verify sender balance is unchanged
    balance_response = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 100

def test_transaction_includes_usernames(authenticated_client):
    client = authenticated_client["client"]
    username = authenticated_client["username"]
    token = authenticated_client["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create a deposit
    deposit_response = client.post(
    "/deposit",
    json={
        "amount": 100
    },
    headers=headers
)
    assert deposit_response.status_code == 200

    # Retrieve transaction history
    response = client.get(
        "/transactions",
        headers=headers
    )

    assert response.status_code == 200

    transactions = response.json()

    # Find the deposit transaction
    deposit = next(
        txn for txn in transactions
        if txn["amount"] == 100.0
        and txn["sender_id"] is None
    )

    assert deposit["sender_username"] is None
    assert deposit["receiver_username"] == username

def test_transfer_includes_usernames(authenticated_client):
    client = authenticated_client["client"]
    username = authenticated_client["username"]
    token = authenticated_client["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create a unique receiver account
    import uuid
    receiver_username = f"receiver_{uuid.uuid4().hex[:8]}"

    register_response = client.post(
    "/register",
    params={
        "username": receiver_username,
        "password": "ReceiverPass123!"
    }
)
    assert register_response.status_code == 200

    # Deposit funds into the sender's account
    deposit_response = client.post(
    "/deposit",
    json={
        "amount": 200
    },
    headers=headers
)
    assert deposit_response.status_code == 200

    # Transfer funds to the receiver
    transfer_response = client.post(
        f"/transfer?receiver={receiver_username}&amount=50",
        headers=headers
    )
    assert transfer_response.status_code == 200

    # Retrieve the sender's transaction history
    response = client.get(
        "/transactions",
        headers=headers
    )
    assert response.status_code == 200

    transactions = response.json()

    transfer = next(
        txn for txn in transactions
        if txn["sender_username"] == username
        and txn["receiver_username"] == receiver_username
        and txn["amount"] == 50.0
    )

    assert transfer["sender_id"] is not None
    assert transfer["receiver_id"] is not None

def test_transactions_filter_deposits(authenticated_client):
    client = authenticated_client["client"]
    token = authenticated_client["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create a deposit
    deposit_response = client.post(
    "/deposit",
    json={
        "amount": 50
    },
    headers=headers
)
    assert deposit_response.status_code == 200

    # Retrieve only deposits
    response = client.get(
        "/transactions?transaction_type=deposit",
        headers=headers
    )

    assert response.status_code == 200
    transactions = response.json()

    assert len(transactions) >= 1
    assert all(
        txn["sender_id"] is None
        for txn in transactions
    )

def test_transactions_filter_transfers(authenticated_client):
    import uuid

    client = authenticated_client["client"]
    username = authenticated_client["username"]
    token = authenticated_client["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Fund the sender
    deposit_response = client.post(
    "/deposit",
    json={
        "amount": 100
    },
    headers=headers
)
    assert deposit_response.status_code == 200

    # Create a receiver
    receiver_username = f"receiver_{uuid.uuid4().hex[:8]}"

    register_response = client.post(
        "/register",
        params={
            "username": receiver_username,
            "password": "ReceiverPass123!"
        }
    )
    assert register_response.status_code == 200

    # Transfer funds
    transfer_response = client.post(
        "/transfer",
        params={
            "receiver": receiver_username,
            "amount": 25
        },
        headers=headers
    )
    assert transfer_response.status_code == 200

    # Retrieve only transfers
    response = client.get(
        "/transactions?transaction_type=transfer",
        headers=headers
    )

    assert response.status_code == 200
    transactions = response.json()

    assert len(transactions) >= 1
    assert all(
        txn["sender_id"] is not None
        for txn in transactions
    )
    assert any(
        txn["sender_id"] is not None
        and txn["receiver_id"] is not None
        for txn in transactions
    )

def test_transactions_invalid_type(authenticated_client):
    client = authenticated_client["client"]
    token = authenticated_client["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(
        "/transactions?transaction_type=withdrawal",
        headers=headers
    )

    assert response.status_code == 422

