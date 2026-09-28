from typing import Iterable


class AIServiceError(RuntimeError):
    """Compatibility error for the local generator."""


def _exercise_line(
    name: str,
    sets: int,
    reps: str,
    rest: str,
) -> str:
    return (
        f"  • {name}: "
        f"{sets} sets × {reps}; "
        f"rest {rest}"
    )


def _intensity_values(
    intensity: str,
) -> tuple[int, int, str]:

    level = intensity.strip().lower()

    if level == "low":
        return 2, 45, "easy"

    if level == "high":
        return 4, 75, "challenging"

    return 3, 60, "moderate"


def _format_day(
    day: str,
    focus: str,
    warmup: str,
    exercises: Iterable[str],
    cooldown: str,
) -> list[str]:

    return [
        f"{day} — {focus}",
        "",
        "Warm-up:",
        warmup,
        "",
        "Exercises:",
        *exercises,
        "",
        "Cooldown:",
        cooldown,
        "",
    ]


def demo_workout(
    goal: str,
    intensity: str,
) -> str:

    sets, rest_seconds, level = _intensity_values(
        intensity
    )

    rest = f"{rest_seconds} seconds"

    goal_text = goal.strip().lower()

    if (
        "cardio" in goal_text
        or "endurance" in goal_text
    ):

        day1_focus = "Cardio Endurance"

        day1 = [
            _exercise_line(
                "Brisk Walk or Cycling",
                1,
                "25–35 minutes",
                "as needed",
            ),
            _exercise_line(
                "Step-ups",
                sets,
                "10 each side",
                rest,
            ),
        ]

    elif (
        "flex" in goal_text
        or "mobility" in goal_text
    ):

        day1_focus = "Mobility & Full Body"

        day1 = [
            _exercise_line(
                "Bodyweight Squat",
                sets,
                "10–12",
                rest,
            ),
            _exercise_line(
                "Glute Bridge",
                sets,
                "12",
                rest,
            ),
            _exercise_line(
                "Mobility Flow",
                2,
                "8–10 minutes",
                "as needed",
            ),
        ]

    elif (
        "strength" in goal_text
        or "muscle" in goal_text
    ):

        day1_focus = "Full Body Strength"

        day1 = [
            _exercise_line(
                "Bodyweight Squat",
                sets,
                "8–12",
                rest,
            ),
            _exercise_line(
                "Incline Push-up",
                sets,
                "8–12",
                rest,
            ),
            _exercise_line(
                "Glute Bridge",
                sets,
                "10–15",
                rest,
            ),
        ]

    else:

        day1_focus = "Full Body Wellness"

        day1 = [
            _exercise_line(
                "Bodyweight Squat",
                sets,
                "10–12",
                rest,
            ),
            _exercise_line(
                "Incline Push-up",
                sets,
                "8–12",
                rest,
            ),
            _exercise_line(
                "Glute Bridge",
                sets,
                "12",
                rest,
            ),
        ]

    days: list[str] = []

    days += _format_day(
        "Day 1",
        day1_focus,
        "5–10 minutes brisk walking and mobility.",
        day1,
        "5 minutes easy stretching.",
    )

    days += _format_day(
        "Day 2",
        "Cardio",
        "5 minutes easy walking.",
        [
            _exercise_line(
                "Brisk Walk or Cycling",
                1,
                "25–30 minutes",
                "as needed",
            )
        ],
        "5 minutes easy movement.",
    )

    days += _format_day(
        "Day 3",
        "Recovery & Mobility",
        "5 minutes gentle movement.",
        [
            _exercise_line(
                "Mobility Flow",
                2,
                "8–10 minutes",
                "as needed",
            ),
            _exercise_line(
                "Easy Walk",
                1,
                "15–20 minutes",
                "as needed",
            ),
        ],
        "Gentle stretching.",
    )

    days += _format_day(
        "Day 4",
        "Upper Body",
        "5–10 minutes.",
        [
            _exercise_line(
                "Incline Push-up",
                sets,
                "8–12",
                rest,
            ),
            _exercise_line(
                "Resistance Band Row",
                sets,
                "10–12",
                rest,
            ),
            _exercise_line(
                "Shoulder Press",
                max(2, sets - 1),
                "8–10",
                rest,
            ),
        ],
        "5 minutes.",
    )

    days += _format_day(
        "Day 5",
        "Lower Body",
        "5–10 minutes.",
        [
            _exercise_line(
                "Squat",
                sets,
                "8–12",
                rest,
            ),
            _exercise_line(
                "Reverse Lunge",
                max(2, sets - 1),
                "8 each side",
                rest,
            ),
            _exercise_line(
                "Calf Raise",
                sets,
                "12–15",
                rest,
            ),
        ],
        "5 minutes.",
    )

    days += _format_day(
        "Day 6",
        "Light Cardio + Core",
        "5 minutes.",
        [
            _exercise_line(
                "Easy Cardio",
                1,
                "20–25 minutes",
                "as needed",
            ),
            _exercise_line(
                "Dead Bug",
                3 if level != "easy" else 2,
                "8 each side",
                "45 seconds",
            ),
            _exercise_line(
                "Plank",
                3 if level == "challenging" else 2,
                "20–30 seconds",
                "45 seconds",
            ),
        ],
        "Gentle stretching.",
    )

    days += [
        "Day 7 — Rest & Recovery",
        "",
        (
            "Take a full rest day or perform "
            "an easy walk and light mobility."
        ),
        "",
        f"Goal: {goal}",
        f"Requested intensity: {intensity}",
        "",
    ]

    days.append(
        "Safety note: Adjust exercise difficulty "
        "to your experience and stop if you feel "
        "pain or become unwell."
    )

    return "\n".join(days).strip()


