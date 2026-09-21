import sys
from pathlib import Path
import uuid

# Add project root to Python path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_is_running():
    response = client.get("/docs")

    assert response.status_code == 200

def test_balance_requires_authentication():
    response = client.get("/balance")

    assert response.status_code == 401

def test_login_with_invalid_password():
    response = client.post(
        "/login",
        data={
            "username": "nonexistent_user",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

def test_balance_with_invalid_token():
    response = client.get(
        "/balance",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401

def test_nonexistent_endpoint():
    response = client.get("/does-not-exist")

    assert response.status_code == 404

def test_transactions_requires_authentication():
    response = client.get("/transactions")

    assert response.status_code == 401

def test_register_with_missing_username():
    response = client.post(
        "/register",
        json={
            "password": "testpassword"
        }
    )

    assert response.status_code == 422

def test_login_with_missing_password():
    response = client.post(
        "/login",
        data={
            "username": "testuser"
        }
    )

    assert response.status_code == 422


def test_successful_login():
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

def test_authenticated_balance_access():
    username = f"balanceuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"

    # Register user
    register_response = client.post(
        "/register",
        params={
            "username": username,
            "password": password
        }
    )

    assert register_response.status_code in [200, 201]

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Access balance using JWT
    balance_response = client.get(
        "/balance",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert balance_response.status_code == 200
    assert "balance" in balance_response.json()

def test_authenticated_deposit():
    username = f"deposituser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"

    # Register
    register_response = client.post(
        "/register",
        params={
            "username": username,
            "password": password
        }
    )

    assert register_response.status_code in [200, 201]

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Deposit
    deposit_response = client.post(
        "/deposit",
        params={"amount": 100},
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert deposit_response.status_code == 200
    assert deposit_response.json()["balance"] == 100

def test_authenticated_transactions():
    username = f"historyuser_{uuid.uuid4().hex[:8]}"
    password = "TestPassword123!"

    # Register
    register_response = client.post(
        "/register",
        params={
            "username": username,
            "password": password
        }
    )

    assert register_response.status_code in [200, 201]

    # Login
    login_response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Access transaction history
    response = client.get(
        "/transactions",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)