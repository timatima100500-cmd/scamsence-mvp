from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import analysis, health


def create_app() -> FastAPI:
    app = FastAPI(
        title="ScamSence API",
        description="Analyze texts, emails and URLs for fraud signs.",
        version="0.1.0",
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
    return app


app = create_app()
