from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=120,
    )

    user_id: str = Field(
        min_length=2,
        max_length=80,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        lt=500,
    )

    goal: Goal

    intensity: Intensity

    @field_validator("username", "user_id")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be blank")

        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=2,
        max_length=80,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

    feedback: str = Field(
        min_length=3,
        max_length=1200,
    )

    @field_validator("feedback")
    @classmethod
    def normalize_feedback(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Feedback cannot be blank")

        return value