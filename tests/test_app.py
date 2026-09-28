import os
from types import SimpleNamespace

from google.genai.errors import APIError


# Use mock AI for automated tests.
os.environ["MOCK_AI"] = "true"

# Use a separate test database.
os.environ["DATABASE_URL"] = "sqlite:///./test_fitbuddy.db"


from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine
from app import gemini_flash_generator
from app import gemini_generator


# Recreate test database.
Base.metadata.drop_all(
    bind=engine
)

Base.metadata.create_all(
    bind=engine
)


client = TestClient(
    app
)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_generate_workout_form():

    response = client.post(
        "/generate-workout",
        data={
            "username": "HTML Test",
            "user_id": "html001",
            "age": 30,
            "weight": 70,
            "goal": "muscle gain",
            "intensity": "medium",
        },
    )

    assert response.status_code == 200
    assert "HTML Test's FitBuddy plan" in response.text

    invalid_response = client.post(
        "/generate-workout",
        data={
            "username": "HTML Test",
            "user_id": "html002",
            "age": 30,
            "weight": 70,
            "goal": "invalid goal",
            "intensity": "medium",
        },
    )

    assert invalid_response.status_code == 422


def test_nutrition_tip_falls_back_when_gemini_is_unavailable(monkeypatch):

    monkeypatch.setattr(
        gemini_flash_generator,
        "get_settings",
        lambda: SimpleNamespace(
            mock_ai=False,
            gemini_tip_model="gemini-3.5-flash-lite",
        ),
    )

    def raise_service_unavailable(*args, **kwargs):
        raise APIError(
            503,
            {"message": "temporarily unavailable"},
        )

    monkeypatch.setattr(
        gemini_flash_generator,
        "generate_text",
        raise_service_unavailable,
    )

    tip = gemini_flash_generator.generate_nutrition_tip_with_flash(
        "general wellness"
    )

    assert "local recovery tip" in tip
    assert "regular hydration" in tip


def test_workout_falls_back_when_gemini_is_unavailable(monkeypatch):

    monkeypatch.setattr(
        gemini_generator,
        "get_settings",
        lambda: SimpleNamespace(
            mock_ai=False,
            gemini_workout_model="gemini-3.5-flash-lite",
        ),
    )

    def raise_quota_exceeded(*args, **kwargs):
        raise APIError(
            429,
            {"message": "quota exceeded"},
        )

    monkeypatch.setattr(
        gemini_generator,
        "generate_text",
        raise_quota_exceeded,
    )

    plan = gemini_generator.generate_workout_gemini(
        "Fallback Test",
        30,
        70,
        "general wellness",
        "low",
    )

    assert "local fallback plan" in plan
    assert "FITBUDDY 7-DAY WORKOUT PLAN" in plan


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_and_update():

    payload = {
        "username": "Test User",
        "user_id": "test001",
        "age": 30,
        "weight": 70,
        "goal": "muscle gain",
        "intensity": "medium",
    }


    response = client.post(
        "/api/generate-workout",
        json=payload,
    )


    assert response.status_code == 200


    body = response.json()


    assert body["plan_id"] > 0


    assert "Day 1" in body["workout_plan"]


    response = client.post(
        "/api/submit-feedback",
        json={
            "user_id": "test001",
            "feedback": "Include more cardio",
        },
    )


    assert response.status_code == 200


    assert (
        "UPDATED FROM FEEDBACK"
        in response.json()["updated_plan"]
    )


def test_admin_page():

    response = client.get(
        "/view-all-users"
    )


    assert response.status_code == 200


    assert "Test User" in response.text