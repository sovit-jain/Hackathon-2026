import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.utils.log_redactor import LogRedactor

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "skillbridge.log"


class RedactingFilter(logging.Filter):
    """Logging filter that redacts sensitive information from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to redact sensitive data."""
        record.msg = LogRedactor.redact(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: LogRedactor.redact_value(v) for k, v in record.args.items()}
            elif isinstance(record.args, (tuple, list)):
                record.args = tuple(LogRedactor.redact_value(v) for v in record.args)
        return True


def setup_logging() -> None:
    log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"),
    ]

    # Add redacting filter to all handlers
    redacting_filter = RedactingFilter()
    for handler in handlers:
        handler.addFilter(redacting_filter)

    logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)

    logging.getLogger("uvicorn").handlers = handlers
    logging.getLogger("uvicorn.error").handlers = handlers
    logging.getLogger("uvicorn.access").handlers = handlers

    # Add redacting filter to uvicorn handlers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        for handler in logging.getLogger(logger_name).handlers:
            handler.addFilter(redacting_filter)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
