from fastapi import FastAPI, APIRouter
from pathlib import Path
from .api.routes import create_routes

def main():
    app = FastAPI(
        docs_url="/api/v1/docs",
        redoc_url=None,
        openapi_url="/api/v1/openapi.json",
    )

    # Prepare the API prefix
    api = APIRouter(prefix="/api/v1")

    # Add all the routes in app.api.routes
    create_routes(api)

    # Add the API routes
    app.include_router(api)

    # Configure the frontend
    BASE_DIR = Path(__file__).resolve().parent
    FRONTEND_DIR = BASE_DIR.parent / "frontend"

    if (FRONTEND_DIR / "index.html").exists():
        app.frontend(
            "/",
            directory=FRONTEND_DIR,
            fallback="index.html",
        )

    return app
