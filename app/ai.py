import json
import re
from typing import Any

from .config import settings


try:
    from google import genai
except ImportError:
    genai = None


class AIServiceError(RuntimeError):
    pass


def _get_client():
    """
    Create a Gemini client.
    """

    if not settings.gemini_api_key:
        raise AIServiceError(
            "GEMINI_API_KEY is not configured."
        )

    if genai is None:
        raise AIServiceError(
            "google-genai is not installed."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _extract_json(text: str) -> Any:
    """
    Safely extract JSON from Gemini's response.

    Gemini should return JSON directly, but this also handles
    accidental markdown code fences.
    """

    if not text:
        raise AIServiceError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        flags=re.S | re.I,
    )

    if match:
        try:
            return json.loads(
                match.group(1)
            )
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:
        try:
            return json.loads(
                text[start:end + 1]
            )
        except json.JSONDecodeError:
            pass

    raise AIServiceError(
        "Gemini returned invalid JSON."
    )


def _generate(
    model: str,
    prompt: str,
) -> str:

    client = _get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "temperature": 0.6,
            "max_output_tokens": 7000,
            "response_mime_type": "application/json",
        },
    )

    if not response.text:
        raise AIServiceError(
            "Gemini returned an empty response."
        )

    return response.text


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a personalized seven-day fitness plan.

User:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Workout intensity: {intensity}

Return ONLY valid JSON.

Required JSON structure:

{{
    "days": [
        {{
            "day": "Day 1",
            "focus": "Full Body",
            "warmup": "5-10 minutes",
            "exercises": [
                {{
                    "name": "Bodyweight Squat",
                    "sets": 3,
                    "reps": "10-12",
                    "rest": "60 seconds"
                }}
            ],
            "cooldown": "5 minutes"
        }}
    ],
    "safety_note": "..."
}}

Rules:

1. Return exactly seven days.
2. Include rest/recovery where appropriate.
3. Match the requested intensity.
4. Make the plan practical and easy to follow.
5. Include warm-up and cooldown.
6. Include exercise name, sets, reps/duration and rest.
7. Do not diagnose medical conditions.
8. Do not provide dangerous or extreme exercise instructions.
9. Do not prescribe extreme calorie restriction.
10. Keep the response concise enough for a web application.
"""

    raw = _generate(
        settings.workout_model,
        prompt,
    )

    data = _extract_json(raw)

    return _format_plan(data)


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str,
) -> str:

    prompt = f"""
You are FitBuddy.

The user wants to modify an existing seven-day workout plan.

Fitness goal:
{goal}

Workout intensity:
{intensity}

User feedback:
{feedback}

Existing workout plan:
{original_plan}

Create a revised seven-day plan.

Return ONLY valid JSON using exactly this structure:

{{
    "days": [
        {{
            "day": "Day 1",
            "focus": "...",
            "warmup": "...",
            "exercises": [
                {{
                    "name": "...",
                    "sets": 3,
                    "reps": "10",
                    "rest": "60 seconds"
                }}
            ],
            "cooldown": "..."
        }}
    ],
    "safety_note": "..."
}}

Rules:

1. Exactly seven days.
2. Apply the user's feedback.
3. Preserve useful parts of the original plan.
4. Keep the requested intensity.
5. Include recovery/rest where appropriate.
6. Avoid medical diagnosis or treatment.
7. Avoid extreme or unsafe recommendations.
"""

    raw = _generate(
        settings.workout_model,
        prompt,
    )

    data = _extract_json(raw)

    return _format_plan(data)


def generate_nutrition_tip_with_flash(
    goal: str,
) -> str:

    prompt = f"""
You are FitBuddy.

Give one concise and practical nutrition or recovery tip
for a person whose fitness goal is:

{goal}

Return ONLY JSON:

{{
    "tip": "..."
}}

Rules:

