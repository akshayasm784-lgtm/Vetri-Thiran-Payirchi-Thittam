from google.genai.errors import APIError

from .config import get_settings
from .gemini_client import generate_text


def _mock_plan(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    return f"""
FITBUDDY 7-DAY WORKOUT PLAN

User: {username}

Profile:
- Age: {age}
- Weight: {weight:.1f} kg
- Goal: {goal.title()}
- Intensity: {intensity.title()}

Day 1 – Full Body

Warm-up:
8 minutes brisk walking and mobility.

Main workout:
- Squats: 3 x 10
- Push-ups: 3 x 8
- Rows: 3 x 10
- Plank: 3 x 30 seconds

Cooldown:
5–10 minutes easy stretching.


Day 2 – Cardio & Core

Warm-up:
5–8 minutes easy cardio.

Main workout:
- Moderate cardio: 25 minutes
- Dead bug: 3 x 10 per side
- Side plank: 3 x 20 seconds per side

Cooldown:
Easy walking and breathing.


Day 3 – Recovery

- 20–30 minute easy walk
- Gentle mobility
- Light stretching


Day 4 – Lower Body

Warm-up:
8 minutes plus hip and ankle mobility.

Main workout:
- Lunges: 3 x 8 per side
- Glute bridges: 3 x 12
- Calf raises: 3 x 15

Cooldown:
5–10 minutes stretching.


Day 5 – Upper Body

Warm-up:
8 minutes shoulder and upper-back mobility.

Main workout:
- Incline push-ups: 3 x 10
- Band rows: 3 x 12
- Shoulder press: 3 x 10

Cooldown:
5–10 minutes stretching.


Day 6 – Goal-Focused Conditioning

Warm-up:
8 minutes easy cardio.

Main workout:
20–30 minutes goal-appropriate cardio at a conversational pace.

Cooldown:
5–10 minutes easy movement.


Day 7 – Rest & Recovery

- Full rest or easy 15–20 minute walk
- Hydration
- Adequate sleep
- Comfortable mobility


Safety note:

This example is educational and is not medical advice.
Stop if you experience pain, dizziness, or unusual symptoms.
"""


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
) -> str:

    settings = get_settings()

    if settings.mock_ai:
        return _mock_plan(
            username,
            age,
            weight,
            goal,
            intensity,
        )

    prompt = f"""
You are FitBuddy, a careful fitness-planning assistant.

Create a personalized 7-day workout plan.

USER PROFILE

Name:
{username}

Age:
{age}

Weight:
{weight} kg

Fitness goal:
{goal}

Preferred intensity:
{intensity}


REQUIREMENTS

1. Provide exactly seven labeled days.

2. Training days should include:
   - 5–10 minute warm-up
   - Main workout
   - Exercise names
   - Sets/repetitions or duration
   - Cooldown/recovery guidance

3. Include appropriate rest and recovery.

4. Avoid unsafe or extreme exercise volume.

5. Tailor the plan to the stated goal.

6. Tailor the difficulty to the requested intensity.

7. Do not diagnose medical conditions.

8. Do not prescribe medical treatment.

9. If medical clearance may be appropriate, mention it briefly.

10. Use readable Markdown headings and bullet points.

11. Do not wrap the response in a code block.

Return only the workout plan.
"""

    try:
        return generate_text(
            settings.gemini_workout_model,
            prompt,
            temperature=0.55,
            max_output_tokens=5000,
        )
    except APIError as exc:
        if exc.code not in {429, 503}:
            raise

        return (
            "Gemini is temporarily unavailable; showing the local fallback plan.\n\n"
            + _mock_plan(
                username,
                age,
                weight,
                goal,
                intensity,
            )
        )