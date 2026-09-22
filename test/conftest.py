import sys
from pathlib import Path
import uuid

# Add project root to Python path
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
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

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return {
        "client": client,
        "username": username,
        "password": password,
        "token": token
    }