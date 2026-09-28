from .config import get_settings
from .gemini_client import generate_text
from .gemini_generator import _mock_plan


def update_workout_plan(
    original_plan: str,
    feedback: str,
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    settings = get_settings()

    if settings.mock_ai:

        return (
            _mock_plan(
                username,
                age,
                weight,
                goal,
                intensity,
            )
            + f"""

UPDATED FROM FEEDBACK

{feedback}
"""
        )

    prompt = f"""
You are updating an existing FitBuddy 7-day workout plan.

USER PROFILE

Name:
{username}

Age:
{age}

Weight:
{weight} kg

Goal:
{goal}

Intensity:
{intensity}


ORIGINAL PLAN

{original_plan}


USER FEEDBACK

{feedback}


TASK

Create a revised seven-day plan that incorporates the user's feedback
while retaining useful parts of the original plan.

Requirements:

1. Keep seven labeled days.
2. Include warm-up guidance.
3. Include main workout guidance.
4. Include cooldown/recovery guidance where appropriate.
5. Include appropriate rest.
6. Do not introduce extreme exercise volume.
7. Do not make medical claims.
8. If the requested change could be unsafe, adapt it conservatively.
9. Explain a safety consideration briefly if necessary.
10. Return readable Markdown.
11. Do not use a code fence.

Return only the revised plan.
"""

    return generate_text(
        settings.gemini_workout_model,
        prompt,
        temperature=0.55,
        max_output_tokens=5000,
    )