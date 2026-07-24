import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL database configuration for the FastAPI app.
# This uses the standard synchronous SQLAlchemy setup that works with
# regular FastAPI dependency-injected database sessions.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        raise ValueError(
            "DATABASE_URL environment variable is required in production. "
            "Set DATABASE_URL to your PostgreSQL connection string."
        )
    # Development: use local PostgreSQL
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/skillbridge"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

DB_SCHEMA = os.getenv("DB_SCHEMA", "skillbridge_schema").strip() or "skillbridge_schema"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "sslmode": "disable",
        "options": f"-csearch_path={DB_SCHEMA}",
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.schema = DB_SCHEMA


def get_schema_setup_statements() -> list[str]:
    safe_schema = DB_SCHEMA.replace('"', '""')
    return [f'CREATE SCHEMA IF NOT EXISTS "{safe_schema}"']


def ensure_schema_permissions() -> None:
    for statement in get_schema_setup_statements():
        with engine.begin() as conn:
            conn.execute(text(statement))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
