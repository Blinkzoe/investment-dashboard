import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_list_accounts(client) -> None:
    response = client.get("/api/v1/accounts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_account_not_found(client) -> None:
    response = client.get("/api/v1/accounts/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"


def test_create_account(client) -> None:
    payload = {
        "institution": "TEST-API",
        "name": "Cuenta API",
        "account_type": "BROKERAGE",
        "base_currency": "MXN",
        "external_id": "TEST-API-ACCOUNT-001",
    }

    response = client.post("/api/v1/accounts", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["institution"] == "TEST-API"
    assert data["name"] == "Cuenta API"
    assert data["account_type"] == "BROKERAGE"
    assert data["base_currency"] == "MXN"
    assert data["external_id"] == "TEST-API-ACCOUNT-001"


def test_get_account(client) -> None:
    create_response = client.post(
        "/api/v1/accounts",
        json={
            "institution": "TEST-API",
            "name": "Cuenta GET",
            "account_type": "BROKERAGE",
            "base_currency": "MXN",
            "external_id": "TEST-API-ACCOUNT-GET-001",
        },
    )

    assert create_response.status_code == 201

    account_id = create_response.json()["id"]

    response = client.get(f"/api/v1/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["id"] == account_id
    assert response.json()["name"] == "Cuenta GET"
