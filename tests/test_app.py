import os

# Force demo mode during automated tests.
os.environ["AI_MODE"] = "demo"
os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_generate_demo():

    response = client.post(
        "/api/generate",
        json={
            "username": "Test User",
            "user_id": "test001",
            "age": 25,
            "weight": 70,
            "goal": "muscle gain",
            "intensity": "medium",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "workout_plan" in data

    assert "nutrition_tip" in data

    assert len(data["workout_plan"]) > 100


def test_feedback_demo():

    response = client.post(
        "/api/feedback",
        json={
            "user_id": "test001",
            "feedback": "Add more cardio.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "updated_plan" in data