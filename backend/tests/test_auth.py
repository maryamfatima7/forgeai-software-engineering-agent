from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_auth_session_protects_workspace_api() -> None:
    client = TestClient(app)
    email = f"{uuid4().hex}@example.com"
    payload = {"files": [{"path": "main.py", "content": "def ok():\n    return True\n"}]}

    assert client.post("/api/v1/code/analyze", json=payload).status_code == 401
    registered = client.post("/api/auth/register", json={"full_name": "ForgeAI Tester", "email": email, "password": "correct-horse-battery", "confirm_password": "correct-horse-battery"})
    assert registered.status_code == 201
    assert client.get("/api/auth/me").json()["user"]["email"] == email
    assert client.post("/api/v1/code/analyze", json=payload).status_code == 200
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/v1/code/analyze", json=payload).status_code == 401


def test_login_rejects_invalid_credentials_without_account_enumeration() -> None:
    client = TestClient(app)
    response = client.post("/api/auth/login", json={"email": "unknown@example.com", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid email or password."