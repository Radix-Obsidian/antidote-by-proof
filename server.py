"""Antidote API server — FastAPI entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api.routes import router
from config import settings

app = FastAPI(
    title="Antidote by PROOF",
    description="Sovereign auth-gap scanner for Python web frameworks",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Serve frontend
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_landing():
        return FileResponse(str(frontend_dir / "landing.html"))

    @app.get("/dashboard")
    def serve_dashboard():
        return FileResponse(str(frontend_dir / "index.html"))


def main():
    import uvicorn
    uvicorn.run(
        "server:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
    )


if __name__ == "__main__":
    main()
