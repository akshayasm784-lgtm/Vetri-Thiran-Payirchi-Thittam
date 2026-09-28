from google.genai.errors import APIError

from .config import get_settings
from .gemini_client import generate_text


def _mock_tip(
    goal: str,
) -> str:

    tips = {
        "weight loss": (
            "Prioritize filling meals built around protein, vegetables, "
            "whole grains, and adequate water. Avoid aggressive restriction."
        ),

        "muscle gain": (
            "Include a protein-rich food at each meal and eat a balanced "
            "post-workout meal containing protein and carbohydrates."
        ),

        "general wellness": (
            "Aim for regular hydration, balanced meals, adequate sleep, "
            "and a consistent eating pattern."
        ),

        "flexibility": (
            "Hydrate normally and include protein-rich foods plus fruits "
            "and vegetables to support overall recovery."
        ),

        "endurance": (
            "Pair endurance training with adequate carbohydrates, fluids, "
            "and protein to support recovery between sessions."
        ),
    }

    return tips.get(
        goal,
        tips["general wellness"],
    )


def generate_nutrition_tip_with_flash(
    goal: str,
) -> str:

    settings = get_settings()

    if settings.mock_ai:
        return _mock_tip(goal)

    prompt = f"""
Give one concise, practical nutrition or recovery tip
for a fitness user whose goal is:

{goal}

Requirements:

- 2–4 sentences.
- Focus on broadly applicable food, hydration, sleep,
  or recovery guidance.
- Do not provide medical treatment.
- Do not recommend extreme dieting.
- Do not provide individualized calorie prescriptions.

Return only the tip.
"""

    try:
        return generate_text(
            settings.gemini_tip_model,
            prompt,
            temperature=0.4,
            max_output_tokens=250,
        )
    except APIError as exc:
        if exc.code not in {429, 503}:
            raise

        return (
            "Gemini is temporarily unavailable; showing a local recovery tip. "
            + _mock_tip(goal)
        )