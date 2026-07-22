import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "skillbridge.log"


def setup_logging() -> None:
    log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"),
    ]

    logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)

    logging.getLogger("uvicorn").handlers = handlers
    logging.getLogger("uvicorn.error").handlers = handlers
    logging.getLogger("uvicorn.access").handlers = handlers

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
