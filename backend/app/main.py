from fastapi import FastAPI

from app.modules.auth.router import router as auth_router
from app.modules.events.router import router as events_router
from app.modules.projects.router import router as projects_router


def create_app() -> FastAPI:
    app = FastAPI(title="Academic Collaboration API", version="0.1.0")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(events_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
