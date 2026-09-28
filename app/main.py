from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .config import (
    BASE_DIR,
    get_settings,
)

from .database import init_db

from .routes import router


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    # Make sure SQLite data directory exists.
    (
        BASE_DIR / "data"
    ).mkdir(
        exist_ok=True
    )

    init_db()

    yield


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "AI-powered 7-day fitness planning application."
    ),
    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),
    name="static",
)


app.include_router(
    router
)