import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=False)
else:
    load_dotenv(override=False)


def resolve_database_url(raw_url: Optional[str]) -> str:
    if not raw_url:
        return f"sqlite:///{(BASE_DIR / 'skillbridge.db').resolve().as_posix()}"

    if raw_url.startswith("sqlite:///./"):
        relative_path = raw_url[len("sqlite:///./"):]
        return f"sqlite:///{(BASE_DIR / relative_path).resolve().as_posix()}"

    if raw_url.startswith("sqlite://./"):
        relative_path = raw_url[len("sqlite://./"):]
        return f"sqlite:///{(BASE_DIR / relative_path).resolve().as_posix()}"

    return raw_url


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./skillbridge.db"
    JWT_SECRET: str = "skillbridge_secret_key_2024_super_secure"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
settings.DATABASE_URL = resolve_database_url(settings.DATABASE_URL)
