import pytest
from flask.testing import FlaskClient


@pytest.fixture
def client() -> FlaskClient:
    """Creates a test client for the Flask app."""
    from run import app  # Ensure this imports your Flask app instance

    app.config["TESTING"] = True
    return app.test_client()


# ---- Functional Tests ---- #


def test_get_auth_token(client):
    """Tests the /login endpoint to get an auth token."""
    data = {"uid": "admin", "pass": "1243"}
    response = client.post("/login", json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "token" in json_data
    return json_data["token"]


def test_user_summary(client):
    """Tests retrieving user statistics."""
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/summary", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "average_age" in data
    assert "total_cities" in data
    assert "total_companies" in data


def test_fetch_users(client):
    """Tests fetching users with pagination and sorting."""
    response = client.get("/api/users?page=1&limit=5")
    assert response.status_code == 200


def test_create_user(client):
    """Tests creating a new user."""
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    data = [
        {
            "id": 111,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "company_name": "Example Inc.",
            "web": "http://example.com",
        }
    ]
    response = client.post("/api/users", json=data, headers=headers)
    assert response.status_code == 200


def test_fetch_user_by_id(client):
    """Tests retrieving a single user by ID."""
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/111", headers=headers)
    assert response.status_code == 200


def test_delete_user(client):
    """Tests deleting a user."""
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/users/111", headers=headers)
    assert response.status_code == 200


def test_update_user(client):
    """Tests updating a user with PUT."""
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "age": 28,
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105",
        "company_name": "TechCorp",
        "web": "http://techcorp.com",
    }
    response = client.put("/api/users/111", json=data, headers=headers)
    assert response.status_code == 200


def test_patch_user(client):
    """Tests partially updating a user with PATCH."""
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    data = {"city": "Los Angeles"}
    response = client.patch("/api/users/111", json=data, headers=headers)
    assert response.status_code == 200
