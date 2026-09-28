from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .ai import ai_or_demo_tip
from .ai import ai_or_demo_workout
from .ai import demo_workout
from .ai import update_workout_plan
from .config import settings
from .crud import get_all_plans
from .crud import get_all_users
from .crud import get_latest_plan
from .crud import get_user
from .crud import save_plan
from .crud import save_user
from .crud import update_plan
from .database import get_db
from app.schemas import FeedbackRequest
from app.schemas import UserInput


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


router = APIRouter()


# ---------------------------------------------------------
# HOME
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
            "error": None,
        },
    )


# ---------------------------------------------------------
# GENERATE WORKOUT
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
    goal: str = Form(...),
    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        user_input = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        user = save_user(
            db,
            user_input,
        )

        workout = ai_or_demo_workout(
            user_input.username,
            user_input.age,
            user_input.weight,
            user_input.goal,
            user_input.intensity,
        )

        nutrition_tip = ai_or_demo_tip(
            user_input.goal
        )

        plan = save_plan(
            db=db,
            user_id=user.user_id,
            workout_plan=workout,
            nutrition_tip=nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "error": None,
                "success": None,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "error": str(exc),
            },
            status_code=400,
        )


# ---------------------------------------------------------
# FEEDBACK PAGE
# ---------------------------------------------------------


@router.get(
    "/feedback",
    response_class=HTMLResponse,
)
def feedback_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="feedback.html",
        context={
            "request": request,
            "error": None,
            "user_id": "",
        },
    )


# ---------------------------------------------------------
# SUBMIT FEEDBACK
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

        payload = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            payload.user_id,
        )

        plan = get_latest_plan(
            db,
            payload.user_id,
        )

        if not user:
            raise ValueError(
                "User was not found."
            )

        if not plan:
            raise ValueError(
                "No workout plan was found for this user."
            )

        if not plan.original_plan:
            raise ValueError(
                "Original workout plan is empty."
            )

        if not settings.gemini_api_key:

            updated_plan = (
                demo_workout(
                    user.goal,
                    user.intensity,
                )
                + "\n\n"
                + "Feedback applied:\n"
                + payload.feedback
            )

        else:

            updated_plan = update_workout_plan(
                original_plan=plan.original_plan,
                feedback=payload.feedback,
                goal=user.goal,
                intensity=user.intensity,
            )

        update_plan(
            db=db,
            plan=plan,
            updated_plan=updated_plan,
            feedback=payload.feedback,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "success": "Your workout plan was updated successfully.",
                "error": None,
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="feedback.html",
            context={
                "request": request,
                "error": str(exc),
                "user_id": user_id,
            },
            status_code=400,
        )


# ---------------------------------------------------------
# ADMIN / ALL USERS
# ---------------------------------------------------------


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):

    users = get_all_users(db)

    plans = get_all_plans(db)

    plan_map = {}

    for plan in plans:

        plan_map.setdefault(
            plan.user_id,
            [],
        ).append(plan)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "request": request,
            "users": users,
            "plan_map": plan_map,
        },
    )


# =========================================================
# JSON API
# =========================================================


@router.get(
    "/api/health",
)
def health():

    return {
        "status": "ok",
        "service": "fitbuddy",
    }


@router.post(
    "/api/generate",
)
def api_generate(
    payload: UserInput,
    db: Session = Depends(get_db),
):

    try:

        user = save_user(
            db,
            payload,
        )

        workout = ai_or_demo_workout(
            payload.username,
            payload.age,
            payload.weight,
            payload.goal,
            payload.intensity,
        )

        nutrition_tip = ai_or_demo_tip(
            payload.goal
        )

        save_plan(
            db=db,
            user_id=user.user_id,
            workout_plan=workout,
            nutrition_tip=nutrition_tip,
        )

        return {
            "user_id": user.user_id,
            "workout_plan": workout,
            "nutrition_tip": nutrition_tip,
        }

    except Exception as exc:

        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc)
            },
        )


@router.post(
    "/api/feedback",
)
def api_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        payload.user_id,
    )

    plan = get_latest_plan(
        db,
        payload.user_id,
    )

    if not user or not plan:

        return JSONResponse(
            status_code=404,
            content={
                "detail":
                    "User or workout plan not found."
            },
        )

    try:

        if not settings.gemini_api_key:

            updated = (
                demo_workout(
                    user.goal,
                    user.intensity,
                )
                + "\n\nFeedback applied:\n"
                + payload.feedback
            )

        else:

            updated = update_workout_plan(
                original_plan=plan.original_plan,
                feedback=payload.feedback,
                goal=user.goal,
                intensity=user.intensity,
            )

        update_plan(
            db=db,
            plan=plan,
            updated_plan=updated,
            feedback=payload.feedback,
        )

        return {
            "user_id": user.user_id,
            "updated_plan": updated,
        }

    except Exception as exc:

        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc)
            },
        )