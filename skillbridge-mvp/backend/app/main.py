import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine, ensure_schema_permissions
from app.routes.assessment import router as assessment_router
from app.routes.auth import router as auth_router
from app.routes.debug import router as debug_router
from app.routes.chat import router as chat_router
from app.routes.jobs import router as jobs_router
from app.routes.learning import router as learning_router
from app.routes.progress import router as progress_router
from app.routes.risk import router as risk_router
from app.routes.user import router as user_router
from app.routes.profile import router as profile_router
from app.utils.logging_config import setup_logging
from app.utils.seed import seed_database
from app.utils.db_migration import ensure_job_columns, ensure_profile_columns

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="DB Career Navigator API", version="1.0.0")

frontend_origin = os.getenv("FRONTEND_URL")
if not frontend_origin:
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        raise ValueError(
            "FRONTEND_URL environment variable is required in production. "
            "Set FRONTEND_URL to your frontend domain (e.g., https://your-app.com)"
        )
    # Development: allow localhost patterns
    frontend_origin = "http://localhost:3000"

allowed_origins = [frontend_origin]
environment = os.getenv("ENVIRONMENT", "development")
if environment == "development":
    allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])

# Allow the configured frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):300[0-9]" if environment == "development" else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(debug_router)
app.include_router(profile_router)
app.include_router(user_router)
app.include_router(assessment_router)
app.include_router(learning_router)
app.include_router(progress_router)
app.include_router(risk_router)
app.include_router(jobs_router)
app.include_router(chat_router)


@app.get("/health")
def health_check() -> dict:
    logger.info("Health check requested")
    return {"status": "ok", "service": "skillbridge"}


@app.on_event("startup")
def startup_event() -> None:
    logger.info("Starting SkillBridge API")
    ensure_schema_permissions()
    Base.metadata.create_all(bind=engine)
    ensure_profile_columns()
    ensure_job_columns()
    seed_database()
    logger.info("Database created/verified and seed data loaded")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception for %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
