from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


ALLOWED_INTENSITIES = {
    "low",
    "medium",
    "high",
}


class UserInput(BaseModel):
    """
    User fitness profile.
    """

    username: str = Field(
        min_length=2,
        max_length=120,
    )

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: str = Field(
        min_length=2,
        max_length=80,
    )

    intensity: str = Field(
        min_length=3,
        max_length=20,
    )

    @field_validator("username", "user_id", "goal")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value

    @field_validator("goal")
    @classmethod
    def normalize_goal(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("intensity")
    @classmethod
    def normalize_intensity(cls, value: str) -> str:
        value = value.strip().lower()

        if value not in ALLOWED_INTENSITIES:
            raise ValueError(
                "Intensity must be low, medium, or high."
            )

        return value


class FeedbackRequest(BaseModel):
    """
    User feedback for plan regeneration.
    """

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )

    @field_validator("user_id", "feedback")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


class PlanResponse(BaseModel):
    user_id: str
    workout_plan: str
    nutrition_tip: str