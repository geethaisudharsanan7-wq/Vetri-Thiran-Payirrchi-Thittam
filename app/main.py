from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import init_db
from .routes import router


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)


app = FastAPI(
    title="FitBuddy - Local Fitness Plan Generator",
   description=(
    "Local personalized workout and "
    "nutrition/recovery planning application."
),
    version="1.0.0",
)


# ---------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static",
)


# ---------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------


templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------


app.include_router(
    router
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------


# Create SQLite tables when the application starts/imports.
init_db()