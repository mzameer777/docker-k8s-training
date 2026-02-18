import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["service"] == "Task API"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_create_and_list_tasks(client):
    resp = client.post("/tasks", json={"title": "Learn Docker"})
    assert resp.status_code == 201

    resp = client.get("/tasks")
    data = resp.get_json()
    assert data["count"] == 1
    assert data["tasks"][0]["title"] == "Learn Docker"