- Keep the tip concise.
- Make it practical.
- Avoid medical advice.
- Avoid extreme dieting.
- Avoid dangerous supplement recommendations.
"""

    raw = _generate(
        settings.tip_model,
        prompt,
    )

    data = _extract_json(raw)

    tip = str(
        data.get(
            "tip",
            "",
        )
    ).strip()

    if not tip:
        raise AIServiceError(
            "Gemini returned an empty nutrition tip."
        )

    return tip


def _format_plan(
    data: dict,
) -> str:

    lines = []

    days = data.get(
        "days",
        [],
    )

    for day in days[:7]:

        lines.append(
            f"{day.get('day', 'Day')} — "
            f"{day.get('focus', 'Workout')}"
        )

        lines.append(
            f"Warm-up: "
            f"{day.get('warmup', '')}"
        )

        exercises = day.get(
            "exercises",
            [],
        )

        for exercise in exercises:

            lines.append(
                "  • "
                f"{exercise.get('name', 'Exercise')}: "
                f"{exercise.get('sets', '')} sets × "
                f"{exercise.get('reps', '')}; "
                f"rest {exercise.get('rest', '')}"
            )

        lines.append(
            f"Cooldown: "
            f"{day.get('cooldown', '')}"
        )

        lines.append("")

    safety_note = data.get(
        "safety_note",
        "Listen to your body and stop if you feel pain or become unwell.",
    )

    lines.append(
        f"Safety note: {safety_note}"
    )

    return "\n".join(
        lines
    ).strip()


# ---------------------------------------------------------
# DEMO / FALLBACK MODE
# ---------------------------------------------------------


def demo_workout(
    goal: str,
    intensity: str,
) -> str:

    return f"""
Day 1 — Full Body

Warm-up:
5–10 minutes brisk walking and mobility.

Exercises:
  • Bodyweight Squat: 3 sets × 10–12; rest 60 seconds
  • Incline Push-up: 3 sets × 8–12; rest 60 seconds
  • Glute Bridge: 3 sets × 12; rest 45 seconds

Cooldown:
5 minutes easy stretching.


Day 2 — Cardio

Warm-up:
5 minutes easy walking.

Exercises:
  • Brisk Walk or Cycling: 25–30 minutes; rest as needed

Cooldown:
5 minutes easy movement.


Day 3 — Recovery & Mobility

Warm-up:
5 minutes gentle movement.

Exercises:
  • Mobility Flow: 15–20 minutes; rest as needed
  • Easy Walk: 15 minutes; rest as needed

Cooldown:
Gentle stretching.


Day 4 — Upper Body

Warm-up:
5–10 minutes.

Exercises:
  • Incline Push-up: 3 sets × 8–12; rest 60 seconds
  • Resistance Band Row: 3 sets × 10–12; rest 60 seconds
  • Shoulder Press: 2 sets × 10; rest 60 seconds

Cooldown:
5 minutes.


Day 5 — Lower Body

Warm-up:
5–10 minutes.

Exercises:
  • Squat: 3 sets × 10; rest 60 seconds
  • Reverse Lunge: 2 sets × 8 each side; rest 60 seconds
  • Calf Raise: 3 sets × 12; rest 45 seconds

Cooldown:
5 minutes.


Day 6 — Light Cardio + Core

Warm-up:
5 minutes.

Exercises:
  • Easy Cardio: 20–25 minutes; rest as needed
  • Dead Bug: 3 sets × 8 each side; rest 45 seconds
  • Plank: 3 sets × 20–30 seconds; rest 45 seconds

Cooldown:
Gentle stretching.


Day 7 — Rest & Recovery

Take a full rest day or perform an easy walk and light mobility.

Goal:
{goal}

Requested intensity:
{intensity}

Safety note:
Adjust exercise difficulty to your experience and stop if you feel pain
or become unwell.
""".strip()


def demo_tip(
    goal: str,
) -> str:

    tips = {

        "muscle gain":
            "Include a protein-rich food at each main meal and prioritize sleep and hydration.",

        "weight loss":
            "Build meals around vegetables, a protein source, whole foods and water while avoiding overly restrictive dieting.",

        "general wellness":
            "Aim for regular meals, plenty of water, a varied diet and consistent sleep.",

        "flexibility":
            "Stay hydrated and include a balanced diet with adequate protein to support recovery.",

        "strength":
            "Pair resistance training with adequate protein, hydration and recovery.",
    }

    return tips.get(
        goal.lower(),
        tips["general wellness"],
    )


def ai_or_demo_workout(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    if (
        settings.ai_mode == "demo"
        or not settings.gemini_api_key
    ):
        return demo_workout(
            goal,
            intensity,
        )

    return generate_workout_gemini(
        username,
        age,
        weight,
        goal,
        intensity,
    )


def ai_or_demo_tip(
    goal: str,
) -> str:

    if (
        settings.ai_mode == "demo"
        or not settings.gemini_api_key
    ):
        return demo_tip(goal)

    return generate_nutrition_tip_with_flash(
        goal
    )