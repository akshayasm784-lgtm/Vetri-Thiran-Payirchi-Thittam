from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .config import BASE_DIR

from .database import get_db

from .database_service import (
    delete_user,
    get_all_users,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)

from .gemini_client import AIConfigurationError

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)

from .gemini_generator import (
    generate_workout_gemini,
)

from .schemas import (
    FeedbackRequest,
    Goal,
    Intensity,
    UserInput,
)

from .updated_plan import (
    update_workout_plan,
)


router = APIRouter()

templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


def render_error(
    request: Request,
    message: str,
    status_code: int = 400,
):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "message": message,
        },
        status_code=status_code,
    )


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
        },
    )


# ---------------------------------------------------------
# HTML - GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: Goal = Form(...),

    intensity: Intensity = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        user = save_user(
            db,
            data,
        )

        workout_plan = generate_workout_gemini(
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            data.goal
        )

        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "message": None,
            },
        )

    except AIConfigurationError as exc:

        return render_error(
            request,
            str(exc),
            503,
        )

    except Exception as exc:

        db.rollback()

        return render_error(
            request,
            f"Could not generate the plan: {exc}",
            500,
        )


# ---------------------------------------------------------
# HTML - FEEDBACK / UPDATE
# ---------------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            data.user_id,
        )

        plan = get_original_plan(
            db,
            data.user_id,
        )

        if not user or not plan:

            return render_error(
                request,
                "User ID was not found. Generate a plan first.",
                404,
            )

        revised = update_workout_plan(
            plan.original_plan,
            data.feedback,
            user.username,
            user.age,
            user.weight,
            user.goal,
            user.intensity,
        )

        tip = generate_nutrition_tip_with_flash(
            user.goal
        )

        update_plan(
            db,
            plan,
            revised,
            data.feedback,
            tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "message": (
                    "Your plan was updated from the feedback."
                ),
            },
        )

    except AIConfigurationError as exc:

        return render_error(
            request,
            str(exc),
            503,
        )

    except Exception as exc:

        db.rollback()

        return render_error(
            request,
            f"Could not update the plan: {exc}",
            500,
        )


# ---------------------------------------------------------
# ADMIN / COACH DASHBOARD
# ---------------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):

    users = get_all_users(
        db
    )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users,
        },
    )


# ---------------------------------------------------------
# DELETE USER
# ---------------------------------------------------------

@router.post(
    "/admin/users/{user_id}/delete"
)
def remove_user(
    user_id: str,
    db: Session = Depends(get_db),
):

    # The original documentation describes this as a local
    # admin/coach feature.
    #
    # Add authentication and authorization before public deployment.

    if not delete_user(
        db,
        user_id,
    ):

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return RedirectResponse(
        url="/view-all-users",
        status_code=status.HTTP_303_SEE_OTHER,
    )


# ---------------------------------------------------------
# API HEALTH
# ---------------------------------------------------------

@router.get(
    "/api/health"
)
def health():

    return {
        "status": "ok",
        "service": "fitbuddy",
    }


# ---------------------------------------------------------
# API - GENERATE WORKOUT
# ---------------------------------------------------------

@router.post(
    "/api/generate-workout"
)
def api_generate_workout(
    data: UserInput,
    db: Session = Depends(get_db),
):

    try:

        user = save_user(
            db,
            data,
        )

        workout_plan = generate_workout_gemini(
            data.username,
            data.age,
            data.weight,
            data.goal,
            data.intensity,
        )

        nutrition_tip = generate_nutrition_tip_with_flash(
            data.goal
        )

        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip,
        )

        return {
            "user_id": user.user_id,
            "plan_id": plan.id,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
        }

    except AIConfigurationError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to generate workout plan",
        ) from exc


# ---------------------------------------------------------
# API - SUBMIT FEEDBACK
# ---------------------------------------------------------

@router.post(
    "/api/submit-feedback"
)
def api_submit_feedback(
    data: FeedbackRequest,
    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        data.user_id,
    )

    plan = get_original_plan(
        db,
        data.user_id,
    )

    if not user or not plan:

        raise HTTPException(
            status_code=404,
            detail="User or plan not found",
        )

    try:

        revised = update_workout_plan(
            plan.original_plan,
            data.feedback,
            user.username,
            user.age,
            user.weight,
            user.goal,
            user.intensity,
        )

        tip = generate_nutrition_tip_with_flash(
            user.goal
        )

        update_plan(
            db,
            plan,
            revised,
            data.feedback,
            tip,
        )

        return {
            "user_id": user.user_id,
            "plan_id": plan.id,
            "updated_plan": revised,
            "nutrition_tip": tip,
        }

    except AIConfigurationError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update workout plan",
        ) from exc


# ---------------------------------------------------------
# API - LIST USERS
# ---------------------------------------------------------

@router.get(
    "/api/users"
)
def api_users(
    db: Session = Depends(get_db),
):

    users = get_all_users(
        db
    )

    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,

            "plans": [
                {
                    "id": plan.id,
                    "original_plan": plan.original_plan,
                    "updated_plan": plan.updated_plan,
                    "feedback": plan.feedback,
                    "nutrition_tip": plan.nutrition_tip,
                    "updated_nutrition_tip": (
                        plan.updated_nutrition_tip
                    ),
                }

                for plan in user.plans
            ],
        }

        for user in users
    ]