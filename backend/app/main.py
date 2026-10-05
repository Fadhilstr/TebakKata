from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.game import router as game_router
from app.db.session import engine, Base
import app.models  # Register models

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Game tebak kata berbasis semantic similarity Bahasa Indonesia",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # Don't log health check repeatedly
    if not request.url.path.endswith("/health"):
        logger.info(
            "%s %s - Status: %d - Time: %.2f ms",
            request.method,
            request.url.path,
            response.status_code,
            process_time
        )
    return response


# Include Routers
app.include_router(game_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing %s backend...", settings.PROJECT_NAME)
    # Ensure tables exist
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified.")
    except Exception as e:
        logger.warning("Database connection note during startup: %s", e)

    # Initialize semantic engine
    from app.semantic.engine import semantic_engine
    logger.info("Semantic Engine vocabulary size: %d words", len(semantic_engine.words))


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/api/docs"
    }
