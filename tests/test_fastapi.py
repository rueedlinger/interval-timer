import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """TestClient fixture with lifespan context so app.state is initialized."""
    with TestClient(app) as c:
        yield c


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_training(client):
    response = client.get("/training")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "intervals" in data
    assert "max_rounds" in data


def test_create_training(client):
    payload = {
        "intervals": [
            {"color": "#FF0000", "name": "Warmup", "time_seconds": 30},
            {"color": "#00FF00", "name": "Work", "time_seconds": 60},
        ],
        "max_rounds": 9,
        "name": "Test Workout",
    }

    response = client.post("/training", json=payload)
    print(response)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workout"
    assert data["max_rounds"] == 9
    assert len(data["intervals"]) == 2


@pytest.mark.parametrize("action", ["start", "pause", "stop"])
def test_timer_actions(client, action):
    response = client.post("/timer", json={"action": action})
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_timer_invalid_action(client):
    response = client.post("/timer", json={"action": "invalid"})
    assert response.status_code == 422
