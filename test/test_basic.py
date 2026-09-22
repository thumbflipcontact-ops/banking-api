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
        params={
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
        params={
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
        params={
            "amount": 0
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid amount"

def test_negative_deposit_rejected(authenticated_client):
    client = authenticated_client["client"]

    response = client.post(
        "/deposit",
        params={
            "amount": -50
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid amount"

def test_invalid_deposit_does_not_change_balance(authenticated_client):
    client = authenticated_client["client"]

    # Get initial balance
    initial_response = client.get("/balance")

    assert initial_response.status_code == 200

    initial_balance = initial_response.json()["balance"]

    # Attempt invalid deposit
    deposit_response = client.post(
        "/deposit",
        params={
            "amount": -100
        }
    )

    assert deposit_response.status_code == 400

    # Check balance again
    final_response = client.get("/balance")

    assert final_response.status_code == 200

    final_balance = final_response.json()["balance"]

    assert final_balance == initial_balance

def test_multiple_deposits_accumulate(authenticated_client):
    client = authenticated_client["client"]

    first_deposit = client.post(
        "/deposit",
        params={"amount": 100}
    )

    assert first_deposit.status_code == 200
    assert first_deposit.json()["balance"] == 100

    second_deposit = client.post(
        "/deposit",
        params={"amount": 50}
    )

    assert second_deposit.status_code == 200
    assert second_deposit.json()["balance"] == 150

    # Verify persisted balance
    balance_response = client.get("/balance")

    assert balance_response.status_code == 200
    assert balance_response.json()["balance"] == 150