import pytest
from flask.testing import FlaskClient


@pytest.fixture
def client() -> FlaskClient:
    from run import app

    app.config["TESTING"] = True
    return app.test_client()


# ---- Functional Tests ---- #


def test_get_auth_token(client):
    data = {"uid": "admin", "pass": "1243"}
    response = client.post("/login", json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "token" in json_data
    return json_data["token"]


def test_user_summary(client):
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/summary", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "average_age" in data
    assert "total_cities" in data
    assert "total_companies" in data


def test_fetch_users(client):
    response = client.get("/api/users?page=1&limit=5")
    assert response.status_code == 200


def test_create_user(client):
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    data = [
        {
            "first_name": "Test",
            "last_name": "Test",
            "email": "test@example.com",
            "age": 999,
            "city": "Test City",
            "state": "Test State",
            "zip": "9999",
            "company_name": "Test Company",
            "web": "http://test.com",
        }
    ]
    response = client.post("/api/users", json=data, headers=headers)
    assert response.status_code == 200


def test_fetch_user_by_id(client):
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/111", headers=headers)
    assert response.status_code == 200


def test_delete_user(client):
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/users/111", headers=headers)
    assert response.status_code == 200


def test_update_user(client):
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "first_name": "Test2",
        "last_name": "Test2",
        "email": "test2@example.com",
        "age": 999,
        "city": "Test City 2",
        "state": "Test State 2",
        "zip": "9999",
        "company_name": "Test Company 2",
        "web": "http://test2.com",
    }
    response = client.put("/api/users/111", json=data, headers=headers)
    assert response.status_code == 200


def test_patch_user(client):
    token = test_get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    data = {"city": "Test City 3"}
    response = client.patch("/api/users/111", json=data, headers=headers)
    assert response.status_code == 200
