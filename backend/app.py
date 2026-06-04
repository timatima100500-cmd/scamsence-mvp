from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analysis, health, voice


def create_app() -> FastAPI:
    app = FastAPI(
        title="ScamSence API",
        description="Analyze texts, emails, URLs and voice/video for fraud signs.",
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=["*"] — Streamlit ports vary, ngrok URL changes on restart
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(analysis.router)
    app.include_router(voice.router)  # День 9: YouTube + Audio analysis
    return app


app = create_app()
