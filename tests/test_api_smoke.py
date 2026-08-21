import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.async_db import get_neo4j_service
from app.main import app


class MockNeo4jService:
    async def write(self, fn, **kwargs):
        return None

    async def read(self, fn, **kwargs):
        return None


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_neo4j_service] = lambda: MockNeo4jService()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to Car App API!"


def test_reports_requires_auth(client: TestClient):
    response = client.get("/reports/")
    assert response.status_code == 401


def test_authenticated_api_flow(client: TestClient):
    suffix = uuid.uuid4().hex[:8]
    user = {
        "username": f"testuser_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "secret123",
    }

    signup = client.post("/auth/signup", json=user)
    assert signup.status_code == 201
    assert signup.json()["email"] == user["email"]

    login = client.post(
        "/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    profile = client.get("/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["username"] == user["username"]

    reports = client.get("/reports/?limit=5", headers=headers)
    assert reports.status_code == 200
    reports_body = reports.json()
    assert "items" in reports_body
    assert "total" in reports_body

    makes = client.get("/makes/", headers=headers)
    assert makes.status_code == 200
    assert isinstance(makes.json(), list)