def demo_tip(
    goal: str,
) -> str:

    tips = {

        "muscle gain":
            (
                "Include a protein-rich food at "
                "each main meal and prioritize "
                "sleep and hydration."
            ),

        "weight loss":
            (
                "Build meals around vegetables, "
                "a protein source, whole foods "
                "and water while avoiding overly "
                "restrictive dieting."
            ),

        "general wellness":
            (
                "Aim for regular meals, plenty "
                "of water, a varied diet and "
                "consistent sleep."
            ),

        "flexibility":
            (
                "Stay hydrated and include a "
                "balanced diet with adequate "
                "protein to support recovery."
            ),

        "strength":
            (
                "Pair resistance training with "
                "adequate protein, hydration "
                "and recovery."
            ),
    }

    return tips.get(
        goal.strip().lower(),
        tips["general wellness"],
    )


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str,
) -> str:

    feedback_lower = feedback.lower()

    revised_intensity = intensity

    if any(
        word in feedback_lower
        for word in (
            "harder",
            "more intense",
            "increase",
            "challenging",
        )
    ):
        revised_intensity = "high"

    elif any(
        word in feedback_lower
        for word in (
            "easier",
            "less intense",
            "reduce",
            "light",
        )
    ):
        revised_intensity = "low"

    plan = demo_workout(
        goal,
        revised_intensity,
    )

    additions = []

    if "cardio" in feedback_lower:
        additions.append(
            "Feedback applied: added cardio emphasis."
        )

    if (
        "rest" in feedback_lower
        or "recovery" in feedback_lower
    ):
        additions.append(
            "Feedback applied: prioritize "
            "additional recovery when needed."
        )

    if "core" in feedback_lower:
        additions.append(
            "Feedback applied: keep the "
            "Day 6 core work."
        )

    if not additions:
        additions.append(
            f"Feedback applied: {feedback.strip()}"
        )

    return (
        plan
        + "\n\n"
        + "\n".join(additions)
    )


def ai_or_demo_workout(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    # Local-only mode.
    # Parameters are kept for compatibility
    # with the existing application.
    return demo_workout(
        goal,
        intensity,
    )


def ai_or_demo_tip(
    goal: str,
) -> str:

    return demo_tip(goal)